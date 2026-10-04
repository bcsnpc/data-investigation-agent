# Monitoring enablement resumed: control-plane checks and UI blocker

2026-10-03 America/Chicago / 2026-10-04 UTC. User explicitly authorized enabling
monitoring only in fixture workspace 149f8d99-1c66-4a0a-9624-759be002bb60,
minimum scoped prerequisite changes, existing dia-reader database viewer only,
no workspace role or identity amendment, at most four accounting probes and one
additional isolated load within the unchanged Part B budget.

## Documented method and exact access failures

[Enable monitoring](https://learn.microsoft.com/en-us/fabric/fundamentals/enable-workspace-monitoring)
documents Workspace settings > Monitoring > +Eventhouse. The newer
[Copy Job guide](https://learn.microsoft.com/en-us/fabric/data-factory/copy-job-workspace-monitoring)
documents turning on Log workspace activity there. The setting provisions the
monitoring Eventhouse and read-only KQL database. A bounded search of Microsoft
Learn Core/Admin REST references found no documented workspace-monitoring
provisioning API. This is a search finding, not proof no such endpoint exists.
An ordinary Eventhouse create call is not evidence of enabling workspace logging
and was not used as a substitute. No guessed/private endpoint was called.

The computer-use skill was read and its native initialization attempted.
Browser inventory: apps=[], browsers=[]. Chrome tab creation returned exactly:

```text
Browser is not available: chrome
```

Native @oai/sky initialization succeeded, but list_apps returned exactly:

```text
Computer Use native pipe is unavailable: failed to connect native pipe: The system cannot find the file specified. (os error 2)
```

The missing component is a working browser/native automation surface connected
to this session. No Fabric toggle was reached; this is not a platform permission
refusal. To resume, expose that runtime, or open the fixture as a workspace admin
at https://app.fabric.microsoft.com/groups/149f8d99-1c66-4a0a-9624-759be002bb60/list
and enable Workspace settings > Monitoring > Log workspace activity / +Eventhouse.
Do not create a standalone Eventhouse as a substitute.

## Before/after and prerequisite findings

Four governed publisher metadata GETs returned HTTP 200:

1. /v1/workspaces/149f8d99-1c66-4a0a-9624-759be002bb60/items
2. /v1/workspaces/149f8d99-1c66-4a0a-9624-759be002bb60
3. /v1/admin/tenantsettings
4. The same workspace /items listing after recording the enablement blocker.

Both complete, unpaginated item lists contain 45 entries and zero Eventhouse,
KQLDatabase, Eventstream or WorkspaceMonitoring items. The workspace reports
capacity ec15bc07-8e88-436e-8dbe-485b9a7f4533, Central US, assignment Completed.
This does not establish active capacity health/SKU or the monitoring toggle state.

| Tenant setting | Returned state | Action |
| --- | --- | --- |
| PlatformMonitoringTenantSetting: Workspace admins can turn on monitoring | enabled, no group restrictions returned | Unchanged |
| FabricGAWorkloads: Users can create Fabric items | enabled, no group restrictions returned | Unchanged |
| MonitoringTenant: Users can create Monitoring items | disabled | Unchanged; not a documented requirement for the Eventhouse route |
| AllowMonitoringDataCollection: Allow monitoring data collection | disabled | Unchanged; no served UI establishes this as the blocking prerequisite |

The first two are the documented tenant prerequisites. The other similarly named
settings were retained rather than silently enabled: their names alone do not
establish that enabling them would provision the requested monitoring surface.
No tenant/capacity/workspace configuration mutation was sent. No capacity purchase
or scope expansion occurred.

## Grant, probe result, and preserved history

Existing dia-reader client ID ddd4d3cf-9cfd-440e-ac5b-be127caa46ea was retained.
No application, service principal, credential, identity, group membership or
permission changed. orderops_investigator remains the SQL reader.

#343-style grant checkpoint: target database absent; before/after KQL permission
reads not performed, exact executable grant unavailable without a database ID,
no grant command sent, no workspace role substituted. Database-viewer support
still needs testing once the actual monitoring database exists.

Accounting probes **0/4**, additional isolated load **0/1**. No ingestion delay
was observed, no KQL query returned empty/refused, and no RowsRead or RowsWritten
were obtained. Result remains **accounting unavailable from this surface ?
blocked before query by unavailable enablement UI and absent monitoring database**.
Earlier blocked results and all receipts remain unchanged. This dated result
supersedes status without rewriting historical claims or substituting counts.
The monitoring-enabled/granted capability cannot truthfully be recorded yet.

## Budget and cleanup

Four physical metadata requests, zero diagnostics/guards/mutations/model calls.
Part B **43 -> 47 / 120**; ordinary rolling allowance **198 -> 202 / 300** at this
checkpoint. No increase, credit, refund or reset. Ledger checkpoint is appended;
an annotation corrects its inherited identity-setup trial label to a monitoring
control-plane checkpoint, without altering counts or the original row.

No monitoring resource was enabled or disabled. Deferred cleanup remains:
turn off collection only in the fixture Workspace settings > Monitoring, capture
and verify the generated database/Eventhouse IDs, retain required evidence, then
use the monitoring settings' delete/remove control under then-current deletion
authorization. Verify the resulting item/collection state. Nothing is removed now.

README, status and CLAUDE updated. No engine/configuration bytes changed; previous
freezes remain invalid. No investigation run or fabricated accounting result.
Prior 398 ledger rows remain unchanged. Local sealed artifact:
`.local/round-two-20261003/monitoring-enable-resume.json`, SHA-256
`7d34a535ac3d700ec6b82f079c5dc1dcb32566e5c74a092d4d44a7bfd6142773`.
