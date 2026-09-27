# Authorised stale-fixture attempt and verified restoration

2026-09-27. PR #274 merged after all six checks passed, `ce574c8`.
One live known-domain attempt: `7ccb7190-079a-44bd-9b18-78a3e7b5d7d8`.
**HELD / UNRESOLVED**, process error `UsageHold`, stop reason `TOOL_UNAVAILABLE`.
No REFRESH_LATENCY, no synthesis and no successful latency demonstration.
The engine and rule were unchanged; no retry was performed.

## Mutation and restoration

An isolated copy would require changing the model's source pointer, so the explicitly
authorised primary-table fallback was used. Only the existing Gold Delta table
was changed. No model definition, permission, schedule, automatic-update setting,
refresh or reframe request was changed or issued.

| State | Delta version | Active rows | Delta units total (snapshot-derived) |
| --- | --- | --- | --- |
| Before | 0 | 406 | 8,765 |
| Append committed | 1 | 407 | 8,778 |
| Append reverted | 2 | 406 | 8,765 |

Before-state rows/schema/total were read from the sole active Parquet file and
checked against the complete version-0 log. The table uses writer protocol2,
no extra configuration or partitioning. The one-row typed Parquet append and
version1 add action were conditionally created without overwriting any file.
Version1 was read back byte-for-byte. Row counts after append and rollback follow
the verified active-file add/remove set, not a fabricated SQL count result.

Exact added row:

```json
{"product_id":5,"movement_id":361,"warehouse_id":3,"units":13,"event_day":"2026-09-17","movement_type":"RECEIPT","rate_version":1,"unit_cost":5,"movement_value":65}
```

Rollback conditionally created version2 removing only the added file from the
active Delta snapshot. That commit was read back byte-for-byte. Historical logs
and the inactive data file remain for Delta history; no original data file was
removed or overwritten. A final independent DAX query as the diagnostic reader
returned **8,765**, with USERPRINCIPALNAME matching the reader. Restoration passed.
The three owner writes were data-file creation, append commit and removal commit.
The owner was admin@skynwhy.com; none is represented as reader evidence.

## What the investigation actually read

| Surface | Served object | Value | Receipt |
| --- | --- | --- | --- |
| Power BI DAX | Model `3484a2bc-98c5-4cef-be5c-a6215484075e` | 8,765 | `ed4db09e-01c4-44eb-8986-2e8c3eab88dc` |
| Fabric SQL | `warehouse_gold_e1b8e1`, declared `dbo.movement_values` | 8,765 | `9ba875d2-a5d0-4ff6-94c3-c70f5636d219` |

Both receipts are SEALED, COMPLETED and COMPLETE_RESPONSE. Both surface reports
identify investigator-reader@skynwhy.com; SQL also reports its database. DAX does
not attest model object, engine or connection; SQL does not attest engine or
connection. These are distinct execution surfaces, but no completed process
comparison/assessment was persisted: the procedure threw before returning its
observations. Receipt-first accounting correctly retains both real reads.

The Delta data changed, but neither queried surface exposed the new total during
the attempt. Thus the requested divergent boundary was **not observed**. The
comparison-based rule did not fire. No claim is made about automatic reframing,
SQL synchronization duration or which service state would have appeared later.

After equality, the procedure attempted ingestion metadata. The run had a two-read
ceiling, reserving the remaining batch reads for mutation verification and mandatory
restoration. Its third-read admission failed; no third investigation read occurred.
That budget allocation prevented a completed equality conclusion. This is a failed
attempt preserved as it happened, not evidence that the new rule succeeded or failed
on a genuinely divergent pair.

One intake model call; **0 investigation planner/definition-judge calls**; no
synthesis call. Deeper boundaries were not read (this run's depth ceiling was1).
No final outcome limits exist because there was no assessment. Receipt limitations
remain: hidden report selections/RLS and cross-system equivalence are not implied;
SQL TOP bounds returned rows rather than scanned work. Reads are not a shared
snapshot and no refresh timestamp or elapsed latency was obtained.

## Verbatim outputs

Business output: **not produced**.

Technical output: **not produced**.

Synthesis status is `NOT_REQUESTED` after the process held. The missing-timestamp
limitation therefore cannot be confirmed in either live output; there are no
outputs to quote. Offline implementation tests are not substituted for live text.

## Authorisation and accounting

The initially offered ceiling70 was already exhausted. The user explicitly
approved ceiling78 for this batch. It was read back before reads and restored to
60 immediately after restoration verification, also read back. Counters were not
reset or refunded: **70 -> 78**, exactly eight additional reads.

- Five owner reads: Delta listing, original commit, original data file, append
  commit verification and rollback commit verification.
- Two investigation reads: one DAX and one Fabric SQL.
- One restoration DAX read.

The investigation ledger row and a separate fixture/restoration audit row account
for all eight without double counting. Full local receipts, exact added Parquet,
conditional write responses, policy snapshots and run recording are retained under
`.local/stale-fixture-20260927/`. The structured report is
[runs/stale-fixture-live.json](runs/stale-fixture-live.json).
No new fixture variant, freeze, engine change, permission or unfamiliar-domain claim.

Documentation validation: generator tests passed (2); `git diff --check` passed. An initial test command referenced a nonexistent test directory and was corrected; it executed no tests. Engine bytes are unchanged from merged #274.
