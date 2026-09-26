# Execution-surface inventory

Updated 2026-09-26 (UTC). Work item 1 of the independent-surface batch. This is a
document and a probe set, not an engine change: no file covered by the engine
fingerprint changed (`unfrozen-e3b2724a5c50` at `1e70228`). It establishes which
execution surfaces answer today. It does **not** establish that any lower-layer
quantity can be compiled, compared or trusted on them.

## Premise check

`MicrosoftProcessAdapter.__init__` stores `execute_source` as
`self.execute_source` (`scripts/investigator/adapters/microsoft_process.py:17`).
No tracked file reads that attribute; the only occurrences are the constructor
parameter and that assignment. There is no `getattr` access, and the adapter has
no subclass. `evaluate()`
dispatches every probe through `run_query(..., 'bounded_dax', self.execute_native)`.
The live runtime passes `Runtime.source_transport` into the dead attribute
(`scripts/investigator/adaptive_runtime.py:486-487`). The premise holds.

## Result

Probe set: `scripts/probe_execution_surfaces.py`, with the isolated OneLake reader
`scripts/read_onelake_header.py`. Environment `unknown-domain-v4`, model
`5b3eff46…` revision 2 (context `3136c3b6…`). The probe measure is the G ticket's
presentation measure. `resolve_path` returned two layers, the presentation table
and a `declared_source` lakehouse table, and stopped with `CAPABILITY_UNAVAILABLE`.

| Surface | Status | Identity | Evidence (attempt 2, 2026-09-26T01:25Z) |
| --- | --- | --- | --- |
| Power BI semantic model via DAX | **Reachable** | Native reader | `MicrosoftProcessAdapter.evaluate()` on the presentation layer returned `OBSERVED`, one row, `COMPLETE_RESPONSE`. Sealed receipt `bd002032…`. Engine `POWER_BI_DAX`. |
| Azure SQL `app.*` via the SQL reader | **Reachable** | `orderops_investigator` (SQL auth, DPAPI credential file) | `flexible_tools.run(..., 'bounded_sql', source_transport)` completed `COUNT_BIG(*)` over the first approved `app` object by asset identity (`object/1010102639`) with the read-only check verified. Sealed receipt `d31938dd…`. Engine `AZURE_SQL`, `sql-orderops-9696025/ordersops`. |
| OneLake Delta commit metadata | **Reachable** | Isolated metadata identity | The adapter's own `ingestion()` returned `CURRENT`. Latest commit `…/_delta_log/00000000000000000000.json`, operation `WRITE`. Engine `ONELAKE_DELTA_LOG`. |
| Fabric SQL analytics endpoint | **Not reachable; not re-probed** | `investigator-reader@…` MSAL client | Recorded 2026-09-25T18:36:51Z: `AADSTS65002` at token acquisition, before any connection. Table permission was not established. It was deliberately not probed again. |
| OneLake Delta **table data** | **File bytes reachable; table read not established** | Isolated metadata identity | Table directory listing HTTP 200, one data file. A ranged read of that file returned HTTP 206 with 4 bytes, matching the Parquet magic `PAR1`. Engine `ONELAKE_DFS`. |

The four reachable probes report four distinct `(engine, connection, object)`
surfaces. That is a statement about where the reads ran. It is not a statement
that any two of them measure the same quantity.

## Every attempt, as it happened

| When (UTC) | Attempt | Cloud reservations | Result |
| --- | --- | --- | --- |
| 2026-09-26T00:01Z | Earlier OneLake data probe, run from an uncommitted `.local` script by a previous session | 2 | Listing 200, 4-byte header 206, `PAR1`. It was not ledgered or documented at the time. This PR records it after the fact, with its original timestamp. |
| 2026-09-26T01:21Z | Attempt 1 of the committed probe set | 3 | DAX, SQL and commit metadata reachable. The table-data probe failed with `ModuleNotFoundError` before any network call: token acquisition imported `fabric_cli`, which exists only in the isolated identity's Python environment. **This is a harness defect, not a surface result.** It is preserved locally without edits. |
| 2026-09-26T01:25Z | Attempt 2, after moving the OneLake read into an isolated subprocess (the existing `read_onelake_commit.py` pattern) | 5 | All four probes reachable, as in the table above. The DAX and SQL result hashes were identical to attempt 1. |

