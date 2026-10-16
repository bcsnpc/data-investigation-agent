# Round Ten rebuild rehearsal

Recorded 2026-10-07 America/Chicago; continued 2026-10-08 UTC. Isolated publication, fresh context approval and the nine once-only attempts are recorded below. The nine historical expectations were not reproduced, and a portable rebuild from zero is not earned. Earlier checkpoints retain what was pending at the time.

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


## Human-approved continuation pot, 2026-10-07 America/Chicago

Reason: credit window closing; rebuild and billing ahead. Round Ten physical pot800 ->1500, rolling3000unchanged, investigation diagnostic12unchanged and model600unchanged. The native reserve remains its original100allocation with5already spent, so95remaining is preserved exactly; setting the allocation itself to95 would incorrectly leave90. No credit was restored, no counter reset, no historical manifest/tape edited. New active continuation manifest preserves the same catalog/environment and records whole-config hash`c9a27319e94d12e27ba797104a3b31f072d98f7302b1666f18937c91c93b65c0` (before`6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75`). Used652/1500at approval; ordinary work stops at1405, leaving753ordinary requests. New rehearsal/billing manifests inherit these budgets and will receive their own fresh context approvals. Configuration control used0estate/model requests.

## Audited load, models and predicate report: continuation checkpoint

The isolated Copy Job `ba52baf6-755a-43f1-a58e-0f6ca31c9b6f` declares the approved application table and the new application landing lakehouse. Data Pipeline `9235a87a-bdc7-48e5-968f-59e6bd601a76` invokes it and records its own activity output in the new ops Warehouse. Existing managed connections were read and reused; no credential or connection scope changed.

The existing publisher CLI could not obtain a SQL token: `[AuthenticationFailed] Failed to get access token`, zero estate requests. The administrator profile was not substituted. One isolated create-only pipeline Script activity created `dbo.load_run_audit` instead, job `279b1d88-c92e-48da-85db-2892756ef6d6`, Completed. This is a recorded manual factory dependency, not a diagnostic execution identity change.

The initial load ran once, instance `b335ae7d-0dea-450c-977d-fd2bcfdd6405`, Completed. As `investigator-reader@skynwhy.com`, the Warehouse returned exactly one audit row for that run, with own counters 360 rows read / 360 written, matching the copy activity's nested `rowsRead` / `rowsCopied`. Copy activity start `2026-10-08T04:47:18.4561973Z`, end `2026-10-08T04:48:45.2564481Z`; audit timestamps match. Watermark is null: it is not invented or inferred. Effective SELECT=1; INSERT/UPDATE/DELETE=0, without a new table grant. These counters establish accounting agreement, not individual delivery or aligned snapshots.

Two new semantic models and one new report are published:

| Item | ID |
| --- | --- |
| Original notebook-fed model | `ade205fe-52b1-43b5-980a-773b7b1de538` |
| Application-load model | `46687aa6-13d7-40ff-9c78-02f7bfd4e73a` |
| Predicate report | `3001db60-723d-44d3-b10c-7a50130f3c45` |

Explicit human Round Ten section3 authorizes the same scopes as the fixture. Existing publisher applied this request separately on each new model, with no write or additional workspace grant:

```json
{"identifier":"investigator-reader@skynwhy.com","datasetUserAccessRight":"ReadExplore","principalType":"User"}
```

On both models, the before listing is `Read`; the after listing is `ReadExplore`. Publisher and definition-reader entries are unchanged. Full before/after listings and requests remain in the sealed private models/report control receipt. The definition reader's existing Contributor role remains restricted by installation to code-definition retrieval, never quantity execution.

The first model baseline failed. A separately recorded same-reader detail request retained HTTP400 `DatasetExecuteQueriesError`, "Failed to execute the DAX query.", Analysis Services code `3242524690`, request `756bd000-78f4-4d2a-89a2-61f33e5e344d`. The publisher had substituted lakehouse IDs for SQL endpoint IDs in `Sql.Database`. Retained original definitions and returned endpoint metadata establish that mismatch. Only the two isolated new model expressions were corrected; original publication and failed probes remain unchanged. The first correction also hit `OperationHasNoResult` after a successful definition update; it was not reissued. A zero-request local selection error is preserved too. The fixture controller now distinguishes result-bearing provisioning from resultless updates, and a regression test guards the endpoint/item distinction.

After the corrections, the actual investigator reader served 8,765 from the notebook-fed model and 7,661 from the application-load model, each with its own quantity-bound identity report and sealed response. No refresh/reframe, elevated execution or altered data was used to obtain those values. This is setup verification, not an investigation or snapshot verification.

Continuation through these baselines charged52physical controls; total rehearsal controls95 including failures, zero investigation diagnostics/model calls. Pot704/1500 before fresh recollection, reserve95remaining, rolling3000/diagnostic12/model600 unchanged. Historical approval proofs and string-semantics observations were removed from the new manifest rather than rebound to new objects. Fresh collection/approval is underway; fresh lineage verification, the portable full apply executor and nine families remain incomplete. Billing has not started.


## Final isolated context and once-only rehearsal, 2026-10-08 UTC

The two original report referents were missing from the initial factory templates. Their retained collected page/visual definitions are now committed as templates and published only in the new workspace: Inventory Health e1b8e1 `3fa351b8-ff17-4b0e-bbce-3a24b1f9536e` and Warehouse Performance e1b8e1 `f650bba1-7e5c-4f42-97b9-60b7c5608da8`. Only model/workspace bindings and new logical IDs changed; original reports and ticket bytes did not.

