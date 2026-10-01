import argparse
import logging
import os
from argparse import Namespace

from .manifest_build import Manifest
from .manifest_build._environment import Environment
from .manifest_build.logging_config import app_name


def get_src_path() -> str:
    deployment_root = "/Workspace/data_pipelines/sql_build/files"
    src = "src"
    path = os.getcwd()
    path = f"{path}/{src}"
    if not os.path.isdir(path):
        path = f"{deployment_root}/{src}"
    if not os.path.isdir(path):
        raise Exception(f"Cannot resolve path to sql source files. Path doesn't exist {path}")


def parse_argument_bool(args:Namespace, value:bool|str|None) -> Namespace:

    if value is None:
        value = args.name
        if isinstance(value, list):
            value = value[0]
        

    if value is None:
        raise ValueError(f"Argument '{args.name}' is required.")

    if isinstance(value, str):
        if value.lower() not in ["true", "false"]:
            raise ValueError(f"Argument '{args.name}' must be a boolean value (true/false). Received value: {value}")
        value = value.lower() == "true"

    return value

def parse_argument_string(args:Namespace, value:str|None) -> Namespace:

    if value is None:
        value = args.name
        if isinstance(value, list):
            value = value[0]

    if value is None:
        raise ValueError(f"Argument '{args.name}' is required.")

    return value

def parse_argument_environment(args:Namespace, value:str|None) -> Namespace:
    log = logging.getLogger(app_name)
    if value is None:
        value = args.name
        if isinstance(value, list):
            value = value[0]

    if value is None:
        raise ValueError(f"Argument '{args.name}' is required.")

    try:
        value = Environment(value)
    except Exception:
        exception_msg = f"Argument '{args.name}' must be a valid environment. Received value: {value}"
        raise ValueError(exception_msg)

    return value


def build_manifest(
        environment:str=None,
        manifest_name:str=None,
        group:str="",
        manifest_path:str=None,
        dry_run:bool=False
    ):

    log = logging.getLogger(app_name)

    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest_name", nargs=1, default=None)
    parser.add_argument("--group", nargs=1, default=None)
    parser.add_argument("--environment", nargs=1, default=None)
    parser.add_argument("--dry-run", nargs=1, default=None)
    parser.add_argument("--manifest-root", nargs=1, default=None)
    args = parser.parse_known_args()
    log.info(f"{args}")

    manifest_name = parse_argument_string(args, manifest_name)
    group = parse_argument_string(args, group)
    environment = parse_argument_environment(args, environment)
    dry_run = parse_argument_bool(args, dry_run)
    manifest_path = parse_argument_string(args, manifest_path)

    Manifest.build_manifest(
        environment=environment,
        manifest_path=manifest_path, 
        group=group, 
        manifest_name=manifest_name, 
        extension="yml",
        dry_run=dry_run
    )
    