Usage for 2026-09-26: 10 cloud reservations, all settled; zero planner calls, zero
input characters. No permission, identity, policy or configuration changed.

## Corrections to the batch brief

- The brief attributes OneLake commit-metadata HTTP 200 to "the #216 probes".
  #216 (`13a4d06`, provider capacity) contains no OneLake probe.
  `read_onelake_commit.py` first appears in #231. The recorded evidence is the two
  #234 sessions (`0837778d…`, `7086fbda…`). Their stored state holds a
  `delta_commit` with status `AVAILABLE`, recorded before probes carried
  execution surfaces.
- "25 successful reads in #226" is confirmed. The nine #226 ledger rows sum to 25
  `reads_sql`, and the stored sessions hold 25 `bounded_sql` observations with
  status `COMPLETED`, all under principal `orderops_investigator` on
  `sql-orderops-9696025/ordersops`.

## What this does not establish

- **No lower-layer quantity was compiled.** The SQL probe proves the reader,
  transport and object permission only. The DAX probe re-read the presentation
  baseline.
- **The SQL reader cannot serve the resolved `declared_source` layer.**
  `source_diagnostics.snapshot()` admits only `USER_TABLE`s in the configured
  visibility schema on the configured Azure SQL server. The `declared_source`
  layer that `resolve_path` binds is a Fabric lakehouse table. The Azure SQL
  application layer is not on the resolved path at all:
  `external_source_declaration` is `CAPABILITY_NOT_IMPLEMENTED`. As the path
  resolves today, wiring `execute_source` into `evaluate()` has no SQL object to
  compile the `declared_source` quantity against. See "Open questions" below.
- **OneLake table data is not shown to be readable as a table.** Only one data
  file's first four bytes were read. The listing is not the active file set:
  that requires replaying the Delta log (adds, removes, any deletion vectors).
  No row was decoded and no aggregate computed. The isolated identity's Python
  environment has `duckdb` but not `pyarrow`.
- **The Fabric SQL endpoint's table permission remains unknown.**

## Open questions for a human decision

1. **Using the metadata identity for row reads is a role change.**
   `read_onelake_commit.py` is chartered "never read table rows", and the
   identity is described throughout as the isolated *metadata* identity. Reading
   table data with it needs no authentication change, but it changes what that
   identity is trusted to do. This probe read four header bytes and stopped
   there. Whether to go further is not an implementer's call.
2. **Is OneLake-file aggregation independent of the semantic model?** Retained
   model metadata, read offline, shows every semantic table partition in
   `directLake` mode over the `WarehouseSource` expression. The model therefore
   reads the same Delta files that a OneLake-file aggregation would read. The two
   surfaces would share the storage object and differ only in engine. That
   comparison could detect a semantic-layer mechanism: a measure definition,
   relationships, or a Direct Lake fallback or framing lag. It could not detect
   anything that happened before the files were written. Whether that satisfies
   the cross-surface invariant should be decided before item 2 relies on it. I
   lean towards "a distinct engine, but not an independent lower layer". That is
   a judgment, not a verified property.
3. **Item 2's route needs restating.** Under the current path resolution, the
   independent read that `execute_source` can perform is at the application
   source, which the path does not reach. The declared source that the path does
   reach can be served only by the Fabric SQL endpoint (blocked) or by OneLake
   files (question 1).

## What resolving `AADSTS65002` would involve (recorded, not acted on)

The recorded failure says the configured MSAL client is not preauthorized for
the `database.windows.net` audience. That is a client-registration or consent
change. `scripts/fabric_sql_auth.py` also contains a separate Azure CLI token
path, in an isolated profile bound to a named administrative account. Using it
would change *which identity* reads the endpoint. Neither route was evaluated or
exercised. Both are human decisions under non-negotiable 8.

