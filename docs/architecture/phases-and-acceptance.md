# Engineering phases and acceptance: revised A-J

Latest continuation: PR #190 merged. [Joint native capture](../joint-native-capture-milestone.md) now obtains a direct native total and supporting projected groups in one response, reconstructs supported arithmetic, and feeds the saved assessment into adaptive planning and the workspace. Live complete, empty and partial checks passed under the dedicated reader. D/H shared-generation, effective report context and causal proof remain open; hosted v2 is still pending.

Latest continuation: PR #184 merged. [Native dependency calculation contexts](../dependency-context-milestone.md) now preserve supported measure-local filters through adaptive child reads, with scope review, sealed context evidence and eight live parity checks. This advances D/E/G; full B-G gates, Phase H and hosted v2 remain open.

Live prerequisite status: the [native proof preflight](../native-proof-preflight-milestone.md) completed on 2026-09-15. D/H live acceptance remains **blocked** on enforceable publication control, shared-generation/fixture evidence and effective identity/context. Definition/role/refresh observations do not satisfy those gates.

Implemented: [aggregate-to-record reconciliation](../record-aggregate-reconciliation-milestone.md) connects supported direct counts/sums to sealed captures and reviewed record projections. This is arithmetic consistency; shared-generation and effective-context proof remain open.

Implemented: [reviewed record discovery](../reviewed-record-discovery-milestone.md) reuses model-level record projections across tickets with complete scope, typed catalog validation, revocation and paired adaptive evidence. Review remains intent, not causal or semantic proof.

**Phase plan with implementation tracked separately.** This replaces the earlier A-I sequence with the [first-class product plan](../../METADATA_DRIVEN_INVESTIGATOR_FIRST_CLASS_PRODUCT_PLAN.md). Phase A is verified; see [baseline evidence](../bounded-v1-baseline.md). B/C have an [implemented onboarding/catalog slice](../model-onboarding.md); D/E now have [native diagnostic](../native-catalog-diagnostics.md) and [capability assessment](../capability-evidence-assessment.md) slices. F now has a [durable typed runtime foundation](../v2-diagnostic-milestone.md). G now has an [evidence-led diagnostic loop](../adaptive-investigation-milestone.md), with [shared usage and cancellation controls](../runtime-governance-milestone.md). D/F/G also include [bounded native/source readback and keyed evidence](../keyed-readback-milestone.md); complete published-generation and causal certification remain open. Remaining B-G gates and H-J are not complete.

A preserves the baseline. B-C establish onboarding and reusable context. D-E provide native tools and semantic capability evaluation. F-G make execution durable and adaptive. H proves architectural generality with eight acceptance families. I-J finish the shared ticket experience and reviewed handoff.

Dependency order: **A -> B -> C -> D -> E -> F -> G -> H -> I -> J**. Contracts can be designed together, but do not defer D's safety to E or F's recovery to G. Basic admin UI belongs to B; full ticket UI belongs to I. Early tests accompany every phase. Avoid unrelated feature PRs; completion is an evidenced exit gate.

## A - Freeze current bounded POC

**Objective/why:** preserve a reproducible `bounded-v1` while building v2.

**Existing:** README, tracker, handoff, demo PR chain, CI and current tests. **New:** baseline manifest/tag after authorized review; no engine rewrite.

**Tasks:** recheck PR144/146 and final branch state; reconcile/merge only under applicable authorization; retain local changes and demos; record exact commit/dependency/fixture hashes; pin engine version for saved runs; correct stale documentation. Run existing CI-equivalent checks and local matrices, with live verification separate.

**Acceptance/tests:** old metrics, holds, evidence readers and both demos reproduce. Record actual fresh test results, not the historical 366-pass count as current. Baseline is identifiable and rollback documented.

**Regression risk/mitigation:** branch-stack loss; compare final trees and keep manifests. **Non-goals:** new scenarios, cloud redesign or report expansion.

## B - Product model onboarding foundation

