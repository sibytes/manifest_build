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
        raise ValueError(f"Cannot resolve path to sql source files. Path doesn't exist {path}")


def parse_argument_bool(args: Namespace, value: bool | str | None, default: bool | None = None) -> Namespace:

    if isinstance(value, bool):
        return value
    
    if value is None:
        value = args.name
        if isinstance(value, list):
            value = value[0]

    if value is None:
        if not isinstance(default, bool):
            raise ValueError(f"Argument '{args.name}' is required unless a default value of type bool is provided.")
        else:
            value = default

    if isinstance(value, str):
        if value.lower() not in ["true", "false"]:
            raise ValueError(f"Argument '{args.name}' must be a boolean value (true/false). Received value: {value}")
        value = value.lower() == "true"

    return value


def parse_argument_string(args: Namespace, value: str | None) -> Namespace:

    if isinstance(value, str):
        value = value.strip()
        return value

    if value is None:
        value = args.name
        if isinstance(value, list):
            value = value[0]

    if value is None:
        if not isinstance(value, str):
            raise ValueError(f"Argument '{args.name}' is required unless a default value of type str is provided.")
        else:
            value = value.strip()

    return value


# def parse_argument_environment(args: Namespace, value: str | None) -> Namespace:
#     log = logging.getLogger(app_name)
#     if value is None:
#         value = args.name
#         if isinstance(value, list):
#             value = value[0]

#     if value is None:
#         raise ValueError(f"Argument '{args.name}' is required.")

#     try:
#         value = Environment(value)
#     except Exception:
#         exception_msg = f"Argument '{args.name}' must be a valid environment. Received value: {value}"
#         raise ValueError(exception_msg)

#     return value

def parse_catalog_name(args: Namespace, component_name: str,  catalog: str | None):
    if catalog is None:
        catalog = args.catalog
        if isinstance(catalog, list):
            catalog = catalog[0]
    if not isinstance(catalog, str):
        raise TypeError("Argument 'catalog' of type string is required.")

    name_parts = catalog.split("_")
    envs = ",".join([e.value for e in Environment])
    exception_msg = f"catalog={catalog} must be a 2 or 3 part name. the prefix must be a valid environment of {envs}. The 2nd part must be the name `{component_name}`. The postfix is optional."

    if not name_parts or len(name_parts) not in (2,3):
        raise ValueError(exception_msg)

    try:
        environment = Environment(name_parts[0])
    except (ValueError, IndexError):
        raise ValueError(exception_msg)

    try:
        if name_parts[1] != component_name:
            raise ValueError(exception_msg)
    except IndexError:
        raise ValueError(exception_msg)

    return environment, catalog

def build_manifest(
    catalog: str|None = None,
    component: str|None = None,
    manifest: str|None = None,
    group: str|None = None,
    manifest_path: str|None = None,
    root_path: str|None = None,
    dry_run: bool = False,
):

    log = logging.getLogger(app_name)

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", nargs=1, default=None)
    parser.add_argument("--component", nargs=1, default=None)
    parser.add_argument("--manifest", nargs=1, default=None)
    parser.add_argument("--group", nargs=1, default=None)
    parser.add_argument("--root-path", nargs=1, default=None)
    parser.add_argument("--manifest-path", nargs=1, default=None)
    parser.add_argument("--dry-run", nargs=1, default=None)
    args = parser.parse_known_args()
    log.info(f"{args}")

    MANIFEST_EXT = "yml"

    catalog = parse_argument_string(args, catalog)
    
    
    environment, catalog = parse_catalog_name(args, component, catalog)

    component = parse_argument_string(args, component)
    manifest = parse_argument_string(args, manifest)
    manifest_path = parse_argument_string(args, manifest_path)
    root_path = parse_argument_string(args, root_path)
    group = parse_argument_string(args, group)
    dry_run = parse_argument_bool(args, dry_run)

    Manifest.build_manifest(
        catalog=catalog,
        environment=environment,
        component=component,
        manifest_name=manifest,
        group=group,
        manifest_path=manifest_path,
        root_path=root_path,
        dry_run=dry_run,
        extension=MANIFEST_EXT,
    )
