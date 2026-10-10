from sql_build.entry_point import deploy_manifest

deploy_manifest(
    catalog="dev_sql_build",
    component="sql_build",
    manifest="dev_sql_build.audit_full_rebuild",
    group="",
    manifest_path="./ci/sql_build",
    root_path="/Users/shaunryan/dev/databricks/sql_build",
    dry_run=False,
)
