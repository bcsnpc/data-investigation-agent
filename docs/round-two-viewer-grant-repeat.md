# Renewed monitoring viewer grant: permission manager lacks Admin

2026-10-03 America/Chicago / 2026-10-04 UTC. Explicit human decision:

> Approved: grant dia-reader viewer-only on the monitoring KQL database.
> Nothing else ? no workspace role, no Eventhouse admin, no other item.
> Apply the prepared grant as written.

The existing publisher admin@skynwhy.com, object
23de217f-6e14-49cf-9acd-47dcd83cb82f, sent the prepared grant unchanged, once.
It was refused. No permission change occurred. The approved scope is unchanged;
a new approval does not change the server's authorization of the executing actor.
No principal was elevated to execute it, no service-managed administrator was
impersonated, and no private endpoint or workspace role was substituted.

Target: fixture monitoring database 7e353019-064f-4aac-9a62-a9770d1399a9,
parent Eventhouse 5f443879-734a-4b02-8be7-4466222c6386. All requests use
https://trd-0795s2y5q96wchvu48.z8.kusto.fabric.microsoft.com.
Permission commands POST /v1/rest/mgmt; reader statements POST /v1/rest/query.
All carry the exact database display name as db. Reader token claims match the
existing dia-reader object/tenant; no user-account fallback.

## before permissions

```kusto
.show database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] principals
```

HTTP 200.

Zero dia-reader principal entries. Full principal rows remain in the sealed local artifact.

## grant

```kusto
.add database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] viewers ('aadapp=ddd4d3cf-9cfd-440e-ac5b-be127caa46ea;dff91047-ebc2-4657-8dbe-5af328d57780') 'Explicit user approval: fixture monitoring viewer only 2026-10-03'
```

HTTP 403.

```text
Forbidden: Caller is not authorized to perform this action
Error details:
ClientRequestId='unspecified;3b5f8457-26af-4428-82cb-5271d06ec5e8', ActivityId='86bd0418-a89a-4561-ab68-310c932b0154', Timestamp='2026-10-04T00:58:23.0291401Z'.
```

## after permissions

```kusto
.show database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] principals
```

HTTP 200.

Zero dia-reader principal entries. Full principal rows remain in the sealed local artifact.

## semantic refresh

```kusto
SemanticModelLogs | where Timestamp > ago(1d) | where OperationName has 'Refresh' or OperationName has 'Process' | take 20
```

HTTP 403.

```text
Forbidden: Caller is not authorized to perform this action
Error details:
ClientRequestId='unspecified;379781b2-0575-4c96-acc3-ca91232f1f51', ActivityId='a0a332d7-9cad-43a0-a973-4770c393d675', Timestamp='2026-10-04T00:58:25.6306436Z'.
```

## copy job history

```kusto
ItemJobEventLogs | where Timestamp > ago(1d) | where ItemKind == 'CopyJob' and ItemId == '57e128c3-6ba0-4aaf-9464-81164ecdc782' | take 20
```

HTTP 403.

```text
Forbidden: Caller is not authorized to perform this action
Error details:
ClientRequestId='unspecified;3c83f9cb-c659-439f-8783-470e91a69d1f', ActivityId='4ce35701-880c-40d7-8621-6c475ab114d2', Timestamp='2026-10-04T00:58:25.8829816Z'.
```

## Why the grant failed: effective roles queried, not assumed

A separate governed publisher query returned HTTP200:

```kusto
.show database ['investigator-fixture-83139e71cbdf6a50_Monitoring_item_investigator-fixture-83139e71cbdf6a50_Database'] principal roles
```

Exact effective-role table rows, abbreviated only by omitting repeated principal
identity (every row names admin@skynwhy.com / its verified object ID):

| Scope | Role |
| --- | --- |
| Cluster | AllDatabasesViewer |
| Cluster | AllDatabasesMonitor |
| 7e353019-064f-4aac-9a62-a9770d1399a9 | Viewer |
| 7e353019-064f-4aac-9a62-a9770d1399a9 | Monitor |

No Database Admin role is served for this actor. [Kusto database role management](https://learn.microsoft.com/en-us/kusto/management/manage-database-security-roles?view=microsoft-fabric)
requires Database Admin. This explains the failure more specifically than the
403 alone. A database-admin-capable operator, or a supported Fabric item-sharing
route, is needed to execute the already approved single-database viewer grant.
This is not a request to grant dia-reader admin or a workspace role. Whether
this special monitoring database supports item-only sharing remains unestablished;
the grant refusal under a Viewer/Monitor actor does not prove it impossible.
No unapproved identity elevation occurred.

## What the reader probes do and do not establish

Both probes returned authorization refusal before schema/data evaluation.
ItemJobEventLogs returned no schema or run rows; RowsRead/RowsWritten are
**unavailable from this source because access was refused**. We cannot say those
columns are absent. The conditional schema read was not issued after the 403.
The distinct documented CopyJobActivityRunDetailsLogs accounting table also
remains unqueried; no counts substituted from source/destination totals.

SemanticModelLogs is the requested candidate statement, not a discovered table
name. Its authorization refusal cannot establish whether the table exists or
whether any refresh operations are logged. No successful refresh-history result
exists here, and presentation_freshness has not been declared merely because
monitoring resources exist. The route-specific REST/XMLA original findings remain
unchanged. A positive reader result would require a dated correction, not editing
those historical receipts. Two probes are failures, not empty successful queries.

## Manifest, B1 and unchanged evidence

[Estate reader manifest seed](estate-reader-manifest.md) consolidates all three
readers, their authentication, recorded privileges, reach and evidence limits.
The SQL principal's approved one-table expansion remains unchanged; existing
Fabric reader permissions remain unchanged; dia-reader still has no successful
monitoring grant. Scope enumeration is qualified where based on prior receipts.

B1 already has the isolated source, managed read-only connection, Copy Job,
served mapping, first completed Bronze load and reader HTTP200 run history.
Binding integration, application execution/producers and the four authored
scenarios remain pending; this PR does not claim their delivery or execute them
behind an unresolved accounting prerequisite. The unreachable-source scenario
requires the load's own accounting, which cannot yet be obtained by its intended
reader. No extra load, fixture mutation, rescan/approval bypass, inference from
names, quota extension or fabricated scenario result was used to hide that gap.
Monitoring remains provisioned; deferred cleanup instructions remain in
[the enablement record](round-two-monitoring-resume.md).

## Counts and local sealed artifacts

Six physical requests: before permission listing, one refused grant, after
listing, two refused reader probes, and one effective-role query. Four metadata
commands/queries plus one additional reader query and one grant attempt;
zero diagnostic investigation calls, extra loads or model calls. Part B
**56 -> 62 / 120**; rolling observed **211 -> 217 / 300**. No cap/credit/refund
change. Original rows and errors retained; an explicit human-decision note is
appended. No engine/configuration change; earlier freezes remain invalid.

| Local receipt | SHA-256 |
| --- | --- |
| monitoring-viewer-grant-approved-repeat.json | `41d08994ff1f6f4692cf8f654d53d5804fe478db7ee8a1b8f3200a5bd7300813` |
| monitoring-publisher-effective-roles.json | `8dd92d059f5c7b563381dcdee9e86fbbcdf4385c034a9a58f7db91c3e5bd78c0` |
