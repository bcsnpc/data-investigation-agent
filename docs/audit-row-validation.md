# Round Three A3: audit validation and endpoint lag

## Dated Warehouse-route supersession, 2026-10-04 UTC

The human declined the prepared OneLake grant and approved a single Warehouse
audit table instead. No OneLake role changed. Earlier blocked-route proposal
below is historical. The workspace Warehouse listing was empty, so a small
isolated `round_three_ops_audit_20261004` was chosen:
`bea673e0-a206-461e-9b2f-1b3b827e80de`. Existing Gold objects are lakehouse SQL
surfaces. The old lakehouse audit table remains unchanged and unused by the
producer.

Only the pipeline's audit writer changed, to a T-SQL Script activity.
CopyApplication was preserved unchanged. The writer uses the successful copy
activity's own nested counters/times, refuses missing/invalid values and inserts
once per pipeline run. No recount or invented watermark. A NULL-status guard
was corrected before the load; both served definitions are preserved.

### Explicit human identity-scope decision

Existing administrator `admin@skynwhy.com` through `.local/azure-fabric-sql`
applied exactly:

```sql
GRANT SELECT ON OBJECT::[dbo].[load_run_audit] TO [investigator-reader@skynwhy.com];
```

Before: reader principal listing `[]`, explicit object permission listing `[]`.
After: `investigator-reader@skynwhy.com`, `EXTERNAL_USER`; `SELECT`, `GRANT`
on this table only. No write/admin, workspace, other table or OneLake grant.
Pre-existing Viewer access was not removed. Sealed before/grant/after:
`warehouse-setup.json`, `warehouse-grant.json`, `warehouse-after.json`.
The ledger, delivery record here and identity manifest record the same decision.

### First pipeline run and independent reader check

Pipeline `ac4b3e8d-9cdb-427e-a9dc-380ac15a50ec` completed 15:31:36.540 UTC;
Script succeeded, one affected row. The guarded Warehouse query as
`investigator-reader` returned exactly its row: **360 read / 360 written**,
matching copy `rowsRead` / `rowsCopied`, run ID and own activity start/end:
15:29:43.7928961 / 15:30:55.2959412 UTC. Watermark remains NULL.
Query-bound identity, Warehouse engine and database match; connection remains
unattested. Four physical requests: one diagnostic query, three safety checks.
Receipts: `warehouse-pipeline-first-run.json`, `warehouse-reader-verification.json`.

Reported load meters: Copy 480,000 CPU-core-ms; InvokeCopyJob 0.03333333333333333
AzureIR billable hours; Script 0.016666666666666666. These are reported meters,
not a monetary estimate.

Schema collection is scoped to explicitly declared Warehouse audit tables,
using the approved reader. The producer compiles discovered columns and requires
query-bound attestation. Lakehouse SQL audit sources refuse with
`LAKEHOUSE_SQL_AUDIT_SYNC_LAG`; see
[adapter known limits](../scripts/investigator/adapters/known-platform-limits.md).
Policy/context integration, A4-A6 and four scenarios remain next; no source
outcome claimed here. Engine changes invalidate prior freezes.

Last observed Part B **381/500**, rolling **521/1000**, diagnostic cap **12**.
Pipeline used five physical requests; verification four. Original records intact.

Dated integration completion: scoped reader catalog recollection returned all
nine Warehouse columns and re-approved the full configuration under hash
`738f75c8a0393692070c589125b5490f30dfea821ce64c367f8be3ce0449ae54`.
Discovery `22355d55-a282-45d1-98d5-cca051b02786` projected application model
context `bf45ac5b-c1e3-4643-a901-c87f77751c71` (revision 6). Unchanged metadata
was retained with its earlier acquisition provenance, not silently rescanned.
The producer executed through that context and returned CURRENT with the same
360/360 own counters; receipt `aa919240-653c-4ada-9fb2-2fc2dcb813ce`, PARTIAL
coverage, matching identity/engine/object, connection unattested. A local helper
initially selected the creation-result shape instead of detailed properties;
that zero-read failure is preserved separately before the resumed check.

131 focused regressions passed, including scoped Warehouse discovery, reader
attestation and lakehouse-audit refusal. A standalone earlier SQL helper had
omitted the initial identity request from its meter. Its original row is
preserved; an appended correction charges that already-observed request once,
with no new query. Latest Part B **390/500**, rolling **530/1000**, diagnostic
cap **12**. A3 integration is complete; A4-A6 and scenarios remain pending.

2026-10-04 UTC. A3 remains incomplete. No scenario re-run, fixture mutation or
permission change. Original Round Two artifacts and ledger rows are preserved.
Engine changes invalidate previous freezes.

