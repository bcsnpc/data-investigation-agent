# Data Investigator: what we built and what comes next

Latest continuation: PR #184 merged. [Native dependency calculation contexts](docs/dependency-context-milestone.md) now preserve supported measure-local filters through adaptive child reads, with scope review, sealed context evidence and eight live parity checks. This advances D/E/G; full B-G gates, Phase H and hosted v2 remain open.

Latest continuation: PR #182 merged. [Reader-bound native execution](docs/reader-bound-execution-milestone.md) now connects the separate reader to actual native scalar, dimensional and record tools with saved principal evidence. Three live queries succeeded and ten projected fixture rows matched; saved replay made no calls. This advances the execution identity prerequisite, not general causal or Phase H acceptance. See [current delivery status](docs/current-delivery-status.md) for cumulative progress and remaining grouped work.


Latest: PR #176 merged; [native proof preflight](docs/native-proof-preflight-milestone.md) completed the live feasibility audit and records the blocked acceptance prerequisites. See [current status](docs/current-delivery-status.md) for implementation and remaining acceptance gates.

**As of:** 2026-09-14  
**Repository:** https://github.com/bcsnpc/data-investigation-agent (private)  
**Reviewed working branch:** `feature/business-demo`, commit `c92d56b`  
**Purpose:** An implementation handoff and next-step decision document, not a claim of product completion.

**Revised engineering plan (first-class product direction):** [Metadata-driven architecture and phased acceptance](docs/architecture/README.md). This package governs the next phases. The historical assessment below is retained; current delivery status is in [the tracker](docs/progress.md). Model onboarding, scan/dependency analysis and [native diagnostic reads](docs/native-catalog-diagnostics.md) now have implementation slices; the [adaptive diagnostic loop](docs/adaptive-investigation-milestone.md) is now implemented, while complete causal investigation remains pending.

This assessment uses the repository's code, configuration, validation records and
the recent architecture discussion. Cloud deployment statements below describe
previously recorded deployments and checks; cloud availability, credentials,
capacity and billing were not rechecked for this document.

**Latest status:** [Current delivery summary](docs/current-delivery-status.md) records the implemented v2 slices and remaining milestones after merged PR #170 and the [grouped keyed readback milestone](docs/keyed-readback-milestone.md). The assessment below describes the earlier bounded foundation.

## 1. The current position

We have built a substantial working business/data platform and a **bounded
deterministic investigator with LLM-assisted ticket understanding**.

We have **not** built the general investigation engine originally intended.
Current cloud reads and comparisons are real, but supported metrics, query
templates, asset paths and much of the investigation strategy are predefined.
The local demonstrations additionally use explicit fixture scope and supported
cause verifiers. They do not demonstrate arbitrary screenshot interpretation or
autonomous investigation of an unfamiliar business metric.

The infrastructure is reusable. The next priority is to make investigation
strategy metadata-driven and evidence-led, rather than adding more scenario branches.

## 2. Product intent and scope

A user reports a business concern without knowing the technical layers. The
investigator resolves context, finds the relevant assets, follows dependencies,
chooses checks, gathers evidence, revises hypotheses, and determines whether the
behavior is expected, defective or unresolved. It quantifies impact and prepares
appropriate routing to a responsible team.

The product boundary is **investigation, evidence, classification, impact,
reviewed notification and bug creation**. Autonomous repairs, code changes,
release agents and production remediation are outside the approved phase.
Engineering PRs created while developing this repository are separate from the
product's runtime ability to create defect tickets.

Source scope: [original specification](cross_system_data_investigator_poc.md),
[ticket/defect-lab extension](DATA_INVESTIGATOR_TICKET_AND_DEFECT_LAB_SCOPE.md),
and [scope alignment](docs/scope-alignment.md).

## 3. Deployment versus local implementation

