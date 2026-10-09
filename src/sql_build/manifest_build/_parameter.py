import logging
from argparse import Namespace

from . import Environment
from .exception import SqlBuildParameterError
from .logging_config import app_name


def parse_argument_bool(
    args: Namespace | tuple, name: str, value: bool | str | None, default: bool | None = None
) -> bool:
    log = logging.getLogger(app_name)

    if isinstance(args, tuple):
        args = args[0]

    log.debug(f"parse_argument_bool: args={args}, name={name}, value={value}, default={default}")

    if isinstance(value, bool):
        return value

    if value is None:
        arg_dict = vars(args)
        value = arg_dict[name]
        log.debug(f"parse_argument_bool: args={args}, name={name}, value={value}, default={default}")
        if isinstance(value, list):
            value = value[0]

    if value is None:
        if not isinstance(default, bool):
            raise SqlBuildParameterError(
                f"Argument '{name}' is required unless a default value of type bool is provided."
            )
        else:
            value = default

    if isinstance(value, str):
        if value.lower() not in ["true", "false"]:
            raise SqlBuildParameterError(
                f"Argument '{name}' must be a boolean value (true/false). Received value: {value}"
            )
        value = value.lower() == "true"

    return value


def parse_argument_string(args: Namespace | tuple, name: str, value: str | None, default: str | None = None) -> str:
    log = logging.getLogger(app_name)

    if isinstance(args, tuple):
        args = args[0]

    log.debug(f"parse_argument_string: args={args}, name={name}, value={value}, default={default}")

    if isinstance(value, str):
        value = value.strip()
        return value

    if value is None:
        arg_dict = vars(args)
        value = arg_dict[name]
        if isinstance(value, list):
            value = value[0]
        log.debug(f"parse_argument_string: args={arg_dict}, name={name}, value={value}, default={default}")

    if value is None:
        if not isinstance(default, str):
            raise SqlBuildParameterError(
                f"Argument '{name}' is required unless a default value of type str is provided."
            )
        else:
            value = default

    return value


def parse_argument_environment(args: Namespace | tuple, name: str, value: str | None) -> Namespace:
    log = logging.getLogger(app_name)

    if isinstance(args, tuple):
        args = args[0]

    log.debug(f"parse_argument_environment: args={args}, name={name}, value={value}")

    if value is None:
        arg_dict = vars(args)
        value = arg_dict[name]
        log.debug(f"parse_argument_environment: args={args}, name={name}, value={value}")
        if isinstance(value, list):
            value = value[0]

    if value is None:
        raise SqlBuildParameterError(f"Argument '{name}' is required.")

    try:
        value = Environment(value)
    except ValueError:
        exception_msg = f"Argument '{name}' must be a valid environment. Received value: {value}"
        raise SqlBuildParameterError(exception_msg)

    return value


def parse_argument_catalog_name(args: Namespace | tuple, component: str, catalog: str | None):
    log = logging.getLogger(app_name)

    if isinstance(args, tuple):
        args = args[0]

    log.debug(f"parse_argument_catalog_name: args={args}, component={component}, catalog={catalog}")

    if catalog is None:
        catalog = args.catalog

        if isinstance(catalog, list):
            catalog = catalog[0]

        log.debug(f"parse_argument_catalog_name: args={args}, component={component}, catalog={catalog}")

    if not isinstance(catalog, str):
        raise SqlBuildParameterError("Argument 'catalog' of type string is required.")

    name_parts = catalog.split("_")
    envs = ",".join([e.value for e in Environment])
    exception_msg = f"catalog={catalog} must be a 2 or 3 part name. the prefix must be a valid environment of {envs}. The 2nd part must be the name `{component}`. The postfix is optional."

    if not name_parts or len(name_parts) not in (2, 3):
        raise SqlBuildParameterError(exception_msg)

    try:
        environment = Environment(name_parts[0])
    except (ValueError, IndexError):
        raise SqlBuildParameterError(exception_msg)

    try:
        if name_parts[1] != component:
            raise ValueError(exception_msg)
    except IndexError:
        raise SqlBuildParameterError(exception_msg)

    return environment, catalog
