# Snapshot alignment audit and reader probes

2026-09-27. Completed three-probe audit; earlier pending sections below retain the pre-approval checkpoint. Investigation and design only. No engine or refresh-latency rule change.
PR #275 merged after six green checks at `fda03095957d71aeb0713be345fdc98941f2b044`.
The failed stale-fixture run remains preserved exactly as recorded.

## What is established

The two quantities were independent execution-surface reads, but neither receipt
identifies the data snapshot it served. `process_debugging.vertical` creates
`CROSS_SURFACE_VERIFIED` after observed, comparable quantities and different
engine/connection/object triples; it does not check snapshot identity
(`scripts/investigator/process_debugging.py`, comparison construction).
`refresh_comparison.valid_proof` validates the unchanged declared-source mapping,
not the served data versions. Existing shared-snapshot prose acknowledges this
limit without expressing it as a machine-readable comparison status.

The source commit was acknowledged at 19:24:40.810269 UTC. The subsequent SQL
receipt was created at 19:25:33.873023 UTC, before dispatch, and its completed
query returned 8,765 rather than the committed 8,778. Thus the recorded experiment
establishes a conservative **53.062754-second lower bound** on visibility lag.
It establishes no upper bound: the append was reverted before any observed SQL
read returned 8,778. This is a censored observation, not an estimate of normal
sync latency. Commit acknowledgement times, rather than the commitInfo timestamp
prepared before upload, provide the bound. Local derivation:
`.local/snapshot-alignment-20260927/historical-lag-bound.json`.

Restored versions 0 and 2 have the same quantity and active original data file.
Reading 8,765 today cannot distinguish those versions. Read-only polling of that
value cannot recover when the transient version 1 became queryable, or whether it
ever became queryable before restoration.

## Version-reporting routes to test

| Surface | Documented route | What it could establish | Current evidence |
| --- | --- | --- | --- |
| OneLake Delta | Transaction log, table UUID and active file manifest at version N | Committed source snapshot; served quantity only if execution is explicitly bound to that manifest/version | Prior owner receipts establish versions 0, 1 and 2; not a reader attestation for SQL or DAX |
| Fabric SQL | `sys.dm_db_external_tables_log_status` | Latest synchronized Delta version and update timestamp | Live test pending; documented for new metadata-sync endpoints and Contributor-or-above access |
| DAX | `INFO.DELTATABLEMETADATASTORAGES()` | CurrentVersion, table/source identity, DeltaLogETag and fallback information | Live test pending; host may require model administrator |
| DAX execution mode | `TABLETRAITS()` | Direct Lake fallback state | Live test pending; does not itself identify a data version |