**Objective/why:** let admins register, review and enable investigation models without hardcoded IDs.

**Existing:** inventory/connectors, configuration, API host and auth patterns. **New:** `scripts/investigator/contracts.py`, `onboarding.py`, `context_store.py`, basic admin API/UI modules.

**Tasks:** persist organization/environment/connection/model/report/metric identities, ModelContextVersion, BusinessDefinition, Owner, Policy and scan/readiness refs. Implement lifecycle and enable/disable controls. Add basic admin forms/status and role separation. Store context provenance and confirmations. Expose models through IDs from registration, not embedded estate assumptions.

**Acceptance/tests:** register two models with duplicate metric names; scan/review/enable one and exclude disabled reports from ticket selection. Reuse confirmed business context across tickets. Reject unauthorized transitions, cross-environment references and stale revisions. Degraded readiness is honest pending C-E.

**Regression risk/mitigation:** enablement bypass and secret exposure; scoped authorization and reference-only credentials. **Non-goals:** polished UI, multi-tenant SaaS hosting or claiming full readiness from registration.

## C - Deep semantic catalog and change detection

**Objective/why:** maintain reusable semantic, report and technical context as models change.

**Existing:** metadata inventory/connectors, lineage graph/gap policy, report bundles, native filters and scan comparison. **New:** `catalog.py`, `semantic_graph.py`, `context_changes.py`, enrichment projection.

**Tasks:** discover all v2 measures; retain definitions, dependencies, relationships, report/page/visual context, source bindings, available run metadata and coverage gaps. Connect technical lineage. Add optional provenance-labeled LLM enrichment. Implement delta/triggered scans, affected-subgraph closure and atomic context publication. Invalidate relevant confirmations/capabilities on material changes.

**Acceptance/tests:** add/rename/delete a measure and change a relationship; catalog updates without Python edits. Partial/denied scans do not infer deletion. LLM-inferred fields cannot become authority. Active plans detect relevant stale context; unrelated changes do not invalidate unaffected evidence.

**Regression risk/mitigation:** guessed edges and latest-scan substitution; same-version hashes and explicit gap tests. **Non-goals:** arbitrary DAX evaluation or assuming all source APIs expose every field.

## D - Semantic execution and typed investigation tools

**Objective/why:** execute safe generic diagnostics against real systems.

**Existing:** query/auth/retry workers, checks, native context, freshness, lineage, source audit schema. **New:** `tools/registry.py`, `semantic.py`, `sql.py`, `context.py`, `comparison.py`, `freshness.py`, `application.py`, `lineage.py`, `transforms.py`; bounded query-plan validators.

**Tasks:** implement typed requests/results/receipts; native measure/dependency/dimensional evaluation; report-context evaluation; bounded DAX/SQL; asset/key/aggregate comparison; transform/run/watermark inspection; application-intent/source reads; upstream/downstream/owner tools. Wrap legacy acquisition explicitly as bounded-v1. Validate scope and limits from the first adapter call.

**Acceptance/tests:** tools accept resolved asset IDs and diagnostic intents, never named scenario dispatch. Real Power BI supplies parent and child values. Test escaping, BLANK, context propagation, dimensional tails, readonly rejection, auth failure and timeouts. Source audit tests distinguish independent intent from committed audit. Probe version-proof feasibility early for H.

**Regression risk/mitigation:** unrestricted execution or hidden data broadening; parser/plan admission, least privilege and derived-scope bounds. **Non-goals:** a second DAX engine, arbitrary stored procedures/notebooks, new source platforms.

## E - Semantic operation and capability evaluator

**Objective/why:** distinguish native queryability from decomposition and upstream proof.

**Existing:** catalog/lineage and D tools; comparison/provenance helpers. **New:** `capabilities.py`, `semantic_operations.py`, supported upstream comparison contracts.