| Component | What exists | Deployment / verification boundary |
| --- | --- | --- |
| Order application | Authenticated browsing and controlled order actions | Deployed to Azure App Service F1; historical live/browser checks recorded |
| Operational database | Azure SQL `ordersops`, relational business dataset and restricted runtime users | Deployed in Central US; historical baseline reconciliation recorded |
| Fabric data platform | Bronze, Silver, Gold, notebooks and snapshot publication helpers | Deployed and historically verified in enterprise Fabric workspace |
| Power BI | Six-table semantic model, 25 measures, three reports | Deployed to Fabric/Power BI; historical DAX/filter/drillthrough checks recorded |
| Azure LLM resource | `investigator-llm` deployment on Azure OpenAI | Provisioned; bounded planning/explanation calls historically verified |
| Metadata, lineage and evidence stores | SQLite collectors, graph builds and saved investigations | Local development machine, not a hosted enterprise metadata service |
| Investigator API/UI/worker | Ticket, review, execution and evidence workflows | Local; no Azure investigator deployment completed |
| Technical and business demos | Isolated DuckDB scenarios, local UI and recordings | Local; business Orders/Reports screens are not the deployed portal/Power BI UI |
| Runtime issue/email delivery | Reviewed drafts, durable adapters, CLI transports | Implemented but real destinations/owners and live acceptance remain incomplete |

Existing application: https://orderops-portal-9696025.azurewebsites.net  
Fabric workspace: https://app.powerbi.com/groups/09cea7db-63ec-41f0-9cf0-872a6dc5c61d/list

Personal Azure resources and enterprise Fabric use separate identities/tenant
contexts. Existing local auth helpers handle those contexts; this is not yet a
portable multi-tenant authentication/onboarding solution.

## 4. Business system and coherent synthetic data

Implemented relational application schema, deterministic generation, lifecycle
rules, manifest-based loading, reconciliation and repeat-load protection.
Orders, lines, payment attempts, shipments, refunds and audit events are related;
they are not independently random tables.

Historically loaded baseline:

| Table | Rows |
| --- | ---: |
| Customers | 20,000 |
| Products | 150 |
| Orders | 100,000 |
| Order lines | 286,652 |
| Payments | 105,047 |
| Shipments | 95,545 |
| Shipment lines | 273,805 |
| Refunds | 7,270 |
| Refund lines | 12,680 |
| Audit log | 509,550 |
| **Total business rows** | **1,410,699** |

These are baseline counts, not a fresh count of today's database. A separate load
manifest tracks dataset identity. Portal operations support shipping, delivery
and full-line returns, with transactional audit and retry/stale-state protections.
This is a scoped operational application, not every feature in the original specification.

Key implementation: [generator](scripts/generate_orders.py),
[SQL schema](infra/sql/001_application_schema.sql),
[lifecycle schema](infra/sql/002_order_lifecycle.sql),
[loader](infra/scripts/Load-OrderBaseline.ps1), [portal](apps/order-portal).
Details: [data rules](docs/synthetic-data.md), [baseline](docs/baseline-validation.md),
[portal deployment/actions](docs/order-portal.md), [runtime identities](docs/runtime-identities.md).

## 5. Fabric and Power BI

### Data layers

- Bronze: ten source business tables; initial copy counts/integrity verified.
  The initial copy was confirmed as overwrite rather than repeated full append.
- Silver: ten validated entities, business aggregation and source/run markers.
- Gold: six reporting tables—order summary, order-line summary, daily sales,
  customer sales, product sales and refund summary—plus three reporting dimensions.
- Transformations retain paid-cancellation and refund history and avoid multiplying
  amounts through raw payment/line joins. Their scope and grains are documented.

Code: [Fabric transformations](infra/fabric), especially
[Gold definitions](infra/fabric/gold_models.py).
Details: [Bronze](docs/fabric-bronze-validation.md), [Silver](docs/fabric-silver.md),
[Gold](docs/fabric-gold.md).

### Analytics

The model contains `DimDate`, `DimCustomer`, `DimProduct`, `FactOrder`,
`FactOrderLine` and `FactRefund`, with five relationships and 25 explicit measures.
Reports: **Executive Sales**, **Order Operations** and **Product Performance**.
Native model/report files are versioned in [infra/powerbi](infra/powerbi).

