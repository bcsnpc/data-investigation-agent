# HealthNet connectivity and bounded totals — 2026-11-26

**The read-only XMLA group experiment succeeded: all three main totals match
their owner authoring baselines.** REST Execute Queries still refuses the same
service principal. SQL connectivity and current-table counts pass; five history
version counts now pass through current-table temporal queries. One ordinary
history-named table has no temporal parent and remains unrun. The anomalous
history INSERT reports remain unexplained, with the strict guard unchanged.

No tickets, AI model calls, injections, sealed test/answer reads, engine reasoning
or prompt changes. Changes are recorded in [the access log](healthnet-access.md),
with every revoke step. Work remains on draft PR #436; no merge or tag.

## Actual reader and surfaces

Existing `dia-investigator-round19` application. Source tokens identify its
home-tenant principal; Fabric SQL, HTTP and XMLA use its Fabric-tenant principal.
Tokens were verified in memory and never persisted. Owner credentials were used
only for the approved administrative changes and permission/configuration
readbacks. Aggregate results below came from the investigator, never the owner.

The laptop used the production gateway and managed SQL worker. ODBC Driver 18
is not installed here, so the supported connection/token seams used native
System.Data.SqlClient with the **same principal**, encrypted connections,
ApplicationIntent=ReadOnly, and the worker's unchanged database/object guards.
This was a real live connector check, not mocked data. Native XMLA used ADOMD
behind the gateway's existing `XMLA_EVALUATE` DAX validation. No Roles override
or EffectiveUserName was supplied. The cloud managed-identity federation
configuration is present but was not newly executed on an Azure worker here.

| Connection | Native database | SELECT 1 | Tables / cataloged columns | Direct unfiltered table counts |
| --- | --- | --- | ---: | ---: |
| clinical | hn_clinical, Azure SQL | PASS | 23 / 271 | 20 |
| billing | hn_billing, Azure SQL | PASS | 14 / 167 | 11 |
| raw | hn_raw, Fabric SQL | PASS | 33 / 350 | 33 |
| warehouse | hn_dw, Fabric SQL | PASS | 25 / 312 | 25 |

The column enumeration includes two source metadata views; table-column assets
in the catalog exclude their 24 columns. All counts and exact SQL object IDs are
in [the structured results](healthnet-smoke-results.json).

Of **89 direct unfiltered counts**, **8** have an identically scoped saved native
authoring baseline: all **8 match**, **0 mismatch**. The remaining **81** have no
identically scoped count in the saved authoring receipts used for comparison.
Filtered source billing summaries are not substituted for unfiltered counts.
This is not an 89/89 baseline-match claim.

### Owner-approved temporal alternative

The guard checks the current object, and Azure SQL performs its native
`FOR SYSTEM_TIME ALL` read using the reader's existing SELECT rights. No direct
history object is named as a FROM source, and no permission check was bypassed.

| Deferred history object | Current temporal object | All returned versions | Historical versions |
| --- | --- | ---: | ---: |
| hn_clinical.app.encounter_history | app.encounter | 250,000 | 0 |
| hn_clinical.app.order_line_history | app.order_line | 1,500,000 | 0 |
| hn_clinical.app.patient_history | app.patient | 60,000 | 0 |
| hn_billing.app.charge_history | app.charge | 505,322 | 0 |
| hn_billing.app.claim_history | app.claim | 289,614 | 0 |
| hn_billing.app.payer_plan_history | No native temporal parent | NOT RUN | NOT MEASURABLE |

These are **temporal-query version counts**, not direct physical history-table
counts. SQL temporal queries can omit zero-duration versions; the report does
not silently equate those scopes. Charge's first attempt returned serverless
resume SQL 40613; one retry passed. Original attempt retained.

Own permission metadata still reports INSERT=1 on all five active history
objects, even with the three earlier clinical DENYs present. No write grant,
owner/admin role or public/schema grant was found to explain it. No additional
DENY/REVOKE, permission change or guard exception was applied. Full audit,
including billingapp and the ordersops SQL 42119 limitation, is in
[healthnet-permission-diagnosis.md](healthnet-permission-diagnosis.md).

### Model totals after the HealthNet-only RLS group change

| Model | Main measure | Native authoring baseline | Gateway XMLA actual | Match | Gateway REST |
| --- | --- | ---: | ---: | --- | --- |
| Operations | Visits | 249,575 | 249,575 | YES | HTTP 401 |
| Revenue | Gross Charges | 1,935,995,659.28 | 1,935,995,659.28 | YES | HTTP 401 |
| Productivity | Visits | 249,575 | 249,575 | YES | HTTP 401 |

Each XMLA result includes `ok=1`. Operations required one propagation retry;
its earlier refusal is preserved. No reduction relative to the owner baseline
was observed for these totals. No conclusion about other filters/users is made.
The model-only unfiltered Investigator role has exactly one member, the newly
created HealthNet-only security group, containing only the existing investigator.
Native role/model readbacks prove that all other model definitions are unchanged.
Viewer and direct Read + Build remain unchanged; no Contributor grant.

REST returns `PowerBINotAuthorizedException` even after the group assignment.
Microsoft [excludes service principals on RLS models from Execute Queries](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group).
The working native XMLA result and the blocked REST route are reported separately;
this task did not change the investigator's runtime query transport or reasoning.
No further workspace permission change was attempted.

