import logging
import argparse
from databricks.sdk.runtime import spark
from argparse import Namespace
from .manifest_build.logging_config import app_name


def parse_argument_string(args:Namespace, value:str|None) -> Namespace:

    if value is None:
        value = args.name
        if isinstance(value, str):
            value = value[0]

    if value is None:
        raise ValueError(f"Argument '{args.name}' is required.")

    return value


def build_manifest(catalog:str=None):

    log = logging.getLogger(app_name)

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", nargs=1, default=None)
    args = parser.parse_known_args()
    log.info(f"{args}")

    catalog = parse_argument_string(args, catalog)




