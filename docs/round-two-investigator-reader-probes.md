# Existing reader monitoring access: positive route, empty history

2026-10-03 America/Chicago / 2026-10-04 UTC. No more grants were attempted.
The human directed both probes to investigator-reader at its existing scope;
dia-reader is retained unchanged with no successful monitoring role.

## Identity and surface

Isolated `.local/azure-reader-sql`, investigator-reader@skynwhy.com, Entra
object 8a582d2a-ecb4-4320-bf72-75a529a0d382. Token tenant and Kusto audience
were validated, with no publisher fallback. Monitoring database
7e353019-064f-4aac-9a62-a9770d1399a9 at
https://trd-0795s2y5q96wchvu48.z8.kusto.fabric.microsoft.com.
Prior recorded scope is workspace Viewer plus model Read/Build. No grant,
identity change, app change, workspace role or permission increase occurred.

## Exact probes

```kusto
ItemJobEventLogs | where Timestamp > ago(1d) | where ItemKind == 'CopyJob' and ItemId == '57e128c3-6ba0-4aaf-9464-81164ecdc782' | take 20
```

HTTP 200.

Primary result rows: `[]`. Returned columns: `Timestamp`, `ItemId`, `ItemKind`, `ItemName`, `WorkspaceId`, `WorkspaceName`, `CapacityId`, `DurationMs`, `ExecutingPrincipalId`, `ExecutingPrincipalType`, `WorkspaceMonitoringTableName`, `JobInstanceId`, `JobInvokeType`, `JobType`, `JobStatus`, `JobDefinitionObjectId`, `JobScheduleTime`, `JobStartTime`, `JobEndTime`.

Query status: Query completed successfully. RequestId `38718728-5f96-4943-9da2-152429b7da55`, ClientActivityId `unspecified;952b1401-d987-4c94-b8a9-b4ecf367df04`.

```kusto
.show table ItemJobEventLogs schema as json
```

HTTP 200.

Exact served table schema:

```json
{
  "Name": "ItemJobEventLogs",
  "OrderedColumns": [
    {
      "Name": "Timestamp",
      "Type": "System.DateTime",
      "CslType": "datetime"
    },
    {
      "Name": "ItemId",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "ItemKind",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "ItemName",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "WorkspaceId",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "WorkspaceName",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "CapacityId",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "DurationMs",
      "Type": "System.Int64",
      "CslType": "long"
    },
    {
      "Name": "ExecutingPrincipalId",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "ExecutingPrincipalType",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "WorkspaceMonitoringTableName",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "JobInstanceId",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "JobInvokeType",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "JobType",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "JobStatus",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "JobDefinitionObjectId",
      "Type": "System.String",
      "CslType": "string"
    },
    {
      "Name": "JobScheduleTime",
      "Type": "System.DateTime",
      "CslType": "datetime"
    },
    {
      "Name": "JobStartTime",
      "Type": "System.DateTime",
      "CslType": "datetime"
    },
    {
      "Name": "JobEndTime",
      "Type": "System.DateTime",
      "CslType": "datetime"
    }
  ]
}
```

```kusto
SemanticModelLogs | where Timestamp > ago(1d) | where OperationName has 'Refresh' or OperationName has 'Process' | take 20
```

HTTP 200.

Primary result rows: `[]`. Returned columns: `Timestamp`, `OperationName`, `ItemId`, `ItemKind`, `ItemName`, `WorkspaceId`, `WorkspaceName`, `CapacityId`, `CorrelationId`, `OperationId`, `Identity`, `CustomerTenantId`, `DurationMs`, `Status`, `Level`, `Region`, `Category`, `CallerIpAddress`, `WorkspaceMonitoringTableName`, `ApplicationContext`, `ApplicationName`, `DatasetMode`, `EventText`, `OperationDetailName`, `ProgressCounter`, `ReplicaId`, `StatusCode`, `User`, `XmlaObjectPath`, `XmlaProperties`, `XmlaSessionId`, `CpuTimeMs`, `ExecutingUser`.

Query status: Query completed successfully. RequestId `d2120b52-e4a4-44ce-98c9-1ab20809946e`, ClientActivityId `unspecified;fdd05c9a-9f5b-474f-bf66-6a5a10dc7413`.

## Findings and dated correction

Both queries succeeded at the existing reader scope. This disproves the blanket
assumption that monitoring history is inaccessible to the least-privilege reader.
It does not undo the original REST/XMLA refusals, which are route-specific.
The semantic operations table is readable, but no Refresh/Process event was
returned for the requested one-day window. This is not a refresh timestamp,
proof that no refresh occurred, proof of complete history, or evidence of currency.
No timestamp finding or latency outcome is certified from an empty result.
A monitoring timing producer could be eligible only with a configured working
reader transport and matching model events; enabling monitoring alone is not
sufficient to supply usable freshness evidence. This PR records access, not an
implemented presentation_freshness producer.

