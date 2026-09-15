# Current assessment and migration

**Planning revision:** the [first-class product plan](../../METADATA_DRIVEN_INVESTIGATOR_FIRST_CLASS_PRODUCT_PLAN.md) supersedes the earlier roadmap. Code facts below remain the inspected baseline; onboarding, native semantic decomposition and A-J are proposed, not implemented.

## Inspection basis and limits

This plan uses the root specifications, [scope alignment](../scope-alignment.md), [progress tracker](../progress.md), [handoff](../../PROJECT_STATE_AND_NEXT_STEPS.md), planning/execution/metadata/lineage code, native report context code, workflow/API/UI code, Fabric transformations, native Power BI model, lab verifiers/evaluators and CI workflow. Implementation paths below are relative to the repository root.

GitHub inspection during planning found PR **144** open from `feature/demo-rehearsal` to `main`, and PR **146** open from `feature/business-demo` to `feature/demo-rehearsal`. PR 142 was already merged. These are observations at inspection time, not permission to merge them now.

Historical verification in the handoff records 366 passing tests and a clean secret scan. This planning task does not rerun those tests or verify present cloud availability. The deployed platform and observed row counts are historical implementation evidence; current credentials, capacities and endpoints must be checked when an approved live test needs them.

## Working foundation to preserve

- Coherent synthetic order lifecycles and related customers, products, order lines, payments, shipments, refunds and audit events; 100,000 orders and 1,410,699 business rows in the recorded baseline.
- Azure order portal and Azure SQL source; bounded serverless-resume handling. Free SQL overage remains disabled. A query budget reduces consumption but cannot guarantee remaining subscription allowance.
- Fabric ingestion and transformations: ten Bronze, ten Silver and nine Gold tables in the recorded estate. Bronze uses overwrite, not an incremental change feed.
- Native Power BI artifacts: six model tables, 25 measures, five relationships and three reports. These are broader than the investigator's two supported metrics.
- Collected definitions, native report bindings, graph edges and explicit lineage gaps; publication and snapshot evidence.
- Reviewed ticket execution, authenticated local API, saved evidence, constrained explanations, local defect evaluations, reviewed issue/email envelopes and receipts.

## Where behavior is currently predefined

