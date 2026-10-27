# Round 23: unscored Opus cached diagnostic

Independent diagnostic grade: **5/13; harmful 0**.

Investigator charges USD3.933922. This is diagnostic only, never the Round23 held-out score. Original static dev expectations and grader rules are unchanged.

| Class | Score / attempted | Not run |
|---|---:|---:|
| v2-application-baseline | 0/2 | 0 |
| v2-billing-mrr | 2/2 | 0 |
| v2-fixture-quantity | 0/2 | 0 |
| v2-billing-invoices | 0/2 | 0 |
| v2-warehouse-scope | 1/2 | 0 |
| v2-before-temporal-retention | 1/2 | 0 |
| v2-record-absent-everywhere | 1/1 | 1 |
| v2-record-repeated-gold | 0/0 | 2 |
| v2-other-collected-definition | 0/0 | 2 |
| v2-screenshot-record-01 | 0/0 | 2 |
| v2-screenshot-record-02 | 0/0 | 2 |
| v2-screenshot-record-03 | 0/0 | 2 |
| v2-screenshot-record-04 | 0/0 | 2 |

Zero grades by independently reported step: {'query error': 1, 'triage': 1, 'wrong conclusion': 5, 'intake': 1}.

Main-loop calls exclude helper calls; the receipt includes all case ledger attempts and their exact charges. Worker-body and harness end-to-end timing are reported separately. Cache audit and matched-ticket Fable costs are separate observations; model, caching and case cap differ, so this is not an isolated model-effect estimate.

[Full per-ticket independent diagnostic grade](runs/round-twenty-three-opusdiag02-cached-partial-grade.json).