**Tasks:** classify additive/count/ratio/derived arithmetic/dependency/filtered/dimensional operations and relationship/time context. Compute the five support states and per-request eligibility. IR describes semantics, never replaces Power BI execution. Register supported upstream equivalents with authoritative source/grain/filter/date/blank contracts. Publish per-metric/report/model readiness.

**Acceptance/tests:** complex derived measures evaluate natively; supported children decompose recursively. Unsupported inherited context produces a decomposition gap without blocking an otherwise safe native parent query. Queryable-but-not-reconcilable cases render PARTIAL accurately. Changing a definition recomputes eligibility. No metric-name whitelist.

**Regression risk/mitigation:** support overclaim; separate capability axes and negative contract tests. **Non-goals:** all calculation groups, many-to-many reconciliation or arbitrary time intelligence.

## F - Persisted InvestigationState and runtime registry

**Objective/why:** make adaptive work resumable and auditable before enabling the planner.

**Existing:** tickets/review/background worker/evidence API. **New:** `state_store.py`, `policy.py`, additive state/receipt/budget migrations.

**Tasks:** pin engine, scope, ModelContextVersion, business context, lineage and capability decisions. Persist hypotheses/tests/assets/questions/observations/evidence/receipts and stop reason. Implement reservations, fenced leases, atomic receipt/state commit, artifact recovery and explicit uncertain-execution holds. Preserve old evidence readers.

**Acceptance/tests:** crashes before dispatch/after result/after commit do not silently duplicate completed work or lose evidence. Stale workers cannot commit; disablement/relevant context change stops new dispatch. Clarification creates a reviewed scope revision. Budget survives restart.

**Regression risk/mitigation:** legacy unreviewed reclaim path; explicit v2 recovery and approval hashes. **Non-goals:** distributed queue or cloud hosting redesign.

## G - Evidence-led planner and deterministic verification

**Objective/why:** tests depend on observations, not a fixed layer path.

**Existing:** LLM invocation, explanation grounding, comparison/provenance and local replay invariants. **New:** `orchestrator.py`, action schema, `verification.py`, `classification.py`, `impact.py`.

**Tasks:** load the relevant context pack, choose eligible tests, persist/revise hypotheses, recurse into divergent dependencies and slice metadata-derived dimensions. Enforce budgets/depth/no-progress stops. Implement generic proof gates for transform replay, context reproduction, freshness and independent application-intent mismatch. Derive impact/ownership from evidence. No new scenario-specific verifier.

**Acceptance/tests:** changed first evidence changes subsequent tool choices; at least one hypothesis rejected/refined. Different supported causes use appropriate tools without named fixture branches. Missing authority/provenance cannot become verified cause. Unknown owner holds routing. Numeric explanation facts come only from receipts.

**Regression risk/mitigation:** fluent false causes or endless loops; deterministic gates, reference validation and bounded planner evaluations. **Non-goals:** autonomous repairs, multi-agent architecture or private chain-of-thought storage.

## H - Complex/unseen metric acceptance

**Execution prerequisite (2026-09-15):** [Reader-bound runtime](../reader-bound-execution-milestone.md) passed scalar, breakdown and record reads under the isolated reader, with sealed identity evidence and zero-query replay. The operator fixture manifest is not a report onboarding scan or hidden evaluator. Effective report/RLS context, shared generation, exclusive publication and all eight acceptance families remain unverified.

**Objective/why:** prove generality after runtime freeze, using real Power BI.

**Existing:** native model artifacts, lab/evaluator isolation, legacy regression matrices. **New:** isolated fixture publisher, hidden evaluator and frozen manifest; no runtime metric/scenario branch.

**Tasks:** execute the protocol and eight acceptance families below. Publish new definitions after freeze; trigger catalog/context/readiness update through onboarding. Verify native parent/child results, dynamic tests, provenance and classified outcomes. Runtime prompts/tools/policy logic remain frozen.

