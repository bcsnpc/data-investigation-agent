# Quality of frozen v0.24 ? Round 25

## Current measurement, 2026-10-31

The completed dev set is correct on **35/40** after raw review, with **two harmful history answers**. The new held-out set is still running: **12/18 graded so far**, with **no harmful finding among those 18**. This partial held-out cohort is not a 60-ticket accuracy result and is not comparable to a full independent-client sample. The source-history pause was lifted for measurement; those harms and later history results remain counted.

| Cohort | Official primary | Strict | Raw-reviewed headline | Raw 95% Wilson | Raw harmful |
|---|---:|---:|---:|---|---:|
|G1 full dev v2|37/40|34/40|35/40|73.9?94.5%|2|
|G2 new held-out v4 (in progress)|12/18|12/18|12/18|43.7?83.7%|0|

G3 (unchanged R22 messy60) and G4 (R23 held-out20 regression) remain not yet run. No claim is made against R22's14/40 dev +5/20 held-out or R23's6/20 until those comparisons are measured.

G1 grader agreement37/40; G2 current verdict/layer/cause agreement17/18. All G2 assessment disagreements are independently reviewed in fresh Claude calls. Two accidental operator exposures to held-out staging/status fragments are disclosed in decisions.md and the round summary; full operator blinding is not claimed. Neither engine nor expectations were tuned after them.

Current G2 classes: failed job6/6, source history2/3, waiting2/3, latency2/3, access0/3. The waiting zero is timing-confounded: the job completed during the third ticket and the independently reviewed answer correctly reported completion, while the sealed expectation still required waiting. Its zero is retained without changing the oracle. Access failures were one intake hold and two unresolved tool/time stops, not harmful findings.

Investigation-only native totals: G1 $16.526970 ($0.413174/ticket), cache67.49%, native median245s/p90317s with36/40 timing observations. G2 $9.595119 ($0.533062/ticket), cache71.04%, native median188s/p90259s with13/18 observations. Missing native times are not estimated. Grading, authoring, controls and release checks are separate from these ticket costs.

The frozen engine has not been repaired in this measurement round. Next-round priorities from saved-trace backtracks are historical-evidence reasoning, target/intake resolution, and bounded tool selection/handoff. Original tapes, expectations and official grades are unchanged. Details and every dimension are in [G1](runs/round-twenty-five-g1-current-grades.json) and [G2](runs/round25-g2-current-grades.json).

## Archived earlier checkpoints

# Quality of frozen v0.24 - Round 25

Current G1 final (40): **raw-reviewed35/40 (87.5%, Wilson73.9-94.5%)**, official37/40 (80.1-97.4%), strict34/40 (70.9-92.9%). **Two raw-confirmed harmful history answers remain counted.** Owner31Oct lifted the history measurement pause; all3G2history will be measured. G2-G4 assessment disagreements will be adjudicated by fresh independent Claude calls, not the exposed operator. G2 headline remains pending.

G1 investigation-only cost $16.526970 ($0.413174/ticket); native median245s,p90 317s (36observed/4unavailable); worker median207.7s,p90 285.3s (40observed); cache-read ratio67.49%. One lost start response was recovered from its original sealed answer without resubmission; its native execution details remain unknown.

## Earlier checkpoint: 31 graded G1 outcomes

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
| G2, new held-out v4 - headline |60 native-verified tickets sealed at c61a5c3e; prepared, not run |
| G3, unchanged R22 text |60 unchanged text inputs prepared; not run |
| G4, prior R23 held-out v2 - regression |20 unchanged sealed inputs prepared; not run |

The independent writer produced60 new tickets:48forms,12free text, six real screenshots and all three estates. Every oracle is native-fact verified and the set was sealed at commit c61a5c3e before any G2 execution; wording remains unopened by the engine developer. Original drafts and all pre-seal oracle versions survive. Wrong-page selections were preserved and independently reviewed. Fresh native fault checks remain required at execution. [Seal](runs/round-twenty-five-v4-seal.json).

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


October checkpoint: further investigation admissions defer because37 investigation requests remain against the unchanged40-request case bound. Remaining9G1 precede G2/G3/G4 in November; this is not a completed Round25 result. All250 owned model reservations (including31 engine case IDs) are settled, all injections are restored, and no local worker/grader remains active. AI account134.455715/146USD; SCAN2291/2500, INV9368/9405, REST45/95 with50restoration requests left; historical70kept. No cap or reserve was changed.