Final discovery used46logical operations/55physical requests. Discovery `e81b21e2-54ef-4b74-b483-447065417c4e`, body hash `b5062f8349d4fdf5d248e6c8d7ce34a04643b5442bb8946b0a6c9688e1090bd9`, approves whole-config hash `5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7`, manifest `f535918e8afe8e7412b8788ed74d993cfaf8cb6ac3f1268b312df59151de9674`. Original model context95583877-28b4-42cb-ac60-b286f5971e8c/hashd9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284; application model contextc3178819-2f02-4469bb1e-c0814a0698cc/hash59343f9f43a0a284e120697c06e34e741c495bb65aa5b84ac4d2d14afb341ff7.

The exact notebook export1f85e5cbabbc56d718b3ade273644df6f050d678f3bf43923eafbd6dc21438d8 is explicitly a local export from retained publisher collection, not a code-reader cloud fetch. The manifest declares that route. Fresh semantics and lineage witnesses are separate from old-estate evidence. SQL observations on lakehouse endpoints are SQL evidence, never Spark evidence; the one literal-only Spark control ran as the fixture publisher, not the investigation reader. Owner-declared binary semantics remain DECLARED. All15 inferred profile witnesses were freshly VERIFIED under the final original-model context;32verification reads within33,72charged physical requests,0investigation diagnostics. These bounded aggregates do not establish global/rowwise equivalence or query-bound snapshot alignment. No snapshot flag was removed.

Nine original tickets each ran once against this baseline. A-G HELD at intake with TARGET_UNRESOLVED; H/I HELD with UNIMPLEMENTED_ROUTE for business-rule decisions. All9tapes validate; all9full historical expectations miss. C's old expected HELD was for a resolver-size limit, whereas this refusal is at intake and lacks the historical report-resolution record. No quantity probe, surface attestation, comparison or synthesis took place. Both deterministic refusal outputs and exact candidate lists are in [the full run map](round-ten-rehearsal-nine-families.md). No replacement or amended ticket. Nine intake model calls,0estate/diagnostic/guard requests; pot1013->1013/1500, rolling1138->1138/3000,95restoration remaining.

### Failed controls and accounting corrections remain visible

The initial binding route used the profile interface where the declared quantity interface was required: `BindingVerificationRoute.compile() takes 5 positional arguments but 6 were given`; its2metadata reads and failure are retained. A separate pass reached the unchanged35verification cap before the final source witness; that HELD remains. The final missing profile was verified in a separately recorded bounded session, and the new final context was subsequently reverified in full32/33. No investigation cap was raised.

The Gold semantics row initially failed the operator's descriptor check because DB_NAME was compared to an endpoint GUID rather than the retained endpoint display name. A separate correction refers to the original served row; no quantity read was repeated. Spark returned a GUID Livy session; the numeric-only helper failed after creation. The same session was resumed, one literal-only statement served and cleanup succeeded; no second session was created. Concurrent global-pot deltas were corrected append-only to session-specific physical reservations: Silver4 and Spark4, rather than their original overlapping deltas. No counters were refunded.

Original-report publication helpers failed locally on an absent import, the wrong create() signature, missing fabric_cli in the system interpreter and a changed uncertain mutation body. Failures are retained; a complete workspace listing established that the failed pre-dispatch attempt had created neither report, and an explicit new mutation key reused the exact prepared body. The module-import attempt retained one charged reservation but performed0estateHTTPrequests; the ledger appends that distinction without editing/refunding the original row. The private nine-case preparer also failed locally on the wrong manifest shape before any approval, model call or estate read. These are operator/tooling defects, not concealed live outcomes.

### Public factory and manual dependencies

`python scripts/fixture/rebuild.py --plan --manifest <existing-manifest>` remains offline. The explicit `--apply --parameters <approved-target.json> --output <new-directory>` path now creates only in an approved empty workspace, verifies the prepared application rows as a guarded reader, uses retained templates and actual returned IDs, compares every served notebook statement before one execution, creates the Warehouse audit table/pipeline and two endpoint-bound models/three reports, exports the served code and writes a fresh unapproved estate.yaml. `--grant-models` is separate and requires an explicit recorded decision for the two returned models. Cap refusal, uncertain mutation and partial publication stop rather than recreating objects. Twenty-seven focused tests passed, including injected end-to-end template binding and lost-notebook/nonempty-workspace refusal.

That command has not been executed from zero against a second empty workspace. The current rehearsal was assembled by the manual controls above, so it must not be retrospectively labelled a successful factory invocation. Workspace creation/roles, the table-only source grant, authorized managed connections, publisher CLI environment, model grants, actual reader audit verification, semantics/code-source declarations, context approval and per-binding verification are the recorded manual installation steps. Fresh installation approval remains explicit and is not manufactured by apply. Existing rehearsal workspace is retained for inspection. Earlier freeze remains invalid; #423 remains draft.

Billing publication is blocked on a connected Fabric editor for the documented Dataflow Gen2 destination step. The prepared source/procedure/report authoring inputs and sealed author-only inventory are recorded in [the billing installation checkpoint](round-ten-billing-install.md). No billing report, source reader scope, owner ticket or earned billing outcome is claimed.