| Code and actual entry points | Current behavior | Migration treatment |
| --- | --- | --- |
| `scripts/ticket_planner.py`: `catalog`, `validate_plan`, `plan_ticket` | Catalog filters to Order Count/Net Cash. Scope is report, metric, currency, optional order ID. LLM drafts constrained fields; unsupported dates/customer/product are held. | Replace v2 metric enum with catalog references and typed scope. Preserve existing v1 validator and approval behavior. |
| `scripts/ticket_worker.py`: `process_one` | Validates those metrics and runs the fixed acquisition path; captured native slicers are held. Worker completion means execution completed, not that a business issue was resolved. | Dispatch by approved engine version; v2 invokes the state machine. Keep old completion semantics and explicit holds. |
| `scripts/cross_layer_investigation.py`: `LAYERS`, `MEASURES`, `asset_path`, `acquire`, `boundaries` | Specific order tables across SQL/Bronze/Silver/Gold/semantic; both metrics acquired. Distinguishes first observed boundary from first verified boundary. | Wrap as legacy tool initially; replace path construction with catalog/lineage-selected edges. Retain ordered-boundary proof requirements. |
| `scripts/investigation_query_worker.py`: `dax`, `extract_dax` and CLI | Repository-owned SQL/PowerShell and fixed DAX; host and filter validation. | Reuse connections, token audiences, response validation and bounded retry. Introduce separately validated IR renderer, not a raw-query parameter. |
| `scripts/investigation_checks.py`: `observation`, `compatible`, `compare`, `freshness` | Decimal and hash checks, exact scope/contract/snapshot comparability, complete-key comparisons, unknown freshness without policy. | Reuse deterministic checks through v2 adapters; strengthen provenance binding before creating comparable contracts. Never invent a snapshot ID to make checks pass. |
| `scripts/investigation_explanation.py`: `catalog`, `render`, `explain` | LLM selects backend finding and next-step IDs; no independent investigation. | Preserve grounding. Add hypothesis/test selection separately; render conclusions from validated outcome facts and references. |
| `scripts/metadata_inventory.py`: `Inventory`, `expand_definition`, `collect_sql` | SQLite scans/assets/observations; hashes, SQL metadata, TMSL `model.bim` expansion and native report parts. | Reuse collector. Build normalized catalog projection; record unsupported or unavailable capabilities rather than interpreting a complete scan as complete knowledge. |
| `scripts/metadata_connectors.py`: `MetadataConnector`, SQL/Fabric/Power BI implementations | Discovery, definitions and available refresh history; SQL freshness explicitly unsupported. | Keep connectors; split discovery capabilities from execution and verification capabilities. |
| `scripts/lineage_graph.py`: `Graph.find`, `Graph.traverse`, graph construction | SQL/notebook/reference-derived graph. DAX references are parsed with regex, not evaluated. Default traversal excludes filter edges. | Reuse graph evidence; add typed expression dependency and relationship semantics. Do not mistake reference discovery for a correct DAX-to-SQL translation. |
| `scripts/lineage_gap_policy.py` | Blocks conclusions for unresolved/conditional lineage; some unscoped notebook gaps block broadly. | Preserve blockers; narrow only with explicit scoped proof and regression coverage. Diagnostics may run without establishing a causal lineage claim. |
| `scripts/report_definition_evidence.py`: `bundle` | Hash-validated, same-scan report/model parts, explicit model binding. By-path or ambiguous binding rejected. | Reuse as catalog provenance. Missing filters are unknown, not proof of an unfiltered report. |
| `scripts/native_plan_context.py`, `scripts/report_slicer_context.py`: `check`, `assess` | Native context tied to lineage scan; supported slicer capture is not execution support. | Normalize typed filter context only when shape, values, relationship propagation and runtime context are supported. Preserve scan binding. |
| `scripts/ticket_workflow.py`: `TicketStore.claim`, `finish` | Durable tickets/events and leases. Reviewed claims do not reclaim expired running work; legacy CLI can reclaim and claim unreviewed work. | New engine uses a fenced lease and durable checkpoints. Do not borrow the unreviewed reclaim path for v2 recovery. |
| `scripts/background_worker.py`, `scripts/serve_investigations.py` | Finite reviewed local worker; fixed execution callback and feature flags. | Keep host and finite sessions; inject v2 executor explicitly. Local deployment is not a production distributed worker. |
| `scripts/investigation_evidence_api.py`: `EvidenceStore`, `create_app` | Read-only saved-run reader, authenticated APIs, legacy JSON result format. | Add versioned v2 endpoints/projections without changing old evidence interpretation. |
| `scripts/lab_filter_cause.py`: `verify_filter`, `verify`; `scripts/lab_refund_arithmetic.py`: `verify` | Specific equality checks against repository-owned defect queries; replay does not execute arbitrary receipt SQL. | Keep as v1 reference tests. New verifier operates on a generic, allowlisted relational IR and trusted baseline contract; no additional scenario-specific verifier. |
| `scripts/evaluate_lab_matrix.py`, `scripts/evaluate_multilayer_matrix.py` | Evaluator-only expected answers; tests include unexplained differences, stale receipts and offsetting records. | Preserve ground-truth separation and all expected outcomes; add a disjoint unseen-metric suite. |
| `scripts/business_demo.py`: `BusinessDemo`; `scripts/demo.py`; `scripts/review_ui.py` | Separate demo paths. Business demo has fixed scope/cause behavior; PNG storage is not screenshot understanding. | Retain recordings and old demos; replace presentation with shared v2 run projections in J. Do not describe old demo text as dynamic diagnosis. |

## Model and transformation constraints that matter

`infra/powerbi/OrderOps.SemanticModel/model.bim` contains `Order Count = DISTINCTCOUNT(FactOrderLine[order_id])`; Net Cash uses `IF(HASONEVALUE(...[currency]), SUM(...[net_cash_amount]))`. Refunded Orders uses `CALCULATE([Order Count], FactOrderLine[refund_amount] > 0)`. Existing ratios use `DIVIDE`. Power BI evaluates these definitions natively. Semantic IR identifies dependencies and comparison requirements; supported upstream equivalents require separate contracts, not a second DAX engine.

