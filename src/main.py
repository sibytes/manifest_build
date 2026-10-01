from sql_build.entry_point import build_manifest

build_manifest(
    catalog="dev_unified",
    component="unified",
    manifest="dev_unified.audit_full_rebuild",
    group="",
    manifest_path="./ci/sql_build",
    root_path="/Users/shaunryan/dev/databricks/sql_build",
    dry_run=False
)
