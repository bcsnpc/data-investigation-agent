# Round Sixteen A1 billing onboarding - 2026-10-12

Billing remains **BLOCKED / NOT_SCORED**, with no published verified profile. Permission blockers were resolved at their approved scope, and native metadata is now retained and replays exactly. Warehouse transformation semantics and binding verification remain unfinished; successful metadata access is not a readiness waiver.

The exact identity changes and before/after controls are in [the section 8 grant record](round-sixteen-billing-grants.md). No identity was created or replaced; credentials, workspace roles and diagnostic identities were not changed.

## Native collection and provenance

Committed engine revision: `a465404`. Session: `billing-native-collection-20261012T061622`.

- Context: `e2c81334-17c6-474f-957b-53ff5bf1565b`.
- Context hash: `1c07c0c75098efe5b2ede369cd92498b7c8160405a0c6991c81ef91e54139c56`.
- Manifest hash: `44a753579fd07f4b580b22455940b7d877efe1e19c69ceb6935d5bd14662f676`.
- Exact tape SHA-256: `9f356b77df43ea319a46007f58f01ad24d59d52ad7c1fe71b8b41d30628b7ab9`.
- Receipt SHA-256: `7b272689a90e08b9b60504abd6600fa55906972389959a8215061099bcdb2d84`.

The operator principal investigator-code-reader returned HTTP200 for the source connection and all three pipeline definitions. Its source-connection User role is recorded separately; the HTTP200 definitions use its existing operator scope. These are operator definition receipts, not diagnostic-reader execution evidence. An operator refresh-history HTTP200 does not overturn the diagnostic reader's permission finding.

The isolated readers returned seven application objects and 42 columns, seven Bronze tables and 42 columns, and 12 Warehouse tables with 54 columns. The source catalog still explicitly lacks whole-schema visibility. Collection of *visible* Warehouse tables and Bronze columns completed, while their evidence says `VISIBLE_OBJECTS_ONLY`, `complete_schema=false`; no invisible-object absence is claimed. The overall context status is PARTIAL and it is not approved.

## Automatic Copy mapping evidence

All seven native Copy activities omit an explicit translator. Matching each declared source projection to the uniquely resolved source and destination schemas produced 42 mapping hypotheses. Seven row-version casts remain transformations rather than identity projections. No mapping is marked verified and no value equivalence is asserted.

| Activity | Inferred columns | Explicit non-identity casts | Status |
|---|---:|---:|---|
| Copy_accounts | 4 | 1 | INFERRED_FROM_CODE / UNVERIFIED |
| Copy_plans | 6 | 1 | INFERRED_FROM_CODE / UNVERIFIED |
| Copy_account_plan_history | 7 | 1 | INFERRED_FROM_CODE / UNVERIFIED |
| Copy_invoices | 7 | 1 | INFERRED_FROM_CODE / UNVERIFIED |
| Copy_payments | 6 | 1 | INFERRED_FROM_CODE / UNVERIFIED |
| Copy_usage_events | 6 | 1 | INFERRED_FROM_CODE / UNVERIFIED |
| Copy_subscriptions | 6 | 1 | INFERRED_FROM_CODE / UNVERIFIED |

The retained inventory `.local/round-sixteen/billing/inferred-copy-mappings.json` binds each hypothesis to the new context, native definition hash and both object hashes. It contains the source and destination declarations, types and native expressions. There are no fixture-specific column branches in the adapter. Unsupported projections are refused.

## Replay and remaining work

Exact offline replay passed: all context/result bytes and 51 physical metadata admissions matched across 27 logical calls. Replay used zero estate reads, zero authentication calls and zero model calls. Five pre-capture authentication controls are retained separately; the replay does not claim to execute authentication or re-test the private caller's deadline/cap. No native temporary-file bytes are claimed: the existing recorded file-result boundary is explicit.

The graph sealed at `a465404` has 14 gaps, including nine unresolved Warehouse-backed semantic partitions. That historical context is unchanged. Subsequent offline integration against the same retained assets resolves those nine partitions by exact native Warehouse item, server and workspace identity, and adds the seven embedded Copy edges. The separately saved derived graph has five unresolved visual-binding gaps. It is not a new approved context, and a graph edge is not a verified value equivalence.

The Copy inventory now produces 35 consumer-valid STATIC column proposals from direct projections, all `INFERRED_FROM_CODE / UNVERIFIED`. The seven row-version CAST outputs are explicitly excluded because the neutral relation contract cannot faithfully express that conversion. No cast is erased or treated as an identity mapping. Source types, destination types and native definition provenance remain in the evidence.

Warehouse semantic partition compilation and verifier routing now accept native Warehouse tables only when the retained item identity and server match the configured reader; type mismatches and filtered-scope comparisons still refuse. A generic parser defect was fixed: cells explicitly labelled T-SQL previously entered the Spark parser. They now use the T-SQL parser, with existing whole-target write restrictions unchanged.

Billing still cannot supply a faithful complete chain. A corrected offline audit of 50 retained Warehouse Script blocks produces 33 refusals for statements outside the supported CTAS/overwrite write form and 17 refusals because the referenced `bronze.*` views are not declared in the visible-table catalog. The 50 includes schema creation and audit-control scripts; it does not imply 50 missing data transformations. The relevant billing paths additionally contain stored-procedure execution, DELETE followed by INSERT, a UNION, and views; their semantics and execution ordering are not represented by the existing neutral AST. The earlier Spark-parser audit remains preserved separately; the corrected audit uses explicit T-SQL and actual retained table metadata.

**Decision:** do not spend reader-verification requests on a partial Copy set that cannot make the requested billing scope ready. No binding verification was admitted, no profile was published, and billing investigations remain NOT_SCORED. A smaller future claim could be proposed explicitly, but it is not whole-billing readiness.

Offline artifacts: `reprojected-graph.json`, `copy-column-proposals.json` and `warehouse-script-tsql-audit.json` under `.local/round-sixteen/billing/`. Each records the retained source context; no live data, model call or approval was used to derive them. Final focused regression: **117 tests passed**, including native Warehouse identity/type refusal, embedded Copy ambiguity, cast exclusion, explicit T-SQL routing through the proposal producer, and the unchanged filtered-scope refusal. Existing test SQLite ResourceWarnings appeared; the process exited 0.

## Accounting and capture controls

A1 charged 71 physical slots in total: 10 grant/resume controls, 5 controls for the failed authentication-wrapper attempt, then 51 metadata requests and 5 authentication HTTP controls in the successful collection. Investigation diagnostic reads 0; model calls 0. The initial A1 operational bound was 100. The successful collection's 51/70 metadata and 5/10 authentication bounds held.

At the collection's recorded post-read snapshot, the round pot was 2712/4000, reserve 95 untouched, ordinary headroom 1193; rolling usage 685/3000. These are timestamped A1 values, not a promise about later concurrent smoke usage.

The failed wrapper and the long shared-catalog read-lock findings remain in the grant record and ledger. The original capture sealed unchanged. Future private captures now audit a consistent in-memory copy after releasing the shared source handle. Both regressions pass: source writes remain possible during audit; rejected synthetic secrets create no durable snapshot. The initial tests' Windows handle-cleanup failure is retained as development history, not an estate result.

Freeze remains invalid: discovery code and identity scopes changed. Draft #423 remains open; no context approval, profile publication, fixture mutation, investigation result or merge is claimed here.
