# Round two: source/history checkpoint and permission stop

2026-10-03. Part B1 partial delivery, not a source-boundary investigation.
No new engine capability, lineage context or latency outcome is claimed.

## Actual history access

The publisher `admin@skynwhy.com` created isolated empty Copy Job
`57e128c3-6ba0-4aaf-9464-81164ecdc782`, named
`investigation_round_two_history_probe_20261003`, in the approved workspace.
There are no source/destination connections, activities or schedule. It has never
executed. A publisher item listing before creation and item GET afterwards both
returned HTTP 200. Creation returned HTTP 201.

As `investigator-reader@skynwhy.com`, using its existing token/audience and
without any grant or app-registration change:

```text
GET /v1/workspaces/149f8d99-1c66-4a0a-9624-759be002bb60/items/57e128c3-6ba0-4aaf-9464-81164ecdc782/jobs/instances
HTTP 200
{"value":[]}
```

This establishes that the reader can list this Copy Job's history. It does not
establish access to a completed run's details, capture cut or activity output:
there has been no run. The original blanket assumption that a Viewer cannot
reach this history route must not be carried forward.

Three metadata reads were charged. The sealed receipt is
`744e7b6bba979185501348cf27c9c3d3fed792ba68d230943d4735b0b49c6fbc`.
The first probe helper failed with `KeyError: 'tenant_id'` before any estate
request: it looked in `fabric` rather than the configured reader/auth profile.
Its zero-read failure and ledger row are preserved separately. The correction
was confined to a new, separately recorded local probe; no engine change.

