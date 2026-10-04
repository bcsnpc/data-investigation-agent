# Round-two workspace monitoring: authorized attempt and blockers

2026-10-03 UTC. The user approved enablement only in fixture workspace
`149f8d99-1c66-4a0a-9624-759be002bb60`, a read-only monitoring-database grant to
`orderops_investigator`, no write/admin/ingest/other-resource access, at most four
probes and one additional isolated load within the existing Part B budget.
This explicit decision is appended to the ledger. It is not permission to
substitute another account or elevate a workspace role.

## Learn findings, followed by the enablement attempt

[Copy Job workspace monitoring](https://learn.microsoft.com/en-us/fabric/data-factory/copy-job-workspace-monitoring)
documents one activity record per source/destination mapping in
`CopyJobActivityRunDetailsLogs`. Fields include parent CopyJobRunId, activity
RunId, source/destination names, status/times and `RowsRead`/`RowsWritten` (long),
plus data/file/throughput/error metrics. This is the job's own accounting surface,
not a destination query total. These are documented fields, not observed values.

[Enable monitoring](https://learn.microsoft.com/en-us/fabric/fundamentals/enable-workspace-monitoring)
documents a workspace-admin UI route under Workspace settings > Monitoring and
creation of the monitoring Eventhouse/database. The Data Factory article describes
the Log workspace activity switch. Current
[overview](https://learn.microsoft.com/en-us/fabric/fundamentals/workspace-monitoring-overview)
also describes a monitoring item whose collection starts off and must be turned
on, no backfill, and query access for workspace users with at least Contributor.
The legacy get-started overview also describes sharing restrictions. These are
documentation/version findings: the fixture's UI and per-database grant behavior
have not been observed, so no actual permission refusal is claimed from them.

Step 2 was attempted regardless of those documented restrictions. The computer-use
surface inventory returned **apps=[] and browsers=[]**. Creating an in-app tab
returned exactly **Browser is not available: iab**. A separate Chrome entry-point
attempt also returned **Browser is not available: chrome**. Thus the documented UI setting
could not be operated in this session. Searches found no supported workspace
monitoring enablement endpoint; this is a bounded search finding, not proof none
exists. The similarly named
[OneLake modifyDiagnostics API](https://learn.microsoft.com/en-us/rest/api/fabric/core/onelake-settings/modify-diagnostics)
sends OneLake diagnostics to a lakehouse; it is not this feature and was not called.
An ordinary manually created Eventhouse would not establish that workspace logging
is enabled, so none was provisioned as a substitute.

Publisher control-plane GETs of the exact fixture workspace items before and after
the failed UI attempt both returned HTTP 200 with complete, unpaginated listings.
Both contained zero Eventhouse, KQLDatabase and Eventstream items. No enabling
mutation was sent. No monitoring resource ID/query endpoint exists in these
responses; the monitoring toggle itself was not read. Do not report a confirmed
Disabled flag, enabled collection, or an accounting-query failure from this evidence.

## Requested identity, approval, and why no grant script was executed

The explicit human authorization was:

> Grant the reader identity orderops_investigator read-only (viewer/query) access
> to that monitoring KQL database only. Do not grant write, admin, or ingest
> rights, and do not grant access to any other database or workspace.

A metadata-only statement executed with the existing SQL reader credential:

```sql
SELECT CURRENT_USER AS reader, DB_NAME() AS database_name,
       type_desc, authentication_type_desc
FROM sys.database_principals
WHERE name = CURRENT_USER
```

The first connection was refused with `SourceReadFailed`, SqlException **40613**,
stage connect. Its charged reservation and sealed result are retained. A separate
fourth admission, after the database resumed, returned:

```json
{"reader":"orderops_investigator","database_name":"ordersops",
 "type_desc":"SQL_USER","authentication_type_desc":"DATABASE"}
```

This is a contained SQL-authentication principal, not an Entra identity token.
[Kusto authentication](https://learn.microsoft.com/en-us/kusto/access-control/?view=microsoft-fabric)
requires an Entra token for the Kusto service, and
[database role commands](https://learn.microsoft.com/en-us/kusto/management/manage-database-security-roles?view=microsoft-fabric)
assign roles to supported Entra principals. The normal viewer-only command needs
both a real database and a resolved Entra principal. Neither exists for this
requested grant here. There is therefore **no executable exact grant script**
that can truthfully grant this contained SQL user the requested KQL access.
No `.add`/`.set` command was sent, no dummy `aaduser=orderops_investigator` was
constructed, and no SQL permission statement was represented as a KQL grant.
Before/after KQL permission reads were **not performed: no target database**.
The SQL principal-kind check is not a substitute KQL permission check.

`investigator-reader@skynwhy.com` is the separate, configured Entra Fabric reader;
it was not substituted or given a new audience/scope/role under this approval.
An identically named newly created Entra user would also be a new identity, not
the existing contained SQL principal. No registration, identity creation,
workspace Contributor elevation or permission change occurred.

## Probe result and budget

| Admission | Actual operation | Result |
| --- | --- | --- |
| 1 | SQL reader principal metadata preparation | Connection 40613; no query result |
| 2 | Publisher fixture workspace item listing before UI attempt | HTTP 200, no monitoring resources |
| 3 | Publisher fixture workspace item listing after UI attempt | HTTP 200, no monitoring resources |
| 4 | Separate SQL reader principal metadata check after resume | SQL_USER / DATABASE established |

Four conservative charged admissions, comprising three completed metadata requests
and one failed connection preparation. Zero diagnostic operations, KQL queries,
guard requests, investigation/model calls or additional Copy Job loads. This
uses the requested maximum four-probe batch; it is **not** four successful queries.
No read-policy change, refill or refund. Part B **33 -> 37 / 120**; ordinary rolling
usage observed **197 -> 201 / 300**. Prior row prefixes and receipts unchanged.
Documentation lookups and UI availability observations are not estate read requests.

Result recorded literally: **accounting unavailable from this surface**.
Reason: requested monitoring surface was not created and its requested SQL
principal cannot authenticate to KQL. It was not queried; no claim that an existing
monitoring table returned empty or refused the reader. No counts estimated,
substituted or copied from the 360-row source. The additional load was not run
because no authorized accounting query could follow it. The prior successful
load and least-privilege REST history capability from #344 remain unchanged.

## Deferred disable/removal instructions; no cleanup executed

Once monitoring is actually enabled, disable only this fixture workspace's data
collection in Workspace settings > Monitoring (Log workspace activity/data
collection Off). Use that setting's delete/remove monitoring database control to
remove its monitoring Eventhouse; the current monitoring-item UI may expose the
lifecycle controls there instead. Capture the generated Eventhouse/database IDs,
confirm they belong to this fixture workspace, retain needed logs, and obtain
then-current deletion authorization before removing them. Verify collection and
item state after any future change. Do not delete the source lakehouse or Copy Job.
No disable, delete or rollback action was performed now; there is no newly enabled
monitoring state to leave on.

## What resumes the task

Expose a supported browser surface or enable collection through the fixture's
workspace-admin UI and report its generated IDs. Separately identify/authorize an
actual Entra monitoring reader; do not replace the SQL user silently. If the
special monitoring database refuses a viewer-only grant, report its exact refusal
and stop rather than granting Contributor. Four probes in this batch are spent;
subsequent estate requests must be separately bounded within the remaining Part B
budget. No source ingestion producer or B3 scenario claim is established here.

README, current status and CLAUDE record this blocked capability without claiming
live accounting absence. No engine bytes changed; earlier freezes remain invalid.

## Sealed local artifacts

| File in .local/round-two-20261003 | SHA-256 |
| --- | --- |
| workspace-monitoring-state.json | `7b7bb4fe08d232725f4e8b6e062b7efbbbab199472fd910a9632e73686c31739` |
| monitoring-reader-principal-kind.json | `0a3833c6730b33c6e0d59679f9b79afc3871ba93158cc4e5fc09c19bfe4d0094` |
| monitoring-reader-principal-kind-after-resume.json | `c9b09b688a535ba263c2c2262e67da9f0aecf247e84440867ffceb3c7cea831a` |
