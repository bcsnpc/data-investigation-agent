# Round Ten rebuild rehearsal

Recorded 2026-10-07 America/Chicago. Rehearsal is incomplete. The isolated application source is seeded and its reader grant verified; foundation items are published. No models, reports or new context have been published. Later checkpoints below name execution state explicitly.

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

Initial preparation checkpoint, superseded by the dated execution below: an isolated `ordersops.app.stock_movements_rebuild_20261008`
source using the 360 committed synthetic movement rows. The parameterized source
plan is sealed locally with SHA-256
`757a5a6467d11e435907ac1eaf6597cdec7ec8e2eda6a42279f689101101ae77`.
The [exact table-only SELECT script](rebuild-application-source-grant.sql) is
reviewable. It names `orderops_investigator`, the existing SQL reader, which is
different from the two identities named in the workspace pre-approval. Its
scope decision was explicitly approved under CLAUDE.md section8 on 2026-10-07
America/Chicago and applied as recorded below. Existing source data and its
permissions are unchanged.

Documented control-plane methods: [Create Workspace](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/create-workspace), [Add Workspace Role Assignment](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/add-workspace-role-assignment).


## Isolated application source: explicit decision and execution

Dated 2026-10-07 America/Chicago. Human decision: "Approve the isolated table and table-only SELECT". The source is ordersops.app.stock_movements_rebuild_20261008, created from the 360 committed synthetic movement rows. Existing SQL database-owner credentials performed the control work; orderops_investigator performed the independent final reader verification. No identity, credential, database role, schema-wide grant or other-object permission changed. The administrator Fabric profile was not used.

The initial before-read failed with SqlException40613: ordersops was not currently available. No mutation was attempted. A separately recorded twenty-second pre-warm wait led to a control-query error156 because the operator used the reserved alias identity without brackets. A corrected attempt reused the governor admission key and was refused before dispatch, zero physical requests. The separately identified corrected control then served successfully. All original failures remain unchanged, followed by a distinct successful resume. These are controls, not investigation retries or diagnostic reads.

Exact applied grant (the prepared script was not changed):

```sql
-- Prepared only. New isolated rehearsal source; existing source and credentials unchanged.
-- Reader scope needs explicit human decision: orderops_investigator is not one of the two workspace readers named in section3.
GRANT SELECT ON OBJECT::[app].[stock_movements_rebuild_20261008] TO [orderops_investigator];
```

Before grant: direct permission listing and database-role listing, followed by the effective per-object check:

```json
[
  [
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": null,
      "major_id": "0",
      "class_desc": "DATABASE",
      "object_name": null,
      "permission_name": "CONNECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "978102525",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "warehouse_locations_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1010102639",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_products_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1042102753",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "product_rates_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1090102924",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "stock_movements_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1154103152",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "purchase_orders_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1218103380",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_adjustments_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1298103665",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "warehouse_locations_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1330103779",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_products_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1362103893",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "product_rates_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1410104064",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "stock_movements_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1474104292",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "purchase_orders_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1538104520",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_adjustments_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1938105945",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "stock_movements_round_two_20261003",
      "permission_name": "SELECT"
    }
  ],
  [
    {
      "role_name": "orderops_investigator_role"
    }
  ],
  [
    {
      "can_insert": "0",
      "can_update": "0",
      "can_delete": "0",
      "can_control": "0",
      "can_select": "0"
    }
  ]
]
```

After grant: the same listings/check and the unchanged existing-source baseline:

```json
[
  [
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": null,
      "major_id": "0",
      "class_desc": "DATABASE",
      "object_name": null,
      "permission_name": "CONNECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "110623437",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "stock_movements_rebuild_20261008",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "978102525",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "warehouse_locations_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1010102639",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_products_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1042102753",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "product_rates_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1090102924",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "stock_movements_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1154103152",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "purchase_orders_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1218103380",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_adjustments_e1b8e1",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1298103665",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "warehouse_locations_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1330103779",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_products_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1362103893",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "product_rates_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1410104064",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "stock_movements_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1474104292",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "purchase_orders_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1538104520",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "inventory_adjustments_0fd86f",
      "permission_name": "SELECT"
    },
    {
      "state_desc": "GRANT",
      "minor_id": "0",
      "schema_name": "app",
      "major_id": "1938105945",
      "class_desc": "OBJECT_OR_COLUMN",
      "object_name": "stock_movements_round_two_20261003",
      "permission_name": "SELECT"
    }
  ],
  [
    {
      "role_name": "orderops_investigator_role"
    }
  ],
  [
    {
      "can_insert": "0",
      "can_update": "0",
      "can_delete": "0",
      "can_control": "0",
      "can_select": "1"
    }
  ],
  [
    {
      "units": "7661",
      "row_count": "360"
    }
  ]
]
```

Only one permission was added: GRANT SELECT on the new object. All prior direct grants and database-role membership were compared and retained. New-table write/control rights remain absent. Actual reader verification:

```json
[
  [
    {
      "database_user": "orderops_investigator",
      "database_name": "ordersops",
      "identity": "orderops_investigator"
    }
  ],
  [
    {
      "first_version": "1",
      "first_modified": "2026-10-08T03:17:50.6199765Z",
      "last_modified": "2026-10-08T03:17:50.6199765Z",
      "last_version": "360",
      "units": "7661",
      "row_count": "360"
    }
  ]
]
```

The create operation used one parameterized JSON input for all committed rows inside a create-only transaction, not interpolated values or an engine-derived result. Exact control SQL:

```sql
SET NOCOUNT ON; SET XACT_ABORT ON; BEGIN TRANSACTION; IF OBJECT_ID(N'app.stock_movements_rebuild_20261008') IS NOT NULL THROW 50001,'Rehearsal source already exists',1; CREATE TABLE [app].[stock_movements_rebuild_20261008] ([movement_id] int NOT NULL, [warehouse_id] int NOT NULL, [product_id] int NOT NULL, [units] int NOT NULL, [event_day] varchar(4000) NOT NULL, [movement_type] varchar(4000) NOT NULL, [source_modified_at_utc] datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(), [source_row_version] bigint IDENTITY(1,1) NOT NULL); INSERT INTO [app].[stock_movements_rebuild_20261008] ([movement_id], [warehouse_id], [product_id], [units], [event_day], [movement_type]) SELECT CAST(JSON_VALUE([value],'$[0]') AS int), CAST(JSON_VALUE([value],'$[1]') AS int), CAST(JSON_VALUE([value],'$[2]') AS int), CAST(JSON_VALUE([value],'$[3]') AS int), CAST(JSON_VALUE([value],'$[4]') AS varchar(4000)), CAST(JSON_VALUE([value],'$[5]') AS varchar(4000)) FROM OPENJSON(@seed_rows); COMMIT TRANSACTION; SELECT COUNT_BIG(*) AS row_count,SUM(CAST(units AS bigint)) AS units,MIN(source_row_version) AS first_version,MAX(source_row_version) AS last_version,MIN(source_modified_at_utc) AS first_modified,MAX(source_modified_at_utc) AS last_modified FROM [app].[stock_movements_rebuild_20261008];
```

Source controls: nine physical requests total (one failed initial connection, one failed SQL pre-warm query, zero-request admission refusal, one successful pre-warm, six successful resumed controls). Zero diagnostic reads/model calls; no cap/reset/refund. Pot619 ->628/800; rolling744 ->753/3000 at the closing snapshot. This establishes the new reader scope and seeded table, not completion of the fixture factory or a source-consistency investigation.

Append-only control metadata correction: the successful source summary computed its auxiliary seal before adding physical_requests. The ledger artifact SHA-256 and SQL receipts remain correct; the original artifact is unchanged. A separate correction binds its exact artifact hash and the corrected complete-payload seal. No evidence, permissions or counts changed.


## Foundation publication and served-definition refusal

Recorded 2026-10-07 America/Chicago, 2026-10-08 UTC. Existing Fabric publisher identity, no administrator profile used, no new permission or credential. The target workspace was verified by ID/name/capacity and a complete empty item listing before creation. Every create was committed to a durable mutation journal before dispatch; uncertain requests are never automatically repeated.

