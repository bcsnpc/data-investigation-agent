# R28 generic fixes — development branch

Branch `round-twenty-eight-fixes` starts at PR #436 head `ef9fde1769cba46d0be2d96f508ed1ad04c7c415`. Draft PR #437 contains these repairs. The official HealthNet test image, sealed tickets/answers, controls, results and grades are unchanged. There are no Anthropic calls, permission changes, injections, merge or tag in this task.

## Repairs

1. **Smaller prompts, full retained evidence.** Setup follows exact native bindings rather than expanding every model with a common owner. Intake receives selected or ranked candidate names; investigation receives their paths and dependencies. Native definition bodies become hash-pinned evidence references; `get_evidence` retrieves the original body without an estate read. Unknown references remain intact. The stored catalog and case retain the complete original evidence.
2. **Bounded delivery repair.** At most two delivery repair attempts are dispatched. Identical rejected drafts at one query frontier stop after three failures; at most six different rejected submissions are permitted there. Revised drafts can still pass the unchanged delivery validator without an unnecessary new data read. A no-tool response after rejection ends in an explicit unresolved handoff instead of another generation with the same evidence. Read-only checks, evidence IDs and target checks remain enforced.
3. **Named setup targets.** No figure-only expansion across the estate. Explicit targets win; report/page fallback contains at most three paths and records whether discovery was exhaustive. It never silently picks one of truncated candidates.
4. **Safe string functions.** SQL and DAX accept explicit safe string operations including `RIGHT`, `LEFT`, trimming, length and replacement. Arbitrary UDFs, external reads, execution, writes and DDL remain refused.
5. **Check form candidates first.** User-facing names are checked in the selected native report/page before asking. Two or three tied visual candidates can receive bounded native value probes; resolution requires every probe to succeed and exactly one precision match. Probe evidence persists into investigation. Explicit parent/target conflicts remain questions. HN-013's saved form still conflicts with its selected page; its offline replay remains `NEEDS_INPUT / VISUAL_OUTSIDE_PAGE`. No ticket-specific override was added.
6. **Discovery readiness.** `dia estate validate` now requires a hash-pinned discovery bundle. It fails on missing columns, native dependencies, exact source-to-named-SQL bindings, model-read receipts or the RLS route. Configuration shape alone cannot claim readiness. Validation itself performs no network reads. The recorded HealthNet metadata bundle passes: 1,828 assets, three models, 28 model-table bindings, zero gaps. This is metadata/read-receipt completeness, not a new data-quality claim.

## Qualified revision

Initial repair source `2ab99c8f35dca8fbff6fbd7f60a5751cc41aad63`:

- Full repository: **6,257 passed, 54 skipped**.
- Image shards: **8/8 passed**.
- [Qualification workflow](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45932901043).
- New development image: `ghcr.io/bcsnpc/data-investigation-agent/offline-worker@sha256:3c6d30b68b20df08d60d9d65d94699554e6c94e26142834c9048a11336c0344f`.

The persistent Azure worker template and frozen official test image were not updated. New executions use only a development execution override.

## Saved-trace proof and its limits

Attempted all 123 saved practice traces and all 18 saved, graded HealthNet traces with network connects forbidden. No new model decisions or query results were generated. Both PR #436 head and the repair source used the same replay harness.

| Replay result | PR #436 head | Final repair |
| --- | ---: | ---: |
| Complete | 72 | 69 |
| Missing saved boundary | 34 | 37 |
| Replay failure | 24 | 24 |
| No investigation case | 11 | 11 |

**65 traces complete on both revisions without any saved-reply reuse: 63 keep their replay classification and two change.** Four additional complete pairs keep their classification but require the harness to repeat the identical saved formatting reply twice; they are reported separately, not strict replay proof. The other 72 are not claimed as classification passes. Saved-response replay is not a fresh quality score or byte-exact tape replay. Missing saved reads, tool-phase divergence and pre-investigation holds are disclosed in the per-case report.

### Preliminary changes before the owner correctness audit

| Saved case | Baseline replay | Initial repair replay | Initial stop |
| --- | --- | --- | --- |
| Practice dev01 history-source-900201 | ANSWERED | UNRESOLVED | Delivery rejection without new reads |
| Practice dev02-advisory history-source-900201 | ANSWERED | UNRESOLVED | No new reads/tool call after rejection |
| HN-002 | BLOCKED | UNRESOLVED | No new reads/tool call after rejection |
| HN-024 | ANSWERED | UNRESOLVED | Target not a unique observed match; bounded rejection |

The table above is the **preliminary** `2ab99c8f` replay, not a final quality verdict. The owner requested an audit of all four changes before accepting them. All historical outputs and grades remain intact.

### Original correctness and delivery audit

| Case | Original saved status | Business output present | Original fully-correct grade |
| --- | --- | --- | --- |
| Practice dev01 history-source-900201 | ANSWERED | Yes | Primary no; reviewed no |
| Practice dev02-advisory history-source-900201 | ANSWERED | Yes | Primary no; reviewed no |
| HN-002 | BLOCKED | Yes, partial findings | Both graders no |
| HN-024 | ANSWERED | Yes | Primary **yes**; secondary and reviewer no (useful handoff) |