Recorded verification includes 15 reconciled DAX totals, eight filter cases and
order/refund drillthrough. This does not mean the investigator can dynamically
investigate every measure or reproduce every report context.
Details: [Power BI model and report links](docs/powerbi.md).

## 6. Snapshot and provenance work

Implemented a transaction-consistent, read-only SQL source export with content
and schema hashes; isolated Bronze publication; pinned-version Silver inputs;
registered Silver/Gold publication evidence; and semantic refresh/run alignment.

The extra snapshot Bronze tables are deliberate isolated copies tied to a source
artifact. They are not another unrelated synthetic dataset. Publication registries
retain source identities, table identities, versions, counts and proof hashes.

**Important limit:** `SEMANTIC_RUN_ALIGNED` and equal totals do not prove the
Direct Lake engine selected the exact same underlying Delta versions. Independent
SQL endpoint reads are not automatically pinned snapshots. Multi-table writes
are not globally atomic, and concurrent writers remain relevant.

Preserve `NOT_COMPARABLE` and uncertainty where proof is missing. Do not turn
observed agreement into verified causal continuity.

Entry points: [source snapshot](scripts/source_snapshot.py),
[Bronze publication](scripts/bronze_publication.py),
[Silver publication](scripts/silver_publication.py),
[Gold publication](scripts/gold_publication.py),
[semantic verification](scripts/semantic_snapshot.py).
Details: [source export](docs/source-snapshot.md), [snapshot Bronze](docs/snapshot-bronze.md),
[Gold publication](docs/gold-snapshot-publication.md),
[semantic refresh limits](docs/semantic-snapshot-refresh.md).

## 7. Metadata, lineage and report context

Implemented live connector-based metadata collection from SQL, Fabric and Power BI;
versioned SQLite scans; source-scoped asset IDs; definition hashes; collection
timestamps; and explicit unavailable/unknown capability records.

Lineage is derived from captured definitions and supporting connection evidence.
It supports upstream/downstream traversal, retained resolution evidence and
eligibility checks that block unsupported lineage conclusions. This is useful
infrastructure, but parsers and resolvers still support particular definition shapes.

Recorded later inventory/lineage coverage includes 39 lakehouse tables, five
notebooks, 403 links and 41 eligible data-bound visual paths. A targeted report
scan retained three reports, four pages, 45 visuals, 25 measures and 67 definition
parts, with 259 stored asset hashes verified. Counts refer to particular scans.

Native report work includes explicit report-to-model binding, definition bundles,
drillthrough context, supported categorical slicer parsing and reviewed scope.
Missing choices are not treated as "all values." Production execution still holds
unsupported slicers. A one-order live comparison of two currency-filter paths
matched, but does not prove general report parity.

Code: [collector](scripts/metadata_inventory.py), [connectors](scripts/metadata_connectors.py),
[lineage graph](scripts/lineage_graph.py), [gap policy](scripts/lineage_gap_policy.py),
[definition bundles](scripts/report_definition_evidence.py),
[native context](scripts/native_plan_context.py), [slicers](scripts/report_slicer_context.py).
Details: [metadata](docs/metadata.md), [lineage](docs/lineage.md),
[targeted collection](docs/targeted-report-metadata.md),
[native diagnostic](docs/native-filter-parity.md).

## 8. Main investigator: implemented behavior and hardcoded limits

| Area | What is dynamic / real | What remains predefined or missing |
| --- | --- | --- |
| Ticket understanding | Optional LLM interprets ticket using a metadata-derived report catalog | Planner explicitly permits only Order Count and Net Cash |
| Scope | Explicit currency and optional order ID; clarification and validation | General date/product/customer filters are not executable; native slicers may be held |
| Asset resolution | Captured report/metric lineage is checked | Acquisition names order-specific tables and a fixed layer path |
| Queries | Executes real bounded SQL/DAX reads | Fixed query templates; no generic semantic-expression/dependency evaluator |
| Comparison | Exact values, availability, recorded scope/provenance and differences | No planner-selected sequence of arbitrary relevant comparisons |
| Cause | Supported local causes have deterministic evidence/replay checks | No general hypothesis/test/revision loop for unfamiliar causes |
| Explanation | Optional LLM selects useful finding/next-step IDs over saved facts | Backend renders predefined text; model does not independently investigate |