The SQL endpoint reads Delta files through synchronized metadata; it is not
necessarily a second physical copy of the data. The new sync preview applies to
new endpoints only. Its presence here must not be assumed. Microsoft documents
both the [sync architecture](https://learn.microsoft.com/en-us/fabric/data-engineering/sql-analytics-endpoint-metadata-sync)
and [version DMV and permissions](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-external-tables-log-status-transact-sql?view=fabric).

DAX exposes [Delta metadata](https://learn.microsoft.com/en-us/dax/info-deltatablemetadatastorages-function-dax),
but this is distinct from previously refused refresh-timestamp metadata. Testing
these new version routes is not repeating the refused refresh-history calls.
[Direct Lake documentation](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-how-it-works)
also documents `TABLETRAITS()` and possible DirectQuery fallback. A DAX query
falling back to SQL could share SQL's stale state; the historical receipts do not
establish whether that happened. It must not be asserted as the explanation.

Even a successful separate metadata query does not automatically attest the
snapshot used by a previous quantity query. Atomic binding, a documented
query-scoped snapshot token, or a demonstrably pinned read is needed. Equal
before/after metadata observations alone require a platform guarantee that the
intervening read used that state.

## Proposed evidence contract, not implemented

Retain surface identity separately from snapshot identity. Each probe should carry
its quantity receipt, execution interval, source-native dataset identity, table
UUID where available, data version/manifest, definition version, execution mode,
attesting identity, and the method binding that snapshot to the quantity query.
An independently collected latest-version watermark must be labelled metadata
observed near the query, not silently promoted to a served snapshot.

Use orthogonal comparison dimensions: execution-surface independence, faithful
quantity equivalence, and snapshot alignment. Suggested snapshot statuses:
`SNAPSHOT_MATCHED`, `SNAPSHOT_MISMATCHED`, `SNAPSHOT_UNVERIFIED`, each with explicit
receipt references and reasons. Only affirmative alignment evidence permits a
claim of snapshot-aligned consistency. Unknown must never default to matched.

For two readers of the same declared source, compare the same source identity
and version, not version integers alone. For transformed layers, Gold version 2
and Silver version 2 have no inherent relationship: alignment needs a declared
job/output manifest linking that output to its actual input version vector and
transformation definition. Commit times alone cannot supply this lineage.

I agree with retaining usable comparisons as `SNAPSHOT_UNVERIFIED`. Every dependent
claim should say specifically which served version is missing: the values agreed
or differed when read, but common data state and currentness were not established.
Preserve original run records and append qualifications; do not rewrite history.

One distinction matters: a **proven snapshot mismatch** can itself be freshness
evidence. Requiring identical snapshots for every useful comparison would prohibit
that experiment by definition. Require matching snapshots for transformation or
consistency attribution, and independently attested ordered versions for a
freshness attribution. Arithmetic equality/difference remains an observation in
either case. This is design advice, not a change to the existing outcome rule.

## Fixture implications

Snapshot identity would reveal what the two surfaces served; it would not force
SQL to advance ahead of the model. The same append-and-immediate-read fixture is
therefore not reliable merely because receipts gain version fields. A valid
future experiment needs an observed interval in which the declared source read
is at the new snapshot and the presentation remains at the old one. If both
advance together, report that negative result rather than tuning the rule.

Options for a separately authorized future experiment are: hold a uniquely
identifiable committed change while bounded polling observes SQL catch up, then
compare with an attested older model frame; or use a genuinely version-pinned
Delta reader as the source comparator, with its own least-privilege access and
attestation. Neither is implemented or authorized by this read-only audit.
Microsoft documents [Delta version reads](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-lake-time-travel)
and [SQL time travel](https://learn.microsoft.com/en-us/fabric/data-warehouse/time-travel);
SQL endpoint time travel is restricted to new metadata-sync endpoints. Support
here remains untested, and an as-of timestamp is not automatically a DAX frame ID.

## Pending bounded probes

Prepared `.local/snapshot-alignment-20260927/probe-plan.json`: three read-only
queries, existing reader, no retries, no mutation, refresh, reframe or elevation.
There are 78 cloud reads already charged today, and the restored standing ceiling
is 60. Requested one-off ceiling 81, restored to 60 afterward. Until approval,
no live probe is executed and no documented capability is claimed as available
in this estate. Exact full synchronization duration remains unestablished.

## Completed approved reader probes ? 2026-09-27

The three planned queries ran once each, without retries, using
investigator-reader@skynwhy.com (principal
`8a582d2a-ecb4-4320-bf72-75a529a0d382`). Token claims were checked against the
configured principal for both SQL and Power BI audiences. This establishes the
credential used, not a returned surface self-report where no rows were served.
No alternate identity, permission change, refresh or reframe was used.

### SQL Delta version route

```sql
SELECT TOP (20) object_id, latest_log_version, latest_checkpoint_version,
       last_update_time_utc, is_blocked,
       SUSER_SNAME() AS reader_identity, DB_NAME() AS database_name
FROM sys.dm_db_external_tables_log_status
WHERE object_id = OBJECT_ID(N'dbo.movement_values')
```

19:41:29.569481?19:41:40.245842 UTC. Exact decoded response:

```json
{"status":"SERVED","rows":[],"stage":"complete"}
```

The query was accepted; there was **no SQL error**. It returned zero rows and
therefore no Delta version, watermark, reader self-report or database self-report.
This is not proof that the reader can obtain table version metadata, nor proof of
a permission refusal. The one filtered query cannot distinguish missing target
DMV rows, metadata visibility, or an unresolvable OBJECT_ID. Do not infer that
this endpoint uses the new synchronization implementation merely because the
DMV query was accepted. No additional query was made to resolve those alternatives.

### DAX framed-version route

```dax
EVALUATE TOPN(20, INFO.DELTATABLEMETADATASTORAGES())
```

19:41:40.254718?19:41:50.840996 UTC, over XMLA. Query-stage refusal;
`MethodInvocationException`, no rows or CurrentVersion returned. Exact inner error:

```text
User '<euii>investigator-reader@skynwhy.com</euii>' needs to be an administrator to read the metadata of the database '3484a2bc-98c5-4cef-be5c-a6215484075e'.

Technical Details:
RootActivityId: 90dfd72c-edf4-46e6-983f-ba757f2960de
Date (UTC): 9/27/2026 7:41:48 PM
```

### DAX fallback-mode route

```dax
EVALUATE TOPN(20, TABLETRAITS())
```

19:41:50.853792?19:41:56.210282 UTC, over XMLA. Query-stage refusal;
`MethodInvocationException`, no fallback indicator returned. Exact inner error:

```text
TABLETRAITS function can be executed only by the user with administrator permissions on the database.

Technical Details:
RootActivityId: aa1bb63e-c7b3-4871-a196-8670fe12a109
Date (UTC): 9/27/2026 7:41:55 PM
```

These are observed refusals for this reader, not a claim that every estate lacks
version APIs. No tested route produced a served-snapshot identity or execution
fallback state. The historical comparison therefore remains SNAPSHOT_UNVERIFIED
as an audit finding; no engine status or original receipt was rewritten.

## OneLake as the fixture oracle: workable design, reader access unestablished

Yes: a committed Delta snapshot read directly from OneLake avoids the SQL metadata
synchronization layer. The earlier fixture already established the source-side
change this way. But its successful OneLake reads used **admin@skynwhy.com**, the
fixture owner, not the diagnostic reader. `before-commit.receipt.json` explicitly
records that identity. The existing runtime ingestion helper also uses the Fabric
CLI metadata identity (`read_onelake_commit.py`); it does not authenticate as
`fabric.native_reader`. Its success cannot establish reader OneLake access.

The known Viewer and semantic Read/Build rights do not, by themselves, establish
raw lakehouse file access. Microsoft distinguishes [SQL access from Spark/OneLake
access](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sharing)
and documents [Viewer's lakehouse limitations](https://learn.microsoft.com/en-us/fabric/data-engineering/workspace-roles-lakehouse).
No reader OneLake probe was included in these three authorized reads. Thus the
honest answer is **not yet demonstrated with the reader's access**, rather than
an invented 403 or an assertion that a new grant is definitely necessary. A future
separately authorized exact-path GET could establish access before any grant is
considered; owner access must remain separately attributed if used as test truth.

A log version alone does not supply the queried total. A faithful direct-Delta
quantity needs the active-file manifest at a pinned version, retained files and
correct schema/deletion semantics. The old fixture's owner verified the one-file
snapshot plus exact appended row; that is a bounded fixture oracle, not a generic
reader-side Delta execution adapter. The current metadata helper also caps listing
at 100 and does not follow continuation, so its chosen last filename must not be
promoted to an authoritative latest version on larger logs without completeness
handling. No such adapter or metadata change was made here.

The proposed experiment can establish: source snapshot N has a changed total,
while a subsequent reader presentation query still serves the old total. With
a pinned source quantity, that is current-source/presentation divergence without
waiting for SQL. Because the DAX frame API refused this reader, matching the old
total still does **not** prove the presentation's exact old frame version or rule
out DirectQuery fallback. It proves a value inconsistent with the verified new
source state, with those limits. Making it a runtime boundary would need an
approved direct-Delta quantity surface and existing comparability/attestation
checks; merely reading a commit through the owner is not that boundary.

## Read-budget finding and proposed replacement ? no change made

The premise that the ceiling no longer binds is not what the code does.
`UsageGovernor.day()` uses UTC dates; `reserve()` sums reservations only for the
current environment and day, then rejects additions exceeding a limit. Records
are never deleted or refunded, but the **window rolls at UTC midnight**.
At 81 against 60, new reads are blocked for the rest of this UTC day unless another
explicit override is authorized. This is a fixed-day admission quota, not a
lifetime counter. It was meant to bound initiated cloud operations across sessions
in this catalog. It is not a billing cap, SQL scan-cost bound, or proof that all
external tool calls are metered.

An offline audit copied only usage rows into an in-memory database: a new cloud
reservation and a new planner reservation both raised `Daily usage limit` at the
restored policy. With an injected clock advanced one day, a cloud reservation was
admitted while every historical usage row remained. The planner block is a real
side effect: reserve checks all quota dimensions even when the attempted action
adds zero cloud reads. The live catalog was not modified by this audit. Its first
harness invocation had an INSERT placeholder-count error, corrected before these
checks; no cloud call resulted.

I recommend retaining a protective shared window but separating **ordinary quota**
from **explicit experiment allowances**, instead of repeatedly rewriting the global
ceiling:

1. A shared rolling 24-hour ordinary-read quota (initially 60 if that remains the
   chosen operational bound) removes the midnight burst opportunity. Keep all
   historical records; calculate the window without resetting counters.
2. An immutable, expiring approval record grants an exact additional count to named
   batch/run IDs, surfaces and identities. Reserve allowance atomically before each
   physical request; unrelated runs cannot spend it. The three-read approval here
   would be a three-credit batch, not a global ceiling of 81.
3. Keep a per-run cap and a separate, explicitly reserved verification/restoration
   allowance where fixtures are mutable. Plan necessary follow-on reads before
   mutation; do not spend rollback capacity on investigation. Refusals, timeouts
   and uncertain calls remain charged; no retries escape admission.
4. Meter at the outbound-request boundary and report request counts separately from
   logical probes. The current `onelake_commit` meter wraps a helper that performs
   **two HTTP GETs** (listing and commit) under one logical read reservation. So even
   a perfectly enforced logical-read ceiling is not an exact network-call quota.
5. Display ordinary-window usage, batch grant consumption, per-run remaining reads,
   and expiration separately. Add provider cost/compute controls if financial risk
   is the objective; request counts alone do not represent that risk.

The proposed policy would hold without global quota drift and without denying
legitimate explicitly approved work. It is a proposal only: no rolling window,
credit mechanism, meter placement or admission behavior was implemented.

## Accounting and validation

Approved exactly three additional reads. Policy read-back before: cloud ceiling
60, today's usage78. During: ceiling81. After the third response: original policy
bytes restored and read back at60; usage81. No resets, refunds, retries, fourth
probe, investigation run, model call or mutation. Three durable cloud reservations
are SETTLED (completed requests include observed refusals). Full responses and
hashes are retained under `.local/snapshot-alignment-20260927/`; sanitized results
are in `docs/runs/snapshot-alignment-probes.json`. README and current status link
this report. The engine and refresh rule remain unchanged.