A delivered status does not imply a correct answer. HN-024 nevertheless triggered the owner's preservation condition because one grader marked it fully correct. The new same-query-frontier retry counter stopped after three **different** drafts, before the saved model's later corrected submission could deliver. This was caused by R28 fix 2, not catalog projection or a weakened validator.

Revision `72f7aacf` separates exact rejected-draft repeats from revisions. Three identical failures stop; six total rejected submissions at one query frontier stop; two model-only repair calls remain the maximum; a no-tool response after rejection still stops immediately. Corrected submissions still pass every existing evidence, target, harmful-claim and read-only check. No answer is automatically promoted merely because it was previously graded correct.

**HN-024's original saved decisions now replay to ANSWERED again**, with no generation or estate reads. Synthetic regressions prove that three different rejected drafts followed by a validated fourth draft deliver after a single native read, and that changing drafts cannot retry indefinitely. All 64 focused tests passed. The [audit JSON](../acceptance/round_twenty_eight_fixes/handoff-regression-audit.json) pins the original result and grade hashes. Revised qualification completed on `72f7aacff4b22590c0b875c093f5f0b7b7736d22`: **6,259 passed, 54 skipped, all eight image shards green**, [workflow](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45935671953). New image: `ghcr.io/bcsnpc/data-investigation-agent/offline-worker@sha256:f9c8fc524fd0e5f00b0855fc3caff2b2640c4aad90ed1a7c42c7fb5acee95457`.

The complete 141-case attempt was repeated offline on this correction. **65 strict comparable traces: 63 unchanged, two changed.** Both HN-024 and practice dev01 history deliver again. The remaining changes are practice dev02 history (`ANSWERED ? UNRESOLVED`) and HN-002 (`BLOCKED ? UNRESOLVED`), both stopping after a rejected delivery receives a no-tool response. Neither original was graded fully correct. There are four additional complete comparisons with repeated saved formatting replies, and 72 non-comparable attempts (37 missing boundaries, 24 failures, 11 without investigation cases). The current JSON/CSV report reflects this final correction; the preliminary report remains in git history at `d6e22fce`.

## Offline prompt sizes

Measured every comparable saved investigation/evaluator request with local `tiktoken` `o200k_base`. These are comparative token counts, **not Anthropic billing tokens**. They include calls that fetch full evidence; some grow.

| Calls | Median before | Median after | Total input reduction | Calls that grew |
| --- | ---: | ---: | ---: | ---: |
| Practice, 741 | 36,413 | 29,230 | 19.72% | 177 |
| HealthNet, 92 | 63,610.5 | 36,412.5 | 35.84% | 2 |

The captured first intake request also shrank substantially: HN-002 **44,809 ? 11,008** offline tokens (125,659 ? 25,820 characters), and HN-008 **44,868 ? 11,067** (125,745 ? 25,906 characters). Both sides use the same offline tokenizer after normalizing provider wire wrappers; these are not mixed-provider billing-token comparisons. The [intake packet counts](../acceptance/round_twenty_eight_fixes/live-intake-prompt-sizes.json) preserve the measurement.

The [per-call CSV](../acceptance/round_twenty_eight_fixes/prompt-sizes-per-call.csv) includes character and token counts. The [per-case replay report](../acceptance/round_twenty_eight_fixes/saved-replay-report.json) includes all attempted traces and limitations. No private model reasoning or expected answers is published.

## Free-model development check

Selected only already-run-and-graded baseline tickets: HN-001, HN-002, HN-003, HN-008, HN-011, HN-013, HN-024 and HN-026. HN-009 and every unrun or controlled ticket are excluded. All AI steps are pinned to OpenRouter `nvidia/nemotron-3.5-super-vl:free`; the development gateway has no Anthropic endpoint. These results are DEV-only and must not replace the frozen HealthNet scores.

Before each pair: disk floors, recorded discovery completeness, shared budget headroom and both SQL free allowances are checked. The forecast is at most 320 physical requests, with the existing 40-request per-case cap. There is no restoration request or allowance increase. OpenRouter's no-generation key/model checks returned 200; the reported free allocation is 1,000 calls/day, with the existing 20 requests/minute queue and concurrency two.

**Eight initial DEV outcomes: 0/8 fully correct, 0 useful handoffs (handoff quality 2), 0 harmful, from one independent Sol grader.** These are not reviewed official HealthNet scores. Seven runs returned UNRESOLVED; HN-013 returned NEEDS_INPUT. They used **217 physical requests**, **82 model calls**, and **$0 generation cost**. Full-evidence grading cost **$3.360152**, including two same-model completions of an omitted `verdict_match` field; every other original grader judgment was retained. No operator-supplied grade or expectation change was made.

