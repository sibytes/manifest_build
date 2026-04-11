import logging
import yaml
from ._environment import Environment
from dataclasses import dataclass, field
from .logging_config import app_name

@dataclass
class Script():
    file:str
    sql:list[str]
    result:dict | None = field(default=None)
    succeeded:bool = field(default=False)

    def load(self):
        log = logging.getLogger(app_name)

    def run(self):
        log = logging.getLogger(app_name)

@dataclass
class ScriptGroup():
    name:str | None = field(default=None)
    glob:str | None = field(default=None)
    scripts:list[Script] | None = field(default_factory=None)
    result:dict | None = field(default=None)
    succeeded:bool = field(default=False)

    def load(self):
        log = logging.getLogger(app_name)

    def run(self):
        log = logging.getLogger(app_name)

@dataclass
class Manifest():
    manifest_file:str
    manifest:dict
    catalog:str | None = field(default=None)
    environment:Environment | None = field(default=None)
    script_group:ScriptGroup | None = field(default=None)

    def load(self, group:str):
        log = logging.getLogger(app_name)

    def run(self):
        log = logging.getLogger(app_name)
        self.script_group.run()

    def _parse_catalog_name(self, catalog:str) -> str:
        log = logging.getLogger(app_name)

        name_parts = catalog.split("_")
        envs = ",".join([e.value for e in Environment])
        exception_msg = f"catalog={catalog} must be a 2 or 3 part name. The prefix must be a valid environment ({envs}). The second part must be the name unified. The suffix can be any name. Examples: dev_unified, dev_unified_test, tst_unified"
        if not name_parts or len(name_parts) not in [2,3]:
            log.error(exception_msg)
            raise Exception(exception_msg)
        
        try:
            environment = Environment(name_parts[0])
        except Exception:
            log.error(exception_msg)
            raise Exception(exception_msg)
        
        try:
            if name_parts[1] != "unified":
                log.error(exception_msg)
                raise Exception(exception_msg)
        except Exception:
            log.error(exception_msg)
            raise Exception(exception_msg)
        
        return environment, catalog
    
    @classmethod
    def _collect_manifest(
        object,
        manifest_name:str,
        manifest_path:str,
        extension:str
    )-> dict:
        
        log = logging.getLogger(app_name)
        manifest_file = f"{manifest_path}/{manifest_name}.{extension}"
        log.info(f"Collecting manifest from {manifest_file}")

        with open(manifest_file, "r") as f:
            manifest = yaml.safe_load(f)
        
        manifest:Manifest = Manifest(
            manifest_file=manifest_file,
            manifest=manifest
        )

        return manifest
    
    def build_manifest(
            object,
            manifest_name:str,
            group:str,
            manifest_path:str,
            extension:str
    )->dict:
        
        manifest:Manifest = object._collect_manifest(
            manifest_name=manifest_name,
            manifest_path=manifest_path,
            extension=extension
        )

        log = logging.getLogger(app_name)

        log.info(f"Loading manifest for group {group}")
        manifest.load(group=group)

        log.info(f"Running manifest for group {group}")
        manifest.run(group=group)
        
        return manifest