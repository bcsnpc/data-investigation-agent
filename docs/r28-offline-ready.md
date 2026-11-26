# R28 offline repairs prepared during the SQL wait

2026-11-26. Offline code and saved evidence only: **zero estate reads and zero model calls**. No official outcome, grade, expectation, sealed input or confirmation runner was changed. PR #435 remains draft; no merge or tag.

## Original confirmation stays first

Original source `6731ead4aa64c0c34980f97dd38df75b1167ce26`, image `sha256:a0e477319eb41c4202bfc45cf62496627646dde5c9f597c1ea5ab3f24b414eeb`, remains frozen. The original result remains 21/25 saved; full gate PENDING. The four outstanding latency, waiting and two access tickets must run on it before any repaired live image.

## Repairs and the exact checks

- Static visuals: complete literal text boxes with no data binding are annotations, even if their text includes a date or number. Exclude before the numeric candidate limit/exhaustiveness calculation; keep a hash-pinned exclusion proof. Missing/dynamic definitions and explicit text-box selections remain protected. Saved R17-05 shrinks from five candidates to three measured cards.
- Source comparisons: `SOURCE_SYSTEM` requires a cited, successful, untruncated application data read. Metadata, unrelated source objects and Fabric warehouse reads do not count. Reuse exact admitted native routes even when optional SOR metadata is absent. A checked UNRESOLVED source handoff stays possible. The two saved billing calculation tickets actually declare `NOTHING`, not a source comparison: their useful-handoff grades do not improve merely because this rule was added.
- Delivery: remove the blanket unselected-target prohibition for a calculation-only, no-value question when all listed alternatives have cited reads; a bounded inventory can explain an exact admitted measure only with its retained native definition and cited measure read. Never claim the unmeasured visuals were exhausted or select one. R17-10 had 32 total candidates, not just the five listed: that incompleteness remains recorded.
- A missing selected-target field can be filled only from the engine's exhaustive, unique, cited native value match. A different non-null selection still fails. Recheck candidate coverage after evaluator repair as well as before it.
- `FAILED_QUERY_DOES_NOT_SUPPORT_TECHNICAL_FINDING`: a failed attempt may remain as attempt history only if an exact same-layer/text/parameters/assets successful retry is also cited. It supplies no successful native result of its own. This removes R17-05's timeout-then-success obstruction.
- `CHECK_TARGET_CANDIDATES_BEFORE_CONCLUSION`: permit a checked UNRESOLVED handoff without claiming a selected target; do not require impossible exhaustive reads to report the precise missing fact. The ordinary evidence, conclusion and evaluator checks still apply.
- `UNRESOLVED_REQUIRES_NOT_FOUND_DETAIL`: normalize observed-value/definition detail to `not found` only when the question disposition is already UNRESOLVED. Preserve facts, limitations, original draft and a recorded reformat. This fixes the older-export handoff's structural label; it does not invent the earliest history time.
- Smoke: accept one native row containing sum plus count only when the expectation explicitly declares the result column. Match that exact column; a matching count cannot substitute for the sum. Existing single-column expectations still work.

## Evaluator cache diagnosis

The saved 21-case telemetry has 22 evaluator calls, 772,579 input tokens, 11,683 cache reads (1.5122%) and 624,480 cache-write tokens. This is the exact observed figure behind the approximate 3% report. Almost every ticket had only one evaluator call. The old cached block included the ticket and the whole cited map: each new ticket, query ID/time or growing result map invalidated that large prefix. Five-minute expiry and asynchronous Batch queue delays also limit reuse.

The new request puts only the CURRENT cited retained definitions before the evidence breakpoint, ordered canonically; ticket, draft, changing native results and formatting feedback follow it. Definitions occur once, rather than being duplicated in uncached content. Tools/system remain cacheable across tickets, and the retained-definition prefix now stays byte-identical across tickets using the same definitions and across changing native reads. Removed evidence is removed from both blocks. TTL and pricing remain unchanged. Offline tests prove placement, stability, exact evidence reconstruction and native usage logging; **no improved live cache percentage is claimed**. Cold calls or Batch delays beyond five minutes can still miss. Measure the real ratio on the later repaired-image proof.

## Saved confirmation replay

All 21 locally saved confirmation results were checked: 20 have investigation cases, one stopped at intake. The replay recompiles all 124 saved native queries against current read-only code and requires identical executed query, parameters and asset bindings before returning a saved result. No previously successful query is newly refused. It exercises all 29 saved submit-finding drafts through reference repair, candidate coverage, conclusion and grounded-finding validators. Derived candidate evidence receives new IDs; original captures and source files are not edited.

This is a boundary counterfactual, not a generated continuation, new live run, or new independent grade. Twenty cases now have at least one code-eligible saved draft. R17-05 and R17-10 now have supported answer drafts; R17-08 and the older export can deliver checked unresolved handoffs. The latter two have not thereby become correct answers. The warehouse-scope-v2 admission typo is covered by the previously qualified exact-parent repair but has no saved investigation to replay. A changed draft still needs its own fresh exact-question evaluator check on the later proof; a saved review of a different final handoff is not reused as approval.

