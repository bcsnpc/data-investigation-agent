# HealthNet status ? read-only inventory

Observed 2026-11-26 18:42 UTC (2026-11-26 12:42 America/Chicago).
This is an owner-side inventory, not a DIA run or a test score. No DIA code, prompt,
rule, configuration, native resource, permission, schedule or data was changed.
No pipeline/refresh was started, no SQL database was resumed, and no model API was called.
Only this report is committed. `config/estates/healthnet.json` was **not written**.

## 1. Existing deployment and refresh status

Fresh Fabric and Power BI metadata GETs as the existing owner `admin@skynwhy.com`
confirm **HealthNet Analytics**, workspace `d237966c-b0b6-4123-bc89-e69643f4bf1f`,
Central US. Its existing capacity `ec15bc07-8e88-436e-8dbe-485b9a7f4533` is **Active,
FTL4, Trial**. The API did not supply its expiry; the October build's ?nine days
left? is not a current expiry claim.

**Row counts below are rough inventory from the October 30/31 owner-verified build,
not fresh counts.** The data is a fixed synthetic population (seed 20261030;
2025-10-01 through 2026-10-29). No business-data queries, DAX queries or new visual
checks were made. Current refresh/job dates below are live metadata observations;
a successful job is not a fresh row-content hash or reconciliation.

| Object | What exists / rough population | Latest recorded producer or refresh, UTC |
| --- | --- | --- |
| Azure SQL `hn_clinical` | 20 application tables; 60,000 patients, 250,000 encounters, 1,500,000 order lines, 2,774,006 results; 360 providers | Initial source build Oct 30; latest successful extraction Nov 26 **02:00:02?02:32:08**. Current last application-row mutation time was not queried. |
| Azure SQL `hn_billing` | 12 application tables; 505,322 charges, 289,614 claims, 579,228 claim lines, 256,716 payments, 268,700 adjustments | Initial source build Oct 30; latest successful extraction Nov 26 **02:40:15?02:54:53**. Current last application-row mutation time was not queried. |
| Lakehouse `hn_raw` (`0d5289e1-3133-4ddb-87bc-77e287b54935`) | 32 raw source-table copies at the build boundary, plus preparation/audit outputs. Source/raw counts matched at build. MPI preparation: 60,000 rows / 59,400 survivors; reference outputs: 14 payer-history and 396 department-mapping rows | Clinical and billing producers completed at **02:32:08 / 02:54:53 Nov 26**; preparation jobs below completed today. |
| SQL endpoint `hn_raw` | Deployed, provisioning **Success**; endpoint ID `ea22fc15-4818-46df-95dc-9c04727e260a` | Endpoint metadata read today; data served from Lakehouse. No separate refresh timestamp inferred. |
| Warehouse `hn_dw` (`ef705467-9870-481c-b977-aad877b83c30`) | 19 core/staging/mart projections and stored procedures. Examples: 60,000 staged patients, 249,575 retained encounters, 1,498,788 retained order lines, 505,322 charges, 95,018 provider-productivity daily rows | Producing nightly pipeline completed **Nov 26 03:35:23**. Its object's `lastUpdatedTime` is an October definition timestamp, not the data-refresh date. |
| Dataflow `df_reference_mapping` | Deployed, current job **Completed** | **Nov 26 03:30:35?03:34:12** |
| Notebook `nb_patient_mpi` | Deployed, current job **Completed** | **Nov 26 03:30:44?03:31:51** |
| Model **HealthNet Revenue** (`df6e3f67-deb6-4cb8-b15a-353176931679`) | Import per build definitions; principally the charge/claim/payment/adjustment marts, e.g. 505,322 charge rows | Scheduled refresh **Completed Nov 26 04:32:11?04:38:50** |
| Model **HealthNet Productivity** (`0ef2b1a3-c6b7-4623-b962-39fe12c84d06`) | Import per build definitions; encounters/procedures/orders and 95,018 daily productivity rows, with 360 providers | Scheduled refresh **Completed Nov 26 05:01:03?05:07:49** |
| Model **HealthNet Operations** (`85e662ed-c4e6-41fb-9e43-be0c5a6aeeae`) | Direct Lake per build definitions; operational marts, e.g. 249,575 encounters and 1,498,788 order lines | Latest recorded **DirectLakeFraming Completed Nov 12 09:16:19?09:16:57**. An Oct 31 framing failure is retained. This date alone does not establish stale results; current framing/data equivalence was not tested. |

