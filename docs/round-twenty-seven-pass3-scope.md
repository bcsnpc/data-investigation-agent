# Round27 pass3 declared scope

39 distinct tickets on source18855ef5 / image9a72dbd5. Every pass2 failure, every harmful ticket and the full20 fixed guard are rerun. No carried positive scores. Inputs are copied without changing ticket/expectation bytes.

| Ticket | Cohort | Selection |
|---|---|---|
| text-R17-01-v1 | baseline | P2_REVIEWED_FAILURE, P2_REVIEWED_HARMFUL |
| text-R17-02-v1 | baseline | P2_REVIEWED_FAILURE, P2_REVIEWED_HARMFUL |
| text-R17-05-v1 | baseline | P2_REVIEWED_FAILURE, P2_REVIEWED_HARMFUL |
| text-latency-900501-v1 | latency | P2_REVIEWED_FAILURE, P2_REVIEWED_HARMFUL |
| text-older-export-movement-1-v2 | baseline | P2_REVIEWED_FAILURE, P2_REVIEWED_HARMFUL |
| form-v2-access-export-v1 | access | FULL_PREDECLARED_GUARD20 |
| form-v2-access-export-v2 | access | FULL_PREDECLARED_GUARD20 |
| form-v2-application-baseline-v1 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-application-baseline-v2 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-billing-invoices-v2 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-billing-mrr-v1 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-failed-application-load-v1 | failed-fixture | FULL_PREDECLARED_GUARD20 |
| form-v2-failed-billing-transform-v1 | failed-billing | FULL_PREDECLARED_GUARD20 |
| form-v2-fixture-quantity-v1 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-latency-record-v1 | latency | FULL_PREDECLARED_GUARD20 |
| form-v2-other-collected-definition-v2 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-record-absent-everywhere-v1 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-record-repeated-gold-v2 | baseline | P2_REVIEWED_FAILURE, FULL_PREDECLARED_GUARD20 |
| form-v2-screenshot-record-01-v1 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-screenshot-record-02-v1 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-screenshot-record-03-v1 | baseline | P2_REVIEWED_FAILURE, FULL_PREDECLARED_GUARD20 |
| form-v2-screenshot-record-04-v1 | baseline | FULL_PREDECLARED_GUARD20 |
| form-v2-source-history-v2 | history | FULL_PREDECLARED_GUARD20 |
| form-v2-waiting-application-load-v2 | waiting | FULL_PREDECLARED_GUARD20 |
| form-v2-warehouse-scope-v1 | baseline | P2_REVIEWED_FAILURE, FULL_PREDECLARED_GUARD20 |
| form-v2-stale-model-v1 | stale | P2_REVIEWED_FAILURE |
| form-v2-stale-model-v2 | stale | P2_REVIEWED_FAILURE |
| form-v2-warehouse-scope-v2 | baseline | P2_REVIEWED_FAILURE |
| text-R17-04-v1 | baseline | P2_REVIEWED_FAILURE |
| text-R17-08-v1 | baseline | P2_REVIEWED_FAILURE |
| text-R17-10-v1 | baseline | P2_REVIEWED_FAILURE |
| text-R17-11-v1 | baseline | P2_REVIEWED_FAILURE |
| text-baseline-S01-v1 | baseline | P2_REVIEWED_FAILURE |
| text-baseline-S02-v1 | baseline | P2_REVIEWED_FAILURE |
| text-different-warehouse-v2 | baseline | P2_REVIEWED_FAILURE |
| text-history-source-900201-v1 | history | P2_REVIEWED_FAILURE |
| text-history-source-900201-v2 | history | P2_REVIEWED_FAILURE |
| text-latency-900501-v2 | latency | P2_REVIEWED_FAILURE |
| text-latency-900502-v2 | latency | P2_REVIEWED_FAILURE |

Cohorts: {'baseline': 25, 'latency': 4, 'access': 2, 'failed-fixture': 1, 'failed-billing': 1, 'history': 3, 'waiting': 1, 'stale': 2}.

Only exact-question evaluator failures block after the existing repair attempts. Other evaluator checks stay advisory. Read-only, secrets, budget, primary-question, native-title priority, record-key and latency checks remain active; context-gap metadata is record-only.

Gate: all required results saved and independently graded,0 reviewed harmful and full guard20/20. Partial results cannot pass. Calibration stays protected and unadmitted until that gate.
