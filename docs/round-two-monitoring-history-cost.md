# Monitoring history probes, identity reconciliation and cost

2026-10-03 America/Chicago / 2026-10-04 UTC. This is monitoring beside the Copy
Job, not a replacement load path. Reader Copy Job REST history previously returned
HTTP 200 with Completed/start/end, but no job-owned RowsRead/RowsWritten. Monitoring
was introduced to test that missing accounting through the documented table.
The isolated SQL-to-Bronze Copy Job and its first completed load remain unchanged.

## Identity decisions reconciled

The approved one-table SELECT expansion applies only to the existing contained
SQL reader orderops_investigator and is unchanged. It is not the entire identity
history: the user subsequently explicitly authorized a new Entra app/service
principal dia-reader under CLAUDE section 8. It is new, not renamed or substituted.
Client ID ddd4d3cf-9cfd-440e-ac5b-be127caa46ea, SP object ID
59dd402b-1510-4289-96fb-f1d34d4494c5; single tenant; no requested delegated API
permissions/consent, no workspace role or successful monitoring grant. Credential
remains local DPAPI. Existing publisher permissions were used, not expanded.
A Kusto audience token authenticates the principal; it is not a database role.

The earlier explicit viewer-only decision was used to attempt exactly one grant
on monitoring database 7e353019-064f-4aac-9a62-a9770d1399a9. It returned 403.
No identity acquired additional data-plane permission from this attempt. The
latest reader-query token claims matched the approved dia-reader SP object and
tenant, and both requested probes were sent using that identity only.

## Endpoint, before/after, exact queries and exact errors

Database properties served HTTP 200: parent Eventhouse
5f443879-734a-4b02-8be7-4466222c6386, databaseType ReadWrite, query endpoint
https://trd-0795s2y5q96wchvu48.z8.kusto.fabric.microsoft.com.
Management requests POST /v1/rest/mgmt; reader queries POST /v1/rest/query;
the exact database display name is supplied in db. DatabaseType is not proof
that this monitoring item allows user permission modifications.

### Before grant

```kusto
.show database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] principals
```

HTTP 200.

The served principal rows contain no dia-reader entry. Full control-plane response retained in the sealed local receipt.

### Viewer grant

```kusto
.add database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] viewers ('aadapp=ddd4d3cf-9cfd-440e-ac5b-be127caa46ea;dff91047-ebc2-4657-8dbe-5af328d57780') 'Explicit user approval: fixture monitoring viewer only 2026-10-03'
```

HTTP 403.

```text
Forbidden: Caller is not authorized to perform this action
Error details:
ClientRequestId='unspecified;d71ba687-cdbb-42b9-9c16-d3f87d629900', ActivityId='572d6a3f-4afe-40d9-9154-ab316247cc97', Timestamp='2026-10-04T00:48:23.6788382Z'.
```

### After grant

```kusto
.show database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] principals
```

HTTP 200.

The served principal rows contain no dia-reader entry. Full control-plane response retained in the sealed local receipt.

### Semantic refresh probe

```kusto
SemanticModelLogs | where Timestamp > ago(1d) | where OperationName has 'Refresh' or OperationName has 'Process' | take 20
```

HTTP 403.

```text
Forbidden: Caller is not authorized to perform this action
Error details:
ClientRequestId='unspecified;bdcd5110-2672-4671-8329-c57e44f6bbc9', ActivityId='0aa1dbd9-62d9-4d58-ad67-3c6fb90765f0', Timestamp='2026-10-04T00:48:26.5282098Z'.
```

### Pipeline history probe

```kusto
ItemJobEventLogs | where Timestamp > ago(1d) | where ItemKind in ('Pipeline', 'DataPipeline', 'Data Pipeline') | project Timestamp, ItemId, ItemKind, JobType, JobStatus, JobStartTime, JobEndTime, JobInstanceId | take 20
```

HTTP 403.

```text
Forbidden: Caller is not authorized to perform this action
Error details:
ClientRequestId='unspecified;9ec1a7b7-85c3-4da4-8dcd-066b4681dba8', ActivityId='4d32fa20-58ba-4155-aebd-aba5313f48d0', Timestamp='2026-10-04T00:48:26.7268789Z'.
```