**Acceptance/tests:** all eight families pass; ratio has healthy/verified defect/precise gap cases; derived metric recursively localizes a child; native DAX receipts mandatory. All-gap answers fail. At least three bounded planner repetitions per required ratio case; report failures and reliability honestly.

**Regression risk/mitigation:** evaluator leakage or local-only proof described as live success; isolated truth and explicit version gate. **Non-goals:** arbitrary unsupported DAX, extra business functionality.

## I - Unified ticket product experience

**Current slice (2026-09-16):** The local workspace now includes business text and reviewed screenshot intake, explicit scope review/start, governed execution, history, cancellation and shared business/technical evidence. Supported totals and record groups can be checked in one native response. The final browser suite covers 30 checks. Local single-operator access does not close this phase; effective report context, hosted authorization and deployment remain. Phase H and general causal proof are still open.

**Objective/why:** one investigation powers business and technical users.

**Existing:** ticket/review API/UI, business and technical demos. **New:** shared v2 timeline/outcome projections and ticket components.

**Tasks:** enabled-report selector, issue text, optional screenshot/page/visual/metric/values/period/priority; context confirmation; persisted timeline; Business Summary, Evidence, Lineage, Impact and Activity tabs. No technical table selection required. Keep old demos until parity.

**Acceptance/tests:** same run/scope/context/outcome hash and values across both views; switching views makes no queries. Browser checks cover success, clarification, disabled model, unsupported context and failed/partial runs. Progress reflects real events. Use actual Power BI screenshots in report demonstrations.

**Regression risk/mitigation:** friendly prose overclaims or duplicated engines; immutable shared projection. **Non-goals:** OCR-only diagnosis or more demo scenarios.

## J - Reviewed routing and triage

**Objective/why:** complete the approved boundary with GitHub/email first.

**Existing:** routing/envelope/owner/destination/transport adapters. **New:** v2 outcome-envelope mapping and triage projection.

**Tasks:** authoritative owner resolution, verified-defect eligibility, reviewed immutable drafts, idempotent deliveries, receipt dependencies and triage status. Preserve issue-before-dependent-email behavior. Changed outcome invalidates approval.

**Acceptance/tests:** verified eligible technical/application defect can yield an approved bug/notification; expected, unsupported and insufficient outcomes cannot auto-send. Dry-run tests cover duplicates, missing owners and stale approvals. Live sends require approval of the concrete envelope.

**Regression risk/mitigation:** bug spam or misleading source labels; evidence gates and reviewed receipts. **Non-goals:** Jira/ADO/ServiceNow rollout, repairs, code PRs or releases.

## Eight required product acceptance families

| Test | Evidence and required gate |
| --- | --- |
| 1 New additive measure | Publish after freeze; delta scan discovers it, capability evaluation admits native read and supported upstream comparison. Matching authoritative scope produces expected behavior without runtime code edits. |
| 2 New ratio measure | Refund Rate parent and dependencies evaluated in Power BI; numerator/denominator compared independently; healthy/defect/gap protocol below. Never sum percentages. |
| 3 Complex derived measure | Publish Adjusted Margin % = DIVIDE([Revenue] - [COGS] - [Returns Adjustment], [Revenue]); recursively evaluate child dependencies, use valid component contexts, identify the divergent child and verify at its supported boundary. Healthy and unsupported-child variants prevent guessed causes. |
| 4 Visual-context issue | Global value agrees but a supported report/page/visual filter differs from confirmed intended context. Capture actual context, reproduce native value, use authorized controlled context changes/dimensional slices and isolate the difference. Mere different filters without an authoritative expectation cannot prove a defect. |
| 5 Freshness issue | Separately stale Bronze, Silver, Gold and semantic fixtures with explicit SLA and version/run evidence; localize the first proven freshness boundary. Missing SLA/version variant remains a gap, never a guessed schedule. No fixed layer-order branch. |
| 6 Application-origin issue | Downstream agrees with SQL; independently recorded authorized intent differs from persisted state. Prove entity/action/version correlation and absence of a later valid superseding action. Classify SOURCE_OR_APPLICATION_DEFECT only with this proof; committed audit alone or missing event yields a gap. |
| 7 Expected behavior | Technical results reconcile and team-confirmed business context explains the change. No defect route; equality alone is insufficient to certify business expectation. |
| 8 Unsupported / insufficient | Distinguish explicit unsupported operation from missing evidence and temporary outage. Preserve diagnostics and exact capability/provenance reason; no invented cause or bug. |