ItemJobEventLogs' full 19-column schema has no RowsRead or RowsWritten and no
nested payload column carrying them. The load's own accounting is unavailable
from **this table**, not proven unavailable from all monitoring surfaces.
CopyJobActivityRunDetailsLogs is the separate documented accounting table.
No totals were substituted as accounting. Successful query statistics are not
load row counts. Empty matching event rows are preserved as successful empty
queries, unlike earlier authorization failures.

## System-managed permission finding

The unchanged viewer command under the existing isolated administrator profile
returned HTTP403. Exact server refusal:

```text
Forbidden: Caller is not authorized to perform this action
ClientRequestId='unspecified;5436c608-2ceb-4fd6-875c-71c4c8b2a5a7'
ActivityId='baf4c9c2-cb0c-4e9c-8872-eb7af6793b3b'
Timestamp='2026-10-04T01:12:59.1919416Z'
```

The principal listings expose Fabric-managed Trident groups; the current actor's
served effective roles are Viewer/Monitor, not Database Admin. Microsoft's
[workspace monitoring documentation](https://learn.microsoft.com/en-us/fabric/fundamentals/workspace-monitoring-overview)
describes workspace-role access and marks legacy monitoring as read-only with
workspace-role sharing. The combined documentation and served group model are
evidence for system-managed access on the tested surface. The 403 alone proves
the actor was refused; it does not prove all item-sharing routes impossible.
No further grants, broader roles or principal deletion will be attempted.
The user's suggestion of a future workspace Viewer alternative was not applied:
this existing reader already has recorded Viewer and these probes succeeded.

## Receipt and initial usage

Local `.local/round-two-20261003/monitoring-investigator-reader-probes.json`, SHA-256 `e29a5aa6002b70304beb8a8f5c1b9c6ce2808019035203913618a9f79f147996`.

Three physical requests; Part B **64 -> 67 / 120**, rolling **219 -> 222 / 300**. No diagnostic/model calls or quota changes. Additional isolated load checkpoint will be appended below.

## Additional authorized isolated load and fourth monitoring probe

One additional isolated Copy Job instance `2cdafdfc-0221-4044-8883-eaeaabb863bf` was
submitted by the existing publisher through the Fabric CLI transport. No
identity, grant, schedule or definition changed. Source credential remains
orderops_investigator. Every history query used investigator-reader.
Both completed-instance interfaces returned HTTP200/Completed:
start `2026-10-04T01:26:58.5564932`, end `2026-10-04T01:28:27.2455298` UTC.
Four physical requests: submit, NotStarted detail, Completed detail and typed
Completed detail. All responses preserved, no replacement execution.

After **141.705 seconds from served completion to query start**,
the fourth monitoring probe as investigator-reader was:

```kusto
CopyJobActivityRunDetailsLogs | where CopyJobRunId == '2cdafdfc-0221-4044-8883-eaeaabb863bf' | project Timestamp, CopyJobRunId, SourceName, DestinationName, Status, RowsRead, RowsWritten, StartTime, EndTime | take 20
```

HTTP200. Exact primary result rows: `[]`. Returned columns:
Timestamp, CopyJobRunId, SourceName, DestinationName, Status, RowsRead, RowsWritten, StartTime, EndTime.
RowsRead/RowsWritten exist on this separate table, but no matching activity row
was served. **Accounting unavailable from this surface at the observed time.**
Time until successful ingestion is unestablished. This is not zero-copy,
missing-row or ingestion-gap evidence. No estimated or substituted counts.
Four monitoring probes and one additional load are now consumed; no further
polling or replacement load was made.

## Remaining binding work and budget boundary

Enterprise discovery does not yet collect the declared connection/mapping as
an executable application binding. Approved context predates these resources;
the isolated Bronze has not been connected to the old literal-seeded model
chain. Binding integration, source producers and four authored scenarios remain
pending, not delivered or passed. Required load accounting for the unreachable-
source scenario remains unavailable and cannot be substituted by run timestamps.
No named-object similarity, stale-context gate bypass or fabricated lineage.

The last broad scan cost 94 operations; 48 Part-B admissions remain. Repeating
that scan exceeds the unchanged ceiling before investigation runs. A bounded
collection with explicit partial coverage or a separately reviewed budget
decision is required before re-approval. No over-budget scan was started.

Final usage: Part B **64 -> 72 / 120**, rolling observed **219 -> 227 / 300**.
Eight physical requests, zero investigation/model calls. Three appended ledger
rows; original prefix preserved. No engine/config change; prior freezes remain
invalid. Monitoring enabled, all three identities retained unchanged.

| Sealed local artifact | SHA-256 |
| --- | --- |
| copy-job-monitoring-load.json | `e0a52ed04cbe2ac4c4b6bc4116acab4d1f8c5b9051e29831745826db1455f953` |
| monitoring-copy-job-accounting.json | `ec7d005d199f65bc5050505922b0bbb783234389d8c839411aca42a363ec549b` |
