# Measure-path nine-run evaluation

Updated 2026-09-25. Related #199 and #224. **KNOWN_DOMAIN_REGRESSION only.**
This is not a freeze, fresh variant or unfamiliar-domain acceptance result.

## Fixed conditions

Nine sequential G trials used commit `be2436f`, engine hash `21aa251ae3c8`, the
same ticket/model/context and the same medium-reasoning GPT-5.4 profile. Each run
allowed twelve investigation calls, six data reads, 48,000 input characters per
call, 384,000 cumulative investigation characters, 8,000 output tokens, a
120-second provider timeout, a 1,800-second run deadline and 65-second pacing.
Separated synthesis was enabled once per run. Every run was recorded and labelled
`KNOWN_DOMAIN_REGRESSION`; no counter was reset or refunded.

The original daily policy was sufficient and remained unchanged at 240 planner
calls, 60 cloud calls, 8,000,000 input characters, 1,500,000 output tokens and
concurrency one. Usage moved from zero to 115 planner/intake reservations, 32
cloud reads, 3,585,333 input characters and 861,500 output tokens. All 147 usage
records are settled and there are no active reservations.

## Results

| Trial | Calls | SQL / DAX | Lookups | Rejections | Reproduction / contribution | Stop | Synthesis | Calibration |
| --- | ---: | --- | ---: | ---: | --- | --- | --- | --- |
| M1 | 11 | 0 / 2 | 4 | 5 | 0 / 2 | No progress | Accepted BCR | Correctly uncertain |
| M2 | 10 | 0 / 0 | 5 | 5 | 0 / 0 | No progress | Text-bound failure | Correctly uncertain rejected proposal |
| M3 | 11 | 5 / 0 | 5 | 1 | 0 / 5 | Read budget | Citation-subset failure | Correctly uncertain rejected proposal |
| M4 | 11 | 4 / 0 | 9 | 0 | 0 / 3 | Read budget | Text-bound failure | Correctly uncertain rejected proposal |
| M5 | 9 | 1 / 1 | 4 | 3 | 0 / 2 | No progress | Accepted UNRESOLVED | Correctly uncertain |
| M6 | 11 | 1 / 4 | 3 | 3 | 0 / 0 | Read budget | Accepted BCR | Correctly uncertain |
| M7 | 11 | 4 / 0 | 7 | 0 | 0 / 0 | Read budget | Accepted UNRESOLVED | Correctly uncertain |
| M8 | 12 | 5 / 0 | 9 | 0 | 0 / 0 | Read budget | Accepted UNRESOLVED | Correctly uncertain |
| M9 | 11 | 5 / 0 | 6 | 0 | 0 / 1 | Read budget | Text-bound failure | Correctly uncertain rejected proposal |

BCR means `BUSINESS_CONTEXT_REQUIRED`. All nine first context decisions used the
new `measure_path` lookup. M1 then executed `TEST_CONTRIBUTION` before any
reproduction, confirming that the runtime did not impose an action sequence.

Totals are **97 investigation calls, nine synthesis calls, 25 SQL reads, seven
DAX reads, 52 context observations, 13 contribution tests and zero labelled
measure reproductions**. Six runs stopped at the read budget and three on no
progress. Wall time totals 7,200.605 seconds and spans 668.493-877.761 seconds.
There were no provider transport errors.

The 17 query rejections comprise 14 unknown/ambiguous DAX-member failures, two
contribution queries that did not compile against their declared upstream object,
and one unsupported SQL `Sign` node. There were four schema-prefetch repairs, no
compiled-duplicate refusal, and two post-hoc equal-result overlaps. The ledger's
SQL-only rate is 2/27 rejected proposals; the broader 17 count includes rejected
DAX/contribution proposals.

## Evidence and calibration review

Five synthesis calls delivered assessments. All five main claims are grounded in
their frozen digest and stored receipt values. Four have intact support. M5 is
grounded but its provider response contains a replacement character in the
remaining-test sentence, so it is excluded from the intact count.

- **5/9 accepted synthesis outputs**.
- **5/9 receipt-grounded synthesis outputs**.
- **4/9 intact receipt-grounded synthesis outputs**.
- **9/9 correctly uncertain delivered outputs or preserved raw proposals**.
- **0 supported cause conclusions** and no verified cause.

M1 is the clearest improvement. Two native contribution tests established that 29
adjustment-linked movement IDs contribute 671 to `Handled Quantity`, including
displayed movement-level comparisons. It still correctly left the intended
adjustment rule unknown. M5 linked the two-adjustment movement 167 to one Activity
row. M6 observed the 8,765 native total and its 6,425/2,340 components, but used
`GENERAL_DIAGNOSTIC`, so it does not count as an explicit reproduction. M7 and M8
found source-side mismatch/multiplicity patterns and explicitly declined to claim
measure impact.

The four synthesis failures are preserved provider responses, not transport
failures. M2, M4 and M9 exceeded the 500-character mechanism bound. M3 omitted
measure-connection citations from the outer assessment evidence list. Their raw
proposals were receipt-consistent uncertainty claims, but failed validation and
are not delivered assessments.

Compared descriptively with #223's differently composed nine-run calibration,
accepted outputs changed 6 -> 5, receipt-grounded outputs stayed 5, and intact
receipt-grounded outputs changed 3 -> 4. Calls changed 86 -> 97; reads changed
44 SQL / 0 DAX -> 25 SQL / 7 DAX. The current nine runs used one identical engine
and protocol; the older nine combined historical and new response contracts, so
this is not a controlled rate comparison.

Every proposal or accepted assessment preserved the central limitation: observed
adjustments, unit differences, fanout or repeated non-key signatures do not prove
incorrect business entries without the intended treatment and a validated
production path. Evaluator-only fixture construction likewise supplies no
authoritative adjustment exclusion/netting rule. Publisher truth was never planner
input.

## Integrity, cost and decision

All **106 investigation/synthesis tapes** load with verified file hashes; no body
was excluded. The nine append-only ledger rows retain every failure. Reference
token cost is **USD 6.069237**, including USD 0.495802 for synthesis, based on
1,367,805 input, 22,912 cached, 180,085 output and 128,805 reasoning tokens.
These are reference rates, not Azure billing; intake/cloud costs are excluded.

The feature worked mechanically: measure-path retrieval was selected consistently,
contribution tests were admitted without a forced order, and cause claims did not
escape without a measure connection. The reliability gate remains open because
no trial used the explicit reproduction purpose, four syntheses failed deterministic
validation, and only one run connected adjustment-linked populations directly to
the native measure. Do not freeze or publish a fresh variant from this result.

Next work should stay narrow: make synthesis output reliably satisfy the existing
concise-text and citation-subset contract, and improve generic planner selection of
`REPRODUCE_MEASURE` before another recorded batch. Do not add a dependency map,
domain branch, fixed query or relaxed intent gate.

See the machine-readable [review](runs/measure-path-nine-review.json), the
[measure-path implementation](measure-path-validation.md), and the earlier
[calibration](synthesis-calibration.md).
