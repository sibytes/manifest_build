import glob
import json
import logging
from dataclasses import dataclass, field
from enum import Enum

import jinja2
import yaml
from databricks.sdk.runtime import spark

from ._environment import Environment
from .exception import SqlBuildCatalogNameError, SqlBuildError, SqlBuildParseError, SqlBuildRuntimeError
from .logging_config import app_name


class Variable(Enum):
    catalog = "catalog"
    environment = "environment"


@dataclass
class Script:
    file: str
    variables: dict[Variable, str]
    catalog: str
    use_catalog: bool
    enable_parse: bool
    sql: str | None = field(default=None)
    error: str | None = field(default=None)
    succeeded: bool = field(default=False)
    parse_errors: list[SqlBuildParseError] | None = field(default=None)

    def __post_init__(self):
        log = logging.getLogger(app_name)
        log.info(f"Loading script {self.file}")
        with open(self.file, "r") as f:
            self.sql = f.read()

        self.sql = self.render_jinja(self.sql, self.variables)
        self.parse_errors = self._parse_sql(self.sql)

    def _parse_sql(self, sql: str):
        log = logging.getLogger(app_name)
        log.info(f"Parsing script {self.file}")
        parse_result = spark.sql(
            """
            select parse_sql({sql}) as result
        """,
            sql=sql,
        )
        result = parse_result.collect()[0]["result"]
        statements: list = json.loads(result)
        parse_errors: list[SqlBuildParseError] = []

        for statement in statements:
            parse_success: bool = statement["parse_success"]
            if not parse_success:
                parse_errors.append(SqlBuildParseError(parse_error=statement, file=self.file, sql=sql))

        return parse_errors

    def run(self, dry_run: bool = False):
        log = logging.getLogger(app_name)
        log.info(f"{self.catalog}: Running script on {self.file}")
        if self.use_catalog:
            use_sql = f"USE CATALOG {self.catalog}"
            log.debug(use_sql)
            if not dry_run:
                try:
                    spark.sql(use_sql)
                except Exception as e:  # noqa: BLE001
                    self.succeeded = False
                    self.error = str(e).split("\n")[0]

        sql_commands = [self.sql]
        if self.sql.strip().startswith("--!script"):
            sql = self.sql.replace("--!script;", "")
            sql_commands = [s.strip() for s in sql.split(";")]

        for sql_command in sql_commands:
            if sql_command:
                log.debug(f"Running SQL command: {sql_command}")
                if not dry_run:
                    try:
                        spark.sql(sql_command)
                    except Exception as e:  # noqa: BLE001
                        self.succeeded = False
                        self.error = str(e)
                        self.error = self.error.split("JVM stacktrace", maxsplit=1)[0]
                        self.error = self.error.strip()
                        log.error(self.error)
                        break

                    self.succeeded = True

    def render_jinja(self, data: str, replacements: dict[Variable, str]) -> str:
        log = logging.getLogger(app_name)
        log.debug(f"Rendering jinja for script {data} with replacements {replacements}")
        if data and isinstance(data, str):
            replace = {k.value: v for (k, v) in replacements.items()}
            skip = False
            for k, v in replace.items():
                if v is None and "{{" + k + "}}" in data.replace(" "):
                    skip = True
                    break
            if not skip:
                template: jinja2.Template = jinja2.Template(data)
                data = template.render(replace)
        log.debug(f"Rendered jinja for script {data}")
        return data


@dataclass
class Group:
    group: str
    scripts: list[Script]
    execution_order: int

    def get_parse_errors(self):
        parse_errors: list[SqlBuildParseError] = []
        for script in self.scripts:
            if script.parse_errors:
                parse_errors.extend(script.parse_errors)

        if parse_errors:
            return parse_errors
        else:
            return None


