from sql_build.entry_point import build_manifest

build_manifest(
    environment="dev",
    manifest_path="./ci/sql_build",
    manifest_name="dev_unified.audit_full_rebuild",
    group="",
    dry_run=False
)

# build_manifest(
#     environment="dev",
#     manifest_path="./ci/sql_build",
#     manifest_name="dev_unified.audit_full_rebuild",
#     group="catalog",
#     dry_run=False
# )

# build_manifest(
#     environment="dev",
#     manifest_path="./ci/sql_build",
#     manifest_name="dev_unified.audit_full_rebuild",
#     group="schema",
#     dry_run=False
# )

# build_manifest(
#     environment="dev",
#     manifest_path="./ci/sql_build",
#     manifest_name="dev_unified.audit_full_rebuild",
#     group="pre_build",
#     dry_run=False
# )

# build_manifest(
#     environment="dev",
#     manifest_path="./ci/sql_build",
#     manifest_name="dev_unified.audit_full_rebuild",
#     group="tables",
#     dry_run=False
# )