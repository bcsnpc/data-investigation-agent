# Project progress

Updated: 2026-09-13. Source plan: [POC specification](../cross_system_data_investigator_poc.md), sections 90–100.

Approved scope extension: [Ticket experience and defect lab](../DATA_INVESTIGATOR_TICKET_AND_DEFECT_LAB_SCOPE.md). This extension governs the investigation experience and scope boundary alongside the original plan. Integration decisions and dependencies are recorded in [scope alignment](scope-alignment.md).

## Current position

Phases 0 (engineering foundation), 1 (business system), 2 (data platform), and 3 (analytics) are **in progress**.
The SQL baseline and authenticated order-browsing portal are implemented.
Ship, deliver and full-line return actions with transactional audit writing are implemented and verified locally against Azure SQL; merged in PR #9 and deployed to Azure App Service; hosted API and browser checks passed. Bronze ingestion is independently verified. Silver has ten conformed tables, 100,000 orders and a READY validation report. Gold has six reporting tables and a READY report with 59 passing checks; all 15 currency totals match independent Azure SQL queries. Power BI now has a six-table semantic model and three reports with verified DAX totals and order drillthrough. The initial metadata connector release is implemented and live-verified: 476 metadata records with no failed attempted capabilities. The lineage backend is now implemented and verified against the captured metadata; lineage UI and AI remain pending.

| Phase | Status | Evidence / remaining work |
|---|---|---|
| 0 Engineering foundation | In progress | Private repository, README, SQL scripts, tests and tracking; broader standards and deployment automation remain |
| 1 Business system | In progress | Azure SQL, 100k baseline and restricted runtime users verified; browsing deployed; transactional actions deployed and verified; broader specification features remain scoped for follow-up |
| 2 Data platform | In progress | Bronze, initial Silver and Gold complete: 100k orders, reconciled reporting tables and independent source totals; recurring orchestration remains |
| 3 Analytics | Initial release complete | Six-table model, 25 measures, three reports, 15 exact DAX totals and sample-order drillthrough verified; [details](powerbi.md) |
| 4A Metadata connectors | Initial collector merged; reusable connector refactor verified | Versioned SQLite inventory, live SQL/Fabric/Power BI definitions and explicit capability gaps; [details](metadata.md) |
| 4B Lineage | Backend merged in PR #22 | 360 evidence-backed links, persisted upstream/downstream traversal and 41 data-bound visual traces; UI remains later |
| 5A Deterministic investigator | In progress | Check engine merged in PR #24; cross-layer adapters implemented with SQL/Power BI live reads; all five layers live-verified; common-source snapshot proof pending |
| 5B Ticket experience | Not started | Ticket form, attachments, investigation workspace and auditable timeline |
| 6 AI investigator | Not started | Ticket interpretation and explanations over verified evidence |
| 7 Defect lab | Not started | Deterministic injection/reset, isolated evaluation ground truth and expected-behavior coverage |
| 7B Routing | Not started | Generic issue/notification providers, ownership-based routing and human triage |
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

Metadata and lineage are merged through PR #22; deterministic check contracts are merged in PR #24. Cross-layer query adapters and ordered boundary checks are implemented. Five-layer live verification passed. Next: establish common-source snapshot evidence for comparable diagnosis. Ticket UI and AI follow the backend. Recurring refresh orchestration remains open.

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

This resolves the authentication/live-verification blockers recorded above. PR #26 is ready for review. Strict comparisons remain NOT_COMPARABLE because independently acquired values do not prove a common source snapshot; classification remains UNRESOLVED. Next: propagate trustworthy source/dependency versions for comparable boundary diagnosis.
