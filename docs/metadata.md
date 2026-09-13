# Metadata inventory

Phase 4A provides a local backend collector and versioned SQLite inventory. It reads live metadata; it does not refresh data, inject defects, or infer lineage. The next phase derives lineage from these stored definitions.

## Run

From the repository root on the existing Windows development machine:

```powershell
python scripts/metadata_inventory.py --config infra/metadata/development.json
python scripts/validate_metadata_inventory.py
```

Prerequisites: the configured Fabric CLI Python environment and its signed-in identity, and the encrypted SQL credential referenced by the configuration file. The collector also uses the CLI virtualenv Python for the OneLake metadata fallback. No LLM key is required. SQL catalog reads use the scoped investigator identity. Fabric definition retrieval uses the already authenticated enterprise identity; Microsoft's read-definition endpoint requires item read/write permission despite performing a read operation.

Outputs are ignored local files:

- `.local/metadata/inventory.sqlite`: immutable scan snapshots, normalized assets and capability observations.
- `.local/metadata/latest.json`: latest scan ID, collection status and counts.
- SQL catalog transfer uses a unique temporary file per run, removed after ingestion; no shared intermediate file is used.

A scan is `COMPLETE` when all attempted capabilities succeed, `PARTIAL` when an attempted capability is unavailable, or `FAILED` when the top-level collection fails. This is collection status, not data-health or freshness certification. Explicit `UNKNOWN` and `NOT_COLLECTED` observations may exist in a complete scan. Never equate missing metadata with an absent asset or a healthy layer.

## Stored contract

Each asset has a stable source-scoped ID, parent ID, kind, name, source endpoint, acquisition time, SHA-256 definition hash and JSON metadata. IDs for SQL objects/columns use catalog IDs; Fabric items use service IDs; model children use their names within the parent; report pages/visuals use native definition IDs/paths. Renaming a name-based child changes its identity; future lineage reconciliation must account for that.

Each scan preserves a separate copy of its assets, including unchanged ones. A new scan does not overwrite the previous snapshot. Removed assets are absent from the new inventory; compare scans only after considering capability coverage. Failed capability extraction rolls back its assets before recording the gap. Definition payloads remain in SQLite, never written to service-supplied filesystem paths.

Collected metadata:

- SQL objects, columns, types, nullability, defaults/computed definitions, unique/primary keys, foreign keys, checks and visible module definitions. `VIEW DEFINITION` is checked at the granted `app` schema scope.
- Fabric workspace items, lakehouse table listings, notebook/pipeline/copy-job definitions and available recent job history.
- Power BI semantic tables/columns, explicit DAX measures, relationships and refresh history; report definition parts, pages, visuals, bindings and filter context.

Definitions and history provide inputs for later lineage and freshness diagnosis. History retention is controlled by the service. Scans span multiple requests and are not atomic snapshots of the external systems; acquisition timestamps and content hashes are retained for this reason.

## Explicit limits

- This is a CLI/backend persistence milestone, not a hosted metadata API or UI.
- Business owner mappings and expected refresh frequency are unknown until verified/configured. Technical access holders are not automatically business owners.
- SQL schema modification timestamps are not data watermarks. Business-data freshness and Delta table version collection are not implemented by this catalog collector. The standard table listing does not return Silver/Gold column schemas; the OneLake fallback includes Bronze column details.
- Schema-enabled lakehouses use a live OneLake table API fallback when the standard table listing fails. It discovers schemas and table details using a storage token from the existing Fabric CLI identity, held only in memory. Unsupported listings remain explicit gaps; local definitions are not substituted. This helper depends on the installed Fabric CLI 1.7.0 authentication interface and runs in its virtualenv.
- TMSL is requested for semantic definitions; unsupported formats fail visibly. Report normalization targets the native PBIR format used by the deployed reports; the raw returned definition remains available for inspection.
- Local snapshots can contain internal definitions and metadata. They stay under `.local/` and are not committed. Raw CLI exception messages are not stored because they may include authentication details. Gaps retain the exception type and source endpoint for targeted diagnosis.
- No automated owner notification or GitHub bug creation occurs during collection.

## Validation

Offline tests cover paginated discovery, untrusted continuation rejection, repeated continuation detection, asynchronous definition result retrieval, failed operations, snapshot preservation and report filter retention. CI runs these tests without Azure access.

