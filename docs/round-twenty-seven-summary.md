# Round 27: redesign, proof attempts and close

> Latest owner steer, November 25 / execution November 26: the additional $10 reopens the funded gate sequence before merge. PR #435 is still open and untagged. Conservative $56 cash covers the unchanged $37.568245 confirmation forecast plus $14.34 calibration and $3 reserve. Static Batch pricing was already included. Evaluator evidence-prefix caching is being qualified; no new Opus call has been admitted. The earlier close-only funding result below is historical and will be superseded by the completed gate report. V5 remains sealed until the December 1 balance and prerequisite gates are confirmed.

**The quality gate was not established.** Paid pass 2 finished at 26/48 reviewed correct, 14 useful handoffs and 5 harmful answers. Paid pass 3 stopped after 21 of 39 required outcomes: 14 correct, 1 useful handoff and 1 harmful answer. Its guard was 11/13 measured, with all 20 required. Confirmation, fresh calibration and held-out v5 did not run. V5 remains sealed.

The owner direction dated 2026-11-25 explicitly authorizes closure when the whole-run funding gate cannot be met. This is an engineering release without a passed quality benchmark. No earlier outcome, expectation or grade was changed.

| Cohort | Reviewed correct | Useful handoff | Harmful | Qualification |
|---|---:|---:|---:|---|
| Paid pass 1 | 5/50 | 20 | 1 | Official/strict 4/50; reviewed 5/50 |
| Paid pass 2 | 26/48 | 14 | 5 | Guard 17/20; FAIL |
| Paid pass 3, partial | 14/21 | 1 | 1 | 39 required; guard 11/13 measured of 20; NOT PASSED |
| Kimi proof | 8 | 5 | 0 | 13 measured; 2 environment-unscored; not a gate |
| Original SuperVL pass | 14 | 13 | 1 | 30 measured of 32; 2 other incorrect; not a gate |
| Native-reference repair | 1 | 3 | 0 | Four distinct replacements; not a gate |

These repeated cohorts are never pooled into one accuracy number. Replacements do not overwrite original harms. The dropped failed-job evidence bug was fixed and its distinct free rerun graded correct. R17-05 still lacks the semantic-rule explanation. Other proof, screenshot and repair cohorts remain separately reported in the [quality report](quality-report-v0.27.md) and the retained per-pass reports.

## Funding and cost cuts

System and investigation-tool caching was already active. Helper calls now mark their own actual tool schema for caching, under the existing cache switch. Saved Opus cache-read shares were 68.6627% for investigation, 55.0831% for intake and 2.0583% for evaluator calls.

Static-only Anthropic Batch transport is prepared with durable owned IDs, reservations before submission, no retry after an unknown POST, bounded result retrieval and 50% rate cards. Fault tickets stay on the normal transport. No live Batch saving is claimed.

The whole 25-ticket confirmation forecast is $37.568245. With $14.34 protected for calibration and the $3 reserve, $54.908245 is needed against the conservative owner cash estimate of $46: a shortfall of $8.908245. The optimistic saved-hit Batch estimate is $18.008947. It is not the admission estimate because the five-minute cache may expire between asynchronous tool-dependent Batch waves. Calibration's protected amount comes from 14 saved nonzero cases at a mean $1.102982, multiplied by ten cases and the 1.3 margin, then rounded up. No fresh calibration usage exists.

The exact Console balance was unavailable: organization usage GET returned 401 with the workspace key, which is not an Admin API key. The lower owner estimate was used, without claiming an exact API balance. No partial confirmation, calibration or v5 was admitted; no December grant was assumed. Round 28 must first confirm available credit and fund the complete prerequisite gates. V5 remains conditional on those gates.

The approved $25 top-up gives a conservative November Anthropic ceiling of $245.108251, preserving $202.108251 charged and $43 headroom; the $3 cash reserve is excluded. At closure, the round's shared-ledger spend deltas were Anthropic $150.388408, OpenAI $16.954951 and Bedrock $0.409536. Free OpenRouter/NVIDIA cost $0. These figures include charged uncertainty and are not provider invoices. No paid generation was made in this closure task. OpenAI is grading-only, with the November 29 expiry and $2 reserve; paid OpenRouter remains blocked and auto-reload stays off.

## Simplification and compatibility

Registered feature flags went from 64 to 3. The evaluator's measured advisory, slim and enabled switches remain; 61 proven fixes are unconditional. Historical default-true specs are accepted as no-ops, while retired off-mode ablations are explicitly refused. Historical baseline-only tests are preserved as source fixtures; current behavior and safety tests remain executable.

Physical executable source lines, including comments and blanks: engine 68,705 to 68,804; tracked harness 21,767 to 21,765; tests 71,591 to 71,572. The prepared Batch and two-model-default modules account for the net engine increase. Active free defaults are SuperVL primary and Kimi backup. Old model test records remain.

All 123 saved `(status, after)` classifications match qualified c7a06c1f: 85 finished, 29 historical negative/incomplete traces and 9 without an investigation case. This is not 123 successful exact replays. Compatibility replay made zero estate or model calls. The [templating audit](templating-audit.md) indexes 4,594 source locations and makes no runtime change.

Two unused generators totaling 5,274 bytes were hash-verified into a committed source archive. Tool policy rejected their deletion, so both originals remain. The owner cleanup script is recorded. No evidence, ledger, seal, RESUME, current worktree or pinned image was deleted. C: had 68.370 GiB free and D: 183.283 GiB, above the 40/80 GiB guards; no freed-space claim is made.

## Fixture and skipped cases

The two stale-refresh cases were skipped because browser control was unavailable. Original uncertain Azure start `f238f1ba-1142-4b55-bdc1-958c61911343` remains unscored and was never resubmitted. No new injection or toggle was made.

Fresh read-only checks confirmed the original 360-row source and schema hashes and model value 7,661. The latest retained native refresh was Completed; all inspected saved control restoration flags were false. Temporal history stays ON by prior decision. Automatic updates were last owner-reported ON; current UI readback was unavailable and is explicitly an owner action. Close verification used four physical requests and zero models. The toggle history and hash receipts are in [injections.md](../tests/tickets/injections.md) and [the restoration record](round-twenty-seven-close-restoration.json).

## Release validation

The original close image, source e1f98b30, passed 6,157 tests (53 skipped) and all eight image shards. Three corrected-input daily checks on that image all ended Azure Succeeded and delivered the expected 7,661-to-8,765 transformation finding, but all three daily checks remained FAIL. The frozen native checker requires a one-column aggregate; the model returned SUM and COUNT together. December's budget readiness was also unconfirmed. These are not three green smokes. Original failures and captures are retained, and no expectation was changed.

A final money-safety correction restricts OpenAI to grading only, as the latest owner direction requires. Earlier close profiles already used free OpenRouter, so no unauthorized paid call occurred. A stale smoke-purpose test was corrected to assert refusal. The final qualification, final-image daily checks and exact merge validation are recorded below when complete; this remains an engineering release without a passed quality gate.