## Metadata and physical layer mapping

Native inventory scan `118e6c7b-ecab-41c1-b6e5-8773e1bc3eb1`, retained in
`.local/healthnet-smoke/catalog.sqlite`: 4 SQL databases, 95 table objects,
1,076 table-column assets, 3 reports, 3 models, 6 pipelines, 1 notebook,
1 dataflow, 2 lakehouses, 2 warehouses and 2 SQL endpoint item records (including
Fabric's dataflow staging lakehouse/warehouse, not additional mapped data layers).
An additional native report-page scan records all **4 pages across 3 reports**.

- All four named SQL connections resolve to native databases and object IDs.
- Source maps to **both** hn_clinical and hn_billing, with separate connection
  names and identity references. Raw maps to hn_raw.
- Silver/Gold share the verified hn_dw physical container. Exact table producer
  and logical layer bindings are not guessed from names or inferred merely by
  listing every warehouse table in both layers. Config retains this discovery gap.
- The three model and report IDs resolve, and model totals above are readable.
- Reader pipeline/notebook run history: **7 available** observations.
- **13 definitions unavailable** to Viewer: 3 reports, 3 models, 6 pipelines,
  1 notebook. Reader refresh history: **3 unavailable** observations. Thus visual
  definitions, measures/relationships and complete transformation bindings were
  not discovered under the investigator's scopes. Owner-only model definitions
  were used to verify the approved role change, not fed to intake.

Native [Get Item Definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item-definition)
requires read and write; [refresh history](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group)
requires Write. These are retained unavailabilities, not reasons to elevate the
investigator. Overall metadata collection remains **PARTIAL**.

## Safety, configuration and qualification

One nonexistent-table UPDATE was refused by the gateway with
`SINGLE_SELECT_REQUIRED`, **0 estate dispatches**. No actual SQL write probe.
The temporal and native DAX reads passed the same existing read-only validation;
no validator or permission guard was relaxed.

`config/estates/healthnet.json` is **READY_SEALED_TEST**, **enabled=false**;
all connectors remain disabled for ticket execution, installation is null.
This owner-requested state marks a sealed test boundary, not a claim of complete
metadata/readiness. `dia estate validate` succeeds offline with 0 network calls
and no secret resolution. The separate named native connection bundle also
validates offline. No draft worker/job was deployed.

Only the earlier owner-authorized generic smoke plumbing changed frozen engine
files: two config state validators and the managed worker's guarded literal
SELECT 1. **830/833 engine files and all 69 prompt-bearing files are unchanged**.
There is no HealthNet-specific intake, prompt, reasoning or verdict adjustment.

The final disabled configuration exposed an obsolete test assertion requiring
the deployment to stay at its original draft status with exactly two connection
entries. That assertion now verifies every permitted non-executable state,
disabled connectors, refusal of engine admission, both application-source roots,
and the unchanged single-connection practice fixture. This test-only correction
allows the two additional native raw/warehouse connection entries. Focused
config/API/SQL-worker verification passed **37 tests and 21 subtests**; no sealed
ticket expectation or engine behavior changed for it.

- Final qualified source `f49d761d`: **6,230 passed / 53 skipped**, 0 failures/errors.
  Its runtime engine/prompts are unchanged from the live smoke's `b80e790e`.
- [Fresh hosted qualification](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45897562482):
  full suite and **all 8 image shards succeeded**. This qualification did not
  publish or deploy an image; the earlier `b80e790e` image remains recorded.
- Saved replay classifications **123/123 unchanged**, including the original
  **28 REPLAY_FAILURE** and **9 NO_INVESTIGATION_CASE**; **86 REPLAY_FINISHED**.
  This is preservation of classifications, not 123 successful investigations.
- Sealed HealthNet artifacts are unchanged from approval commit `6e800e15`;
  no ticket or encrypted-answer body was inspected in this task.

Compute and final shared-ledger counters are in the structured results. Both
HealthNet databases retain their own free offer, mandatory AutoPause at its
limit, and 60-minute inactivity auto-pause. No paid continuation or SKU change.
Azure's CPU-billed metric is usage evidence, not an invoice. No current free-
balance datapoint was returned, so no fresh remaining-balance number is claimed.

| Final usage observation | Value |
| --- | ---: |
| Clinical CPU-billed metric, 20:00–21:16:44 UTC | 2,670.506 vCore-seconds |
| Billing CPU-billed metric, same window | 2,618.365 vCore-seconds |
| Task's metered reservations | 479 SETTLED, 0 open |
| Shared November physical ledger | 19,298 / 20,500 |
| Investigation allocation | 16,817 / 17,905 |
| SCAN allocation | 2,430 / 2,500 |
| Restoration allocation | 51 / 95; this task used 0, 44 remain |
| AI calls / AI spend in this task | 0 / $0 |

The ledger is above its 80% warning thresholds; no limit or usage counter was
reset. Administrative permission changes and initial failures are retained in
the access receipts; metered reservations are not a claim that every request
successfully dispatched a business query.

Original local receipts are pinned by [SHA-256](healthnet-smoke-evidence.json).
Remaining owner items: investigate the unexplained temporal INSERT report if
direct history access is required; decide separately whether the ordinary
history-named table may be counted directly; reconsider REST versus native XMLA
integration before an actual sealed test. No permission change is awaiting
automatic application.
