import glob
import logging
from dataclasses import dataclass, field
from typing import Final

import yaml

from ._environment import Environment
from ._manifest_comp import Group, Options
from ._script import Script, Variable
from .exception import SqlBuildError, SqlBuildParameterError, SqlBuildParseError, SqlBuildRuntimeError
from .logging_config import app_name


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
    options: Options | None = field(default=None)
    _HEADERS: Final[tuple[str, ...]] = ("name", "sql_project_root", "catalog_name", "options")

    def parse(self, group: str | list[str] = ""):
        log = logging.getLogger(app_name)
        log.info(f"Loading manifest for group {group}")

        self._set_header()
        self._set_options()
        self._set_groups(group)
        self._collect_parse_errors()
        self.raise_parse_errors()

    def _set_header(self):

        log = logging.getLogger(app_name)
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

    def _set_options(self):
        log = logging.getLogger(app_name)

        allow_drop_tables = False
        allow_drop_catalogs = False

        try:
            options: dict[str, bool] = self.manifest["manifest"]["options"]
            allow_drop_catalogs = options.get("allow_drop_tables", allow_drop_catalogs)
            allow_drop_tables = options.get("allow_drop_tables", allow_drop_tables)

        except (ValueError, TypeError):
            log.warning(
                """Failed to find options in manifest header at manifest.options. Applying non-destructive default options:
                \tallow_drop_catalogs: False
                \tallow_drop_tables: False"""
            )
            allow_drop_tables = False
            allow_drop_catalogs = False

        self.options = Options(allow_drop_catalogs=allow_drop_catalogs, allow_drop_tables=allow_drop_tables)
        log.info(str(self.options))

    def _set_groups(self, group: list[str]):

        log = logging.getLogger(app_name)
        self.groups: list[Group] = []
        groups: set[str] = []
        manifest: dict = self.manifest["manifest"]

        match group:
            case None | [] | [""]:
                groups = [grp for grp in manifest if grp not in self._HEADERS]
            case [*_]:
                groups = group
            case _:
                raise TypeError

        for grp in groups:
            if grp not in manifest:
                msg = f"Warning loading manifest file {self.manifest_file}: group called {grp} is not defined in the manifest"
                raise SqlBuildParameterError(msg)

            try:
                manifest_group = manifest[grp]
                execution_order: int = int(manifest_group.get("execution_order", 0))
            except (ValueError, TypeError):
                execution_order = 0
                warning_msg = f"Warning loading manifest file {self.manifest_file}: integer execution_order for group {grp} is not defined"
                log.warning(warning_msg)

            # load the script files defined in that group
            scripts: list[Script] = self._load_group_script(grp)
            # create a group type and add to class list
            self.groups.append(Group(group=grp, scripts=scripts, execution_order=execution_order))

        # sort them in order they are defined to execut
        self.groups.sort(key=lambda grp: grp.execution_order)

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
    def validate_catalog_name(cls, catalog: str, component: str, environment: Environment = None):
        log = logging.getLogger(app_name)
        log.info(f"Validating catalog name {catalog}, component {component}, environment {environment}")

        name_parts = catalog.split(component)
        envs = ",".join([e.value for e in Environment])
        exception_msg = f"catalog={catalog} must be a 2 or 3 part name. the prefix must be a valid environment of {envs}. The 2nd part must be the name `{component}`. The postfix is optional."

        if not name_parts or len(name_parts) not in (1, 2):
            raise SqlBuildParameterError(exception_msg)

        try:
            catalog_environment = name_parts[0].removesuffix("_")
            catalog_environment = Environment(catalog_environment)
        except (ValueError, IndexError):
            raise SqlBuildParameterError(exception_msg)

        if environment is not None and catalog_environment != environment:
            raise SqlBuildParameterError(
                f"Environment in the catalog name '{catalog_environment.name}' and is not the environment it is being validated against '{environment.name}'"
            )

        try:
            catalog_component = catalog.removeprefix(name_parts[0]).removesuffix(name_parts[1])
            if catalog_component != component:
                raise ValueError(exception_msg)
        except IndexError:
            raise SqlBuildParameterError(exception_msg)

        return catalog_environment, catalog

    @classmethod
    def load(
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
