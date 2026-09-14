# Project progress

Updated: 2026-09-13. Source plan: [POC specification](../cross_system_data_investigator_poc.md), sections 90–100.

Approved scope extension: [Ticket experience and defect lab](../DATA_INVESTIGATOR_TICKET_AND_DEFECT_LAB_SCOPE.md). This extension governs the investigation experience and scope boundary alongside the original plan. Integration decisions and dependencies are recorded in [scope alignment](scope-alignment.md).

## Current position

Phases 0 (engineering foundation), 1 (business system) and 2 (data platform) remain in progress; the initial analytics release is complete.
The 100,000-order SQL baseline and authenticated operational portal are deployed. Verified source snapshots now propagate through Bronze, Silver and nine Gold reporting/dimension tables. The six-table semantic model and three reports have verified measures and filter cases. Current metadata includes 39 lakehouse tables and five notebooks; the reviewed lineage graph has 403 links and 41 eligible data-bound visual paths. Live five-layer metrics have been verified, while exact model snapshot comparability remains explicitly unproven. A local evidence API, ticket intake and durable execution/status workflow are implemented. The local review UI supports ticket intake, scope approval, related ticket navigation and evidence display. Bounded background execution and opt-in, idempotent post-run explanations are merged through PR #70. Model planning and constrained explanation selection have live verification. Local lab findings now include verified filter cause, exact record impact, expected refund behavior and source-version freshness. Local routing review and delivery rehearsal are implemented. Broader tool/scenario coverage, attachments, investigator hosting and real delivery remain pending.

| Phase | Status | Evidence / remaining work |
|---|---|---|
| 0 Engineering foundation | In progress | Private repository, README, SQL scripts, tests and tracking; broader standards and deployment automation remain |
| 1 Business system | In progress | Azure SQL, 100k baseline and restricted runtime users verified; browsing deployed; transactional actions deployed and verified; broader specification features remain scoped for follow-up |
| 2 Data platform | In progress | Transaction-consistent source and verified Bronze/Silver/Gold publications complete; recurring orchestration remains |
| 3 Analytics | Initial release complete | Six-table model, 25 measures, three reports, 15 exact DAX totals and sample-order drillthrough verified; [details](powerbi.md) |
| 4A Metadata connectors | Initial collector merged; reusable connector refactor verified | Versioned SQLite inventory, live SQL/Fabric/Power BI definitions and explicit capability gaps; [details](metadata.md) |
| 4B Lineage | Reviewed scope backend merged | 403 links, retained resolution evidence and 41 eligible visual paths; UI remains later |
| 5A Deterministic investigator | In progress | Check engine merged in PR #24; cross-layer adapters implemented with SQL/Power BI live reads; all five layers live-verified; common-source snapshot proof pending |
| 5B Ticket experience | Local workflow and UI implemented | Intake, review, related statuses, evidence and bounded worker implemented; attachments, richer context, lineage/impact views and hosting remain |
| 6 AI investigator | Scoped planning and explanations implemented | Azure planning and model-selected evidence highlights verified; local deterministic cause/impact checks implemented; broader hypothesis/tool orchestration and live cause coverage remain |
| 7 Defect lab | Local scenarios and review integration implemented | Ten-case Silver/Gold matrix plus three-layer propagated discrepancy and reset; reviewed multi-layer execution/UI and five-case boundary matrix implemented; transformation/model cause proof remains |
| 7B Routing | Review, adapters and operator transport integration implemented | Browser/CLI approval and durable attempts; real provider configuration, live acceptance, recovery and hosted permissions remain |
| 8 Portfolio polish | Not started | Hosted demo, screenshots, video and presentation |

## Work record

