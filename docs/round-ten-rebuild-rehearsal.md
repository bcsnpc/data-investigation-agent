# Round Ten rebuild rehearsal

Recorded 2026-10-07 America/Chicago. Rehearsal is incomplete; no data, models, reports or new context have been published.

Explicit human authority: Round Ten section3 preapproved one `dia-rebuild-rehearsal` workspace on the current capacity, administrator profile for workspace creation only, and the same investigator-reader/code-reader scopes as the fixture. Workspace remains in place; original fixture untouched.

Workspace `d028fa2b-0d1b-4dd8-b423-37dd161cd5d0`, capacity `ec15bc07-8e88-436e-8dbe-485b9a7f4533`. Creation returned HTTP201; GET verified the returned workspace. Actor `admin@skynwhy.com`, object `23de217f-6e14-49cf-9acd-47dcd83cb82f`, isolated `.local/azure-fabric-sql` profile. Existing publisher CLI performed before/after reads and subsequent grants; no further admin-profile request.

## Identity scope change: explicit human decision

The original fixture role listing established exactly Viewer for investigator-reader and Contributor for investigator-code-reader. Both were absent before; exact requests and verified after listing follow. No new registration, token audience, credential or existing-workspace permission changed. Contributor remains the code-definition identity, never an investigation executor.

| Principal | Before | After |
| --- | --- | --- |
| investigator-reader@skynwhy.com (`8a582d2a-ecb4-4320-bf72-75a529a0d382`) | No assignment | Viewer on this workspace |
| investigator-code-reader (`dc89155f-9a9a-4daa-9c20-7eff55818ccd`) | No assignment | Contributor on this workspace |

Exact grant requests:

`POST /v1/workspaces/d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/roleAssignments`

```json
{
  "principal": {
    "id": "8a582d2a-ecb4-4320-bf72-75a529a0d382",
    "type": "User"
  },
  "role": "Viewer"
}
```

`POST /v1/workspaces/d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/roleAssignments`

```json
{
  "principal": {
    "id": "dc89155f-9a9a-4daa-9c20-7eff55818ccd",
    "type": "ServicePrincipal"
  },
  "role": "Contributor"
}
```

Before listing:

```json
{
  "value": [
    {
      "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
      "principal": {
        "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
        "displayName": "Chaitanya Bhogireddy",
        "type": "User",
        "userDetails": {
          "userPrincipalName": "admin@skynwhy.com"
        }
      },
      "role": "Admin"
    }
  ]
}
```

After listing:

```json
{
  "value": [
    {
      "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
      "principal": {
        "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
        "displayName": "Chaitanya Bhogireddy",
        "type": "User",
        "userDetails": {
          "userPrincipalName": "admin@skynwhy.com"
        }
      },
      "role": "Admin"
    },
    {
      "id": "8a582d2a-ecb4-4320-bf72-75a529a0d382",
      "principal": {
        "id": "8a582d2a-ecb4-4320-bf72-75a529a0d382",
        "displayName": "investigator reader",
        "type": "User",
        "userDetails": {
          "userPrincipalName": "investigator-reader@skynwhy.com"
        }
      },
      "role": "Viewer"
    },
    {
      "id": "dc89155f-9a9a-4daa-9c20-7eff55818ccd",
      "principal": {
        "id": "dc89155f-9a9a-4daa-9c20-7eff55818ccd",
        "displayName": "investigator-code-reader",
        "type": "ServicePrincipal",
        "servicePrincipalDetails": {
          "aadAppId": "2dd2f5c3-f7af-4804-b79e-6019e63efa60"
        }
      },
      "role": "Contributor"
    }
  ]
}
```

Workspace creation and role controls charged ten physical requests, zero diagnostic reads and zero model calls. Pot609 ->619/800; rolling734 ->744/3,000. No cap changed. Exact responses, headers and durable non-retrying mutation journal stay private; ledger records the human decision and before/after.

## Procedure gap

`scripts/fixture/rebuild.py` accepts only `--plan`; its tests deliberately reject `--apply`. The committed plan lacks an executor, so the requested rehearsal cannot be described as completed by that script. This is a migration-procedure gap, not an estate investigation result. Apply implementation and its prerequisite validation are pending. No new SQL table or reader grant is inferred from a plan.

Documented control-plane methods: [Create Workspace](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/create-workspace), [Add Workspace Role Assignment](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/add-workspace-role-assignment).
