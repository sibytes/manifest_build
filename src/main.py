from sql_build.entry_point import build_manifest

build_manifest(
    "dev",
    "dev_unified.audit_full_rebuild",
    "catalog",
    dry_run=True
)