Three deployed reports are still bound to the intended models:

| Report | Link | Data freshness |
| --- | --- | --- |
| HealthNet Operations | [Open](https://app.powerbi.com/groups/d237966c-b0b6-4123-bc89-e69643f4bf1f/reports/da276dc2-b133-40a9-8da4-fde9f9980545) | Uses Operations model above; no independent report-data refresh. |
| HealthNet Revenue | [Open](https://app.powerbi.com/groups/d237966c-b0b6-4123-bc89-e69643f4bf1f/reports/d47bb5e2-608f-4294-85cd-8fb0ade7a5d4) | Uses Revenue model above. |
| HealthNet Doctor Productivity | [Open](https://app.powerbi.com/groups/d237966c-b0b6-4123-bc89-e69643f4bf1f/reports/48b38369-2aac-427c-9c4b-a184fb464808) | Uses Productivity model above. |

The build records 36 visual containers, two filtered bookmarks and a doctor
drill-through; these were not re-rendered today. Reports do not store a separate
row population. Build counts/security observations: [build summary](hospital-estate-summary.md)
and [unsealed build baseline](hospital-estate-baseline.md). Models have dynamic RLS
and Doctor column restrictions; owner-visible results must not be assumed to equal
an ordinary user's results.

Six pipelines remain deployed:

| Pipeline | Latest native job | Schedule |
| --- | --- | --- |
| `pl_clinical` (`db94b75c-7898-4cc8-94d3-33356b834948`) | Completed Nov 26 **02:32:08**, run `5baecf03-85d0-4875-83b6-0fc480ba0e6f` | Enabled, daily **02:00 UTC** |
| `pl_billing` (`006744b8-2e01-4a39-b46b-6066330dfe1b`) | Completed Nov 26 **02:54:53**, run `12769e55-9f58-467c-a02e-4ee91b5a5cf7` | Enabled, daily **02:40 UTC** |
| `pl_nightly_run_all` (`d91893e9-aed1-4585-b56b-6c3c488bed8a`) | Completed Nov 26 **03:35:23**, run `09d39c4d-3783-422a-ab8b-abff3ed691dc` | Enabled, daily **03:30 UTC** |
| `pl_owner_connectivity` | Historical setup run Failed Oct 30 **23:52:37**, missing `workspaceId` | No schedule; retained build attempt, not a current production-pipeline failure |
| `pl_owner_connectivity_v2` | Completed Oct 30 **23:54:42** | No schedule |
| `pl_owner_connectivity_v3` | Completed Oct 30 **23:56:34** | No schedule |

Also deployed: Dataflow-managed `StagingLakehouseForDataflows_20261030235002`
(lakehouse `2f71c331-c25a-4778-9a80-6bd8d732a43f`, SQL endpoint
`0ba8841d-a9f0-4438-9ad4-4ce2972cc46f`) and
`StagingWarehouseForDataflows_20261030235002`
(`6ac1c979-f64b-43b4-879b-7cdd8fa42740`). Their row populations were not enumerated;
these are staging artifacts, not extra source systems. Workspace item listing
returned 20 objects total; no continuation was reported.

## 2. SQL databases and November allowance

HealthNet uses **both `hn_clinical` and `hn_billing`**, on
`sql-orderops-9696025.database.windows.net`, resource group `rg-investigator-dev`,
subscription `d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9`, Central US.
It does **not** use `ordersops` or `billingapp` as its application source.

Both are General Purpose serverless `GP_S_Gen5`, max 2 vCores / 32 GiB;
ARM reports `useFreeLimit=true`, `freeLimitExhaustionBehavior=AutoPause`, and
`autoPauseDelay=60`. Both currently report **Paused**.

| Database | Latest remaining free vCore-seconds (conservative minimum) | Consumed | Pause timestamp, UTC |
| --- | ---: | ---: | --- |
| `hn_clinical` | **58,442** | 41,558 | Nov 26 **02:47:13** |
| `hn_billing` | **78,324** | 21,676 | Nov 26 **03:09:32** |

The latest nonempty Azure Monitor hourly buckets are stamped **Nov 26 02:35 UTC**;
remaining/consumed change within a bucket, so the table uses minimum remaining and
maximum consumed. These are latest recorded metrics, not an instantaneous counter.
The positive balances and today's successful extractions do **not** indicate
November free-limit exhaustion; their paused state is consistent with inactivity.
No SQL login was attempted to wake them or obtain a new 42119 result.

Each free-offer database has its **own** monthly 100,000 vCore-second allowance,
renewing on the first of the month. `ordersops` exhausting its allowance does not
exhaust HealthNet's two allowances. [Microsoft free-offer FAQ](https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer-faq?view=azuresql)
No paid-continuation setting was changed.

## 3. Test tickets, expectations and seals

**No dedicated HealthNet test set was identified: 0 ticket files, 0 expected-answer
files, 0 seals and 0 grading packets in the named/tracked inventory.**

- Checked filenames under `acceptance/tickets/`, `tests/tickets/` and
  `fixtures/hospital/`, plus named local/Downloads locations. There is no dedicated
  HealthNet ticket directory in those locations.
- `fixtures/hospital/` contains builder, SQL, pipeline, notebook, model and report
  assets. The generator's unit tests are not investigation tickets.
- The existing build baseline documents 64 default/bookmark contexts (58 native
  data-query checks and six static contexts). These are **unsealed build checks**,
  not an independently authored sealed ticket/expected-answer set.
- Generic `acceptance/tickets/guided-v5/` contains sealed ticket/expectation files.
  Its seal metadata says 40 tickets and has no HealthNet source reference. The
  sealed ticket and expectation contents were **not opened** or repurposed. This
  does not certify the contents of any external/private set unknown to this inventory.
- Historical `.local/hospital-estate/` build-receipt paths mentioned in the docs are
  no longer present at the checked current/older workspace paths. No archive was
  downloaded or rehydrated for this check.

## 4. Prior DIA use and tuning: evidence and limits

**No HealthNet DIA scan, investigation, scored run or engine tuning was found.**
The evidence supports retaining it as an unseen-runtime estate:

1. Hospital build PR #433 merged at `3e2c30c8bfa1c15f0f2525eca618e304fa131209`.
   Its 102 changed files are 96 hospital fixture assets, five docs and one generator
   test file; **zero `scripts/investigator/` changes**. The build summary explicitly
   records no hospital ticket/DIA scan/investigation/model call and no DIA grants.
2. All-ref git searches for HealthNet's name, workspace ID and source DB names found
   no matching changes in the investigator/cloud investigation paths or estate
   installations. Hospital-related script changes are builder/generator tests,
   not investigator reasoning or prompts.
3. **3,404 retained run/deployment metadata files** were checked for HealthNet
   references, with **zero matches**. Only deployment-envelope fields were examined;
   no sealed ticket/expected-answer files were opened. This is retained local history,
   not a claim to have exhaustively searched every deleted/archived/external log.
4. Current workspace role assignments list **only the owner Admin**. Each model's
   direct users list also contains only the owner. No investigator/scanner principal
   or security group is listed. Source SQL grants were not queried while paused;
   the build/owner-action records say those grants were deliberately left unapplied.

The builder/operator has seen the architecture and public build baseline; that is
not operator blinding. **Do not supply this report, build answers or grading truth
as the future DIA investigator's context.** No result of this inventory was added
to engine code, prompts, rules, a DIA graph, case file or model request.

## 5. Mapping to `config/estates/healthnet.json` (not created)

| R28A field | Maps cleanly | Still missing / qualification |
| --- | --- | --- |
| Identity/references | Estate name, existing Fabric tenant `dff91047-ebc2-4657-8dbe-5af328d57780`, source Azure tenant `aeb4d0a9-e637-4a7e-8efc-63cf0c3827df`, subscription/RG and workspace ID are known. Per-identity tenant references support the split. | Choose the permanent estate ID and only approved DIA identity references; owner connections are not investigator credentials. |
| Connectors/objects | Native workspace, lakehouse, warehouse/SQL endpoints, six pipelines, three models and three report IDs are known; source server/database names are known. | Current table/object IDs and exact admitted bindings are not in a HealthNet DIA inventory; no discovery was performed by DIA. |
| Layers | Source = the two application DBs; Bronze = `hn_raw`; refinement = MPI/reference preparation and warehouse staging/core objects; serving = warehouse marts; then model/report. | Silver/Gold are logical roles within the deployed artifacts, not separate Silver/Gold lakehouses. Validate the concrete per-path bindings rather than invent physical layers or links. |
| Source of truth / deepest reach | Source role can name the application systems conceptually. | Deepest *DIA-accessible* layer is not established; even report/model access is ungranted. Do not copy the practice estate's reachability. |
| Identity/secrets | Existing investigator/scanner and existing vault can be referenced by name, without new secret values. | HealthNet scope/grants and identity/endpoint readback are pending owner approval; no secrets were read or copied. |
| Model/limits/optional sources | R28A fields are available; optional catalog/ontology/glossary can remain off. | Select provider/model and explicit HealthNet budget allocation later. Existing R27 funds/reserves are not a HealthNet allocation. |
| Native installation | Existing same-platform adapter is relevant. | **Current executable bundle has one `sql.database` slot and requires exactly one connection bundle** (`adapters/estate_installation.py`; `metadata_config.py`). Two source DBs cannot simply be written into that scalar. A complete enabled multi-source config is not established by filling the outer connector list. Multi-root/per-path native support needs a separate generic qualification; it was not changed or tested here. |

A **disabled draft** is describable from existing metadata. A fully admitted,
validated, executable HealthNet installation is **not yet ready**. No configuration
file or workaround was written, and no claim is made that the current R28A runtime
has already qualified this multi-source architecture.

## 6. Missing before a zero-context test

- **Data:** estate is populated; no missing initial seed is apparent. Counts/hashes
  are historical. Establish a current, owner-side baseline/reset receipt at test
  time without feeding answers to DIA. Keep any future scenario changes separate
  and reversible; none were made here.
- **Refresh:** today's main jobs and Import refreshes are successful. Confirm current
  Operations framing/data readiness before testing; its latest explicit framing
  record is Nov 12. No refresh was triggered or stale-data verdict asserted here.
- **Permissions:** separate owner approval/application of the existing DIA reader's
  workspace Viewer, model Read/Build and source/warehouse read-only scopes; the
  scanner's established definition/history-only pattern if required. Verify RLS/OLS
  behavior as the actual reader, without impersonating the owner or a business user.
  Source contained-user/role membership remains to be checked directly later.
- **Configuration/native access:** fill and validate a real HealthNet config only
  after its generic multi-source binding gap and per-path source roots are resolved;
  perform native metadata discovery under the approved read identity, not by copying
  build answers. No HealthNet config exists yet.
- **Tickets/oracle:** independently author tickets and expected records; owner/reviewer
  approve and hash-seal them before DIA sees any ticket. No dedicated set was found.
- **Grading:** prepare blinded ticket/expectation/evidence packets, independent graders,
  disagreement review and explicit funding/caps. No HealthNet packets or score exist.
- **Zero-context boundary:** freeze the generic engine before the test, exclude this
  report/build baselines from its prompts, and retain a first-use audit. This inventory
  supplies no HealthNet-specific engine fix, rule, prompt or example.

## Evidence retained locally

Fresh read-only receipts are under `.local/healthnet-status/`: `sql-databases.json`,
`hn_clinical-metrics.json`, `hn_billing-metrics.json`, `fabric-metadata.json` and
`log-inventory.json`. Fabric/Power BI inspection made 30 metadata GETs as the existing
owner; Azure CLI made control-plane/monitor reads only. Tokens stayed in memory.
No clinical/billing row contents were fetched. Sealed bodies were not opened.
Public build/history references: [summary](hospital-estate-summary.md),
[design history](hospital-estate-design.md), [owner actions](owner-actions.md).
