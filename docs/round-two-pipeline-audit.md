# Round two: approved caps, pipeline audit and delayed monitoring

2026-10-03 America/Chicago; receipt timestamps are 2026-10-04 UTC. This is
isolated estate preparation, not an investigation or unfamiliar-domain acceptance.
The user requested a checkpoint after the delayed probes if anything surprising
occurred. The original publication and failed run remain sealed and unchanged.

## Authorized limits and identities

The human explicitly approved rolling ordinary physical allowance 300 → 600 and
Part B cumulative physical ceiling 120 → 300. Diagnostic allowance stays 12 per
run. Before/after control reads retained all 227 charged requests at the change;
no refund, counter reset, model allowance change or deadline extension occurred.
The committed controls are `infra/runtime/autonomous-round-limits.json` and
`infra/runtime/round-two-part-b-limits.json`; local usage policy cloud_calls is 600.
The boundary test preserves history and refuses the 601st ordinary request.

Publisher `admin@skynwhy.com` creates/updates the two isolated items and submits
the pipeline. Every job detail, activity output and KQL probe is read as existing
`investigator-reader@skynwhy.com`, with its expected Entra object ID checked.
Existing Copy Job source authentication remains `orderops_investigator`, with
the approved SELECT on the single isolated app table. `dia-reader` is unchanged
and has no successful monitoring grant. No identity gained permissions, roles,
audiences or scopes. See [the reader manifest](estate-reader-manifest.md).

## Published estate and preserved failures

| Item | Identifier |
| --- | --- |
| Fixture workspace | `149f8d99-1c66-4a0a-9624-759be002bb60` |
| Existing isolated Copy Job | `57e128c3-6ba0-4aaf-9464-81164ecdc782` |
| New pipeline | `b4871498-bd35-45be-916c-9a642568012c`, `round_two_application_load_audited_20261003` |
| New writer notebook | `549274ae-ac77-4ba4-95d7-818f132694f5`, `round_two_load_audit_writer_20261003` |
| Isolated Bronze lakehouse | `33618b8d-46eb-4fe7-b80b-122c331260a3` |
| Intended audit table | `dbo.load_run_audit` in that isolated lakehouse |

Initial notebook creation returned HTTP202. The helper rejected the service's
regional operation URL before polling. The accepted operation was resumed through
the documented canonical operation-ID endpoint, not resubmitted. Notebook and
pipeline publication then succeeded and the served pipeline definition was read.
The two attempts cost two and six physical requests respectively.

The first pipeline instance `fc5b0854-158c-4cd4-ae88-ba75568e78ef` failed. Its
CopyApplication activity returned error 2015:

> The external references connection cannot be found in the trident payload.

No Copy Job started. RecordOwnAccounting received `copy_output_json=""` and
raised JSONDecodeError before writing a row. That defect and the bad invocation
definition were ours; a successful publication did not establish an executable
pipeline. The run consumed four requests; a separate activity-output probe cost
one. Both failures remain recorded.

The existing publisher connection listing returned HTTP200, complete, including
CopyJob connection `7c5376ed-4227-446e-8442-c60f23b976c9`. The isolated pipeline
was corrected to reference that existing connection. No new connection, principal
or grant was created. The writer's parser now produces explicit nullable
UNAVAILABLE_COPY_OUTPUT accounting for empty, null or malformed activity output;
it never defaults absent counts to zero. The supplied failed/success status is
retained. An incomplete control row is written before the writer reports its
unavailability. Six parser regressions passed after the nested-output correction described below. Updated notebook source and
connection reference were checked against served definitions, costing eleven
physical requests including asynchronous definition polling.

The writer takes counters only from the copy activity's own rowsRead/rowsCopied.
It records missing times and high watermark as unavailable rather than replacing
them with the time the audit was written. No table recount or quantity comparison
supplies counters. This is a fixture producer; engine audit-source integration is
not implemented here.

## Connected run: own accounting observed, writer failed

The corrected pipeline instance `7d797def-9587-45bb-803d-5a58090cf658` ran from
2026-10-04T02:01:05.7496196 to 02:04:09.8166667 UTC and ended Failed. Its
CopyApplication activity succeeded, with its nested copy activity running from
02:01:37.2325164Z to 02:02:46.5889476Z. The reader's HTTP200 activity output
contains `value[0].output.rowsRead=360` and `rowsCopied=360`; these are the
load's own counters, not a source/destination recount. `watermarkInfo` is null.
No capture cut or high watermark is established by these counts or timestamps.
This is one actual additional isolated load; the first failed invocation above
launched none. No replacement load was attempted.

RecordOwnAccounting failed after writing its explicit incomplete audit because
its first parser inspected the wrapper's top level. Its exact error was:

> Copy activity output did not establish rowsRead and rowsCopied; audit marked UNAVAILABLE_COPY_OUTPUT

This was a producer shape defect, not unavailable load accounting: the nested
output does contain the counters. Its original run, notebook error and output
stay unchanged. The repaired parser now accepts exactly one successful completed
copy-activity entry from a complete invocation response, retaining its own
counters and activity timestamps. Multiple entries, continuation or a failed
entry remain explicit unavailable accounting rather than selection or summing.
Applying that parser offline to the sealed response returns 360/360 and the
reported activity start/end; high watermark and Copy Job run identity remain
unavailable. The opaque child `id` is not promoted into a job identity.

