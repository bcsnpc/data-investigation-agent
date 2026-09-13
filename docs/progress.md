# Project progress

Updated: 2026-09-13. Source plan: [POC specification](../cross_system_data_investigator_poc.md), sections 90–100.

## Current position

Phases 0 (engineering foundation), 1 (business system), and 2 (data platform) are **in progress**.
The SQL baseline and authenticated order-browsing portal are implemented.
Ship, deliver and full-line return actions with transactional audit writing are implemented and verified locally against Azure SQL; merged in PR #9 and deployed to Azure App Service; hosted API and browser checks passed. Bronze ingestion is independently verified. Silver has ten conformed tables, 100,000 orders and a READY validation report. Gold has six reporting tables and a READY report with 59 passing checks; all 15 currency totals match independent Azure SQL queries. Power BI, lineage and AI remain pending.

| Phase | Status | Evidence / remaining work |
|---|---|---|
| 0 Engineering foundation | In progress | Private repository, README, SQL scripts, tests and tracking; broader standards and deployment automation remain |
| 1 Business system | In progress | Azure SQL, 100k baseline and restricted runtime users verified; browsing deployed; transactional actions deployed and verified; broader specification features remain scoped for follow-up |
| 2 Data platform | In progress | Bronze, initial Silver and Gold complete: 100k orders, reconciled reporting tables and independent source totals; recurring orchestration remains |
| 3 Analytics | Not started | Semantic model, DAX and reports |
| 4 Metadata and lineage | Not started | Connectors, graph, traversal and UI |
| 5 Deterministic investigator | Not started | Cross-layer comparisons, first divergence and evidence |
| 6 AI investigator | Not started | Ticket interpretation and explanations over verified evidence |
| 7 Defect lab | Not started | Named defect injection, reset and golden regression results |
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

Silver is merged in PR #12. Gold is deployed and verified; implementation PR review is next, followed by the Power BI semantic model and reports. The end-to-end milestone is not achieved until one
order can be traced from the app through Azure SQL, Fabric and Power BI.

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

- [FAB-003: Build reconciled Gold reporting tables](https://github.com/bcsnpc/data-investigation-agent/issues/13) - deployed and verified; 59 Fabric checks and 15 independent source totals passed; implementation PR review pending
