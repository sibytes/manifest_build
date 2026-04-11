import logging
import yaml
from ._environment import Environment
from dataclasses import dataclass, field
from .logging_config import app_name
import os
import glob
from enum import Enum
import jinja2
from databricks.sdk.runtime import spark

class Variable(Enum):
    catalog = "catalog"
    environment = "environment"

@dataclass
class Script():
    file:str
    variables:dict[Variable, str]
    sql:str | None = field(default=None)
    error:str | None = field(default=None)
    succeeded:bool = field(default=False)

    def __post_init__(self):
        log = logging.getLogger(app_name)
        log.info(f"Loading script {self.file}")
        with open(self.file, "r") as f:
            self.sql = f.read()

        self.sql = self.render_jinja(self.sql, self.variables)

    def run(self, dry_run:bool=False):
        log = logging.getLogger(app_name)
        log.info(f"Running script {self.file}")
        sql_commands = [s.strip() for s in self.sql.split(";")]

        for sql_command in sql_commands:
            if sql_command:
                try:
                    log.info(f"Running SQL command: {sql_command}")
                    if not dry_run:
                        spark.sql(sql_command)
                    self.succeeded = True
                except Exception as e:
                    log.error(f"Error running script {self.file}: {e}")
                    self.succeeded = False
                    self.error = str(e)
                    break


    def render_jinja(
            self, data:str, 
            replacements:dict[Variable, str]
        ) -> str:
        log = logging.getLogger(app_name)
        log.info(f"Rendering jinja for script {data} with replacements {replacements}")
        if data and isinstance(data, str):
            replace = {k.value: v for (k,v) in replacements.items()}
            skip = False
            for k,v in replace.items():
                if v is None and "{{" + k + "}}" in data.replace(" "):
                    skip = True
                    break
            if not skip:
                template: jinja2.Template = jinja2.Template(data)
                data = template.render(replace)
        log.info(f"Rendered jinja for script {data}")
        return data


@dataclass
class Manifest():
    manifest_file:str
    manifest:dict
    environment:Environment
    catalog:str | None = field(default=None)
    sql_project_root:str | None = field(default=None)
    scripts:list[Script] | None = field(default=None)
    errors:dict[str, str] | None = field(default=None)

    def load(self, group:str):
        log = logging.getLogger(app_name)
        try:
            self.catalog = self.manifest["manifest"]["catalog_name"]
        except Exception as e:            
            log.error(f"Error loading manifest file {self.manifest_file}: {e}")
            raise Exception(f"Error loading manifest file {self.manifest_file}: {e}")
    
        Manifest.validate_catalog_name(self.catalog, self.environment)
        
        try:
            self.sql_project_root = self.manifest["manifest"]["sql_project_root"]
        except Exception as e:            
            log.error(f"Error loading manifest file {self.manifest_file}: {e}")
            raise Exception(f"Error loading manifest file {self.manifest_file}: {e}")
        self.sql_project_root = os.getcwd() + "/" + self.sql_project_root

        try:
            script_group:list[str] = self.manifest["manifest"][group]["scripts"]
        except Exception as e:            
            log.error(f"Error loading manifest file {self.manifest_file}: {e}")
            raise Exception(f"Error loading manifest file {self.manifest_file}: {e}")
        
        self.scripts:list[Script] = []
        for script_file in script_group:
            glob_path = self.sql_project_root + "/" + script_file
            log.info(f"Loading script(s) {glob_path}")
            files = glob.glob(glob_path)
            for file in files:
                script:Script = Script(
                    file=file,
                    variables={
                        Variable.catalog: self.catalog,
                        Variable.environment: self.environment.value
                    }
                )
                self.scripts.append(script)

        log = logging.getLogger(app_name)

    def run(self, dry_run:bool=False):
        self.errors = {}
        for script in self.scripts:
            script.run(dry_run=dry_run)
            if not script.succeeded:
                self.errors[script.file] = script.error

    def raise_errors(self):
        if self.errors:
            error_messages = "\n".join([f"{file}: {error}" for file, error in self.errors.items()])
            raise Exception(f"Errors occurred while running manifest {self.manifest_file}:\n{error_messages}")


    @classmethod
    def validate_catalog_name(cls, catalog:str, environment:Environment) -> str:
        log = logging.getLogger(app_name)

        name_parts = catalog.split("_")
        envs = ",".join([e.value for e in Environment])
        exception_msg = f"catalog={catalog} must be a 2 or 3 part name. The prefix must be a valid environment ({envs}). The second part must be the name unified. The suffix can be any name. Examples: dev_unified, dev_unified_test, tst_unified"
        if not name_parts or len(name_parts) not in [2,3]:
            log.error(exception_msg)
            raise Exception(exception_msg)
        
        try:
            catalog_environment = Environment(name_parts[0])
        except Exception:
            log.error(exception_msg)
            raise Exception(exception_msg)
        
        if catalog_environment != environment:
            exception_msg = f"Catalog environment {catalog_environment} does not match manifest environment {environment}"
            log.error(exception_msg)
            raise Exception(exception_msg)
        
        try:
            if name_parts[1] != "unified":
                log.error(exception_msg)
                raise Exception(exception_msg)
        except Exception:
            log.error(exception_msg)
            raise Exception(exception_msg)

    
    @classmethod
    def _collect_manifest(
        cls,
        environment:Environment,
        manifest_name:str,
        manifest_path:str,
        extension:str
    )-> dict:
        
        log = logging.getLogger(app_name)
        manifest_file = f"{manifest_path}/{environment.name}/{manifest_name}.{extension}"
        log.info(f"Collecting manifest from {manifest_file}")
        log.info(f"Current working directory: {os.getcwd()}")

        with open(manifest_file, "r") as f:
            manifest = yaml.safe_load(f)
        
        manifest:Manifest = Manifest(
            environment=environment,
            manifest_file=manifest_file,
            manifest=manifest
        )

        return manifest
    
    @classmethod
    def build_manifest(
            cls,
            environment:Environment,
            manifest_name:str,
            group:str,
            manifest_path:str,
            extension:str="yml",
            dry_run:bool=False
    )->dict:
        
        manifest:Manifest = cls._collect_manifest(
            environment=environment,
            manifest_name=manifest_name,
            manifest_path=manifest_path,
            extension=extension
        )

        log = logging.getLogger(app_name)

        log.info(f"Loading manifest for group {group}")
        manifest.load(group=group)

        log.info(f"Running manifest for group {group}")
        manifest.run(dry_run=dry_run)

        manifest.raise_errors()
        
        return manifest