All tests use separate evaluator truth and bounded readonly investigator identities. Fixture publication/injection/reset is test-harness work, not an investigator capability. Reuse existing data structures; do not add a production scenario branch to satisfy a test.

## Exact unseen-measure protocol

### Freeze and isolation

1. Pass existing regressions and A-G tests. Record engine commit, dependency lock hashes, prompt hashes, registry/semantic-operation versions and policy configuration. Separate runtime files from evaluator/fixture files in the manifest.
2. Use an isolated test estate/model; never inject a defect into the working business baseline. The investigator's credentials are read-only and cannot read evaluator labels or expected results.
3. After freezing, publish a new measure named **Refund Rate** with `DIVIDE([Refunded Orders], [Delivered Orders])`. Publish Delivered Orders as a supported dependency if absent. Current model already has Refunded Orders; it does not have Delivered Orders. All newly required definitions are metadata, not Python branches.
4. Define the test business cohort explicitly: ten distinct delivered orders in the confirmed date window and USD scope, two of which were refunded. The fixture's Refunded Orders and Delivered Orders definitions must refer to that same delivered cohort. Do not reuse a differently scoped numerator merely because its name matches.
5. In the isolated fixture, base measures can use DISTINCTCOUNT plus supported CALCULATE predicates on `delivered_flag` and `refunded_flag`. Supply authoritative flag/date/grain mappings through collected definitions and the approved business contract. No new runtime operator or handler may be added after freeze. Native DAX supplies parent/child values; semantic IR supplies decomposition/comparison metadata.
6. Collect new metadata and resolve the user's report/metric/window. Include renamed asset and measure variants and distracting out-of-window/other-currency rows. The evaluator stores expected answers separately and assesses only after the investigation returns.

### Version-proof gate

Use a deliberately small isolated native Power BI model with an immutable fixture generation for this acceptance test. Recommend an isolated Import test model for controllable publication; preserve the production Direct Lake model unchanged. Provisioning/test publication is a fixture responsibility, never an investigator tool.

Before treating semantic observations as comparable, the fixture harness must establish all of:

- Approved model/relationship/measure hashes and exact input artifact hashes.
- A successful publication/refresh receipt bound to the fixture generation.
- Complete readback of the bounded model data needed by the metric, matched by keys and values to that generation, using the generic read capability and recorded identity.
- An exclusive fixture publication lease and write controls preventing refresh/data/definition changes throughout capture, with before/after identity/version checks. A local lock alone cannot constrain an external writer; inability to enforce the write boundary is a failed prerequisite.
- Shared scope, date role, relationship/filter semantics and effective identity for the metric and upstream reads.

Import mode or a refresh timestamp alone is not proof. If the available Power BI interface or permission model cannot establish these conditions, stop the **live acceptance gate** as blocked and state the missing capability. Local frozen-fixture upstream-contract/planner tests can pass independently, but must not be reported as passing the native Power BI healthy/defect experiment. Resolve this prerequisite early in D/H test-harness work rather than discovering it after building the UI.

### Required runs and outcomes