| Date | Work | Result |
|---|---|---|
| 2026-09-12 | Reviewed specification and prerequisites | Personal Azure SQL plus enterprise Fabric planned; enterprise permissions still need validation |
| 2026-09-12 | Provisioned Azure SQL | Central US; `ordersops` on `sql-orderops-9696025`; free offer with overage billing disabled |
| 2026-09-12 | Established connectivity | SQL authentication and client firewall access verified |
| 2026-09-12 | Created core schema | Seven application tables; lifecycle extensions add shipment/refund lines and load manifest |
| 2026-09-12 | Defined synthetic business rules | [Rules and limitations](synthetic-data.md) |
| 2026-09-12 | Built generator and loader | Fixed seed/cutoff, checked relationships, transactional bulk copy |
| 2026-09-12 | Validated and loaded baseline | 100,000 orders; 1,410,699 business rows; [verification](baseline-validation.md) |
| 2026-09-12 | Established source control and tracking | Initial repository bootstrap; subsequent changes use feature branches and PRs |
| 2026-09-12 | Implemented DB-002 runtime identities | Three contained users, scoped roles, encrypted local credentials and live permission tests; [details](runtime-identities.md) |
| 2026-09-12 | Implemented APP-001 browsing release | React/Vite portal, authenticated Node API, live SQL reads and local browser/API verification; [details](order-portal.md) |
| 2026-09-12 | Deployed portal to Azure App Service | Central US, F1 Free, HTTPS; public API smoke tests passed; browsing release (PR #8) |
| 2026-09-12 | Implemented controlled order actions | Ship/deliver/return, exact SQL refund arithmetic, atomic audit, stale/retry/concurrency protection; API-to-SQL and mobile browser verification rolled back; merged in PR #9 |
| 2026-09-12 | Deployed controlled action release | Azure F1 Free; hosted browsing and action rejection checks passed; ship/deliver/return forms and mobile refund preview verified; no business writes committed during deployment checks |

| 2026-09-12 | Validated initial Fabric Bronze load | User-reported successful copy; screenshot confirms all 10 baseline counts; user confirmed eight integrity checks returned zero; [evidence and remaining work](fabric-bronze-validation.md) |

| 2026-09-12 | Built and verified Silver directly in Fabric | Notebook completed; ten tables, 100k orders, eleven zero-failure checks, source/row run metadata and successful eight-table SQL/Bronze trace; [details](fabric-silver.md) |

| 2026-09-13 | Built and verified Gold directly in Fabric | Six reporting tables, 59 checks, 15 exact SQL/Gold totals and six adversarial fixtures passed; paid cancellations retain capture/refund history with zero net values; [details](fabric-gold.md) |

| 2026-09-13 | Deployed semantic model and three reports | Six Direct Lake tables, 25 explicit measures, 15 DAX totals equal Gold, eight filter cases and refund event checks passed; browser order drillthrough verified; [details](powerbi.md) |

## Decisions and departures from the original draft

- User increased baseline from the draft's 50,000 orders to 100,000. Related
  counts are derived from lifecycles; 20,000 customers and 150 products are used.
- SQL and data generation preceded the full Phase 0 foundation. This was an
  intentional response to the user's setup and data requests, not completion
  of the whole first phase.
- Current directories are a small working layout, not the full proposed monorepo.
  App/service directories will be introduced as those components are implemented.
- A root commit is needed to bootstrap the empty repository. Normal development
  after bootstrap will use feature branches and pull requests.
- Synthetic audit events exist; portal actions now write audit events atomically. Write verification used rollback-only transactions, preserving the baseline.
- Admin credentials remain for schema/setup scripts. Restricted app, Fabric and
  investigator users are provisioned and verified; future runtime integrations
  must use their designated credentials.
- No production data or intentional defects have been loaded.

## Next milestone

PR #70 is merged. The isolated acceptance baseline exercises ticket-to-evidence/explanation flow with equal values, missing source evidence and comparable divergence. Workflow passes while product acceptance remains incomplete. Initial local lab baseline/reset and deterministic record-impact investigation are implemented. One scoped expected-refund case is implemented. One local filter cause is now verified. Isolated lab ticket/UI integration is implemented. Next: multi-layer cause/freshness coverage and acceptance evaluation. Live model snapshot comparability, recurring data refresh, routing and investigator hosting remain open. See [acceptance baseline](acceptance-baseline.md).

## Tracking convention

GitHub issues track actionable work; this file tracks phase status and decisions.
Each PR should reference its issue, explain behavior, record validation and update
relevant documentation. Mark completed work based on evidence, not intended work.

## GitHub work items

- [DATA-001: Connected 100,000-order baseline](https://github.com/bcsnpc/data-investigation-agent/issues/1) - closed
- [ENG-001: Complete engineering foundation](https://github.com/bcsnpc/data-investigation-agent/issues/2) - open
- [DB-002: Add restricted runtime SQL identities](https://github.com/bcsnpc/data-investigation-agent/issues/3) - closed; merged in PR #6
- [APP-001: Build Order Operations Portal](https://github.com/bcsnpc/data-investigation-agent/issues/4) - closed: browsing and controlled actions deployed and verified; PRs #8 and #9 merged
- [FAB-001: Validate enterprise access and ingest Azure SQL to Bronze](https://github.com/bcsnpc/data-investigation-agent/issues/5) - closed: direct API/run evidence, Overwrite confirmation, counts/keys/integrity and full sample-order comparison passed

- [INF-001: Deploy authenticated portal](https://github.com/bcsnpc/data-investigation-agent/issues/7) - closed; deployment merged in PR #8, user confirmed portal access

- [FAB-002: Build and validate Silver](https://github.com/bcsnpc/data-investigation-agent/issues/11) - closed; implemented, executed successfully and merged in PR #12

- [FAB-003: Build reconciled Gold reporting tables](https://github.com/bcsnpc/data-investigation-agent/issues/13) - deployed and verified; 59 Fabric checks and 15 independent source totals passed; closed; [PR #14](https://github.com/bcsnpc/data-investigation-agent/pull/14) merged

- [PBI-001/002: Semantic model and reports](https://github.com/bcsnpc/data-investigation-agent/issues/15) - deployed and verified; [PR #16](https://github.com/bcsnpc/data-investigation-agent/pull/16) merged

## Scope extension review

Reviewed the ticket and defect lab scope before starting the next implementation. The product begins with a business-facing ticket and ends at verified findings, classification, impact, appropriate bug/notification routing and human triage. Autonomous remediation is excluded. Phase 4A incorporates the additional evidence, ownership and freshness contracts described in [scope alignment](scope-alignment.md). No defects have been injected and no runtime behavior changed during this review.

Scenario clarification: scope examples illustrate defect patterns. Select controlled scenarios using existing orders, payments, refunds, transformations and reports; reinstatement and incremental ingestion are not prerequisites. Candidate injections and baseline protections are recorded in [scope alignment](scope-alignment.md).

- [META-001: Metadata connectors](https://github.com/bcsnpc/data-investigation-agent/issues/17) - initial collector implemented and live-verified; eight offline contract tests passed; [PR #18](https://github.com/bcsnpc/data-investigation-agent/pull/18) merged; issue closed.

## Metadata milestone evidence

Scan `a2ca371b-6377-444b-ae5d-d41c91baf9eb` completed with 476 metadata records and zero failed attempted capabilities. Live validation passed: 11 SQL objects/81 columns, 11 foreign-key relationships, 29 lakehouse tables (Bronze 10, Silver 10, Gold 9), 25 measures matching deployed DAX exactly, five semantic relationships, four report pages and 45 visuals. Bronze schema discovery includes 74 columns through the OneLake API. Source data was not modified.

Remaining boundaries are explicit: business ownership and expected refresh schedules are unknown; business-data watermarks and Silver/Gold Delta column/version collection remain follow-up enrichment. This milestone supplies a local collector and SQLite persistence, not a hosted API, lineage graph or ticket UI. Next is Phase 4B: derive lineage from the acquired definitions and mappings, retain provenance and unresolved dependencies, then provide traversal. See [metadata documentation](metadata.md).

## Reusable connector milestone

[META-002](https://github.com/bcsnpc/data-investigation-agent/issues/19) separates connection configuration, authentication adapters and metadata discovery before Phase 4B. SQL server/database/schema and Fabric workspace/tenant are configuration-driven. Local DPAPI and CLI authentication remain supported behind injected reader/token interfaces. The hosted credential adapter is an extension point; no service principal, managed identity or permissions have been provisioned. Sixteen offline metadata tests and two generator tests pass. Live scan `5d11f419-0596-412a-9002-1971b3fed6ad` is COMPLETE with zero unavailable attempted capabilities. Parity against scan `a2ca371b-6377-444b-ae5d-d41c91baf9eb` passed: all 476 asset IDs, parents, names and definitions unchanged (excluding the SQL acquisition timestamp). The existing POC count/DAX validation also passed. [PR #20](https://github.com/bcsnpc/data-investigation-agent/pull/20) merged; issue #19 closed. Phase 4B backend evidence follows below.

## Lineage backend milestone

[LIN-001](https://github.com/bcsnpc/data-investigation-agent/issues/21) derives the graph from captured definitions and supplemental connection/endpoint API evidence. Build `b5db8886-61e4-49cc-92c5-4f682ab7268f` over inventory scan `5d11f419-0596-412a-9002-1971b3fed6ad` contains 360 typed links and zero detected unresolved references. All 41 data-bound visuals trace to SQL. Net Sales reaches six independently expected source tables and downstream Executive Sales/Product Performance reports. Twelve adversarial lineage tests, sixteen metadata tests and two generator tests pass.

The backend stores lineage runs, edges and gaps in SQLite, with definition hashes and source evidence. Static Python/SQL parsing never executes notebook code. Unsupported constructs remain gaps; completeness is limited to the supported parser and captured snapshot. No cloud definitions, refreshes or business data changed. The lineage UI, runtime filter reproduction, application-event correlation and deterministic value comparisons remain future work. See [lineage documentation](lineage.md). [PR #22](https://github.com/bcsnpc/data-investigation-agent/pull/22) merged; issue #21 closed. Phase 5A begins with the deterministic check contracts below.

## Deterministic checks: initial Phase 5A slice

[INV-001](https://github.com/bcsnpc/data-investigation-agent/issues/23) adds exact decimal totals, composite-key multiset comparison, strict metric/filter/grain/currency/snapshot compatibility, report/metric resolution and freshness policy evaluation. Evidence and results are retained atomically in local SQLite against an explicit lineage build. Missing snapshot context stays NOT_COMPARABLE; no configured freshness policy stays UNKNOWN. Results do not automatically classify a defect.

Live semantic refresh acquisition persisted run `7b04d9cc-01ed-42e2-be04-d1ad34c774a0`; the connection succeeded and freshness remains UNKNOWN because no policy is configured. Executive Sales / Net Sales resolved uniquely with zero relevant lineage gaps. Twelve investigation tests, twelve lineage tests, sixteen metadata tests and two generator tests pass. See [contracts and verification](investigation-checks.md).

This is a backend foundation, not completed end-to-end investigation: live cross-layer business query adapters, runtime filter reproduction, snapshot propagation and root-cause classification remain next. No cloud data, definitions or refresh schedules changed. [PR #24](https://github.com/bcsnpc/data-investigation-agent/pull/24) merged; issue #23 closed.

## Cross-layer value acquisition (INV-002)

[Issue #25](https://github.com/bcsnpc/data-investigation-agent/issues/25) implements fixed read-only Order Count and Net Cash queries across SQL, Bronze, Silver, Gold and the semantic model, with required currency and optional order filters. Ordered boundaries distinguish numerical differences from snapshot-comparable divergence. Evidence, adapter/query hashes, endpoint acquisition and sanitized failures are retained in SQLite. Missing earlier evidence prevents an unsupported first-boundary claim.

Twelve new tests pass, including actual source SQL business-rule fixtures and partial-acquisition persistence. Live Azure SQL and Power BI agree on 100,000 orders and USD 64,892,824.49 net cash; sample ORD-000002 agrees at one order and USD 1,529.64. Persisted endpoint check `1cae5e66-3293-41b4-9491-b59ccc3de7cb` remains NOT_COMPARABLE because no common source snapshot is proven.

Fabric SQL endpoint live verification is pending an additional enterprise SQL audience sign-in; the existing REST and Power BI sessions work. No five-layer success, verified root cause, bug creation or cloud mutation is claimed. See [query contracts and verification](cross-layer-queries.md). [Draft PR #26](https://github.com/bcsnpc/data-investigation-agent/pull/26) awaits live verification. Next after authentication: complete the live five-layer checks, then capture trustworthy common-source version evidence for causal boundary analysis.

INV-002 authentication follow-up: the Windows broker showed a different account and failed. The SQL-only helper now uses browser authentication, explicitly selects the development operator and validates the tenant/account. Existing REST/Power BI sessions are preserved. Twelve query tests pass; user browser sign-in and the five-layer live check remain pending.

INV-002 confirmed auth cause: AADSTS65002 identifies missing first-party preauthorization between Fabric CLI and the SQL resource. SQL auth now uses Azure CLI in an isolated enterprise profile; no personal Azure session or tenant permissions are changed. Additional user sign-in remains pending.

## INV-002 live verification complete

The isolated Azure CLI enterprise sign-in succeeded. Sample run `464fd436-1667-46de-b5a8-607c0689d4bf` returned one order and USD 1,529.64 net cash across SQL, Bronze, Silver, Gold and Power BI. Full baseline run `188e33fd-2363-4980-9557-b9ad1ff93c45` returned 100,000 orders and USD 64,892,824.49 net cash in all five layers. Each run has eight observed boundary matches and no unavailable layers. Evidence is retained in SQLite; no cloud data or definitions changed.

This resolves the authentication/live-verification blockers recorded above. PR #26 merged; issue #25 closed. Strict comparisons remain NOT_COMPARABLE because independently acquired values do not prove a common source snapshot; classification remains UNRESOLVED. Next: propagate trustworthy source/dependency versions for comparable boundary diagnosis.

## INV-003 run provenance evidence

[Issue #27](https://github.com/bcsnpc/data-investigation-agent/issues/27) captures publication run IDs, distinct/null counts and scope row counts in the same query as the metrics. Live run `9a1976a2-0699-4361-a88c-6509fc36d02b` verified Silver-to-Gold and Gold-to-model run alignment with no mixed or missing markers. All five layers still agree on 100,000 orders and USD 64,892,824.49 net cash. Six new provenance tests and 26 query/investigation/generator tests pass.

This improves available version evidence but does not complete common-source snapshot proof. The original SQL-to-Bronze ingestion has no captured immutable extraction identity; SQL endpoint reads are not pinned Delta snapshots. Source snapshot remains null, strict comparisons remain NOT_COMPARABLE and classification remains UNRESOLVED. The ingestion/publication changes required for proof are specified in [snapshot provenance](snapshot-provenance.md). No pipelines, cloud data or definitions changed. [PR #28](https://github.com/bcsnpc/data-investigation-agent/pull/28) merged; issue #27 closed.

## ING-001 transaction-consistent source artifact

[Issue #29](https://github.com/bcsnpc/data-investigation-agent/issues/29) implements a read-only ten-table export in one SQL SNAPSHOT transaction. The finalized source artifact `3b9354f3-af21-4296-a936-91b4a299777a` contains 1,410,699 rows with verified content/schema hashes; its manifest reference is registered in SQLite. Exported data independently reconciles to 100,000 orders and USD 64,892,824.49 net cash. Eight source/manifest contract tests and two generator tests pass.

The planned Bronze publication uses an isolated snapshot schema and requires actual Delta table identities/versions and content reconciliation. This is a source artifact plus publication contract, not a deployed replacement ingestion pipeline. Existing cross-layer snapshot gaps remain until Bronze and downstream publications consume this exact artifact. No cloud data or definitions changed. See [source snapshot documentation](source-snapshot.md). Next: execute and independently verify the isolated Bronze publication, then propagate its version chain. [PR #30](https://github.com/bcsnpc/data-investigation-agent/pull/30) merged; issue #29 closed.

## ING-002 isolated Bronze publication verified

[Issue #31](https://github.com/bcsnpc/data-investigation-agent/issues/31) stages the exact registered source artifact and publishes ten typed Delta tables under `snapshot_3b9354f3af214296a93691b4a299777a`. Publisher job `8091da39-ff69-4a8e-ac86-7cb583270380` and independent verifier job `ee41fc12-0e81-4d44-a68f-a4ce47cbdcde` both completed successfully. All 1,410,699 rows reconcile in both directions, with ten distinct Delta IDs pinned at version 0. The source-to-Bronze evidence is registered in SQLite as SOURCE_TO_BRONZE_VERIFIED.

Six new publication/upload tests, eight source contract tests and two generator tests passed. The existing app Bronze/Silver/Gold/model path remains separate; it has not been assigned this source snapshot. Details, job IDs, guarantees and limitations are in [isolated Bronze publication](snapshot-bronze.md), with environment references in infra/fabric/environment.json. [PR #32](https://github.com/bcsnpc/data-investigation-agent/pull/32) merged at `1cee5d6153821d97442cf6d6de87c19ebccc9c51`; issue #31 closed.

## ING-003 Silver input binding

[Issue #33](https://github.com/bcsnpc/data-investigation-agent/issues/33) adds a registry-backed input builder and pinned Delta reader for the verified Bronze snapshot. Six offline contract/reader tests and two generator tests pass. No additional cloud tables or notebooks are created. This is the input preparation slice: wiring and live publication into the existing Silver tables, output version receipts, Gold propagation and semantic refresh remain outstanding. See [Silver input contract](silver-snapshot-input.md).

Local verification against the registered source artifact and completed Bronze proof produced BOUND_INPUTS for all ten tables. This verifies binding construction; live Spark execution remains pending.

[PR #34](https://github.com/bcsnpc/data-investigation-agent/pull/34) merged at `33f8be08ee4d1cb79acec3baa5155ac0636985a1`; issue #33 closed. Full-history secret scan passed with no leaks.

## ING-004 Silver snapshot publication

[Issue #35](https://github.com/bcsnpc/data-investigation-agent/issues/35) wires the verified input binding into the existing Silver notebook and adds output Delta identities/versions, two-way content reconciliation, and a registry recorder. The existing ten Silver destinations are reused. Four publication tests, six input tests, twelve lineage tests and two generator tests passed.

Live job `885d3567-c838-4a35-bbe2-136a5524cffe` completed successfully. READY run `63a22c91-21b2-4fb1-a41c-cc5a97ac4284` reconciled all ten outputs (1,410,699 rows) and was registered as SOURCE_TO_SILVER_PUBLISHED in SQLite. Source snapshot and exact Bronze proof references are retained in the receipt and output rows. [PR #36](https://github.com/bcsnpc/data-investigation-agent/pull/36) contains this publication; CI and the full-history secret scan passed on the implementation commit.

Gold/model propagation and refreshed metadata lineage remain outstanding. Current Silver now has a newer run than the Silver run referenced by existing Gold; that expected publication gap must not be classified as a technical defect. The old metadata graph has not been refreshed to describe the new notebook input path. No end-to-end common snapshot or independent Silver verifier is claimed. [PR #36](https://github.com/bcsnpc/data-investigation-agent/pull/36) merged at `9923792444523a65bd9e23339a9cfe6ed6468541`; issue #35 closed.

## ING-005 Gold snapshot propagation

[Issue #37](https://github.com/bcsnpc/data-investigation-agent/issues/37) binds Gold to the registered Silver proof and recorded Delta identities/versions. The existing six reporting tables and three dimensions now publish in one run with source evidence and output version receipts. Four new evidence tests, six Gold rule tests, twelve lineage tests and two generator tests pass.

Live job `a05cdfd0-7e65-4c55-9a84-14d32af5aad1` completed successfully. READY run `e6559c75-d1ba-49bc-a87e-61cc47ecaf99` passed all 115 checks; all nine outputs are pinned at Delta version 1. Gold retains 100,000 orders, 286,652 order lines and USD 64,892,824.49 net cash. Evidence is registered in SQLite as SOURCE_TO_GOLD_PUBLISHED. The earlier Silver-to-Gold publication gap is resolved for these pinned outputs. [PR #38](https://github.com/bcsnpc/data-investigation-agent/pull/38) contains the implementation; implementation CI and full-history secret scan passed.

See [Gold snapshot publication](gold-snapshot-publication.md). [PR #38](https://github.com/bcsnpc/data-investigation-agent/pull/38) merged at `beaa07615f7d419f0a50f32d34d3ad1140ad490b`; issue #37 closed. The legacy reporting-dimension receipt is superseded for this path. End-to-end model snapshot comparability is not yet claimed.

## ING-006 Semantic refresh and verification

[Issue #39](https://github.com/bcsnpc/data-investigation-agent/issues/39) updates refresh to consume the registered nine-table Gold receipt. All six model tables are checked for exact run IDs, counts and missing run markers; financial/filter evidence is retained with the refresh in SQLite. Four semantic evidence tests, five model/report contract tests and two generator tests pass.

Live transactional refresh `63e0ebc6-d4e3-4544-8e9b-92c07778819e` completed successfully against Gold run `e6559c75-d1ba-49bc-a87e-61cc47ecaf99`. All six tables aligned with expected counts and zero physical rows with missing run markers. Fifteen business totals, order count, eight filter cases and refund drillthrough passed. Combined evidence is stored in SQLite `semantic_snapshot_verifications` as SEMANTIC_RUN_ALIGNED. [PR #40](https://github.com/bcsnpc/data-investigation-agent/pull/40) contains this change; implementation CI and full-history secret scan passed.

See [semantic refresh evidence](semantic-snapshot-refresh.md). Exact engine Delta-version selection is not exposed by these DAX checks; snapshot comparability remains false. [PR #40](https://github.com/bcsnpc/data-investigation-agent/pull/40) merged at `0471a84dea91f75765e9d03fb0557c7fd850da76`; issue #39 closed.

## LIN-002 refreshed metadata and lineage

[Issue #41](https://github.com/bcsnpc/data-investigation-agent/issues/41) recollects current definitions and adds conservative support for the reviewed pinned Bronze reader plus verified source-publication mappings. Scan `4f443959-2657-4ca3-911a-0627441fa25f` is COMPLETE with zero unavailable capabilities, 39 lakehouse tables and five notebooks.

Graph `18791918-710b-4dfc-9360-ae328d7ada00` has 373 links and SQL paths for all 41 data-bound visuals. Status remains PARTIAL: ten static-parser gaps in the snapshot publisher/verifier are retained. The initial rebuild without receipt-backed mappings (`f7ae59db-bbd2-4dd4-b258-6bda766d0713`) is retained as historical evidence, not selected as the current build. Seven new audit/parser tests, twelve existing lineage tests and two generator tests pass. No cloud data, definitions or refreshes changed in this step.

See [refreshed lineage](refreshed-lineage.md). Next: make investigation consumers use the explicit refreshed graph and present its publication evidence and remaining limitations; do not infer exact model Delta-version comparability or hide unresolved dependencies.

[PR #42](https://github.com/bcsnpc/data-investigation-agent/pull/42) contains the refreshed lineage work and awaits review. Full-history secret scan passed with no leaks.

PR #42 pre-merge follow-up: added gap classification and enforcement in generic investigation checks and cross-layer boundary evaluation. Relevant or unscoped gaps return INSUFFICIENT_EVIDENCE, preserve diagnostic comparisons, and block verified divergence claims; unrelated scoped gaps do not block a supported path. All ten current publisher/verifier gaps are UNSCOPED, so the audit finds 41 SQL paths but zero paths eligible for definitive lineage conclusions. No gaps were relabeled resolved. Six policy tests and 33 comparison/investigation/audit/generator tests pass. PR #42 remains unmerged. Next: establish execution-specific scope for these ten gaps or extend reviewed parser support before enabling conclusions on affected paths.

PR #42 subsequently merged at `e509efd0ffb3864a8c3abeb06792de692eefb8c7`; issue #41 closed. Its blocked graph is retained as historical evidence.

## LIN-003 reviewed publication scope

[Issue #43](https://github.com/bcsnpc/data-investigation-agent/issues/43) adds a narrow exact-code contract for the captured publisher/verifier. Review establishes ten possible publisher table destinations and zero verifier table writes, bound to the verified source manifest and Bronze proof. This resolves finite dependency scope without inventing historical branch-execution evidence.

Build `549f1a33-5b04-40c3-8b64-718d507e480c` contains 403 links, zero remaining parser gaps and ten retained RESOLVED_BY_REVIEWED_CONTRACT records. All 41 data-bound visuals pass the lineage eligibility check. Changed code, parameters or publication mappings restore the blocks. Six contract tests, twelve lineage tests, six gap-policy tests, seven audit tests and two generator tests pass. No cloud mutation occurred. See [publication scope review](publication-lineage-scope.md).

Next: use this explicit graph build in investigation acquisition and expose its versioned evidence. Metric/snapshot compatibility checks remain required; exact model Delta-version comparability is still false and no automatic defect routing is enabled.

[PR #44](https://github.com/bcsnpc/data-investigation-agent/pull/44) contains the reviewed scope resolution and awaits review. Full-history secret scan passed with no leaks.

PR #44 subsequently merged at `db1ba1f6d483ee5625e469b936422721fb1e8d1d`; issue #43 closed.

## INV-004 current lineage acquisition

[Issue #45](https://github.com/bcsnpc/data-investigation-agent/issues/45) pins development acquisition to reviewed graph `549f1a33-5b04-40c3-8b64-718d507e480c`, resolves snapshot Bronze assets and queries the matching schema. Actual paths, expected publication references and eligibility are retained alongside evidence. Four selection tests, twelve cross-layer tests and two generator tests pass; PowerShell syntax is valid.

Live full-baseline run `203157aa-0ccd-4bca-9188-1111191c8cc1` returned 100,000 orders and USD 64,892,824.49 net cash across all five layers, with eight observed boundary matches and lineage eligibility supported. Sample run `6fee7189-fa82-4bdd-a510-74c95cdd1573` matched Bronze through semantic at one order/USD 1,529.64; source SQL returned 40613 at connection time and remains explicitly unavailable in that historical run. The full-baseline retry subsequently succeeded without changing source data.

[PR #46](https://github.com/bcsnpc/data-investigation-agent/pull/46) contains this integration; full-history secret scan passed. See [current-lineage acquisition](investigation-current-lineage.md). Live endpoint reads remain unpinned and do not inherit snapshot comparability from publication references; strict boundaries remain NOT_COMPARABLE and classification remains UNRESOLVED. Next: expose the stored investigation evidence through the backend workflow, preserving these statuses and limitations.

PR #46 subsequently merged at `18f983a680b628c342682387a5416776952c70e0`; issue #45 closed.

## API-001 saved investigation evidence

[Issue #47](https://github.com/bcsnpc/data-investigation-agent/issues/47) adds an authenticated loopback-only WSGI service with bounded list/detail endpoints over read-only SQLite. Saved statuses, graph references and evidence are preserved; no cloud query execution or defect routing is exposed. Six API tests and two generator tests passed, including a real HTTP round trip and SQLite mutation rejection.

A local HTTP smoke check successfully retrieved stored five-layer run `203157aa-0ccd-4bca-9188-1111191c8cc1`, preserving the 100,000-order totals and NOT_COMPARABLE boundaries. It executed zero cloud queries, and the temporary server was stopped. See [evidence API](investigation-evidence-api.md). No public backend deployment occurred. Next: ticket intake and the investigation execution/status workflow before adding the user interface.

[PR #48](https://github.com/bcsnpc/data-investigation-agent/pull/48) contains the local evidence API and awaits review. Full-history secret scan passed with no leaks.

PR #48 subsequently merged at `0f8f25ad029cdf168cb079b152f6641f57e46d1f`; issue #47 closed.

## WF-001 ticket intake and execution

[Issue #49](https://github.com/bcsnpc/data-investigation-agent/issues/49) adds optional authenticated ticket intake, UUID idempotency, a separate durable SQLite queue, status/timeline and a bounded worker. The worker resolves explicit report/metric scope on the pinned graph and links saved evidence. Missing scope becomes NEEDS_INPUT; COMPLETED does not claim ticket resolution. Claims have fenced 30-minute leases with at-least-once recovery. Six workflow tests, six evidence API tests and two generator tests pass.

Live baseline-verification ticket `f2fa6c29-7080-4d54-a882-3d99772b5b0b` completed through HTTP intake, separate worker, status retrieval and linked evidence retrieval. Its investigation is `d8cab0ab-c823-4171-a98a-6f20497e63b7`: Bronze/Silver/Gold/semantic matched at 100,000 orders and USD 64,892,824.49; source SQL was unavailable. The outcome preserves UNAVAILABLE and NOT_COMPARABLE, with classification UNRESOLVED. No full five-layer success is claimed for this run. The test server stopped after verification.

[PR #50](https://github.com/bcsnpc/data-investigation-agent/pull/50) contains the workflow; full-history secret scan passed. See [ticket workflow](ticket-workflow.md). No LLM or defect-routing capability is enabled. Next: configure the LLM provider and add structured ticket interpretation/planning over validated tools with explicit missing-input handling.


PR #50 merged at 307710d0e16ec57440e1fff585a4001d9c42b9bb; issue #49 closed.

## AI-001 structured ticket drafts

Issue #51 adds an opt-in Azure Responses adapter, strict local scope validation and persisted planning attempts in workflow.sqlite. Drafts require review and cannot execute queries or classify defects. Seven planner tests, six workflow tests and two generator tests passed. No Azure model deployment is configured or live model call verified. See [LLM ticket planning](llm-ticket-planning.md). Next: Azure deployment configuration, live ambiguity/filter evaluations and reviewed handoff. Bounded SQL availability retries remain a separate follow-up; the current completed partial run is not automatically requeued.


## AI-002 Azure deployment and live smoke evaluation

Issue #53: PR #52 merged; browser login restored personal Azure access. Registered the AI provider and created aoai-investigator-9696025 / investigator-llm in East US 2 using GPT-4.1 mini 2025-04-14, GlobalStandard capacity 10. Six live planning cases passed (3,344 total tokens); an existing ticket draft was persisted through the local operator launcher (550 tokens). Seven planner tests and two generator tests passed. No business queries or mutations occurred. Model credentials remain in process memory only. See [deployment verification](azure-llm-deployment.md). Next: reviewed handoff and evidence-grounded explanations; broader model evaluation and SQL availability retries remain pending.


## AI-003 reviewed execution handoff and evidence summaries

Issue #55: PR #54 merged at 06ceda3dcfeb76ab78afe0514499ea87c063399d. Explicit approval revalidates saved plan inputs and current lineage, then atomically creates one linked worker ticket with reviewer assertion and plan hash. Concurrent/repeated approvals are idempotent and failure rolls back new work. Evidence API detail now includes deterministic summaries with exact values, original statuses and evidence pointers. Six handoff/summary tests, six evidence API tests, six workflow tests and two generator tests pass. See [reviewed handoff](reviewed-handoff.md). Live approval created ticket af8d5a78-e7cb-433f-82ef-23f63bc0bde5; repeat approval returned the same ticket. Worker run d70036f1-9288-4f52-9a0a-411ee57b5c03 completed and its summary was verified over real HTTP. Bronze through semantic matched 100,000 orders and USD 64,892,824.49; SQL returned connection error 40613. Classification remains UNRESOLVED with UNAVAILABLE and NOT_COMPARABLE boundaries. The temporary server stopped. Next: HTTP review experience and evidence-grounded LLM narrative validation; SQL transient retries remain pending.


## API-003 draft review and explicit approval

Issue #59: SQL retry PR #58 merged at 3522f9a23852a12b53129c97905989e8b7de381a. PR #56 remains a dependency for this review API. Added opt-in authenticated draft listing/detail and approval bound to the displayed draft hash. Approval reloads estate configuration, rejects stale context and creates one linked ticket through the transactional handoff. Five new API tests, six handoff tests, six evidence API tests, six workflow tests and two generator tests passed, including real local HTTP approval. No SQL or model calls occurred. See [plan review API](plan-review-api.md). SQL free-limit and AutoPause-on-exhaustion remain mandatory; no paid overage is authorized. Next: review UI and validated evidence-grounded LLM narratives.
## Reliability: SQL auto-resume retries

Issue #57: Azure activity logs and successful reads after resume identified SQL auto-resume plus missing initial-connection retry as the recurring 40613 mechanism. Added at most three SQL-only connection attempts with 10/20-second delays for connection-stage 40613; query/authentication/unknown errors are not replayed. Saved observations retain attempt history. Five retry tests, twelve cross-layer tests and two generator tests passed. Live run 5a161256-05a0-4f81-9fdb-ab3c238284b4 successfully read all five layers at 100,000 orders and USD 64,892,824.49. SQL was already awake and succeeded on attempt one; recovery/exhaustion are simulated tests, not a live cold-start claim. See [SQL retry details](sql-connect-retries.md). No database settings or business data changed.


User constraint: Azure SQL must remain within its free allowance. Verified useFreeLimit=true and freeLimitExhaustionBehavior=AutoPause; normal idle autoPauseDelay=60 minutes. Do not enable paid overage, remove the free limit or upgrade SQL compute without explicit user authorization. Accept quota-exhaustion unavailability until allowance renews; bounded connection retries must not change these settings. Minimize avoidable full-estate validation runs.


## UI-001 local investigation review

Issue #61: PR #56 and PR #60 merged. Added a same-origin local review screen for saved tickets, drafts, scope confirmation, queued investigation status and evidence summaries. Browser verification passed on desktop and 390px mobile, including token rejection, approval, partial evidence and disconnect; fixture server/browser stopped. Two UI route/auth tests, five review API tests, six evidence API tests and two generator tests passed; JavaScript syntax checked. No SQL or LLM calls occurred. See [review UI](investigation-review-ui.md). The UI is local; ticket creation/planning and workers remain CLI workflows. Next: integrate ticket intake/planning experience and validate evidence-grounded LLM narratives. SQL free limits and AutoPause-on-exhaustion remain mandatory.


## UI-002 ticket intake and live planning

Issue #63: PR #62 merged at 1923b5654b18b7c823260bc91404561efb760c54. Added UI ticket submission and explicit idempotent model planning with persisted request state and isolated credential-handling subprocess. Four request tests, seven review API tests, seven planner tests, two UI tests, six workflow tests and two generator tests passed. Live browser submission/planning/approval produced worker run 9ef75410-0b9e-433b-b648-6b20b806c73a: all five layers returned one order and USD 1,529.64. SQL recovered from actual connection-stage 40613 on attempt two after the 10-second retry delay. UI displayed the saved results; classification remains UNRESOLVED with NOT_COMPARABLE boundaries. Two model calls used 1,104 tokens. Browser/server stopped and temporary operator token removed. No business data writes or SQL free-limit changes. See [UI ticket planning](ui-ticket-planning.md). User authorizes bounded live testing while retaining SQL free-allowance protections. Next: validated evidence-grounded LLM narratives and smoother background worker orchestration.

## AI-004 grounded explanation selection

Issue #65: PR #64 merged at c8901009d716addb92cf6973e98616bda24ae08d. Added explicit operator generation of model-selected findings and next steps over saved evidence, with backend wording, mandatory limitations, evidence references and hash-bound persisted attempts. This is constrained selection, not unrestricted root-cause narrative generation. Authenticated detail API and local review UI display validated explanations. All 174 script tests pass, including five new explanation tests; JavaScript syntax passes. Live final explanations validated both complete and SQL-unavailable saved runs, preserving UNRESOLVED and NOT_COMPARABLE (2,529 tokens for these two calls). Two earlier development calls included one rejected selection; one lacked retained usage before failure accounting was improved, so total development token usage is not fully known. Desktop/mobile browser checks passed with no console errors or horizontal page overflow. A stale local test server was discovered and replaced during verification. See [grounded explanations](grounded-explanations.md). No new business queries, data writes or SQL settings changes. Next: bounded background worker orchestration, explanation integration and clearer parent/child ticket status.

## WORKER-001 bounded local orchestration

Issue #67: PR #66 merged after all CI checks passed. Added opt-in background processing to the local review server, defaulting to one approved queued ticket within a 15-minute claim window. Finite session limits, graceful active-run completion, authenticated worker status and approved-only transactional claims are implemented. Expired uncertain runs are not automatically replayed. All 180 script tests pass, including six new orchestration tests with the real local handoff/queue and simulated cloud acquisition. No live SQL/Fabric/LLM calls or cloud setting changes occurred for this step. See [background worker](background-worker.md). This is local opt-in orchestration, not a deployed service; limits reset per server session. Next: bounded explanation integration after completion and clearer parent/child ticket status.

## WORKER-002 post-run explanations and related tickets

Issue #69: PR #68 merged after all CI checks passed. Added opt-in automatic explanation callbacks with durable per-run request state, reuse of validated explanations, and no automatic replay of failed or uncertain calls. Explanation failures preserve completed evidence. Ticket API/UI expose related approval links and individual statuses without rewriting original histories. All 188 script tests pass; JavaScript syntax passes. Browser navigation verified against saved original/child tickets; the existing explanation for run 9ef75410-0b9e-433b-b648-6b20b806c73a was reused through the new request path without a paid model call. See [post-run explanations](post-run-explanations.md). No new cloud queries or SQL settings changes. Historical catch-up is manual; local orchestration is not deployed. Next: a controlled end-to-end ticket/defect-lab acceptance run covering expected behavior and evidence gaps before expanding investigation scope.


## ACCEPT-001 workflow acceptance baseline

Issue #71: PR #70 merged after all CI checks passed. Added a repeatable isolated acceptance harness spanning authenticated WSGI intake/planning/approval, background execution, saved evidence, automatic explanations and related statuses. Three cases pass: equal unpinned values, unavailable SQL and comparable Gold divergence. All remain UNRESOLVED; only the comparable case identifies Silver to Gold as the first verified divergence. All 189 script tests pass. Full product acceptance is explicitly false. Tracker overview and next milestone now reflect recent work. No cloud calls or baseline mutations. See [acceptance baseline](acceptance-baseline.md). Next: isolated lab baseline/reset and business-grounded expected-behavior verification.


## LAB-001 isolated omission and reset

Issue #73: PR #72 merged after all CI checks passed. Added a local DuckDB lab using shared Gold SQL and a three-order partial-return/paid/unpaid fixture. The controlled Gold omission reduces net cash from USD 154 to USD 55; independent evaluator truth identifies one affected order and USD 99 difference. Transactional reset restores original table/schema fingerprints and rejects source/code drift. All 195 script tests pass, including six new lab tests; CLI initialization, injection, evidence and reset were exercised and the local lab is READY. Evaluation truth is excluded from the business evidence projection. This is a materialized-output omission, not cloud defect injection or agent root-cause verification. See [defect lab](defect-lab.md). Next: investigator integration and affected-record/impact verification, followed by no-defect business explanation and multi-layer coverage.


## LAB-002 record reconciliation and exact impact

Issue #75: PR #74 merged after all CI checks passed. Added a deterministic lab investigator over the business-only projection, expanded to retain extra Gold keys. Missing/extra/value mismatches and exact per-currency impacts are persisted in an isolated EvidenceStore-compatible database with row references. The local injection run d03cf387-91a9-4578-bd10-6627054ff417 identified ORD-000001 and USD -99.0000; reset returned READY. All 200 script tests pass, including five new impact tests. No evaluator truth, cloud queries, model calls or cloud settings changes. Root cause remains unverified and classification UNRESOLVED. See [lab record impact](lab-record-impact.md). Lab-specific ticket/UI integration, business-grounded expected behavior, cause verification and multi-layer coverage remain pending.


## LAB-003 scoped expected refund behavior

Issue #77: PR #76 merged after all CI checks passed. Added an explicit local net-cash-after-refunds contract requiring matching records and complete, exact capture/refund evidence. The reset lab proves USD 253 captured minus USD 99 refunded equals USD 154 net cash and returns EXPECTED_BEHAVIOR, with routing disabled. Plain matching, incomplete drivers, unsupported questions and mismatches are not promoted. Evidence and contract are persisted. See [expected refund behavior](expected-refund-behavior.md). No cloud/model calls or baseline mutations. All 205 script tests pass, including five new business-verification tests. This covers one scoped no-defect case; technical-cause verification, live estate coverage and ticket/UI integration remain pending.


## LAB-004 verified local filter cause

Issue #79: PR #78 merged after all CI checks passed. Added an explicit filter-build variant with transactional build receipt and deterministic supported-query replay. Current source/output fingerprints, observation equality, filtered replay and unfiltered Silver reconciliation are required for TECHNICAL_DEFECT. The original output deletion remains UNRESOLVED. Local run 3eaec492-8777-42fe-bce0-8ba468c75d63 verified one omitted partially returned order and USD 99 impact; reset restored READY. All 209 script tests pass. Evidence is persisted; routing remains disabled. No cloud or LLM calls. See [verified lab filter](verified-lab-filter.md). Next: reviewed ticket/UI integration of lab results and broader cause/freshness scenarios.


## LAB-005 reviewed lab tickets and findings UI

Issue #81: PR #80 merged after all CI checks passed. Added an isolated lab review server with an explicitly fixed local Net Cash/USD catalog and draft mode; no cloud or LLM calls. Approved tickets run through the existing bounded worker and save lab findings separately. UI displays deterministic cause, affected orders, exact per-currency impact and verified business arithmetic. All 210 script tests pass, including both classification paths through actual review/worker APIs. Browser submission/approval/completion and mobile technical-defect display passed with no console errors or page overflow. Browser/server stopped, temporary token removed and lab reset READY. See [lab review UI](lab-review-ui.md). Next: expand resettable cause/freshness scenarios and acceptance coverage before ownership/routing.


## LAB-006 source-version freshness distinction

Issue #83: PR #82 merged after all CI checks passed. Added resettable inject-stale using the unchanged Gold transformation over a controlled prior empty-refund source view. Receipt/hash/current-observation agreement and prior/current replay are required for REFRESH_FRESHNESS. Filter-build defects remain TECHNICAL_DEFECT, missing/drifted proof remains UNRESOLVED. Local run eb5ccabd-f6b5-43dc-86d7-a27bc93c367f proved one order overstated by USD 99; reset restored READY. All 213 script tests pass; the reviewed API test now covers all three supported classifications. No cloud/model calls or SQL settings changes. See [lab freshness](lab-freshness.md). This does not prove cloud snapshots or refresh SLA. Next: broaden scenario evaluation and ownership/routing contracts; live freshness, richer AI/UI and hosting remain pending.


## ROUTE-001 ownership-aware draft contracts

Issue #85: PR #84 merged after all CI checks passed. Added explicit ownership policy, provider interfaces and deterministic evidence-bound routing drafts. Expected behavior is NO_BUG; non-technical findings require human triage. Supported local technical findings require recomputed impact, consistent cause and an explicit owner. Repeated preparation is idempotent; changed evidence/policy gets a new draft. Real saved run 3eaec492-8777-42fe-bce0-8ba468c75d63 returned NEEDS_OWNER under the deliberately empty policy. All 217 script tests pass, including four routing tests. Tests use fixture teams; no real owner is invented. No bugs/notifications sent, no cloud/model calls. See [routing drafts](routing-drafts.md). Next: review/approval experience and provider delivery contracts, with real ownership/recipients required before enabling delivery. Broader scenarios, live freshness, richer AI/UI and hosting remain open.


## ROUTE-002 local routing review and approval

Issue #87: PR #86 merged after all six CI checks passed. Added authenticated draft preparation/detail/approval endpoints and an explicit review checkbox in the isolated lab UI. Approval binds the displayed draft hash and revalidates saved evidence and ownership; concurrent/repeated approval is idempotent. Default real ownership remains empty. All 221 script tests pass; JavaScript syntax and desktop/mobile browser review/approval pass with no console errors or horizontal overflow. Browser verification used Fixture Data Team in an isolated policy and saved evidence. Browser/server stopped and temporary token removed. No issues/notifications delivered or cloud/model calls made. See [routing review](routing-review.md). Next: approval-bound provider delivery contracts and recovery. Remaining: real owners/recipients and adapters, broader cause/scenario evaluation, live snapshot/freshness guarantees, richer AI and ticket context, investigator hosting/auth/monitoring, and full product acceptance.


## ROUTE-003 durable local delivery rehearsal

Issue #89: PR #88 merged after all six CI checks passed. Added a CLI and durable local rehearsal journal for approved routing drafts, separate issue/notification stages, stable operation keys and explicit receipt reconciliation. Current evidence/ownership is revalidated at each stage. Interrupted attempts are held without automatic replay; notification waits for an issue receipt. All 229 script tests pass, including eight rehearsal tests covering concurrency, restart, both stage interruptions, conflicting/missing receipts, stale evidence/ownership and CLI recovery. All delivery receipts are simulated locally; no external issues/messages, cloud/model calls or SQL changes. See [delivery rehearsal](routing-delivery-rehearsal.md). Next: destination-bound review and real provider adapter contracts, followed by authorized delivery and provider-specific recovery validation. Remaining: real owners/recipients; broader defect/evaluation coverage; live snapshot/freshness guarantees; richer AI, attachments and lineage views; hosted investigator/auth/monitoring; full product acceptance.


## ROUTE-004 destination and content review

Issue #91: PR #90 merged after all six CI checks passed. Optional explicit GitHub repository/email recipient configuration now generates deterministic proposed content in routing drafts. The UI displays destinations, title/subject and bodies before approval. Hashes bind this preview; changed repository/recipients require a new review and block stale rehearsal execution. Legacy finding-only reviews remain explicit. All 235 script tests pass, including six destination tests; JavaScript syntax and fixture browser approval/mobile checks pass. No real ownership or recipients configured, no external delivery or cloud calls. See [routing destinations](routing-destinations.md). Next: provider adapters and provider-specific receipt recovery with explicit authorized destinations. Remaining: real routing configuration/delivery; broader scenarios/evaluation; live freshness/snapshot guarantees; richer AI/context/lineage; hosted investigator/auth/monitoring; full product acceptance.


## ROUTE-005 GitHub issue adapter and held-outcome recovery

Issue #93: PR #92 merged after all six CI checks passed. Added a transport-injected GitHub issue adapter with durable draft/content claims, exact approval revalidation, one creation attempt and bounded receipt reconciliation. The operation marker is included in the proposed issue body before approval, so older destination previews require a fresh review. Missing, duplicated, edited or incomplete receipts remain held without automatic replay. All 243 script tests pass, including eight adapter tests. No live defect issue or notification was sent; no SQL/model usage. See [GitHub adapter](github-issue-adapter.md). This adapter is not wired to a live transport, UI or worker. Next: email provider adapter and delivery integration, then explicitly authorized live acceptance. Remaining: real owners/recipients and credentials, provider recovery/authorization UI, broader scenario evaluation, live snapshot/freshness checks, richer AI/context/lineage, hosting/auth/monitoring and full product acceptance.


## ROUTE-006 email adapter and issue prerequisite

Issue #95: PR #94 merged after all six CI checks passed. Added an SMTP-injected adapter requiring a confirmed issue receipt, current draft approval and explicit sender/envelope hash authorization. Durable claims prevent duplicate concurrent calls; accepted, partial, refused and uncertain outcomes remain distinct. Acceptance never claims mailbox delivery. All 251 script tests pass, including eight email tests. No live emails/defect issues, SQL or model calls. See [email adapter](email-delivery-adapter.md). Next: envelope review and hosted delivery orchestration; live transport/credentials and explicitly authorized acceptance remain required. Pending: real owners/recipients, provider recovery operations, broader scenarios/evaluation, live snapshot/freshness guarantees, richer AI/context/lineage, investigator hosting/auth/monitoring and full acceptance/demo.


## ROUTE-007 durable envelope approval and coordinator

Issue #97: PR #96 merged after all six CI checks passed. Added persisted envelope previews, explicit hash-bound approval, local CLI review/status and a disabled-by-default execution coordinator. Current evidence, ownership and issue receipt are revalidated before adapter execution. Saved attempt status survives restarts; held sends are not replayed. All 258 script tests pass, including seven workflow tests and CLI review verification. Enabled tests use simulated SMTP; no live messages, SQL or model calls. See [envelope workflow](envelope-workflow.md). Next: browser/hosted envelope review and authorized delivery integration. Pending: live transports/credentials and real recipients, recovery operations, broader scenarios/evaluation, live snapshot/freshness checks, richer AI/context/lineage, hosting/auth/monitoring and full acceptance/demo.


## ROUTE-008 browser envelope review

Issue #99: PR #98 merged after all six CI checks passed. Added authenticated review-only envelope preparation/status/approval endpoints and lab browser sender/message review. The API refuses an enabled coordinator, has no send endpoint, and validates bounded JSON and explicit confirmation. All 262 script tests pass, including four envelope API tests; JavaScript syntax and browser preparation/approval/mobile checks pass. Browser fixture uses a simulated issue receipt and no live SMTP. No real recipients configured or messages sent. See [browser envelope review](browser-envelope-review.md). Next: live transport configuration and explicitly authorized delivery acceptance, plus hosted integration. Remaining: real owners/recipients/credentials, recovery operations, broader defect evaluation, live freshness/snapshot checks, richer AI/context/lineage, hosting/auth/monitoring and full acceptance/demo.


## ROUTE-009 explicit transport integration

Issue #101: PR #100 merged after all six CI checks passed. Added fixed-origin HTTPS and TLS SMTP transports plus an explicit external-action CLI using existing approval checks and durable adapters. Credentials come from environment variables; review servers/workers do not activate transports. Redirects, plaintext fallback and automatic retries are disabled. All 271 script tests pass, including nine mocked transport/CLI tests. No live issue/email or cloud query was executed. Real destination/provider information requested from the user remains pending. See [live transports](live-delivery-transports.md). Next: configure approved real destinations/provider and perform authorized delivery acceptance; investigate provider-specific gaps if needed. Remaining: hosted permission/recovery integration, broader defect evaluation, live snapshot/freshness checks, richer AI/context/lineage, hosting/auth/monitoring and full product acceptance/demo.


## EVAL-002 repeatable local classification matrix

Issue #103: PR #102 merged after all six CI checks passed. Delivery acceptance still awaits real repository/recipient/provider details, so work moved to independent scenario evaluation. Added a nine-case runner covering expected refunds, verified filter/freshness and unresolved evidence gaps, including a new unexplained USD 10 value change. Expected answers remain evaluator-only; exact classification/impact/affected count/cause/routing and reset are checked. Local report .local/lab-evaluations/af9dbfc5-504b-4184-9caf-6259797a43a3/report.json passed 9/9; all cases reset READY. All 274 script tests pass. No cloud/LLM/delivery calls or live baseline mutations. See [lab matrix](lab-evaluation-matrix.md). Product acceptance remains false. Next independent work: broader multi-layer defect coverage; live delivery verification can proceed once configuration is supplied. Remaining: hosted permissions/recovery, snapshot/freshness guarantees, richer AI/context/lineage, hosting/monitoring and full product acceptance/demo.


## LAB-007 three-layer propagated discrepancy

Issue #105: PR #104 merged after all six CI checks passed. Added isolated Bronze/Silver/Gold projection, adjacent record reconciliation and earliest observed local boundary reporting. The Silver order/line USD 10 mutation propagates into shared Gold SQL: Bronze/Silver differs 154 vs 164 while Silver/Gold matches 164. Classification remains UNRESOLVED without transformation-cause proof. Final report .local/multilayer-evaluations/2ee0fd32-2dda-4d33-8ee4-527db8863bfd/report.json retained evidence and reset READY. All 279 script tests pass, including five multi-layer tests. No cloud/model/delivery calls or live baseline mutations. See [multi-layer lab](multilayer-lab.md). This result shape is not yet integrated into review/routing or the nine-case matrix. Next: integrate multi-layer evidence and broaden transformation/model scenarios. Remaining: real delivery setup/acceptance, cloud snapshot/freshness guarantees, richer AI/context/lineage, hosted permissions/recovery/monitoring and full product acceptance/demo.


## UI-003 saved multi-layer evidence display

Issue #107: PR #106 merged after all six CI checks passed. The evidence summary now includes local Bronze/Silver/Gold order observations and adjacent boundaries. The review UI displays earliest observed discrepancy, exact per-currency totals/impact and affected records while retaining UNRESOLVED and no cause/routing claim. All 282 script tests pass, including three summary/API tests; browser checks verify the saved propagated-discrepancy fixture on desktop/mobile. No cloud/model/delivery calls or baseline changes. See [multi-layer review](multilayer-review.md). This is saved-evidence display; normal lab ticket execution remains two-layer. Next: reviewed multi-layer ticket execution and expanded evaluation. Remaining: broader transformation/model scenarios, real delivery configuration/testing, cloud snapshot/freshness, richer AI/context/lineage, hosting/permissions/recovery/monitoring and full acceptance/demo.


## WORKER-003 reviewed multi-layer execution

Issue #109: PR #108 merged after all six CI checks passed. Added a distinct three-layer report/lineage and loopback review server using the existing approved-child queue and one-job worker. Review folders are bound to mode and source path. Approved execution captures current Bronze/Silver/Gold evidence and renders results; no defect injection or cloud/LLM calls. All 285 script tests pass, including three execution/isolation tests. Browser baseline ticket bd6d05a6-457f-4a03-8d85-7d428765e13b approved child 9c0e5170-5d9d-46a6-9748-33ff8104fc9f completed with both boundaries matching USD 154 and classification UNRESOLVED. Propagated-discrepancy test detected the expected earlier boundary and reset READY. See [multi-layer ticket execution](multilayer-ticket-execution.md). Next: broaden transformation/model scenario proof and evaluation. Remaining: real delivery setup/acceptance, cloud snapshot/freshness guarantees, richer AI/context/lineage, hosting/permissions/recovery/monitoring and full product acceptance/demo.


## EVAL-003 multi-layer and offsetting-error matrix

Issue #111: PR #110 merged after all six CI checks passed. Added a five-case multi-layer matrix for matching, propagated, downstream-only, offsetting and two-boundary discrepancies. Exact affected IDs, per-boundary gap/status, earliest observed boundary and no false cause/routing promotion are checked. The offsetting case preserves USD 154 totals but detects two changed orders. Report .local/multilayer-matrices/f581c09e-27bb-4df5-aaca-9c6d148b7389/report.json passed 5/5 and all fixtures reset READY. All 288 script tests pass. No cloud/model/delivery calls or live baseline changes. See [multi-layer matrix](multilayer-evaluation-matrix.md). Product acceptance remains false. Next: transformation/model scenario proof beyond local value discrepancies. Remaining: real delivery configuration/testing, cloud freshness/snapshot guarantees, richer AI/context/lineage, hosted permissions/recovery/monitoring and full acceptance/demo.


## LAB-008 verified refund arithmetic build

Issue #113: PR #112 merged after all six CI checks passed. Added a resettable double-refund Gold query, transactional build receipt and supported-query replay verification. Successful local proof identifies ORD-000001 understated USD 99; missing/forged/drifted proof stays UNRESOLVED. The two-layer reviewed worker and evaluation matrix include the new case. Routing remains HUMAN_TRIAGE because its proof contract does not yet support this arithmetic cause. All 292 script tests pass, including four new arithmetic tests. The Silver/Gold matrix passed 10/10 with reset READY in .local/lab-evaluations/c0aa3751-bbbf-48a3-96b4-f20a293ad564/report.json. No cloud/model/delivery operations or live baseline mutations. See [arithmetic proof](refund-arithmetic-proof.md). Next: reviewed routing evidence contract for this cause and broader model scenarios. Remaining: real delivery configuration/testing, cloud snapshot/freshness guarantees, richer AI/context/lineage, hosting/permissions/recovery/monitoring and full acceptance/demo.


## ROUTE-010 arithmetic cause routing contract

Issue #115: PR #114 merged after all six CI checks passed. Routing now selects exact supported filter/arithmetic query and replay contracts, checks cause/classification agreement and retains independent evidence/impact reconciliation. Verified arithmetic findings require explicit ownership before review-only draft preparation; mixed/unknown/stale proof stays on hold. All 296 script tests pass, including four arithmetic routing tests spanning preparation, approval and local rehearsal. No real owner configuration or live delivery occurred. See [arithmetic routing](arithmetic-routing.md). Next: broader model/report cause scenarios and evaluation. Remaining: real delivery configuration/acceptance, live snapshot/freshness guarantees, richer AI/context/lineage, hosting/permissions/recovery/monitoring and full product acceptance/demo.


## LAB-009 report filter scope replay

Issue #117: PR #116 merged after all six CI checks passed. Added a read-only local Gold/report-filter simulation with explicit requested scope, per-order impact and persisted evidence. Five cases cover intended/unintended exclusion, matching all orders, missing context and extra report records; all passed with baseline READY. Classification remains UNRESOLVED because local SQL simulation does not prove deployed Power BI/DAX behavior. See [report scope lab](report-scope-lab.md). Validation: all 301 script tests passed, including five new report-scope tests added to CI. No cloud, LLM or delivery operations. Next: actual report/measure context acquisition and provenance. Remaining: broader semantic/relationship scenarios, live comparable snapshots/freshness, richer AI/context/lineage, real delivery acceptance, investigator hosting/auth/recovery/monitoring and full product acceptance/demo.


## LAB-010 reviewed report scope execution

Issue #119: reviewed PR #118 and merged after all six CI checks passed. Added a distinct fixed-scope report-filter mode to the authenticated ticket/plan/approval worker and a loopback API entrypoint. Mode and source binding prevent reuse of other lab approvals; USD scope is checked before persistence. The approved child completes with retained -99 USD evidence while the original stays queued. Four new tests cover workflow and rejection paths. See [report scope review](report-scope-review.md). All 305 script tests passed, including four new report-scope execution tests added to CI. No cloud, LLM or delivery operations; no UI deployment. Next: actual report/measure definitions and context acquisition. Remaining: dedicated report UI, broader semantic/relationship scenarios, live snapshots/freshness, richer AI/context/lineage, real delivery acceptance, hosting/auth/recovery/monitoring and full product acceptance/demo.


## META-004 targeted live report/model refresh

Issue #121: PR #120 merged after all six CI checks passed. Added explicit-ID targeted native report/model collection using existing metadata connectors, with no SQL scan or business queries. Four tests cover retained DAX, selection validation, partial failure/redaction and prior-scan preservation. Live scan 93324a35-8a2b-459e-a979-22b9bd75b03e completed with zero unavailable capabilities: 3 reports, 45 visuals, 25 measures, 5 relationships, 67 definition parts; all 259 asset hashes verified. Stored locally in .local/metadata/report-definitions.sqlite. See [targeted metadata](targeted-report-metadata.md). No model refresh, SQL, LLM or delivery operations. All 309 script tests passed, including four new targeted metadata tests added to CI. Next: native report-to-model binding and filter/measure evidence bundles. Remaining: dedicated report UI, broader semantic defects, live snapshot/freshness guarantees, richer AI/context/lineage, real delivery acceptance, hosting/auth/recovery/monitoring and full product acceptance/demo.


## META-005 native report binding evidence

Issue #123: PR #122 merged after all six CI checks passed. Added read-only single-scan evidence bundles with verified stored hashes, explicit semanticmodelid resolution, retained native report/filter/query and model/DAX definitions, and missing-evidence gaps. All three live-captured reports resolve by explicit model ID; 52 report/page/visual context entries retained in .local/report-definition-bundles/ae65178f-9d0d-4a81-b27e-3d8baa6831b9. This is definition evidence, not runtime filter/DAX evaluation or root-cause proof. All 314 script tests passed, including five new definition-evidence tests added to CI. See [definition evidence](report-definition-evidence.md). No new cloud, SQL, LLM or delivery calls. Next: supported native filter/measure evaluation and reviewed-ticket bundle integration. Remaining: dedicated report UI, broader semantic defects, live snapshot/freshness guarantees, richer AI/context/lineage, real delivery acceptance, hosting/auth/recovery/monitoring and full product acceptance/demo.


## META-006 native drillthrough context requirement

Issue #125: PR #124 merged after all six CI checks passed. Added a native single-order drillthrough requirement check over verified definition bundles. Missing context returns NEEDS_INPUT; explicit valid order returns CONTEXT_SUPPLIED without claiming runtime application or root cause. Unsupported page/filter/binding remains unsupported. Five focused tests pass. Retained live Order Operations page verified both states; artifacts .local/drillthrough-context/8a40b268-9318-4b42-a27d-be11803660a2. See [drillthrough context](report-drillthrough-context.md). All 319 script tests passed, including five new native drillthrough tests added to CI. No cloud, SQL, LLM or delivery calls. Next: reviewed-ticket context integration and broader native filter/measure evaluation. Remaining: report UI, broader semantic defects, live snapshot/freshness guarantees, richer AI/context/lineage, real delivery acceptance, hosting/auth/recovery/monitoring and full product acceptance/demo.


## META-007 native context plan and approval gate

Issue #127: PR #126 merged after all six CI checks passed. Added opt-in native page context to ticket planning using the ticket lineage scan; missing or merely inferred order context blocks approval. Explicit context retains a review-only draft, and approval rebuilds/checks the saved native evidence before creating a bounded worker child. All 324 script tests passed, including five new native-context planning tests added to CI. See [native context planning](native-context-planning.md). No cloud, SQL business queries, LLM or delivery calls. UI selection and runtime report execution remain pending. Next: reviewed page selection and broader native filter/measure evaluation. Remaining: dedicated report UI, broader semantic defects, live snapshot/freshness guarantees, richer AI/context/lineage, real delivery acceptance, hosting/auth/recovery/monitoring and full product acceptance/demo.


## UI-014 retained native page selection

Issue #129: PR #128 merged after all six CI checks passed. Added retained page choices and structured order input to ticket creation, persisted native_page scope, automatic planning enforcement and native-check display in review. Standard Azure launcher passes metadata configuration; unsupported lab context fails closed. All 327 script tests pass. Browser verified page selection, persisted context, clarification and blocked approval using an isolated deterministic fixture. See [native page UI](native-page-review-ui.md). No cloud, SQL business queries, LLM or delivery calls. Next: broader native filter/measure semantics and runtime evidence. Remaining: broader semantic defects, live snapshot/freshness guarantees, richer AI/context/lineage, real delivery acceptance, hosting/auth/recovery/monitoring and full product acceptance/demo.