Microsoft contracts used: [item definitions](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item-definition), [job history](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/list-item-job-instances), and [lakehouse tables](https://learn.microsoft.com/en-us/rest/api/fabric/lakehouse/tables/list-tables).

OneLake fallback contract: [Delta table API](https://learn.microsoft.com/en-us/fabric/onelake/table-apis/delta-table-apis-get-started).

The live validation command checks parent references, all 29 expected lakehouse tables, source foreign keys, semantic/report counts, and exact DAX equality with the version-controlled deployment. It is an explicit POC regression check, not discovery logic; model/report changes require updating the validation contract.

Live scan `a2ca371b-6377-444b-ae5d-d41c91baf9eb`: COMPLETE, 476 records, no unavailable attempted capabilities. Regression validation PASS: 29 lakehouse tables, 11 source foreign-key relationships, 25 exact DAX expressions, five semantic relationships, four report pages and 45 visuals. Eight offline contract tests pass. No business data or service definitions were changed.

## Reusable connection configuration

`infra/metadata/development.json` contains only connection settings and credential references: SQL hostname/database, schema for the visibility check, DPAPI credential-file path, Fabric workspace, expected enterprise tenant, CLI Python path and output database. Copy it to `.local/metadata-config.json` and edit it for a different environment. Relative paths resolve against the repository root, independent of the shell working directory. Use a separate output directory for each environment. Unknown fields and unsupported authentication modes are rejected; never put passwords or access tokens in this file.

```powershell
python scripts/metadata_inventory.py --config .local/metadata-config.json
```

The SQL hostname currently uses Azure SQL's port 1433. Database names are passed to a connection-string builder and the schema visibility check uses a SQL parameter. The configured schema controls the visibility check, not a filter on discovered objects: the inventory includes objects visible to the chosen identity.

## Connector and authentication boundaries

- `MetadataConnector` exposes discovery, definition retrieval and refresh-history methods, with declared capabilities. SQL explicitly reports refresh history as unsupported.
- `SqlMetadataConnector` accepts a catalog reader. The local `PowerShellSqlCatalog` adapter supplies DPAPI authentication; a future hosted driver can implement the reader contract without changing normalization/storage.
- `FabricMetadataConnector` accepts an HTTP transport and OneLake table reader. `PowerBIMetadataConnector` shares that transport for semantic/report definitions and uses the Power BI API for refresh history.
- `MetadataHttp` accepts a `TokenProvider`. It only permits metadata GET requests and Fabric `getDefinition` POST requests to fixed Microsoft service endpoints, with redirects disabled.
- `WorkerTransport` runs the development authentication worker in the configured CLI Python environment. The worker silently acquires tokens through the existing CLI identity, checks the token tenant against configuration, and returns metadata only. Tokens are not sent through command arguments, stdout or configuration.
- `AzureCredentialTokens` adapts an injected Azure Identity credential's `get_token()` method. This is an extension point, not a deployed service identity. The configuration factory currently supports only the verified local `fabric_cli` and SQL `dpapi_file` modes. No app registration, tenant permission or cloud identity was changed.

For a hosted deployment, construct an approved Azure Identity credential and inject it into `MetadataHttp` through `AzureCredentialTokens`; provide a corresponding table reader and SQL catalog reader. Service identity permissions and endpoint support must be verified then. See Microsoft's [Azure Identity credential contract](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python) and [Fabric identity support](https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support). Key Vault integration and a hosted configuration API remain later work.

## Refactor parity

`compare_metadata_scans.py --baseline <scan-id> --current <scan-id>` compares stable IDs, parents, kinds, names and metadata for two complete scans in the same database. It ignores only the SQL database acquisition timestamp; definitions, DAX and filters must remain identical. Changing collection provenance or run history does not alter asset identity and is tracked separately in observations. Use `--database` for a non-default inventory. This comparison is distinct from the POC-specific count/DAX validation.

The local SQL adapter retries a small set of transient Azure SQL connection errors at most three times, with five-second delays. Authentication/permission errors are not retried. No query or business transaction is retried by this adapter.

Refactor live evidence: scan `5d11f419-0596-412a-9002-1971b3fed6ad` completed with 476 records and no failed attempted capabilities. Parity against `a2ca371b-6377-444b-ae5d-d41c91baf9eb` passed with zero added, removed or changed assets; only the SQL acquisition timestamp is excluded. The POC validation also passed. Sixteen offline metadata tests and two generator tests passed.