| Saved ticket | Original status | Code-eligible saved draft |
|---|---|---|
| form-v2-application-baseline-v1 | ANSWERED | yes |
| form-v2-application-baseline-v2 | ANSWERED | yes |
| form-v2-billing-invoices-v2 | ANSWERED | yes |
| form-v2-billing-mrr-v1 | ANSWERED | yes |
| form-v2-failed-application-load-v1 | ANSWERED | yes |
| form-v2-failed-billing-transform-v1 | ANSWERED | yes |
| form-v2-fixture-quantity-v1 | ANSWERED | yes |
| form-v2-other-collected-definition-v2 | ANSWERED | yes |
| form-v2-record-absent-everywhere-v1 | ANSWERED | yes |
| form-v2-record-repeated-gold-v2 | ANSWERED | yes |
| form-v2-screenshot-record-01-v1 | ANSWERED | yes |
| form-v2-screenshot-record-02-v1 | ANSWERED | yes |
| form-v2-screenshot-record-03-v1 | ANSWERED | yes |
| form-v2-screenshot-record-04-v1 | ANSWERED | yes |
| form-v2-source-history-v2 | ANSWERED | yes |
| form-v2-warehouse-scope-v1 | ANSWERED | yes |
| form-v2-warehouse-scope-v2 | NEEDS_INPUT | no saved investigation |
| text-older-export-movement-1-v2-preflight-repair1 | UNRESOLVED | yes |
| text-R17-05-v1-preflight-repair1 | UNRESOLVED | yes |
| text-R17-08-v1 | UNRESOLVED | yes |
| text-R17-10-v1 | UNRESOLVED | yes |

The ordered 123-case replay completed: baseline **85 completed / 29 negative / 9 without an investigation case** becomes **86 completed / 28 negative / 9 without a case**. **120 classifications are unchanged**, two saved continuations now complete, and one previously completed trace stops at the new mandatory source-coverage check. Therefore I cannot claim all 123 classifications are identical.

| Changed saved trace | Before | After | Reason |
|---|---|---|---|
| dev01 / screenshot-record-04-v1 | replay failure | completed UNRESOLVED | Conservative delivery-detail normalization enables the saved handoff. |
| dev01 / text-R17-11-v1 | replay failure | completed ANSWERED | Exact successful retry can support the answer while the failed attempt remains history. |
| dev02-advisory / fixture-quantity-v1 | completed ANSWERED | new source-check refusal | This source-comparison trace never read the application source. Returning its old answer would violate the new owner rule. No saved response exists for the newly required step; no continuation was fabricated. |

All nine no-case classifications remain unchanged. No previously successful saved native query is newly refused by the compiler. The one tightened delivery is intentional source coverage; this is not a newly measured harmful or correct count. Full per-case comparison: `docs/r28-saved-classification-comparison.json`.

## December 1 sequence

1. After SQL renews, first restore the downstream original 360 rows; hash-check the source and original pipeline, verify model value 7,661, and confirm no temporary control remains. Retain temporal history. Never enable paid SQL continuation.
2. Check December budgets and valid grading funding, then finish only the four unadmitted original confirmation tickets on frozen image a0e47731, preserving the 21 originals. Grade independently and report the whole gate; do not start the repaired image first.
3. Qualify the repaired image on SuperVL for failed confirmation tickets, with its existing synthetic-data and budget rules. Then rerun only those failures on Opus once, if whole-step funding fits. Preserve original outcomes and report replacements separately.
4. Calibration follows only if the gate and confirmed Anthropic cash plus independent grading funding permit it; keep the $3 reserve. Never run partial calibration or v5. v5 stays sealed until its own whole-run gate/funding check.
5. Owner actions: OpenAI grading credit expires 2026-11-29; December grading needs a top-up/valid owner-approved funding. Confirm the exact December 1 Anthropic balance before further paid admission.

## Qualification and review state

Corrected implementation source: `c544d70d769203cf7fd9987d42c6f12d8c685770`. Full clean-checkout repository suite: **6206 passed, 53 skipped, zero failures/errors**. All **8/8 network-disabled image shards passed**, and 130 focused tests passed locally. Workflow [45869021667](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45869021667) published only the tested immutable commit image:

`ghcr.io/bcsnpc/data-investigation-agent/offline-worker@sha256:65aacf992ef4a57e3f6f66fa28c68beb9ecf2a0ad4c2a35fa1b8bbc6a6e4bf70`

It has **not been deployed or admitted for live proof**. The original a0e47731 confirmation image and all 248 files in its archived checkpoint remain byte-identical. No original grade, expected answer, tape, allowance or ledger counter changed. No merge or tag was performed.

The earlier qualification of b03f7874 was superseded when CI caught diagnostic-precedence and adapter-boundary issues; both were corrected in source c544d70d without changing the pre-existing tests or expectations. Final qualification uses c544d70d. The redundant local full-suite runs were stopped; the complete clean-checkout hosted suite above is the full-suite result.

Verification receipts: `docs/r28-offline-qualification.json`, `docs/r28-offline-confirmation-replay.json`, `docs/r28-saved-classification-comparison.json`, and `docs/r28-confirmation-immutability.json`. The full tool-schema check independently agrees with all 20 code-eligible saved cases. Changed drafts still require fresh exact-question evaluation; no repaired live score or improved live cache ratio is claimed.

The prepared smoke configuration format for multi-column results is `reads: {asset_id: {column: "units", value: 8765}}` (using the actual declared result column for that surface). Apply it to the smoke's own configuration at the later authorised live step; do not edit the frozen confirmation runner to add it.