The corrected notebook was published and its served source matched, costing eight
physical requests, without another invocation. The
existing audit row is not repaired or overwritten. A separate guarded SQL reader
probe of the isolated audit row failed after four physical requests (one data
request and three identity/permission requests); it established no readable row.
Its safe transport failure is preserved; the retained category does not identify
its precise server error, so neither SQL synchronization nor permissions are
asserted as the cause. Audit-table readability and a successful corrected writer
execution remain unverified. Do not declare the audit source usable yet.

## Delayed monitoring probes

The last actually completed Copy Job was `2cdafdfc-0221-4044-8883-eaeaabb863bf`,
ending 2026-10-04T01:28:27.2455298 UTC. The delayed batch began 1,418.704452
seconds later: 23 minutes 38.704 seconds, exceeding the requested 15 minutes.
The failed pipeline above did not launch a new Copy Job.

All three requests ran as investigator-reader at unchanged scope. All returned
HTTP200 and zero rows in their primary result table:

```kusto
ItemJobEventLogs | where Timestamp > ago(1d) | where ItemKind == 'CopyJob' and ItemId == '57e128c3-6ba0-4aaf-9464-81164ecdc782' | take 20
```

```kusto
CopyJobActivityRunDetailsLogs | where CopyJobRunId == '2cdafdfc-0221-4044-8883-eaeaabb863bf' | project Timestamp, CopyJobRunId, SourceName, DestinationName, Status, RowsRead, RowsWritten, StartTime, EndTime | take 20
```

```kusto
SemanticModelLogs | where Timestamp > ago(1d) | where OperationName has 'Refresh' or OperationName has 'Process' | take 20
```

The accounting query returned typed RowsRead/RowsWritten columns but no observed
counts. Accounting unavailable from this surface at the observed delay. The
refresh query established access, not an actual refresh timestamp. No same-run
accounting agreement can be asserted; absence does not determine whether logs
will arrive later. No further monitoring retry or grant was attempted.

## API evidence and cost

The reader also returned HTTP200 for the pipeline activity-run query, including
both failed activities' status, input, output and exact errors. This is positive
least-privilege activity-output access, separate from the KQL table's empty data.
Read-only POST getDefinition/queryactivityruns requests were initially counted as
mutations by a local generic helper. Appended ledger corrections fix their type
and the first run's mistaken Copy Job count; physical admissions remain unchanged.

[Microsoft's Copy Job activity instructions](https://learn.microsoft.com/en-us/fabric/data-factory/copy-job-activity)
require an invocation connection, separate from the job's SQL source connection.
[Copy activity monitoring](https://learn.microsoft.com/en-us/fabric/data-factory/monitor-copy-activity)
documents rowsRead/rowsCopied. Those properties must be observed on InvokeCopyJob;
the separate Copy activity documentation does not prove this wrapper returns them.

[Pipeline pricing](https://learn.microsoft.com/en-us/fabric/data-factory/pricing-pipelines)
lists 0.0056 CU-hours per non-copy orchestration activity: two activities imply
0.0112 CU-hours of orchestration at that rate. Invoked job and notebook compute
are additional. This is a documented rate calculation, not measured total usage.
The failed notebook's activity receipt lists an AzureIR billable duration of one
minute; it does not establish Spark CU-hours. The FTL4 trial is active; actual
per-run capacity consumption and storage charges have not been measured, so no
all-inclusive currency price is asserted.

## Receipts and remaining delivery

Immutable local receipts live under `.local/round-two-20261003/`:
approved-cap-change.json, pipeline-audit-publication.json,
pipeline-audit-publication-resume.json, pipeline-audit-first-run.json,
pipeline-activity-output-probe.json, monitoring-delayed-retry.json,
pipeline-invocation-connections.json and pipeline-audit-repair.json.
Their SHA256 seals are recorded per attempt in the append-only ledger.

No historical run or receipt was edited. Monitoring remains enabled; the
[deferred cleanup instructions](round-two-workspace-monitoring.md) remain.
Existing reports, model, baseline tables, SQL permissions and schedules were not
edited. The configuration approval is not refreshed in this checkpoint. Audit
declaration, application binding integration, collection/reapproval, audited
latency/gap producers, the four authored scenarios and E remain pending.
There is no new engine freeze or unfamiliar-domain claim. Prior freezes remain
invalid; the approved usage-policy changes alter their recorded control envelope.


Checkpoint usage: Part B 119/300 physical admissions; ordinary rolling window
274/600. This continuation added 47 physical requests to the preceding 72/227
checkpoint, including all failed attempts and definition polling. One audit-row
data request and three SQL guard requests are counted; other requests are
metadata/control work. The two pipeline invocations launched only one Copy Job.
No investigation-planner, judge, synthesis or intake model calls occurred. Six
fixture-parser regressions and the approved-allowance boundary regression passed.
The corrected writer has not executed; the audit source is not yet declared in
configuration or integrated into engine outcomes.

Additional sealed receipts: pipeline-audit-connected-run.json,
pipeline-connected-activity-output-probe.json, pipeline-audit-row-reader-probe.json
and pipeline-audit-nested-output-repair.json. The incomplete table row was not
rewritten; the SQL reader probe obtained no row. Recollection and reapproval must
follow a usable audit declaration and declared application binding, not precede
those changes and immediately become stale again.


Local validation: 25 tests passed in the project's llm-env (six audit parser,
one approved-cap boundary, eighteen physical-budget tests). The first broader
budget-test invocation used fabric-cli-env, which lacks sqlglot and other runtime
dependencies; it failed with three import errors and was rerun in llm-env without
code changes. The targeted tests and ledger/document preservation audit passed.
CI is the final merge gate; no local browser or cloud investigation was run.
