import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

import jinja2
from databricks.sdk.runtime import spark

from .exception import SqlBuildParseError
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
