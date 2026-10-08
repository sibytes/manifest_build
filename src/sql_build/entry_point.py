import argparse
import logging

from .manifest_build import (
    Manifest,
    app_name,
    parse_argument_bool,
    parse_argument_catalog_name,
    parse_argument_string,
)


def build_manifest(
    catalog: str | None = None,
    component: str | None = None,
    manifest: str | None = None,
    group: str | None = None,
    manifest_path: str | None = None,
    root_path: str | None = None,
    dry_run: bool = False,
    enable_parse: bool = True,
):
    log = logging.getLogger(app_name)

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", nargs=1, default=None)
    parser.add_argument("--component", nargs=1, default=None)
    parser.add_argument("--manifest", nargs=1, default=None)
    parser.add_argument("--group", nargs=1, default=None)
    parser.add_argument("--root-path", nargs=1, default=None)
    parser.add_argument("--manifest-path", nargs=1, default=None)
    parser.add_argument("--enable-parse", nargs=1, default=None)
    parser.add_argument("--dry-run", nargs=1, default=None)
    args = parser.parse_known_args()
    log.info(f"{args}")

    MANIFEST_EXT = "yml"

    component = parse_argument_string(args, "component", component)
    environment, catalog = parse_argument_catalog_name(args, component, catalog)
    manifest = parse_argument_string(args, "manifest", manifest)
    manifest_path = parse_argument_string(args, "manifest_path", manifest_path)
    root_path = parse_argument_string(args, "root_path", root_path)
    group = parse_argument_string(args, "group", group)
    enable_parse = parse_argument_bool(args, "enable_pase", enable_parse)
    dry_run = parse_argument_bool(args, "dry_run", dry_run)

    Manifest.build_manifest(
        catalog=catalog,
        environment=environment,
        component=component,
        manifest_name=manifest,
        group=group,
        manifest_path=manifest_path,
        root_path=root_path,
        dry_run=dry_run,
        enable_parse=enable_parse,
        extension=MANIFEST_EXT,
    )
