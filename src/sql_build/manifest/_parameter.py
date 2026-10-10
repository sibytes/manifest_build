import logging
from argparse import Namespace

from . import Environment
from .exception import SqlBuildParameterError
from .logging_config import app_name
from .manifest import Manifest


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


def parse_argument_string_list(
    args: Namespace | tuple, name: str, value: str | None, default: str | None = None
) -> str:
    log = logging.getLogger(app_name)

    if isinstance(args, tuple):
        args = args[0]

    log.debug(f"parse_argument_string: args={args}, name={name}, value={value}, default={default}")

    if isinstance(value, str):
        value = value.strip()

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

    list_value: list[str] = value.split(",")
    list_value = [v.strip() for v in list_value]

    return list_value


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

    return Manifest.validate_catalog_name(catalog=catalog, component=component)
