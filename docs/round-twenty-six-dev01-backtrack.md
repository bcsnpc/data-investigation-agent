# Round 26 dev01 partial backtrack

48 of 52 planned outcomes are graded. FORM: 5/10; TEXT: 13/38. Four stale-refresh cases remain pending; these are not complete-pass scores. The primary grader flags one harmful answer; the independent saved-evidence review disputes that flag. Original grades remain unchanged.

This table separates what the saved trace establishes from the grader?s proposed first wrong step. Limit exhaustion alone cannot establish an earlier reasoning error. No estate reads or model calls were made for this table.

| Kind / ticket | Saved trace | Grader first step | Observed failure group |
|---|---|---|---|
| form / v2-billing-invoices-v1 | BLOCKED; 10 queries; UsageHold: GUIDED_PHYSICAL_CAP_REACHED | intake | local read-cap closure |
| form / v2-warehouse-scope-v2 | NEEDS_INPUT; 0 queries; UNKNOWN_REPORT | target | intake/target resolution |
| form / v2-before-temporal-retention-v1 | UNRESOLVED; 10 queries; TOOL_OR_TIME_LIMIT | wrong conclusion | investigation did not deliver |
| form / v2-other-collected-definition-v1 | UNRESOLVED; 6 queries; TOOL_OR_TIME_LIMIT | triage | investigation did not deliver |
| form / v2-source-history-v1 | UNRESOLVED; 7 queries; TOOL_OR_TIME_LIMIT | target | investigation did not deliver |
| text / R17-01-v1 | ANSWERED; 7 queries; answer delivered | target | delivered answer mismatch (grader) |
| text / R17-04-v1 | NEEDS_INPUT; 0 queries; answer delivered | target | intake/target resolution |
| text / R17-05-v1 | ANSWERED; 3 queries; answer delivered | target | delivered answer mismatch (grader) |
| text / R17-08-v1 | NEEDS_INPUT; 0 queries; answer delivered | intake | intake/target resolution |
| text / R17-09-v1 | ANSWERED; 4 queries; answer delivered | target | delivered answer mismatch (grader) |
| text / R17-10-v1 | NEEDS_INPUT; 0 queries; answer delivered | intake | intake/target resolution |
| text / R17-11-v1 | ANSWERED; 7 queries; answer delivered | target | delivered answer mismatch (grader) |
| text / R17-12-v1 | UNRESOLVED; 6 queries; TOOL_OR_TIME_LIMIT | target | investigation did not deliver |
| text / baseline-S02-v1 | UNRESOLVED; 11 queries; TOOL_OR_TIME_LIMIT | triage | investigation did not deliver |
| text / baseline-S03-v1 | ANSWERED; 3 queries; answer delivered | target | delivered answer mismatch (grader) |
| text / different-warehouse-v2 | NEEDS_INPUT; 0 queries; answer delivered | intake | intake/target resolution |
| text / older-export-movement-1-v1 | NEEDS_INPUT; 0 queries; answer delivered | target | intake/target resolution |
| text / older-export-movement-1-v2 | NEEDS_INPUT; 0 queries; answer delivered | target | intake/target resolution |
| text / failed-fixture-load-v1 | NEEDS_INPUT; 0 queries; REQUESTED_RUN_NOT_IN_RETAINED_HISTORY | target | native run selection |
| text / failed-fixture-load-v2 | NEEDS_INPUT; 0 queries; REQUESTED_RUN_NOT_IN_RETAINED_HISTORY | intake | native run selection |
| text / failed-billing-transform-v1 | NEEDS_INPUT; 0 queries; REQUESTED_RUN_NOT_IN_RETAINED_HISTORY | target | native run selection |
| text / history-source-900201-v1 | ANSWERED; 6 queries; answer delivered | target | delivered answer mismatch (grader) |
| text / history-source-900201-v2 | UNRESOLVED; 6 queries; TOOL_OR_TIME_LIMIT | target | investigation did not deliver |
| text / latency-900501-v1 | NEEDS_INPUT; 0 queries; answer delivered | intake | intake/target resolution |
| text / latency-900501-v2 | BLOCKED; 2 queries; UsageHold: GUIDED_PHYSICAL_CAP_REACHED | target | local read-cap closure |
| text / latency-900502-v1 | NEEDS_INPUT; 0 queries; answer delivered | target | intake/target resolution |
| text / latency-900502-v2 | BLOCKED; 2 queries; UsageHold: GUIDED_PHYSICAL_CAP_REACHED | triage | local read-cap closure |
| text / access-export-1-v1 | NEEDS_INPUT; 0 queries; answer delivered | intake | intake/target resolution |
| text / access-export-1-v2 | NEEDS_INPUT; 0 queries; answer delivered | intake | intake/target resolution |
| text / waiting-fixture-load-v1 | ANSWERED; 0 queries; answer delivered | triage | delivered answer mismatch (grader) |

Detailed observations, original grader reasons and source hashes are in [the structured backtrack](round-twenty-six-dev01-backtrack.json). Four generic fixes are already committed for dev02; none changes these original results or expectations.