Primary constraints live in [ticket_planner.py](scripts/ticket_planner.py),
[ticket_worker.py](scripts/ticket_worker.py),
[cross_layer_investigation.py](scripts/cross_layer_investigation.py),
[query worker](scripts/investigation_query_worker.py),
[SQL reader](infra/scripts/Read-InvestigationMetric.ps1) and
[explanation selection](scripts/investigation_explanation.py).

The catalog is not entirely hardcoded, but it is filtered to the supported metrics.
The LLM integration is real when enabled; its current role is deliberately narrow.
There is no general tool registry/orchestrator that dynamically decides the next
investigation operation from accumulated evidence. That refactor is not implemented.

Historically, bounded reads across SQL/Bronze/Silver/Gold/Power BI returned matching
100,000-order baseline totals. The retained classification can still be UNRESOLVED
and strict comparison NOT_COMPARABLE. Completion means acquisition finished, not
that the user's issue is resolved.

## 9. Ticket, review, execution and evidence workflow

Built local authenticated evidence endpoints, ticket intake, idempotent submissions,
durable workflow/status records, pinned lineage, plan drafts, clarification,
hash-bound approval, related original/approved tickets and bounded background work.
Evidence is persisted and can be reopened. Optional post-run explanation requests
have their own records. Failures and uncertain operations are not hidden as success.

The operator UI supports intake, review, approval, status and saved evidence.
Authentication is a local bearer token, not enterprise user identity/RBAC.
SQLite workflows and local worker bounds are not a complete hosted queue/recovery service.

Code: [workflow](scripts/ticket_workflow.py), [planner](scripts/ticket_planner.py),
[approval](scripts/review_ticket_plan.py), [worker](scripts/background_worker.py),
[server](scripts/serve_investigations.py), [evidence API](scripts/investigation_evidence_api.py),
[review UI](apps/investigation-review).
Details: [ticket workflow](docs/ticket-workflow.md), [planning](docs/llm-ticket-planning.md),
[background worker](docs/background-worker.md), [explanations](docs/grounded-explanations.md).

## 10. Defect lab and demonstrations

The local DuckDB lab provides repeatable initialization, controlled injections,
evidence capture and verified reset. It reuses Gold transformation definitions.
Supported checks include missing records, unexpected filtering, double-refund
arithmetic, expected refund behavior and stale source evidence.

Evaluation coverage includes a ten-case classification matrix and a five-case
multi-layer matrix, including offsetting errors that aggregate totals alone miss.
Missing/stale proof must remain unresolved. The evaluator holds expected answers;
the cause verifiers themselves are still scenario-specific implementations.

There are also local report-scope and categorical-filter replays, snapshot-bound
approval, one-attempt execution and a dedicated replay UI. These do not establish
live Power BI filter/DAX equivalence.

Two presentation experiences exist today:

- **Technical demo:** existing ticket/plan review, deterministic execution, saved
  layer comparison and review-only defect draft.
- **Business demo:** separate local Orders/Reports views; a business question;
  report/application PNG attachments; recorded backend steps; expected/reported
  values and plain-language explanation with collapsed technical detail.

**They are currently separate demo workflows, not two views of one shared general
agent session.** The business demo's scope comes from its selected local Net Cash
report, not the narrative or image recognition. Screenshots are retained with
hashes; they are not OCR interpreted. Its result wording includes scenario-specific
templates. The shown $55/$154/$99 discrepancy belongs to the isolated dataset,
not the deployed Power BI report or live order application.

Artifacts on the development machine (ignored by Git):