| Ticket | Outcome | Fully correct | Useful handoff | Harmful | Grader's first wrong step | Physical requests |
| --- | --- | --- | --- | --- | --- | ---: |
| HN-001 | UNRESOLVED | No | No | No | Query validation | 36 |
| HN-002 | UNRESOLVED | No | No | No | Target | 40 |
| HN-003 | UNRESOLVED | No | No | No | Wrong conclusion | 24 |
| HN-008 | UNRESOLVED | No | No | No | Wrong conclusion | 32 |
| HN-011 | UNRESOLVED | No | No | No | Wrong conclusion | 31 |
| HN-013 | NEEDS_INPUT | No | No | No | Target | 0 |
| HN-024 | UNRESOLVED | No | No | No | Intake | 25 |
| HN-026 | UNRESOLVED | No | No | No | Query validation | 29 |

The [development results](../acceptance/round_twenty_eight_fixes/free-dev-results.json) pin each capture seal, execution/image, model and step costs. These measurements **do not demonstrate answer-quality improvement**. SuperVL left evidence-supported explanations unfinished, constructed rejected multi-statement queries and misidentified some targets. Smaller prompts and a bounded failure path do not solve those reasoning failures. HN-013's conflicting explicit form parents remain a legitimate code limitation; its sealed expectation stays unchanged.

HN-026 reached investigation on the revised image: two candidate paths, five admitted layers, four queries, 14 model calls, 29 physical requests; route/schema preparation took 71.0 seconds. It no longer exhausts a 40-endpoint fallback before reaching the model. It still failed to complete the answer.

Image disclosure: Five initial cases used source `2ab99c8f`; HN-013 and HN-024 also began on that qualified image after a local UTF-16 CI-log parsing error left the prior-image queue active. Their originals are retained. HN-026 uses qualified source `72f7aacf`, and one separate revised-image HN-024 development comparison will follow. There is no substitution in the official frozen test.


## Separate corrected-image check and final accounting

HN-024 was measured once more on the qualified corrected image, separately from the eight-case pass. It returned **UNRESOLVED**, used **27 physical requests and 14 SuperVL calls**, and cost **$0**. Its sealed capture and all 411 normal audit batches are hash-verified. This is a fresh weaker-model development result, not the saved Opus replay: the saved replay preserves the original ANSWERED delivery, while the fresh SuperVL run still fails to finish the answer.

This additional run is **ungraded**, not counted as correct or harmless. Its complete original grading projection is 1,087,109 bytes. The local grading-only packet bound was increased from 1,000,000 to 4,000,000 characters without changing the engine/image or omitting evidence. A budgeted Terra grade was then refused **before generation or reservation**: native input count 316,381 plus 4,096 reservation margin exceeds the client's configured **272,000-token pricing/context bound**, `DOCUMENTED_RATE_CONTEXT_BOUND_EXCEEDED`. The larger-model forecast also exceeded the remaining internal OpenAI allowance. No limit was relaxed, evidence dropped or operator judgment substituted. The initial 4,000-output-token forecast was unfunded; a smaller 1,800-output-token reservation fit but still met the provider bound. Both unsent forecasts and token-count evidence are retained locally.

Totals for this task: **244 physical requests, 96 free-model calls, $0 SuperVL generation, $3.360152 OpenAI grading**. Anthropic committed spend is unchanged at **$237.326068**; its protected $8 was not used. OpenAI has **$0.651532 remaining under its existing internal allowance**, with no budget increase. There are **zero open reservations**. Monthly physical use is **20,213/20,500**: investigation 17,701/17,905, SCAN 2,430/2,500, restoration 82/95. This task used **zero restoration requests**. Disk remaining: C: 68.91 GiB, D: 182.45 GiB, above both standing floors.

All nine development executions have terminal Azure readbacks and sealed outcomes. Their Azure failure status reflects undelivered/unresolved answers; it is not reclassified as an environmental failure. Only the initial HN-002 quota-observation failure (zero AI/native reads) and the two local capture-prefix rejections are retained separately as setup failures, with originals preserved. The existing approved OpenRouter daily quota observation was recorded; no allowance was raised.

PR #436 head remains `ef9fde1769cba46d0be2d96f508ed1ad04c7c415`. The frozen image, sealed tickets/answers, estate config and remaining controls are unchanged. No permissions, identities, secrets, persistent Azure job settings or estate data changed. No new admissions remain. Draft PR #437 stays unmerged and untagged.

The final readiness-only correction also requires the RLS receipt identity to equal the model-read receipt identity. A mismatched-reader regression is tested, and the recorded 1,828-asset bundle still validates offline with zero gaps/network calls. It does not change prompts, investigator decisions or any live test result; final full-suite/image-shard qualification is recorded below.

Final source `3ee682aee907093cf3f49452d8d9cf683aecd7a3`: **6259 passed, 54 skipped, all eight image shards green**, [qualification run](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45938483031). This final readiness-only image was tested offline and was not deployed. The live investigator image remains the qualified `72f7aacf` image described above.