| New artifact | Returned item ID |
| --- | --- |
| bronze | `1cbc0cde-434a-4f6b-82d4-4da300076736` |
| silver | `cfd8d7d5-a914-4ff8-96d0-bb8ccbc45d74` |
| gold | `0b36ee15-643c-464f-81b3-776aa4616872` |
| application-landing | `4e7523f8-a985-46c4-a14f-bfe297970ec0` |
| audit-warehouse | `b662d40d-dd16-4c8e-8e2c-ecc9d1941461` |
| notebook | `449097a3-945c-496b-956f-d7325a2b3d87` |

The four lakehouses separate notebook-seeded Bronze/Silver/Gold from the application Copy Job landing. The ops Warehouse is created but does not yet hold an audit table. No Copy Job, pipeline, model or report has been created in this workspace. Foundation publication charged13physical controls,0diagnostics/model calls; pot628 ->641/800, rolling753 ->766/3000 at its closing snapshot.

A local bootstrap using system Python failed with `ModuleNotFoundError: No module named 'fabric_cli'` before authentication or dispatch,0requests. The separate invocation used the existing configured Fabric CLI Python environment. This manual environment dependency is part of the migration record, not omitted from it.

The first served notebook definition retained only `# Fabric notebook source`,26characters and0executable statements. The intended path-rebound committed notebook carries13statements and20,179characters. Statement comparison refused with `RuntimeError: Served notebook statements differ from committed seed/transform; refuse execution`. The original response and failed attempt are preserved. No execution request or job was submitted. Definition retrieval charged3physical controls,0diagnostics/model calls; pot641 ->644/800, rolling766 ->769/3000 at closing. This is a publication-format failure; it does not establish that the original committed notebook was wrong or that a reader rejected it.

The separately recorded correction uses the documented ipynb representation on this isolated new notebook only. It does not edit the committed transformation statements or any original-estate item. Served statements must match before the single execution can proceed. The initial failed definition is retained, not overwritten. See Microsoft Learn's [notebook definition formats](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/notebook-definition) and [notebook execution API](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/background-jobs/run-on-demand-notebook). Correction/execution is pending at this checkpoint.

Budget preflight read the existing durable catalog, never a fresh counter:628used with5restoration requests already spent left77ordinary requests before foundation publication. The governor reserves the remaining95, so the actual ordinary boundary is705/800, not700. No cap or reserve changed; this explains the difference from a conservative earlier estimate. A new rehearsal manifest must retain this shared accounting and cannot reset usage by creating a new catalog/environment.


## Corrected notebook: served statements match, execution completed

The separately recorded ipynb correction on the isolated rehearsal notebook retained all13statements. Parsing the served FabricGitSource response and comparing ASTs against the path-rebound committed source passed before dispatch. No transformation or seeded row changed. The publisher then submitted one notebook execution, explicitly Spark with the new Bronze lakehouse as default.

Job `00b38ff0-a591-46c0-a849-d5f88a5f6010` returned `Completed`, failureReasonnull. This establishes successful fixture execution, not independent reader verification of every table or a completed investigation. There was no retry of notebook execution: the original failed served-definition check had submitted no job.

Correction, served-definition retrieval, one execution and its status reads charged8physical controls,0diagnostics/model calls. Pot644 ->652/800, rolling769 ->777/3000 at the recorded closing snapshot. Rehearsal controls total43physical including all failed requests. The remaining restoration reserve is95; the actual ordinary boundary is705, leaving53ordinary requests at this checkpoint. Investigation diagnostic12, rolling3000 and model600 remain unchanged. No counter reset/refund or new batch credit.

Outstanding: Copy Job and audited pipeline, Warehouse audit table and reader verification, two models, predicate report, state declarations, executable estate manifest, fresh context collection/approval/lineage verification, and nine once-only investigations. `scripts/fixture/rebuild.py` still has no complete apply executor: these durable operator controls are recorded manual steps, not represented as a portable factory or successful migration rehearsal. Billing has not started.