The before/after principal responses were byte-equivalent at the parsed principal
rows, with dia-reader absent. The metadata publisher could list principals but
was refused permission to add a viewer. This establishes refusal for that actor,
not proof no database-level sharing route can exist. No workspace Contributor,
Member, Admin, database admin or ingest role was attempted as a fallback.
The monitoring documentation describes special sharing restrictions; the bounded
REST documentation search found no supported item-only sharing endpoint to use.
UI access remains unavailable. A principal authorized to manage this exact
database must apply the prepared viewer-only command or report its own refusal;
no broadened identity scope has been approved or silently substituted.

Both reader probes were authorization-refused before the query could establish
whether the named table/columns exist or contain rows. The semantic table name in
the attempted statement is a candidate, not a discovered schema. This is not
an empty result, absent history, successful refresh-timing read or a general
platform impossibility. No correction of the REST/XMLA route-specific refusals
is warranted from these denials. A future readable monitoring result would be a
dated new-route correction; prior route receipts remain true.

## Actual capacity and the idle-hour premise

Publisher GET capacities served active FTL4 trial capacity
 ec15bc07-8e88-436e-8dbe-485b9a7f4533, Central US. GET Eventhouse properties
served minimumConsumptionUnits=0.0. No paid capacity was purchased or resized,
and no always-on minimum was enabled here. The configured static idle compute
floor is therefore **0 CU-hours per hour**. That is a floor, not a measurement of
actual idle consumption or proof monitoring costs nothing: background ingestion
can keep compute active and storage remains.

[Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial)
is free trial capacity; thus current trial compute has **$0 paid capacity charge
per hour while this trial remains active**. We did not inspect an Azure invoice or
claim all ancillary billing is zero. The earlier premise that every existing
Eventhouse has a fixed hourly compute charge is incorrect. [Consumption](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/real-time-intelligence-consumption)
is active UpTime times autoscaled compute, with separately reported storage.
No actual CU/hour, storage GB or paid SKU dollar/hour measurement was obtained.
Paid estates need observed UpTime and storage plus their capacity/storage rates;
no fabricated fixed dollar figure replaces those measurements. Eventstream
consumption is separate and has not been measured. Monitoring remains enabled;
cleanup instructions remain deferred, not executed.

## B1 continuation and explicit limits

Already delivered: isolated application source, approved SELECT, managed
read-only source connection, Copy Job, served exact mapping and one completed
Bronze load; reader REST history HTTP 200. Monitoring does not replace those.
Still undelivered: approved-context projection of the Copy Job connection/binding,
application execution layer, row-capture/latency producers and the four authored
scenarios plus E. Existing notebook paths stop at literal-seeded Bronze; the
isolated Copy Job destination has not been spliced into that path. Native item
relations returned destination Association only, so no Datasource binding is
claimed from them. Connection+mapping evidence must be collected and normalized
as definition authority before the resolver can execute that source hop.

The no-application-access scenario specifically requires this load's own row
accounting. The requested reader cannot query it yet; no new load was spent on
an accounting test that could not follow it. Those scenarios have not run and
must not be reported as passed. Current metadata context still predates the new
source/job; no approval bypass, name-inferred edge or fake count was introduced.
The viewer-only authorization step needs an external permission-management route,
not an engine change that consumes admin observations as reader evidence.

## Budget and receipts

Three property/capacity metadata requests plus five Kusto requests: two permission
GET-equivalent commands, one refused grant and two authorization-refused reader
queries. Eight physical admissions; Part B **48 -> 56 / 120**, rolling observed
**203 -> 211 / 300**. No diagnostic investigation/model calls or extra load.
No credit/limit/reset/refund. The two reader history probes are separate from the
up-to-four Copy Job row-accounting probes, of which zero have run. The initial
monitoring-resource check is recorded in the same PR; cumulative Part B remains
56, not double-counted. Original ledger entries and failures remain unchanged.

| Local receipt | SHA-256 |
| --- | --- |
| monitoring-enabled-now-check.json | `bd71d3315b585ad928072803763f8dafa0459960b435faa9dd41bf5e33417790` |
| monitoring-kql-properties-cost.json | `9e8b24bf757ee3ec81f227c8de4d4d78063a26175aed37b06f314f32a50dcd90` |
| monitoring-kql-reader-probes.json | `64259c12a6db0b21175c98cff817626cd0b23835bbf33924a67b69e8d0a5a05f` |
