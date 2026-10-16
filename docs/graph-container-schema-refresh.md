# Retained container schema refresh

`scan_estate_graph.py` accepts an optional `container_schemas` array in an investigator-authenticated job. It is forbidden in `federated_scanner` jobs; scanner tokens never reach SQL. Each entry has `identity`, the existing Microsoft reader `config`, and `owners`. The owner map uses exact `fabric://workspace/item` keys already declared by the job. Each value is a list of existing target-catalog objects with `asset_id`, `connection`, `database`, and `catalog.metadata.schema_name/name`.

The existing gateway must already admit that investigator, server, database, exact user objects, and CATALOG control. This configuration grants nothing. The job uses the existing shared meter and guarded SQL worker; at most eight exact tables share one bounded catalog query, with fewer than 250 total column rows. Every result must attest the configured investigator, database, engine, and read-only guard. Policy and budget refusals stop the job.

This refresh establishes complete column enumeration only for the exact declared retained tables. All retained tables under an owner must be covered. A missing declared table, invisible table, empty result, duplicate column, wrong identity, or row limit refuses the owner refresh. No partially assembled payload is published; old tables and columns remain intact and the owner is marked unavailable. A complete per-table response may remove a formerly retained column from that table.

Retained parent metadata and locations are preserved byte-for-byte with their original observation timestamps. Fresh column assets and a `GraphSchemaEvidence` asset retain the new native catalog proof. Retention timestamps cannot be assigned to changed content. Catalog and graph publication still share the existing revision-checked transaction.

This is not a complete database inventory: newly created or permission-hidden tables outside the declared list are not discovered. The proof explicitly says `complete_database_inventory: false`. SQL endpoint items without owned retained table assets remain unavailable; they cannot borrow another Lakehouse owner's children. Existing general discovery's `VISIBLE_OBJECTS_ONLY` inventory is not used as replacement authority because it cannot prove that absent tables were deleted.

No additional permission, authentication audience, or gateway allowance is created. An operator must prepare a separate investigator job with existing exact-object scopes; the Contributor scanner job continues to refuse SQL.