| Case | Controlled setup, hidden from investigator | Required observed behavior |
| --- | --- | --- |
| Healthy | Ten eligible orders; two refunded; unchanged authoritative transform; user has questioned 20% | Discover ratio and both dependencies; apply explicit week/date role and currency; read native measure 0.20, numerator 2, denominator 10; reconcile complete scoped records and authoritative contract. Classify EXPECTED_BEHAVIOR **for the tested definition/scope**, not a claim that 20% is commercially desirable. |
| Controlled defect | Captured materialization contains a supported predicate that omits two non-refunded eligible orders. Authoritative baseline includes them. Output has numerator 2 and denominator 8, hence 0.25 | Observe 25% versus reference 20%; rule out an initial scope/freshness hypothesis using evidence, then test denominator membership. Identify two missing keys, inspect captured transform, reproduce output and reconcile baseline. Classify TECHNICAL_DEFECT only at the proven boundary; report +5 percentage points and two affected orders with references. |
| Insufficient evidence | Same numeric discrepancy, but remove a required transform/input-version receipt or runtime filter proof | Retain measured values, mark comparison/cause gap precisely, classify INSUFFICIENT_EVIDENCE with no verified cause or defect delivery eligibility. For missing user scope use NEEDS_INPUT rather than executing a guessed window. |

Do not add a runtime condition such as `if metric == 'Refund Rate'`, a new fixture-name branch, a literal expected ratio, or a comparison path specific to these tables. Predicate values and asset names should vary in evaluator variants. The generic verifier uses the supported IR and authoritative baseline, not knowledge of which defect was injected.

### Evidence needed to pass

- Frozen runtime manifest unchanged before/after all runs; review configuration changes for hidden executable logic.
- Native model/measure discovery receipts, model-context version and semantic IR showing DIVIDE and recursive dependencies; native parent/child DAX receipts.
- Confirmed scope/filter/date-role evidence and capability decisions.
- Persisted planner trajectory showing evidence-dependent test selection and at least one rejected/refined hypothesis. Do not require identical prose or identical valid test order.
- Generic query receipts, ratio components, complete record-set comparison and causal replay evidence for the defect case.
- Three outcomes matching the gates above; business and technical numeric projections agree when I is added.
- Repeat healthy/defect/gap with renamed objects and varied data through the same operators; zero false verified causes in the negative variants. Report planner reliability across at least three bounded repetitions per required case, with any failure blocking the milestone until understood.

## Regression strategy

| Surface | Existing tests/artifacts to preserve | New checks |
| --- | --- | --- |
| Order data and reporting | Generator, Gold models, Power BI contract tests and CI portal build/tests | No schema/data/report mutation from investigator execution |
| Old metric execution | `test_cross_layer_investigation.py`, selection, query/retry checks | v1 parity; v2 equivalent results only when contracts are truly comparable |
| Scope/review | Planner, reviewed handoff, native context, slicer, drillthrough and categorical replay tests | No dropped filters, no stale-scan substitution, approval bound to engine/scope |
| Provenance | Snapshot/source/Bronze/Silver/Gold/semantic publication suites | Missing identity/version stays NOT_COMPARABLE; run alignment alone still insufficient |
| Local causes and limits | Lab matrix, multilayer matrix, filter/arithmetic/freshness tests | Preserve unexplained cases as unresolved; offsetting records still detected |
| Durable execution | Workflow, background worker and evidence API tests | Fenced restart, uncertain receipt, cancellation and budget accounting |
| Explanation and UI | Grounded explanations, review UI and both demo tests | Same outcome across views; no unsupported causal language or invented values |
| Delivery | Routing, envelope, destination and transport tests | No automatic send from planner; outcome revision invalidates stale approvals |

Keep legacy tests unchanged until an explicit compatibility migration is reviewed. V2 uses the new classifications; do not relabel historical outcomes as newly proven causes. Add operator/property tests for decimal/BLANK behavior, duplicate keys, nulls, denominator zero, multi-currency filters and date boundaries. Use deterministic planner stubs for CI control-flow coverage, then bounded real-LLM runs for planning reliability; neither substitutes for the other.

Track each gate as planned/in progress/passed/blocked with commit, test artifact and limitation. **The next-stage completion statement is justified only when the frozen unseen-measure healthy, defect and gap runs pass—not by counting phases, PRs, tables or tools.**