`infra/fabric/gold_models.py` deliberately separates order-day sales cohorts from refund-day events, aggregates child rows before joining, and computes net amounts from captured/refunded amounts. The agent must discover and honor these definitions. Summing a count from the wrong grain or applying the refund-event date to an order cohort can produce a plausible but invalid diagnosis.

`infra/fabric/bronze_to_silver.py` validates relationships, amounts and statuses before publishing; `infra/fabric/silver_to_gold.py` validates reporting outputs. Keep these checks. The new investigator reads their definitions/receipts as evidence and does not execute arbitrary notebook text.

## Existing debt and honest capability boundaries

1. **Documentation drift:** README and tracker previously lagged later work. This planning revision updates their summaries; Phase A still verifies branch/test evidence and preserves historical entries.
2. **Branch stack:** the latest demo code is not yet on main. Reconcile the stack before declaring a new baseline.
3. **Snapshot proof:** semantic run alignment does not prove the precise Direct Lake table versions that answered a query. Preserve `NOT_COMPARABLE` where that proof is absent.
4. **Metadata coverage:** a successful scan or 403 graph links is not proof that every filter, relationship, owner or runtime context is known. Missing RLS/bookmarks/runtime filters remain explicit gaps.
5. **Persistence:** local SQLite stores are useful and real, but not yet a hosted multi-user investigation service. Keep clear separation between proposed engine state and old result JSON.
6. **Causality:** existing discrepancy localization and local scenario replays do not constitute a general hypothesis/tool/evidence loop.
7. **Routing:** adapters and review workflows exist; standard investigator hosting does not automatically make every lab routing integration available. Verify composition in J. Preserve current issue-receipt-before-email sequencing where the envelope requires it.

## Migration sequence and removal policy

### Roadmap crosswalk

| Earlier roadmap | Revised location |
| --- | --- |
| A baseline | A baseline retained |
| B catalog | B onboarding plus C catalog/change detection |
| C tools/compiler | D native semantic tools plus E semantic analysis/capability evaluator; local DAX-engine proposal removed |
| D state/capabilities | F durable runtime state; onboarding readiness begins in B and is evaluated in E |
| E adaptive planner | G planner and deterministic verification |
| F generic cause/impact | D tool contracts and G verification/impact, tested in H |
| G unseen measure | H complex/unseen acceptance, expanded to eight families |
| H shared UI | I ticket workspace; basic admin UI moves earlier to B |
| I routing | J reviewed routing |

This crosswalk supersedes earlier phase letters; historical work records retain their original labels. No additional production data or scenario-specific handler is required simply because the roadmap expanded.

Use new package `scripts/investigator/` with `contracts.py`, `onboarding.py`, `context_store.py`, `catalog.py`, `semantic_graph.py`, `context_changes.py`, `capabilities.py`, `state_store.py`, `policy.py`, `orchestrator.py`, `classification.py`, `impact.py`, and `tools/`. These paths are proposed, not present implementation claims. Keep existing CLI wrappers and imports stable during migration.

1. Capture baseline and reconcile docs/PRs after approval.
2. Add registered/enabled models and immutable context versions through onboarding, then catalog resolution alongside the old planner. The v2 approved plan contains engine version, scope hash, metadata version and capability decisions.
3. Wrap old adapters as explicitly bounded tools; add native measure/dependency/dimensional execution and source/run/audit/impact tools separately. A legacy wrapper cannot advertise support for an unknown metric.
4. Persist v2 state and execute it through the existing reviewed host. Old runs stay readable through their original schemas.
5. Run v2 in isolated local tests; compare to v1 on supported old contracts. Live shadow runs are separately approved/budgeted and never double-query by default.
6. Pass revised A-H, including all eight acceptance families, before switching the default engine or adding broader demos.
7. Move business and technical views to the same outcomes, then connect reviewed routing.
8. Deprecate fixed-path orchestration only after old metrics, evidence reads, holds and UI acceptance pass under v2. Remove old engine branches in a later explicit cleanup; retain fixture/evaluator history and schema readers as needed.

No source data, Fabric table, report or semantic model needs to be removed for this migration. Rollback selects `bounded-v1` for new reviewed work; it never rewrites an existing v2 run or resumes it under different semantics.
