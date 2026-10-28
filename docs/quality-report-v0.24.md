# Quality of frozen v0.24 - Round 25

Measurement is in progress. The primary and secondary graders disagree materially on the history family, so the current primary score must not be presented as a clean quality pass. No investigator, prompt, model, caching or query change has been made.

The raw-reviewed headline for the 31 double-graded G1 tickets is **26/31** (95% Wilson 67.4-92.9%), with **2 harmful historical-question answers**. Official primary is 28/31 (75.1-96.7%); strict is 25/31 (63.7-90.8%). Raw review supports the second grader on both history disagreements; the history family is paused. Original grades and expectations remain unchanged.

| Completed G1 | Official primary | Strict | Raw-reviewed (headline) |
|---|---|---|---|
| Correct / graded | 28/31 | 25/31 | 26/31 |
| 95% Wilson | 75.1-96.7% | 63.7-90.8% | 67.4-92.9% |
| Harmful flags | 0 | 2 (either grader) | 2 confirmed |

R24's held-out official score remains18/20. Retrospective raw review finds the secondary right on the absent-record cause, and both graders overly strict on its verdict label under the existing substance-based contract. The earlier raw review is preserved with a dated correction; no ticket, expectation, official score, engine run or provider grade was changed. [Saved-capture review](runs/round-twenty-five-r24-held-disagreement-raw-review.json).

Agreement is 28/31 (95% Wilson 75.1-96.7%). Related variants share fixtures; these intervals describe the observed sample and do not establish accuracy on independent client estates.

| Cohort | Status |
|---|---|
| G1, unchanged v2 dev | 31/40 double-graded so far; remaining cases pending |
| G2, new held-out v4 - headline | Not started; native fact verification and sealing pending |
| G3, unchanged R22 text | Not started; lower priority |
| G4, prior R23 held-out v2 - regression | Not started; lower priority |

The independent writer produced 60 unsealed drafts, including 12 free-text inputs, six unchanged real screenshots and all three estates. New held-out wording remains unopened. A separate writer correction supplies the native comparison report omitted from one scaffold; the original draft is retained. Native target definitions, model partitions, source/landing numbers and producer definitions have been captured for independent oracle verification. No unverified scenario is sealed.

| Class (G1 interim) | Official primary (95% CI) | Strict (95% CI) | Raw-reviewed (95% CI) |
|---|---|---|---|
|v2-access-export|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-application-baseline|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-before-temporal-retention|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|v2-billing-invoices|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-billing-mrr|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-failed-application-load|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-failed-billing-transform|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-fixture-quantity|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-latency-record|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-other-collected-definition|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|v2-record-absent-everywhere|2/2 (34.2-100.0%)|1/2 (9.5-90.5%)|2/2 (34.2-100.0%)|
|v2-record-repeated-gold|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-source-history|2/2 (34.2-100.0%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|v2-stale-model|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-waiting-application-load|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-warehouse-scope|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|

The warehouse-scope-v2 benchmark zero is an authored report-ID contract finding; it remains in the unchanged denominator and is not demonstrated engine scope-comparison failure. See the native catalog/hash audit.

## Current failure pattern

Both history cases compare current source47 against landing/model41 and choose latency. They explicitly admit that no retained source history was read. The second grader correctly distinguishes that current-state observation from proving a historical edit. The primary treats the two verdict classes as interchangeable and passes both. Both explanations are preserved in [the per-ticket record](runs/round-twenty-five-g1-current-grades.json), with [raw-output review](runs/round-twenty-five-history-raw-review.json) and [saved-trace backtrack](failure-backtrack.md). This is an interpretation disagreement, not lost projection bytes or an altered expectation; no engine rerun or silent score override was made.

The native current-state numbers are supported. The unsupported step is presenting latency as the answer to the historical-change question. The answer footer also reports job details unavailable after the narrative has named a successful job window. These belong in the next-round fix list; the engine remains frozen here.

The two pre-retention cases are different: current16 was readable at all compared layers, but attempts to read an unavailable audit object replaced the necessary source-history check. They exhausted the tool/time limit without a retention-boundary answer. Raw review supports the secondary grader on the first bad query and the incomplete handoff. The five current raw zeros therefore comprise four engine failures and one input-contract finding; all benchmark scores remain unchanged. [Backtrack index and three walkthroughs](failure-backtrack.md).

## Timing, costs and retained operational failures

The 31 double-graded cases used **$13.325343** for investigation, averaging **$0.429850** per ticket. Native Azure duration, including startup and publication, had median227.5s and p90299s (nearest rank) for the 28/31 executions with native start/end times. Missing native end times are not estimated. Provider-settled cached input was4,794,667 of7,111,716 input tokens: **67.42%**. Every case cost matched its authoritative reservation settlements. Authoring, grading and fixture controls are separate. [Per-ticket observed costs, timing and cache](runs/round-twenty-five-g1-observed-cost-timing-cache.json).

| Timing group | Tickets | Native durations observed | Native median / p90 seconds | Worker wall median / p90 seconds |
|---|---:|---:|---|---|
|full investigation|25|25|236.0 / 299.0|193.64776847400003 / 270.064544503|
|hold|3|0|not available|226.12211136400003 / 234.758102028|
|operational status without layer queries|3|3|188.0 / 190.0|154.97200069000002 / 159.73575022|

The billing control first stopped on a 5-second PostgreSQL budget lock before scoring. Its existing failed job was reconciled and the original pipeline hash restored. One open request was settled UNCERTAIN and remains charged. The normal billing bootstrap still returns its pre-existing2011 CREATE SCHEMA error; it was not repaired. Waiting completed and restored its original hash. The first history precheck timed out before mutation; its distinct continuation delivered both cases and restored the original360-row/source-schema hashes plus a successful real load. A billing boundary probe correctly rejected a fixture-policy connection; one replacement used the unchanged billing reader route. The first latency case failed on a PostgreSQL lock before delivery and preserved a partial capture; its source row/schedule were restored, and its one new-case replacement completed. Both latency cases are sealed, the owned source row and schedule were removed, and original row/schema hashes matched. No identity or permission was changed.