The [history API](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/list-item-job-instances)
documents the list response, statuses/times and delegated item-read scopes.
The [Copy Job creation API](https://learn.microsoft.com/en-us/rest/api/fabric/copyjob/items/create-copy-job)
permits creation without a public definition. Documentation guided the probe;
the HTTP response establishes this identity's observed access.

## Source readiness, failure preserved

Publisher preflight of the existing isolated SQL movements failed at connection:

```text
{"error":"SourceReadFailed","error_kind":"SqlException","error_number":40613,"stage":"connect"}
```

The first admission remains charged. No SQL statement executed, as the transport
did not reach its query stage. This is one conservative preparation reservation,
not evidence that the database served a failed quantity query. An appended ledger
annotation records that distinction; no refund or original-row edit.

A read-only Azure control-plane GET then reported `Online`, resumed at
`2026-10-03T22:47:32.400000+00:00`, `useFreeLimit=true`,
`freeLimitExhaustionBehavior=AutoPause`, and auto-pause delay 60. No control-plane
setting changed. A separate preflight after this observed resume succeeded:
360 rows, 360 distinct movement IDs, 7,661 units; publisher session `dbo` in
`ordersops`. The explicit database/schema SELECT-grant count for
`orderops_investigator` was zero. This justified another readiness probe; it did
not replace the failed one or retry an investigation.

## Isolated source published; exact grant is the human checkpoint

The database-owner credential reference published only
`app.stock_movements_round_two_20261003`. A bounded transaction copied the six
ordinary movement columns from the existing isolated application fixture, imposed
a movement-ID primary key, and added `source_modified_at_utc` and
`source_row_version`. It aborts if the target exists or the source exceeds 1,000
rows. The source-change timestamp is distinct from the original event date;
future fixture arrivals must preserve that distinction.

Verification as the publisher: 360 rows, 360 distinct IDs, 7,661 units,
source-change time `2026-10-03T22:51:16.8820249`, 200 KiB allocated storage.
The original source still totaled 7,661. Neither the old source, literal-seeded
lakehouses, models, reports, schedules nor permission records were modified.
The new row-version column exists, but its first queried varchar representation
contained nonprinting bytes. That representation is not admitted as a usable
version report; a later adapter must request a proper binary/hex representation.

The dedicated source reader's own session answered:

```text
reader: orderops_investigator
database_name: ordersops
HAS_PERMS_BY_NAME('app.stock_movements_round_two_20261003','OBJECT','SELECT'): 0
```

Permission receipt seal:
`221656974c319e4cc07561c20d134220d7533131c94db3ba4699aa261581c69b`.
No source quantity read was attempted with that unavailable permission.

The exact request is prepared locally at
`.local/round-two-20261003/reader-source-select-grant.sql`:

```sql
GRANT SELECT ON OBJECT::[app].[stock_movements_round_two_20261003]
TO [orderops_investigator];
```

It has **not** executed. `CLAUDE.md` prohibits an identity gaining a new scope
without an explicit human decision; the round also requires stopping there.
Consequently there is no managed source connection or Copy Job mapping yet,
no new Bronze load, no declared application binding, and no re-approval.
The gap/latency tickets and unchanged family E were NOT_RUN, not predicted passes.

## Design qualifications before further work

The #266 design remains the governing declared-connection/full-copy approach.
This round isolates a single movement source first and adds explicit source
change/version fields. Event dates alone cannot establish arrival freshness.
Connection and mapping responses must supply DECLARED_BY_DEFINITION authority;
name similarity remains forbidden.

The proposed gap and latency states overlap if both merely mean rows have not
yet copied. An older successful job shows pending delivery, not a demonstrated
breach of a promised capture cut. A gap test must specify expected delivered
membership/version; a latency test must expose pending newer source state and
the last successful delivery. Neither establishes an SLA violation without an
authoritative SLA. This distinction remains a design finding, not an implemented
taxonomy change or an invented classification precedence.

Endpoint sync-lag producer work has not begun. The existing empty/refused served-
version probes remain binding; no new sync state or currency proof was assumed.
The completed family I repeat remains scoped to L2. The literal upstream and
unwalked boundaries remain unchanged; the new SQL table is not yet in its lineage.

## Budgets, costs and configuration

Part A: ten physical requests, four diagnostics, six guards; one intake, one
judge, one synthesis, zero investigation-planner calls. Both outputs and every
original quantity probe are in [the I report](round-two-family-i.md).

Part B: nine charged physical admissions of 120. Eight estate requests completed;
one source connection preparation failed before SQL dispatch. These comprise
three Fabric metadata GETs, one Azure database GET, two source preflights (one
failed), one bounded source-copy transaction, one source verification and one
reader permission query. Zero investigation diagnostics, model calls or Copy Job
runs. The Copy Job creation is separately recorded as one metadata mutation,
not a diagnostic or an uncharged quantity read. No credit grant/refill or policy
increase. Starting ordinary usage 155/300; Part A ended 165; current observed
usage 173/300. Nineteen admissions were added, while one old slot aged out of
the rolling window. That expiry is not a counter reset or refund.

Copy Job execution consumption: zero runs. No new OneLake data storage or Spark
execution. The SQL fixture allocated 200 KiB; its publication/verification used
SQL compute under unchanged free-limit/AutoPause settings. Dollar cost is not
established from read counts. Future full copy costs
`1.5 × optimization resources × elapsed hours` CU-hours, plus SQL work,
destination storage, applicable transfer and downstream processing; region price
and measured resources/duration are required for dollars. See
[Microsoft Copy Job pricing](https://learn.microsoft.com/en-us/fabric/data-factory/pricing-copy-job).

No configuration bytes changed. Before/after raw file SHA-256:
`4362a6c7d6bb3ed7ebd58aa78e9bb0159790b42edd76c6ae30320c4beb0e4c5e`.
The unchanged loaded-config policy digest, which the discovery gate pins, is
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
The latest existing complete scan is
`37923df5-83d6-425d-8eff-b4f691941bb5` (94 operations), predating these new
objects. It was not rewritten or promoted to evidence for the new path.
A subsequent discovery/re-approval and further live tests must fit the remaining
111 Part B admissions; the historical 94-operation full scan is a budget risk,
not a reason to silently expand the allowance.

All helper failures, receipts and rows are preserved. This PR records an estate
checkpoint and a permission stop, not application-boundary or latency success.
Prior freezes remain invalid; no new freeze or unfamiliar-domain claim.
