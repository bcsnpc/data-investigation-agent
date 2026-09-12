# Project progress

Updated: 2026-09-12. Source plan: [POC specification](../cross_system_data_investigator_poc.md), sections 90–100.

## Current position

Phase 0 (engineering foundation) and Phase 1 (business system) are **in progress**.
The SQL database and synthetic baseline are complete. The business application
is not built. No Fabric, Power BI, lineage engine or AI integration is complete.

| Phase | Status | Evidence / remaining work |
|---|---|---|
| 0 Engineering foundation | In progress | Private repository, README, SQL scripts, tests and tracking; broader standards and deployment automation remain |
| 1 Business system | In progress | Azure SQL, 100k baseline and restricted runtime users verified; portal and live audit writing remain |
| 2 Data platform | Not started | Fabric Bronze/Silver/Gold, ingestion and validation |
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
- Synthetic audit events exist, but live application audit logging is pending.
- Admin credentials remain for schema/setup scripts. Restricted app, Fabric and
  investigator users are provisioned and verified; future runtime integrations
  must use their designated credentials.
- No production data or intentional defects have been loaded.

## Next milestone

Complete the operational business system: an order list,
order details and safe updates with transactional audit events. Then establish
the first Fabric pipeline. The end-to-end milestone is not achieved until one
order can be traced from the app through Azure SQL, Fabric and Power BI.

## Tracking convention

GitHub issues track actionable work; this file tracks phase status and decisions.
Each PR should reference its issue, explain behavior, record validation and update
relevant documentation. Mark completed work based on evidence, not intended work.

## GitHub work items

- [DATA-001: Connected 100,000-order baseline](https://github.com/bcsnpc/data-investigation-agent/issues/1) - closed
- [ENG-001: Complete engineering foundation](https://github.com/bcsnpc/data-investigation-agent/issues/2) - open
- [DB-002: Add restricted runtime SQL identities](https://github.com/bcsnpc/data-investigation-agent/issues/3) - implemented and verified; PR review pending
- [APP-001: Build Order Operations Portal](https://github.com/bcsnpc/data-investigation-agent/issues/4) - open
- [FAB-001: Validate enterprise access and ingest Azure SQL to Bronze](https://github.com/bcsnpc/data-investigation-agent/issues/5) - open
