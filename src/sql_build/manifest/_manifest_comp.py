import glob
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

import jinja2
from databricks.sdk.runtime import spark

from ._default_statement import default_statement
from .exception import SqlBuildError, SqlBuildParseError, SqlBuildOptionError
from .logging_config import app_name


class Variable(Enum):
    catalog = "catalog"
    environment = "environment"


class ScriptType(Enum):
    catalog = "catalog"
    schema = "schema"
    volume = "volume"
    view = "view"
    table = "table"
    function = "function"
    procedure = "procedure"

@dataclass
class Options:
    allow_drop_tables: bool
    allow_drop_catalogs: bool
    allow_delete_where: bool

    def __post_init__(self):

        self._not_allowed = []
        if not self.allow_drop_tables:
            self._not_allowed.append("DROP TABLE")
        if not self.allow_drop_catalogs:
            self._not_allowed.append("DROP CATALOG")
        if not self.allow_delete_where:
            self._not_allowed.append("DELETE WHERE")


    def __str__(self):
        values = [f"\n\t{a}: {v}" for a, v in self.__dict__.items()]
        values = "".join(values)
        return f"Manifest options:{values}"

    def check(self, parse_result:dict[UUID, list[dict]], file:str):
        option_errors: list[SqlBuildOptionError] = []
        if self._not_allowed:
            for statements in parse_result:
                if statements and isinstance(statements, dict):
                    statement = statements.get("statement_identifier", None)
                    if statement in self._not_allowed:
                        option_errors.append(SqlBuildOptionError(statement=statement, file=file))

        return option_errors
    
@dataclass
class Script:
    file: str
    variables: dict[Variable, str]
    catalog: str
    use_catalog: bool
    enable_parse: bool
    options:Options
    sql: str | None = field(default=None)
    parse_result: str | None = field(default=None)
    error: str | None = field(default=None)
    succeeded: bool = field(default=False)
    parse_errors: list[SqlBuildParseError|SqlBuildOptionError] | None = field(default=None)
    key: UUID | None = field(default=uuid4())
    type: ScriptType | None = field(default=None)

    def __post_init__(self):
        log = logging.getLogger(app_name)
        log.info(f"Loading script {self.file}")
        with open(self.file, "r") as f:
            self.sql = f.read()

        self.sql = self.render_jinja(self.sql, self.variables)
        self.parse_errors = self._parse_sql(self.sql)

    def _parse_sql(self, sql: str):
        log = logging.getLogger(app_name)

        parse_errors: list[SqlBuildParseError|SqlBuildOptionError] = []

        if not self.enable_parse:
            log.warning(f"SQL Parsing disabled, Skipping parsing script {self.file}")
            return parse_errors

        else:
            log.info(f"Parsing script {self.file}")
            parse_result = spark.sql(
                """
                select parse_sql({sql}) as result
            """,
                sql=sql,
            )
            self.result = json.loads(parse_result.collect()[0]["result"])

            for result in self.result:
                parse_success: bool = result["parse_success"]
                if not parse_success:
                    parse_errors.append(SqlBuildParseError(parse_error=result, file=self.file, sql=sql))
            self.result = default_statement(sql, self.result)

            option_errors:list[SqlBuildParseError|SqlBuildOptionError] = self.options.check(parse_result=self.result, file=self.file)
            parse_errors.extend(option_errors)

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
    execution_order: int
    manifest: object
    scripts: dict[UUID, Script] | None = field(default=None)

    def __post_init__(self):
        self._load_group_script()

    def get_parse_errors(self):
        parse_errors: list[SqlBuildParseError] = []
        for script in self.scripts.values():
            if script.parse_errors:
                parse_errors.extend(script.parse_errors)

        if parse_errors:
            return parse_errors
        else:
            return None

    def _load_group_script(self):
        log = logging.getLogger(app_name)
        self.scripts = {}

        try:
            script_group: list[str] = self.manifest.manifest["manifest"][self.group]["scripts"]
        except (KeyError, TypeError) as e:
            error_msg = f"Error loading manifest file {self.manifest.manifest_file}: {e}"
            raise SqlBuildError(error_msg)

        for script_file in script_group:
            glob_path = self.manifest.sql_project_root + "/" + script_file
            log.info(f"Loading script(s) {glob_path}")
            files = glob.glob(glob_path)
            if not files:
                error_msg = f"No files found for script {script_file} with glob path {glob_path} in manifest {self.manifest.manifest_file}"
                raise SqlBuildError(error_msg)

            for file in files:
                key = uuid4()
                script: Script = Script(
                    options=self.manifest.options,
                    catalog=self.manifest.catalog,
                    use_catalog=self.group != "catalog",
                    file=file,
                    variables={
                        Variable.catalog: self.manifest.catalog,
                        Variable.environment: self.manifest.environment.value,
                    },
                    enable_parse=self.manifest.enable_parse,
                    key=key,
                )

                self.scripts[key] = script
