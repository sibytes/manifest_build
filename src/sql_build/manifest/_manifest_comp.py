import glob
import logging
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from ._script import Script, Variable
from .exception import SqlBuildError, SqlBuildParseError
from .logging_config import app_name


@dataclass
class Group:
    group: str
    execution_order: int
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
            script_group: list[str] = self.manifest["manifest"][self.group]["scripts"]
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
                key = uuid4()
                script: Script = Script(
                    catalog=self.catalog,
                    use_catalog=self.group != "catalog",
                    file=file,
                    variables={Variable.catalog: self.catalog, Variable.environment: self.environment.value},
                    enable_parse=self.enable_parse,
                    key=key,
                )

                self.scripts[key] = script
