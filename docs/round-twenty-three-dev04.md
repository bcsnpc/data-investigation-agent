# Round 23: complete dev04 pass

Independent score: **1/40; harmful: 0**. The earlier partial dev03 was 0/32, with eight not run. Expectations and original captures are unchanged.

Investigator model cost: USD21.580202. Unresolved handoff grades: {'2': 18, '1': 18, '0': 3}. These do not replace answer accuracy.

| Class | Score / attempted |
|---|---:|
| v2-application-baseline | 0/2 |
| v2-billing-mrr | 0/2 |
| v2-fixture-quantity | 0/2 |
| v2-billing-invoices | 0/2 |
| v2-failed-application-load | 0/2 |
| v2-failed-billing-transform | 0/2 |
| v2-waiting-application-load | 0/2 |
| v2-latency-record | 0/2 |
| v2-stale-model | 0/2 |
| v2-access-export | 0/2 |
| v2-warehouse-scope | 0/2 |
| v2-before-temporal-retention | 0/2 |
| v2-record-absent-everywhere | 1/2 |
| v2-record-repeated-gold | 0/2 |
| v2-source-history | 0/2 |
| v2-other-collected-definition | 0/2 |
| v2-screenshot-record-01 | 0/2 |
| v2-screenshot-record-02 | 0/2 |
| v2-screenshot-record-03 | 0/2 |
| v2-screenshot-record-04 | 0/2 |

Zero grades by raw failing step: {'wrong conclusion': 12, 'triage': 19, 'none': 3, 'target': 1, 'query error': 3, 'query validation': 1}. Three zero grades used none despite the grading instruction; retained and flagged, not silently reclassified.

The dominant runtime stop was the ticket model cap. One application-load case was interrupted by a PostgreSQL acquisition timeout; one unknown literal report remained a saved intake question. The single successful absence finding does not establish general capability. All temporary cohort mutations were restored, including automatic updates, source rows, schedules, native definitions and access objects. Temporal history remains on.

[Per-ticket grades, timings, costs and pinned outcome hashes](runs/round-twenty-three-dev04-grade.json). Timing includes the structured startup/investigation/publication fields; quick unresolved stops are not completed investigations.