@dataclass
class Manifest:
    catalog: str
    component: str
    root_path: str
    manifest_file: str
    manifest: dict
    environment: Environment
    sql_project_root: str | None = field(default=None)
    groups: list[Group] = field(default=None)
    runtime_errors: list[SqlBuildRuntimeError] | None = field(default=None)
    parse_errors: list[SqlBuildParseError] | None = field(default=None)
    enable_parse: bool | None = field(default=True)

    def parse(self, group: str | list[str] = ""):
        log = logging.getLogger(app_name)
        log.info(f"Loading manifest for group {group}")

        try:
            manifest_catalog = self.manifest["manifest"]["catalog_name"]
        except KeyError as e:
            error_msg = f"Error loading manifest file {self.manifest_file}: {e}"
            raise SqlBuildError(error_msg)

        if manifest_catalog != self.catalog:
            raise SqlBuildError(
                f"The manifest catalog {manifest_catalog} name does not match the catalog argument {self.catalog}"
            )

        log.info(
            f"Validating catalog: {self.catalog} with component: {self.component} and environment: {self.environment.name}"
        )
        Manifest.validate_catalog_name(self.catalog, self.component, self.environment)

        try:
            self.sql_project_root = self.manifest["manifest"]["sql_project_root"]
        except (KeyError, TypeError) as e:
            error_msg = f"Error loading manifest file {self.manifest_file}: {e}"
            raise SqlBuildError(error_msg)

        self.sql_project_root = self.root_path + "/" + self.sql_project_root
        log.info(f"Project root path: {self.sql_project_root}")
        self.groups: list[Group] = []

        if isinstance(group, str) and group == "":
            for grp, data in self.manifest["manifest"].items():
                if grp in ["name", "catalog_name", "sql_project_root"]:
                    continue

                try:
                    execution_order: int = int(data.get("execution_order", 0))
                except (ValueError, TypeError):
                    execution_order = 0
                    warning_msg = f"Warning loading manifest file {self.manifest_file}: integer execution_order for group {grp} is not defined"
                    raise Warning(warning_msg)

                self.groups.append(
                    Group(group=grp, scripts=self._load_group_script(grp), execution_order=execution_order)
                )
            self.groups.sort(key=lambda grp: grp.execution_order)

        elif isinstance(group, str) and group != "":
            self.groups.append(Group(group=group, scripts=self._load_group_script(group), execution_order=0))
        elif isinstance(group, list):
            for g in group:
                if not isinstance(g, str) or not g:
                    error_msg = f"Invalid group type {type(g)} for group {g} in manifest {self.manifest_file}. Group must be a string."
                    raise SqlBuildError(error_msg)
                self.groups.append(Group(group=g, scripts=self._load_group_script(g), execution_order=0))
        else:
            error_msg = f"Invalid group type {type(group)} for group {group} in manifest {self.manifest_file}"
            raise SqlBuildError(error_msg)

        self._collect_parse_errors()
        self.raise_parse_errors()

    def _collect_parse_errors(self):
        self.parse_errors = []
        for grp in self.groups:
            grp_parse_errors = grp.get_parse_errors()
            if grp_parse_errors:
                self.parse_errors.extend(grp_parse_errors)

    def _load_group_script(self, group: str):
        log = logging.getLogger(app_name)
        scripts: list[Script] = []

        try:
            script_group: list[str] = self.manifest["manifest"][group]["scripts"]
        except (KeyError, TypeError) as e:
            error_msg = f"Error loading manifest file {self.manifest_file}: {e}"
            raise SqlBuildError(error_msg)

        for script_file in script_group:
            glob_path = self.sql_project_root + "/" + script_file
            log.info(f"Loading script(s) {glob_path}")
            files = glob.glob(glob_path)
            if not files:
                error_msg = f"No files found for script {script_file} with glob path {glob_path} in manifest {self.manifest_file}"
                raise SqlBuildError(error_msg)

            for file in files:
                script: Script = Script(
                    catalog=self.catalog,
                    use_catalog=group != "catalog",
                    file=file,
                    variables={Variable.catalog: self.catalog, Variable.environment: self.environment.value},
                    enable_parse=self.enable_parse,
                )
                scripts.append(script)

        return scripts

    def run(self, dry_run: bool = False):
        log = logging.getLogger(app_name)
        log.info(f"Running manifest for group {self.manifest}")
        self.runtime_errors = []
        for group in self.groups:
            log.info(f"Running group {group.group} with execution order {group.execution_order}")
            for script in group.scripts:
                script.run(dry_run=dry_run)
                if not script.succeeded:
                    self.runtime_errors.append(
                        SqlBuildRuntimeError(group=group.group, file=script.file, error=script.error)
                    )
        self.raise_runtime_errors()

    def raise_runtime_errors(self, log_and_continue: bool = False):
        log = logging.getLogger(app_name)
        if self.runtime_errors:
            error_messages = "\n".join([error.message for error in self.runtime_errors])
            if log_and_continue:
                log.error(f"Errors occurred while running manifest {self.manifest_file}:\n{error_messages}")
            else:
                raise SqlBuildError(f"Errors occurred while running manifest {self.manifest_file}:\n{error_messages}")

    def raise_parse_errors(self, log_and_continue: bool = False):
        log = logging.getLogger(app_name)
        if self.parse_errors:
            error_messages = "\n".join([error.message for error in self.parse_errors])
            if log_and_continue:
                log.error(f"Errors occurred while parsing manifest {self.manifest_file}:\n{error_messages}")
            else:
                raise SqlBuildError(f"Errors occurred while parsing manifest {self.manifest_file}:\n{error_messages}")

    @classmethod
    def validate_catalog_name(cls, catalog: str, component: str, environment: Environment) -> str:
        log = logging.getLogger(app_name)
        log.info(f"Validating catalog name {catalog}, component {component}, environment {environment}")

        name_parts = catalog.split("_")
        envs = ",".join([e.value for e in Environment])
        exception_msg = f"catalog={catalog} must be a 2 or 3 part name. The prefix must be a valid environment ({envs}). The second part must be the name {component}. The suffix can be any name. Examples: dev_{component}, dev_{component}_test, tst_{component}"
        if not name_parts or len(name_parts) not in [2, 3]:
            raise SqlBuildCatalogNameError(exception_msg)

        try:
            catalog_environment = Environment(name_parts[0])
        except (IndexError, ValueError):
            raise SqlBuildCatalogNameError(exception_msg)

        if catalog_environment != environment:
            exception_msg = (
                f"Catalog environment {catalog_environment} does not match manifest environment {environment}"
            )
            raise SqlBuildCatalogNameError(exception_msg)

        try:
            if name_parts[1] != component:
                raise SqlBuildCatalogNameError(exception_msg)
        except IndexError:
            raise SqlBuildCatalogNameError(exception_msg)

    @classmethod
    def collect_manifest(
        cls,
        catalog: str,
        component: str,
        root_path: str,
        environment: Environment,
        manifest: str,
        manifest_path: str,
        extension: str,
        enable_parse: bool,
    ) -> dict:
        
        log = logging.getLogger(app_name)
        manifest_file = f"{root_path}/{manifest_path}/{environment.name}/{manifest}.{extension}"
        log.info(f"Collecting manifest from {manifest_file}")

        with open(manifest_file, "r") as f:
            manifest = yaml.safe_load(f)

        manifest: Manifest = Manifest(
            catalog=catalog,
            component=component,
            root_path=root_path,
            environment=environment,
            manifest_file=manifest_file,
            manifest=manifest,
            enable_parse=enable_parse,
        )

        return manifest
