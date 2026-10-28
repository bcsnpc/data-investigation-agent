# Quality of frozen v0.24 - Round 25

Measurement is in progress. The primary and secondary graders disagree materially on the history family, so the current primary score must not be presented as a clean quality pass. No investigator, prompt, model, caching or query change has been made.

The raw-reviewed headline for the 13 completed G1 tickets is **11/13** (95% Wilson 57.8?95.7%), with **2 harmful historical-question answers**. Official primary is 13/13 (77.2?100.0%); strict is 11/13 (57.8?95.7%). Both latency outcomes pass both graders. Raw review supports the second grader on both history disagreements; the history family is paused. Original grades and expectations remain unchanged.

| Completed G1 | Official primary | Strict | Raw-reviewed (headline) |
|---|---|---|---|
| Correct / graded | 13/13 | 11/13 | 11/13 |
| 95% Wilson | 77.2?100.0% | 57.8?95.7% | 57.8?95.7% |
| Harmful flags | 0 | 2 (either grader) | 2 confirmed |

R24's held-out disagreement was also checked from its saved raw capture, without a run or regrade. The second grader was right on cause: three successful zero-row record lookups established absence at source, Bronze and model, and the answer explicitly ruled out a pipeline drop. Both graders still marked the delivered `not found` verdict wrong against `as designed`. Thus its all-three zero and R24's official 18/20 remain unchanged. [Raw review and query receipts](runs/round-twenty-five-r24-held-disagreement-raw-review.json).

Agreement is 11/13 (95% Wilson 57.8?95.7%). Related variants share fixtures; these intervals describe the observed sample and do not establish accuracy on independent client estates.

| Cohort | Status |
|---|---|
| G1, unchanged v2 dev | 13/40 double-graded so far; remaining cases pending |
| G2, new held-out v4 - headline | Not started; native fact verification and sealing pending |
| G3, unchanged R22 text | Not started; lower priority |
| G4, prior R23 held-out v2 - regression | Not started; lower priority |

The independent writer produced 60 unsealed drafts, including 12 free-text inputs, six unchanged real screenshots and all three estates. New held-out wording remains unopened. A separate writer correction supplies the native comparison report omitted from one scaffold; the original draft is retained. Native target definitions, model partitions, source/landing numbers and producer definitions have been captured for independent oracle verification. No unverified scenario is sealed.

## Current failure pattern

Both history cases compare current source47 against landing/model41 and choose latency. They explicitly admit that no retained source history was read. The second grader correctly distinguishes that current-state observation from proving a historical edit. The primary treats the two verdict classes as interchangeable and passes both. Both explanations are preserved in [the per-ticket record](runs/round-twenty-five-g1-current-grades.json), with [raw-output review](runs/round-twenty-five-history-raw-review.json) and [saved-trace backtrack](failure-backtrack.md). This is an interpretation disagreement, not lost projection bytes or an altered expectation; no engine rerun or silent score override was made.

The native current-state numbers are supported. The unsupported step is presenting latency as the answer to the historical-change question. The answer footer also reports job details unavailable after the narrative has named a successful job window. These belong in the next-round fix list; the engine remains frozen here.

## Timing, costs and retained operational failures

The first9 uncontested cases used $3.898022 for investigation, averaging $0.433114 and26.1estate requests per ticket. Native Azure duration (startup and publication included) had median213.0s,p90299.0s. Complete per-class timing, cache and cost tables will follow the full measurement. Authoring, grading and controls are separate costs.

The billing control first stopped on a 5-second PostgreSQL budget lock before scoring. Its existing failed job was reconciled and the original pipeline hash restored. One open request was settled UNCERTAIN and remains charged. The normal billing bootstrap still returns its pre-existing2011 CREATE SCHEMA error; it was not repaired. Waiting completed and restored its original hash. The first history precheck timed out before mutation; its distinct continuation delivered both cases and restored the original360-row/source-schema hashes plus a successful real load. A billing boundary probe correctly rejected a fixture-policy connection; one replacement used the unchanged billing reader route. The first latency case failed on a PostgreSQL lock before delivery and preserved a partial capture; its source row/schedule were restored, and its one new-case replacement completed. Both latency cases are sealed, the owned source row and schedule were removed, and original row/schema hashes matched. No identity or permission was changed.
