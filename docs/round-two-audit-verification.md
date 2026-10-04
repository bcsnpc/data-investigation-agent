# Round two: monitoring identity and successful audit-source verification

2026-10-03 America/Chicago (2026-10-04 UTC receipts). This is estate preparation
and discovery integration, not an investigation or unfamiliar-domain acceptance.

## Monitoring provenance and correction

The human confirmed **Workspace settings → Monitoring: ON** during this round.
No monitoring setting, resource, table, identity or grant was changed here.
The current complete workspace listing contains native Monitoring item
`56bd6e85-d840-4d4a-8b85-4e9e8f46bd25`, Eventstream
`72b37e0e-0510-4226-9809-b132fdd7d9c6`, Eventhouse
`5f443879-734a-4b02-8be7-4466222c6386`, and KQL database
`7e353019-064f-4aac-9a62-a9770d1399a9`. The Eventstream and Eventhouse descriptions
identify them as backing a Workspace Monitoring artifact. No hand-created
Eventhouse, KQL database or log-table creation was found in the implementation's
estate-operation scripts; provisioning through the human's UI was not observed
by the agent.

Both the original investigator-reader probes and the three delayed probes used
**that same database**, its parent Eventhouse above, and query endpoint
`https://trd-0795s2y5q96wchvu48.z8.kusto.fabric.microsoft.com`. There is no database
mismatch to correct with replacement probes. Their HTTP200/empty results remain
unchanged; they do not establish that monitoring was disabled or a handmade
database was queried, nor do they establish actual refresh history or counters.

**Dated correction:** the earlier phrase “monitoring is readable” established
reader access to the queried database/table schemas with empty requested
histories. It did not independently establish the active logging setting or
the presence of monitoring events. The human's current ON confirmation is a
separate source of evidence, not an agent control-plane read of that toggle.

The three current control-plane reads cost three physical requests. GET workspace
and GET items returned HTTP200. The documented workspace response contains no
monitoring-toggle field. Eventstream getDefinition returned HTTP401:

```json
{"requestId":"93491c94-ca38-49a5-b27b-992afc0201a8","errorCode":"Unauthorized","message":"User is not authorized","isRetriable":false}
```

No connected browser was available to independently read the UI toggle. The
[documented enablement procedure](https://learn.microsoft.com/en-us/fabric/fundamentals/enable-workspace-monitoring)
and [GET workspace contract](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/get-workspace)
are distinct: resource existence cannot substitute for a logging-toggle read.
Deferred monitoring cleanup instructions in the earlier records remain unchanged.

## The original audit failure: exact evidence and its limit

The earlier probe ran as **investigator-reader@skynwhy.com**, against the **Fabric
lakehouse SQL analytics endpoint**, database `round_two_bronze_20261003`, table
`dbo.load_run_audit`; neither a warehouse nor direct OneLake. Its retained error
was `LowerReadError: Fabric SQL read unavailable`, without a SQL error number or
underlying server message. This is a recording gap; the exact historical server
error cannot be recovered from that receipt. It does not establish a permission
failure or endpoint synchronization lag.

A repeat at 02:22:11 UTC consumed four physical requests and failed with
`sql_error_kind=TransportError`, `sql_error_stage=query`, `sql_error_number=null`.
A local transport copy retained the underlying message if the error recurred,
while preserving all three safety checks and the same query. That subsequent
probe began 02:23:28 UTC and succeeded: one original row was readable, with null
counters and `UNAVAILABLE_COPY_OUTPUT`. That original failed writer row was not
edited. The elapsed observation times are recorded; no specific sync-lag duration
or mechanism is inferred without the original error. Existing reader access now
works, without permission changes. Each probe cost one diagnostic plus three guards.

An initial local helper invocation used an environment without fabric_cli and
failed before any cloud request. It was rerun using the existing Fabric CLI
environment; no cloud failure, reservation refund or replacement load was hidden.

## One corrected pipeline run and one matching audit row

The one authorized rerun of pipeline `b4871498-bd35-45be-916c-9a642568012c`
produced instance **`2a3801ae-ef67-4106-ba39-2c77fe68a158`**, terminal Completed,
02:24:45.3245744–02:27:50.06 UTC. Publisher admin submitted the run; history and
activity output were read as investigator-reader. CopyApplication and the fixed
RecordOwnAccounting completed. Submission, polling and activity output cost six
physical requests. Previous failed runs and their rows remain unchanged.

The reader then queried the isolated lakehouse SQL endpoint. Exactly one audit
row exists for that pipeline instance:

| Field | Audit row and copy activity's own output |
| --- | --- |
| run_id | `2a3801ae-ef67-4106-ba39-2c77fe68a158` |
| status | Succeeded |
| rows_read | 360 |
| rows_written / rowsCopied | 360 |
| accounting_state | OBSERVED_COPY_OUTPUT |
| copy activity start | 2026-10-04T02:25:15.2840632Z |
| copy activity end | 2026-10-04T02:26:24.1249979Z |
| high watermark | null / unavailable |

The verification asserts same pipeline run ID, exactly one row, matching own
counters and matching activity start/end. It links the sealed activity-output
receipt, SHA256 `3777f110cf9f43c4715901c8d2a80081a627ac045b41cc076815f70b1d70caea`.
These are observed activity counters, not table recounts. The opaque nested child
ID is not promoted to a Copy Job run identity. The audit read cost four physical
requests: one diagnostic plus three identity/permission guards. The value query
self-reported investigator-reader, database round_two_bronze_20261003 and engine
Microsoft Azure SQL Data Warehouse; read-only verification passed.

This establishes **audit accounting agreement for this one run**. A null high
watermark does not establish a source capture cut, row-version completeness,
snapshot alignment, LOAD_LATENCY or INGESTION_GAP.

## B1 discovery integration

Discovery now follows only managed connection IDs declared by collected Copy Job
definitions. It retrieves each referenced connection once, retains only its ID,
connector type and path, and requires the exact configured source server/database.
Credential material is excluded. A refused, mismatched, stale or out-of-scope
connection leaves the mapping unresolved. The graph receives current connection
evidence and can derive the application-to-destination edge from the served Copy
Job mapping. Native relations still do not supply that source edge; provenance
is definition plus exact declared connection, not name similarity.

Regression cases cover scope/identity rejection, credential exclusion and retained
asset coverage. The golden planner directory stays **28 entries / 11 SQL objects**,
with **5,543 payload characters before and after**, even with 50 additional
connection evidence assets. Its test requires byte-identical planner payloads.
Fifteen connection/projection tests passed; the earlier discovery/lineage run
passed 49 tests. This is metadata binding integration, **not yet an executable
application quantity path or an audit-first latency/gap producer**. Recollection,
full-config re-approval, downstream fixture wiring, four scenarios and unchanged
family E remain pending. Engine bytes changed; previous freezes are invalid.

## Recording and budget

All live receipts are sealed under `.local/round-two-20261003/`: current monitoring
control-plane verification; audit retest and exact-error transport probe; corrected
pipeline run; verified audit row. Corresponding ledger rows are appended. No
original receipt, failed run, old row or allowance counter was reset or rewritten.
This round consumed **21 physical requests**: three metadata controls, three
guarded audit probes (three diagnostics/nine guards), and six pipeline operations.
Part B is **140/300**, rolling ordinary use **295/600** at the final observation.
Per-investigation diagnostic cap remains 12. No new credit or allowance increase.