| Artifact | Local path |
| --- | --- |
| Combined, trimmed 60-second video | `.local/combined-demo/investigator-combined-60s.mp4` |
| Business recording, 88 seconds | `.local/business-video/business-user-demo.mp4` |
| Technical recording, 95 seconds | `.local/demo-video/investigator-demo.mp4` |
| Business application/report/result screenshots | `.local/business-video/orders.png`, `report.png`, `result.png` |
| Automated technical rehearsal | `.local/demo-acceptance-143/rehearsal.json` |

Recordings are captioned, without voiceover. Labs were reset after recording.
Details: [technical runbook](docs/demo-runbook.md), [business runbook](docs/business-user-demo.md),
[classification matrix](docs/lab-evaluation-matrix.md),
[multi-layer matrix](docs/multilayer-evaluation-matrix.md).

## 11. Routing and delivery

Built evidence/ownership-gated defect drafts, separate review, destination binding,
local simulated delivery receipts, GitHub issue and email adapters, envelope
review, durable attempts, and operator-invoked HTTPS/SMTP transports.

Real owner mapping, destination/provider configuration, delivery authorization
enforcement in a hosted system, and live provider acceptance remain incomplete.
SMTP acceptance is not proof of inbox delivery. Uncertain attempts are held;
local simulated receipts do not prove third-party guarantees.

No runtime business defect issue/email delivery was demonstrated. Development
issues/PRs in this repo are engineering activity, not evidence of runtime delivery.
Details: [routing](docs/routing-drafts.md), [review](docs/routing-review.md),
[rehearsal](docs/routing-delivery-rehearsal.md), [transports](docs/live-delivery-transports.md),
[envelopes](docs/envelope-workflow.md).

## 12. Security, runtime and validation

- Restricted app/Fabric/investigator SQL users; local encrypted credential files
  and separate auth contexts. Development secrets are excluded from source control.
- Azure SQL auto-resume error 40613 has bounded connection-stage retries; generic
  query/auth errors are not blindly retried. Preserve free-offer/overage protection.
- Azure LLM access uses a local launcher that retrieves a key into process memory.
  Hosted managed identity and enterprise permission enforcement remain later work.
- Latest full local Python run: **366 tests passed**. CI includes Python tests,
  PowerShell parsing and portal tests/build. JavaScript syntax/browser checks were
  performed for the business demo. Latest recorded full-history secret scan was clean.
- Tests prove their covered contracts, not generality, current cloud availability,
  production deployment, or complete product acceptance. No tests were rerun merely
  to write this document.

Local checks, when code changes justify them:

```powershell
python -m unittest discover -s scripts -p 'test_*.py'
node --check apps/business-demo/app.js
```

The Python suite requires the repository's test dependencies; see
[requirements](scripts/requirements-fabric-tests.txt) and the
[CI workflow](.github/workflows/validation.yml). Live scripts require their configured
identities and may consume SQL/LLM capacity; they are not implied by offline checks.

## 13. Source-control and documentation state

**Phase A update:** PR144 and PR146 are now merged; `bounded-v1-20260914` identifies the verified baseline. The observations below describe the earlier inspection and are retained for context.

Checked on 2026-09-14:

- PR #142 is merged (bounded native currency diagnostic).
- [PR #144](https://github.com/bcsnpc/data-investigation-agent/pull/144) is open:
  `feature/demo-rehearsal` -> `main`.
- [PR #146](https://github.com/bcsnpc/data-investigation-agent/pull/146) is open:
  `feature/business-demo` -> `feature/demo-rehearsal`; it depends on #144.
- Therefore the reviewed working branch contains demo work not yet on `main`.
  Resolve that PR chain deliberately before starting the engine refactor.

Some documentation is historical milestone text, not current status. In particular:

- The prior README summary lagged deployed Fabric/Gold work; this planning revision corrects the summary.
- The tracker summary now separates the bounded baseline from proposed A-J work; historical entries retain their original context.
- Early component documents describe limitations later slices partly addressed;
  for example, transport/envelope integration progressed beyond initial adapter docs.

Use this handoff for the consolidated assessment, current code for behavior, and
the [progress log](docs/progress.md) for historical evidence. This document does
not silently mark all earlier phases complete or rewrite their history.

## 14. Revised product architecture direction

The [first-class product plan](METADATA_DRIVEN_INVESTIGATOR_FIRST_CLASS_PRODUCT_PLAN.md) now governs the next architecture. The [engineering package](docs/architecture/README.md) expands it into implementation tasks and gates. This supersedes the earlier catalog-only roadmap; it does not change what has already been implemented.

Admin teams register models/connections, deep-scan metadata, review business context and readiness, and enable models. Versioned context and change detection maintain semantic dependencies, report filters, technical lineage, policies and ownership. Business users select an enabled report and describe a symptom without choosing technical layers.

Power BI is the authoritative DAX engine. Generic tools evaluate measures, child dependencies and dimensional/visual context natively. Semantic IR supports decomposition and safe upstream comparison; it does not reproduce arbitrary DAX. Persist a dynamic hypothesis/tool/evidence loop and deterministic verification. Complex measures, application-intent evidence and freshness localization are core acceptance work.

One investigation ID, context, scope, evidence and outcome power business and technical views. Reviewed GitHub/email delivery ends the product boundary; no runtime repair or code PRs.

## 15. Revised phases and acceptance gates

Phase A is verified in [baseline evidence](docs/bounded-v1-baseline.md). B/C now have a [working onboarding/catalog slice](docs/model-onboarding.md); the remaining requirements stay open.

| Phase | Deliverable | Exit gate |
| --- | --- | --- |
| A | Freeze bounded-v1 | Reproducible baseline, reconciled branch/status and regressions |
| B | Model onboarding foundation | Register, scan, review, enable/disable through basic admin UI/API |
| C | Deep catalog and change detection | New measures discovered; affected context/readiness invalidated on changes |
| D | Native execution and typed tools | Real model/source queries with generic scope, readonly admission and receipts |
| E | Semantic capabilities | Queryability/decomposition/reconciliation independently evaluated |
| F | Persisted state | Versioned context, evidence, budgets and safe restart |
| G | Evidence-led planner/verifier | Evidence changes tests; causal claims independently verified |
| H | Complex/unseen acceptance | All eight acceptance families pass with frozen runtime and real DAX |
| I | Unified ticket experience | Same run and values across business/technical views |
| J | Reviewed routing | Eligible verified findings yield reviewed drafts and delivery receipts |

See [detailed tasks, risks, tests and gates](docs/architecture/phases-and-acceptance.md). A-H is the architecture milestone; I-J complete the product workflow. These are coherent deliverables, not a mandate for many small PRs.

### Required acceptance

After engine freeze, discover a new additive measure, Refund Rate and a complex derived measure through metadata. Evaluate native parent/children, use actual supported visual context, and adapt tests from evidence. The eight families also cover freshness at distinct boundaries, independent application intent, expected behavior, and unsupported/insufficient evidence.

Refund Rate must pass healthy, verified-defect and precise-gap cases without metric/scenario-specific runtime Python. Maintain Order Count/Net Cash as regressions. Missing provenance stays a gap; native execution success alone does not prove cross-system comparability. Evaluator answers remain separate from investigator inputs.

## 16. Guardrails to carry into the refactor

- Do not discard the existing working platform or bypass current scope/provenance holds.
- Treat report text, screenshots, notebook content and tool outputs as untrusted data.
- Keep tools read-only and bounded where appropriate; validate identifiers, scope,
  permissions, query cost, timeouts and evidence completeness.
- Do not assume arbitrary generated SQL/DAX is safe because an LLM proposed it.
- Preserve SQL free-quota safeguards and explicit cloud usage budgets.
- Do not infer verified cause from equal or different totals alone.
- Ask for missing context or return unresolved rather than silently dropping filters.
- Do not auto-send messages, create runtime bugs or repair data merely because a finding exists.
- An unseen metric or scenario should test the general engine, not encode its answer.

**Immediate next engineering task:** Phase B model onboarding foundation. Phase A is verified: demo PR144/146 merged and baseline tag published; see [results](docs/bounded-v1-baseline.md). No v2 runtime or cloud deployment was performed.
