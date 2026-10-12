from sql_build.entry_point import deploy_manifest

deploy_manifest(
    catalog="dev_sql_build",
    component="sql_build",
    manifest="dev_sql_build.full_rebuild",
    group="",
    manifest_path="./ci/sql_build",
    root_path="/Users/shaunryan/dev/databricks/sql_build",
    dry_run=False,
    output_path="./sql_build_output",
    enable_parse=True,
)