## Per-row validation

Each malformed row is named by original index, bounded run identity and reason,
then excluded. Valid covering rows are ordered by their own start timestamps.
No valid covering row means UNAVAILABLE. A valid latest failed, in-progress,
cancelled or not-started run cannot be hidden by an older success. Distinct tied
latest runs still refuse. Exclusions survive original-receipt validation and
engine rendering. Successful accounting establishes the latest valid record,
not that no later run exists.

Seven new regressions cover these invariants and original-receipt tampering.
110 focused tests passed across audit rows, source delivery, audit adapter,
system of record, process debugging and synthesis. Initial planner directory
content is unchanged. CI is tracked on the PR.

## Delta versus SQL

Investigator-reader's direct OneLake listing returned HTTP 403:

> User is not authorized to perform current operation for workspace
> '149f8d99-1c66-4a0a-9624-759be002bb60', artifact
> '33618b8d-46eb-4fe7-b80b-122c331260a3'.

The explicitly authorised administrator diagnostic read served the same Delta
log and the two committed data files. These are administrator observations,
never investigation-reader attestations.

| Delta version | Commit UTC | Pipeline run | Own rows read / written | Copy start / end UTC |
| --- | --- | --- | --- | --- |
| 2 | 05:27:27.704 | 293c0cd7-8f1f-4e74-8278-2dfafee4a04f | 361 / 361 | 05:26:01.7731559 / 05:26:24.5916107 |
| 3 | 05:38:04.185 | 13ab6783-eeb2-4521-85f8-2ab6d74ab10e | 360 / 360 | 05:36:40.2253523 / 05:37:00.4531747 |

Both commits insert one audit row, with no removed file or deletion vector.
Full Parquet rows establish the run IDs and counters; commit statistics were
not substituted for accounting. Watermarks remain unavailable.

The preserved gap SQL read was admitted at 05:33:47.963836 UTC and returned without
run 293c0cd7. Delta committed that row at 05:27:27.704: SQL omitted a committed
row at least **6 minutes 20.259836 seconds** after commit. A new reader SQL
response at 06:54:15.941351 exposes both newer rows alongside the earlier
success and malformed row. Actual convergence occurred between observations;
its exact time was not measured. This establishes endpoint synchronization lag
for the earlier missing row, not writer failure or a usual lag duration.

The new SQL query self-reported identity, Microsoft Azure SQL Data Warehouse
engine and database object. Connection remains unattested. One diagnostic query
and two guards were charged. No administrator SQL read substituted for it.

[Microsoft documents asynchronous lakehouse endpoint metadata sync](https://learn.microsoft.com/en-us/fabric/data-engineering/sql-analytics-endpoint-metadata-sync).
The observed timestamps establish this estate's lag.

## Non-lagging route remains blocked before a scope change

The audit should live in a Warehouse or be read directly from committed Delta
by an authorised reader. Never call a stale lakehouse SQL last-run view load
latency. The existing reader cannot use the direct route. The complete OneLake
role listing served only DefaultReader, using ReadAll-based virtual membership.

A table-only role request is prepared, not applied, at
`.local/round-three-20261004/audit-reader-role-grant-prepared.json`. It preserves
DefaultReader unchanged and adds only Read on `/Tables/dbo/load_run_audit` for
investigator-reader. No ReadAll, workspace role, write or other table is proposed.
The [documented role API](https://learn.microsoft.com/en-us/rest/api/fabric/core/onelake-data-access-security/create-or-update-data-access-roles)
supports an explicit table path and named Entra member. A fresh before listing
and server ETag must guard application against changed prior state.

CLAUDE.md section 8 requires an explicit human decision before a new identity
scope. No PUT was made. Direct audit execution and attestation integration are
not yet implemented; a permission grant alone would not establish them.

## Receipts and budgets

Five sealed probe records under `.local/round-three-20261004`:
`audit-delta-reader-listing.json`, `audit-delta-admin-listing.json`,
`audit-delta-admin-rows.json`, `audit-sql-current.json`,
`audit-onelake-role-before.json`. Hashes and count-only rows are appended to the
ledger. Ten physical requests: five metadata requests, two administrator-only
Parquet diagnostic reads, one reader SQL diagnostic query, two SQL guards.
An appended type correction separates the two Parquet reads from their two log
metadata reads; it charges no additional requests and preserves the original row.
Zero model calls or fixture changes.
Part B **358/500**, rolling last observed **498/1000**, diagnostic cap **12**.
No new pipeline run or load cost. A3's non-lagging reader integration and A4-A6
must finish before the four outcomes are attempted.
