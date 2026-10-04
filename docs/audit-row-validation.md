# Round Three A3: audit validation and endpoint lag

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

The preserved gap SQL receipt was persisted at 05:33:47.963836 UTC without
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
ledger. Ten physical requests: seven metadata/direct diagnostic-file requests,
one SQL diagnostic query, two SQL guards. Zero model calls or fixture changes.
Part B **358/500**, rolling last observed **498/1000**, diagnostic cap **12**.
No new pipeline run or load cost. A3's non-lagging reader integration and A4-A6
must finish before the four outcomes are attempted.