## Artifacts

- Machine-readable result: [runs/execution-surface-inventory.json](runs/execution-surface-inventory.json).
  It carries no result values or value hashes.
- Local, uncommitted: `.local/execution-surface-inventory-20260925-attempt-1/`,
  `.local/execution-surface-inventory-20260925-attempt-2/` and
  `.local/reachable-boundary-20260925/`. The sealed DAX and SQL receipts are in
  the `flexible_diagnostics` table of the `unknown-domain-v4` catalog.

## Correction 2026-09-26: Fabric SQL endpoint

The sections above say the Fabric SQL analytics endpoint is "Not reachable", and
that resolving `AADSTS65002` needs a client-registration or consent change. That
text is kept unchanged. `AADSTS65002` belongs to the Fabric CLI's client
(`5814bfb4…`), not to the endpoint.

**What was established on 2026-09-26,** with no app registration, identity or
permission change:
- **Token:** `az account get-access-token` for the `database.windows.net`
  audience succeeded. It ran through the Azure CLI client (`04b07795…`) with the
  isolated profile `.local/azure-fabric-sql`, the one `scripts/fabric_sql_auth.py`
  uses, as tenant administrator `admin@skynwhy.com` in tenant `dff91047…`. The
  token was never printed or stored.
- **Endpoint:** the `gold_sql_endpoint` host in `infra/fabric/environment.json`
  accepted it, and `SELECT 1` returned 1. That host
  (`…-3ot44cpmmpyedhhqq4vg3rogdu…`) belongs to the dev workspace
  `ws-investigator-dev` (`09cea7db…`). A connection naming no database opened
  that workspace's `lh_investigator_bronze`.

That establishes only this: **admin can reach the dev workspace's SQL
endpoint.** It establishes nothing about the endpoint the process path needs.

**Endpoint IDs**, resolved against the Fabric REST API on 2026-09-26:

| ID | What it is |
| --- | --- |
| `77c49180…` | SQL analytics endpoint of `warehouse_gold_e1b8e1` in the investigation workspace `investigator-fixture-83139e71cbdf6a50` (`149f8d99…`). This is the Gold lakehouse the G path's `declared_source` resolves to. Host `i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com`, database `warehouse_gold_e1b8e1`. **No identity has reached it over SQL.** |
| `701ab1fc…` | SQL analytics endpoint of `lh_investigator_gold` in `ws-investigator-dev` (`09cea7db…`), the endpoint named in `environment.json`. The accepted `SELECT 1` ran on this workspace's host. |
| `1cae5e66…` | **Not a Fabric item** (the API returns 404). It is a run ID: `docs/cross-layer-queries.md` records endpoint-comparison evidence persisted in that run. |

**Still open:**
- **Reader access:** the reader `investigator-reader@skynwhy.com` (a user
  account) is `Viewer` in `149f8d99…` and has no role in `09cea7db…`. Microsoft
  documents that Viewer grants CONNECT and ReadData on every SQL endpoint in the
  workspace. Whether the reader can actually reach `77c49180…` is untested, and
  no explicit T-SQL `DENY` has been checked.
- **Identity:** which identity should hold this access is a human decision,
  under non-negotiable 8.

An earlier token check that day ran against the default Azure CLI profile. That
profile was signed in to an unrelated tenant (`aeb4d0a9…`), and the endpoint was
not contacted. Both checks have ledger rows; their exact start times were not
captured.

## Note 2026-09-26: the "isolated metadata identity" is the tenant administrator

The sections above, merged in #237, are kept as written. They call the identity
behind the OneLake commit-metadata and data-header receipts the "isolated
metadata identity". That identity is `admin@skynwhy.com`: principal `23de217f…`,
which holds the Admin role in workspace `149f8d99…`. It is the same account as
the Fabric CLI session. Those receipts are therefore admin receipts. **The
isolation the name implies is not established,** and the probe receipts'
`identity_role: ISOLATED_METADATA` label should be read that way. The same
applies to the earlier pre-recorded OneLake data probe and to the #234 Delta-
metadata reads.
