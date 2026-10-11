# Round Ten C — current intake dry-run stop

Updated 2026-10-08 UTC. PR #423 remains draft. This is a failed and incomplete current-prompt intake evaluation, not a live investigation or an enlarged acceptance claim.

## Result and stop

The first 32 of 59 intake records completed. Fourteen match every authored structured field: 14/32 completed (43.75%), or 14/50 of the required fifty (28%) when uncompleted cases remain in the denominator. Seven of the fourteen matches are qualified semantic holds, not admitted investigations. Eighteen completed records miss at least one field. Seventeen records are PROPOSED and fifteen HELD; these statuses alone are not correctness grades.

The next case, `question-hiding-rows`, was refused by the governor before a provider call: `investigator.usage_governance.UsageHold: Daily usage limit`. Its sealed tape retains the refusal and FINAL with null result; it was not fabricated into an intake response. Twenty-six other original cases and all nine rebuilt-estate cases were not started. Both required nine-family resolution columns are therefore **unattempted**, not nine observed refusals each. The dry gate is FAILED/INCOMPLETE; section 5 live runs, the rehearsal and billing were not attempted. Even matching all remaining eighteen fifty-suite cases would reach only 32/50 (64%), below the required 90%.

## Work performed and remaining defects

The zero-read section 1 audit is in [the verbatim audit](round-ten-c-intake-audit.md): 29 preserved attempts, consisting of 19 mandatory-name refusals, seven mixed-business refusals, two precision clarifications and one starting-measure clarification. The six visual-variety attempts did not all fail at intake: three reproduced their figure but missed the sealed outcome, one address failed intake, and two reached an outcome without reproduction.

The committed implementation resolves an unnamed target when retained report/measure and supported cell constraints leave exactly one candidate. It records RESOLVED and the match basis; multiple candidates refuse TARGET_AMBIGUOUS, zero refuse TARGET_UNRESOLVED. No value read, default, position or data-bearing candidate selection is used. Mixed technical asks retain their technical route and an engine-rendered decline of business meaning; sole business-rule asks retain the refusal. Synthetic unique/multiple/zero, mixed/sole and sealed wrong-cell tests pass. **These limited tests did not establish the broader rule: the dry run exposed an unsafe admission.**

### Secondary comparison treated as the primary referent

`family-D-noisy` states: “I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.” The admitted record retains North as a REQUESTED selection (span 228–233), yet takes “global value” (span 269–281) as its UNGROUPED mode source and chooses Inventory Health [25189fcc]. Its own basis states `selection_in_inventory` is absent. `family-D-typo` makes the same class of admission. This is not proof that the primary requested cell was uniquely resolved: a comparison reference was used to narrow the primary referent. It is a release blocker, preserved without a mid-batch patch. The existing named-card wrong-cell regression did not cover this primary-versus-comparison relationship.

The neutral visual inventory exposes names, report/measure bindings, grouping columns and unsupported status. The present resolver does not receive a declared selection-to-visual match or a declared figure in that inventory. It explicitly records those absences. Several retained report/measure scopes therefore have multiple candidates. This is a remaining context-matching gap, not authority to choose a card or a matrix default merely to meet nine resolved families. The fresh model additionally returns unresolved rather than ambiguous on several typo variants because its quoted visual constraint matches no retained name. Exact reasons and candidates remain in each saved response.

### Every completed miss

| Case(s) | Observed difference from the pre-call golden | Assessment |
| --- | --- | --- |
| B-noisy, B-terse, B-typo | Correct target and METRIC_COMPONENTS, but BUSINESS_QUESTION/NONE rather than MISMATCH_COMPLAINT/VERTICAL | Full-record mismatch. A definition question can plausibly be framed this way; the golden's stricter shape is not retroactively changed or described as proven semantic truth. |
| C-noisy | Correct target, BUSINESS_QUESTION/NONE and METRIC_COMPONENTS rather than the golden mismatch/vertical and DERIVED_CALCULATION | Shape/mode and question-kind mismatch. |
| C-terse, C-typo | Correct target and DERIVED_CALCULATION; BUSINESS_QUESTION/NONE rather than mismatch/vertical | Shape/mode mismatch; admitted does not mean full-record match. |
| D-noisy, D-typo | Admitted the ungrouped card using the comparison's global reference; FILTER_EFFECT rather than VISUAL_CONTENT | Unsafe primary-referent admission described above. Golden ambiguous hold unchanged. |
| D-terse | TARGET_UNRESOLVED/FILTER_EFFECT rather than TARGET_AMBIGUOUS/VISUAL_CONTENT | Refusal reason and nomination mismatch; no successful record to score. |
| E-mention | Correct card and FRESHNESS; BUSINESS_QUESTION/NONE rather than mismatch/vertical | Shape/mode mismatch; not a latency execution or outcome. |
| E-typo | TARGET_UNRESOLVED rather than TARGET_AMBIGUOUS; FRESHNESS nomination agrees | The supplied visual constraint produced zero name matches instead of preserving the eligible ambiguity. |
| G-mention | Correct card and SOURCE_CORRECTNESS; BUSINESS_QUESTION/NONE rather than mismatch/vertical | Shape/mode mismatch. |
| G-typo | TARGET_UNRESOLVED rather than TARGET_AMBIGUOUS; SOURCE_CORRECTNESS nomination agrees | Same zero-name-match refusal class as E-typo. |
| H-noisy | Ambiguous hold, but DERIVED_CALCULATION rather than METRIC_COMPONENTS | Retained nomination mismatch; technical ask was retried, not refused wholesale as meaning. |
| H-terse | Ambiguous hold, but FIGURE_DIFFERENCE rather than METRIC_COMPONENTS | Retained nomination mismatch; technical ask was retried. |
| I-noisy, I-typo | Ambiguous hold, but TRANSFORMATION_MECHANISM rather than SOURCE_CORRECTNESS | Retained nomination mismatch. |
| I-terse | Ambiguous hold, but EXPECTED_BEHAVIOR rather than SOURCE_CORRECTNESS | Retained nomination mismatch. |

H-typo matches the golden ambiguous hold and METRIC_COMPONENTS nomination after its one retry. None of these holds earns the separately required nine-family resolution criterion. No per-ticket patch, old outcome-expectation edit or replacement run was used. Wire-valid nomination differences cannot all be rejected by shape validation alone; any stricter semantic rule still needs a defensible contract, rather than a list of ticket-specific corrections.

## CI blind spot and validation

Historical 72/72 consists of sealed producer replay (15 archived + 15 inferred + 42 earned records). It does not invoke the new intake prompt and cannot establish current model quality. It remains the historical result, not a new result from this checkpoint.

The new `current-intake-evaluation` CI job invokes the real current prompt/validator over all 59 sealed texts, with no data transport and no saved-response fallback; it enforces the 90% fifty full-record threshold and nine resolved families. The hosted job is prepared, not green: the new model-provider Actions-secret location is awaiting the explicit decision already requested. Only aggregate scores/plan metadata are configured for artifact upload, not provider bodies. It also cannot be green while the current quality gate fails. PR #423 stays draft.

Dated post-push finding, 2026-10-08 07:30 UTC: the [hosted current-intake job](https://github.com/bcsnpc/data-investigation-agent/actions/runs/37743831192/job/113200521009) ran and failed before any provider request. Both provider environment values were empty. Exact error: `RuntimeError: Model provider authentication and endpoint are required; no cached-response fallback.` The separate push-triggered job refused the same way. Score/plan artifacts were retained; no credential was installed, no model call or estate read occurred in these jobs, and no cached response was substituted. This is a tested configuration blocker, not a hosted quality score.

The committed-engine regression log reports **2,389 tests, OK**; focused intake, wrong-cell, model-evaluation and changed consumer tests also passed. The preserved first dirty-tree regression failed on uncommitted-engine replay fencing and stale target builders; it was not erased. The passing committed run is the relevant regression result. It does not replace the failed dry model check.

Golden expectations were written before the new provider responses. They can count an honest ambiguous HOLD as a full-record match; the independent nine-resolved requirement was not relaxed to match those holds. Original ticket texts, sealed outcomes, tapes, ledger rows and fixture states remain unchanged.

Context-cost measurement, before/after on the same sealed input: six models, 39 measures, 97 columns, 52 visual entries and zero SQL-object entries on both sides. Pre-wire payload characters 36,815→36,815; instructions 7,732→8,291; schema 6,261→6,289. Coverage did not fall. The governor's reserved input-character amount is recorded separately below; it is not a token count.

## Usage and evidence

| Measure | Before | After / batch |
| --- | --- | --- |
| Round Ten physical pot | 1,013/1,500 | 1,013/1,500; zero estate requests |
| Restoration reserve | 95 remaining | 95 remaining |
| Rolling ordinary physical requests | 1,138/3,000 | 1,138/3,000 |
| Investigation diagnostics | 0/12 | 0/12; no guard or control requests |
| Daily model calls | 74/600 | 109/600; 35 intake calls |
| Daily reserved input characters | 5,276,574/8,000,000 | 7,997,743/8,000,000 |
| Daily output-token reservations | 137,000/1,500,000 | 189,500/1,500,000 |

The refused request needed 77,661 input characters with only 2,257 left; admission would have reached 8,075,404. It was not charged and did not call the model. The completed batch contains three separately recorded rule retries (H-noisy, H-terse, H-typo), not clean first responses. Investigation planner and synthesis calls are zero. No allowance, counter, identity, permission or fixture changed.

Engine fingerprint: `46f38581b21ce67a68825794dcb17fe81c9f682ec5cf8645e35953adf2c8c2dc`. Committed implementation: `0e7bae5`. Golden hash: `bb724be6c27e1e7641de5a708bcc9544fbb02a4dc44f63a66f6a0e65845881b7`. Budget-refusal tape SHA-256: `a3bb5735be72e7f85aea51abfbea850470e07f0c07f6948b4ed802dfa2e02b6f`. Private exact artifacts are under `.local/round-ten-20261007/part-b/part-c/original-59/`; public ledger notes carry the result and the separately appended budget refusal. Event counts include 35 provider requests and 35 provider responses; no estate transport was installed.

The original archived expectations and tape bodies were not rewritten. Engine changes invalidate prior freezes; no freeze or unfamiliar-domain/general capability claim is made. Billing's newly approved Pipeline Copy route is recorded as authorised but unimplemented, conditional on rehearsal 9/9. Its sealed author-only description is unchanged until that later authorised step.

## Original estate — fifty texts plus nine families

Current prompt and validator: 32/59 completed records; zero estate reads. A recorded pre-provider budget refusal is labelled separately below.

| Ticket | Expected target / kind | Observed target / kind | Full record match / mismatches |
| --- | --- | --- | --- |
| family-A-mention | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | YES |
| family-A-noisy | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | YES |
| family-A-terse | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | YES |
| family-A-typo | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | YES |
| family-B-noisy | Inventory Health [d78c6da0] / METRIC_COMPONENTS | Inventory Health [d78c6da0] / METRIC_COMPONENTS | NO: ticket_shape, comparison_mode |
| family-B-terse | Inventory Health [d78c6da0] / METRIC_COMPONENTS | Inventory Health [d78c6da0] / METRIC_COMPONENTS | NO: ticket_shape, comparison_mode |
| family-B-typo | Inventory Health [d78c6da0] / METRIC_COMPONENTS | Inventory Health [d78c6da0] / METRIC_COMPONENTS | NO: ticket_shape, comparison_mode |
| family-C-noisy | Inventory Health [886713d3] / DERIVED_CALCULATION | Inventory Health [886713d3] / METRIC_COMPONENTS | NO: ticket_shape, comparison_mode, question_kind, nominated_question_kind |
| family-C-terse | Inventory Health [886713d3] / DERIVED_CALCULATION | Inventory Health [886713d3] / DERIVED_CALCULATION | NO: ticket_shape, comparison_mode |
| family-C-typo | Inventory Health [886713d3] / DERIVED_CALCULATION | Inventory Health [886713d3] / DERIVED_CALCULATION | NO: ticket_shape, comparison_mode |
| family-D-noisy | TARGET_AMBIGUOUS / VISUAL_CONTENT | Inventory Health [25189fcc] / FILTER_EFFECT | NO: status, error, target_id, cell_mode, action, model_id, measure_id, ticket_shape, comparison_mode, question_kind, selection_value, nominated_question_kind |
| family-D-terse | TARGET_AMBIGUOUS / VISUAL_CONTENT | TARGET_UNRESOLVED / FILTER_EFFECT | NO: status, error, target_id, cell_mode, action, model_id, measure_id, ticket_shape, comparison_mode, question_kind, dimension_ids, filters, figure_state, figure_value, figure_precision, selection_value, nominated_question_kind |
| family-D-typo | TARGET_AMBIGUOUS / VISUAL_CONTENT | Inventory Health [25189fcc] / FILTER_EFFECT | NO: status, error, target_id, cell_mode, action, model_id, measure_id, ticket_shape, comparison_mode, question_kind, selection_value, nominated_question_kind |
| family-E-mention | Inventory Health [25189fcc] / FRESHNESS | Inventory Health [25189fcc] / FRESHNESS | NO: ticket_shape, comparison_mode |
| family-E-noisy | TARGET_AMBIGUOUS / FRESHNESS | TARGET_AMBIGUOUS / FRESHNESS | YES |
| family-E-terse | TARGET_AMBIGUOUS / FRESHNESS | TARGET_AMBIGUOUS / FRESHNESS | YES |
| family-E-typo | TARGET_AMBIGUOUS / FRESHNESS | TARGET_UNRESOLVED / FRESHNESS | NO: status, error, target_id, cell_mode, action, model_id, measure_id, ticket_shape, comparison_mode, question_kind, dimension_ids, filters, figure_state, figure_value, figure_precision, selection_value, nominated_question_kind |
| family-F-noisy | Inventory Health [8ab0a658] / TRANSFORMATION_MECHANISM | Inventory Health [8ab0a658] / TRANSFORMATION_MECHANISM | YES |
| family-F-terse | Inventory Health [8ab0a658] / TRANSFORMATION_MECHANISM | Inventory Health [8ab0a658] / TRANSFORMATION_MECHANISM | YES |
| family-F-typo | Inventory Health [8ab0a658] / TRANSFORMATION_MECHANISM | Inventory Health [8ab0a658] / TRANSFORMATION_MECHANISM | YES |
| family-G-mention | Inventory Health [25189fcc] / SOURCE_CORRECTNESS | Inventory Health [25189fcc] / SOURCE_CORRECTNESS | NO: ticket_shape, comparison_mode |
| family-G-noisy | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | YES |
| family-G-terse | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | YES |
| family-G-typo | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | TARGET_UNRESOLVED / SOURCE_CORRECTNESS | NO: status, error, target_id, cell_mode, action, model_id, measure_id, ticket_shape, comparison_mode, question_kind, dimension_ids, filters, figure_state, figure_value, figure_precision, selection_value, nominated_question_kind |
| family-H-noisy | TARGET_AMBIGUOUS / METRIC_COMPONENTS | TARGET_AMBIGUOUS / DERIVED_CALCULATION | NO: nominated_question_kind |
| family-H-terse | TARGET_AMBIGUOUS / METRIC_COMPONENTS | TARGET_AMBIGUOUS / FIGURE_DIFFERENCE | NO: nominated_question_kind |
| family-H-typo | TARGET_AMBIGUOUS / METRIC_COMPONENTS | TARGET_AMBIGUOUS / METRIC_COMPONENTS | YES |
| family-I-noisy | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | TARGET_AMBIGUOUS / TRANSFORMATION_MECHANISM | NO: nominated_question_kind |
| family-I-terse | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | TARGET_AMBIGUOUS / EXPECTED_BEHAVIOR | NO: nominated_question_kind |
| family-I-typo | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | TARGET_AMBIGUOUS / TRANSFORMATION_MECHANISM | NO: nominated_question_kind |
| question-change-days | UNIMPLEMENTED_ROUTE / TEMPORAL_COMPARISON | UNIMPLEMENTED_ROUTE / TEMPORAL_COMPARISON | YES |
| question-change-week | UNIMPLEMENTED_ROUTE / TEMPORAL_COMPARISON | UNIMPLEMENTED_ROUTE / TEMPORAL_COMPARISON | YES |
| question-hiding-rows | TARGET_AMBIGUOUS / FILTER_EFFECT | BUDGET REFUSED before provider | NO: no intake record |
| question-stale-no-sla | TARGET_AMBIGUOUS / FRESHNESS | NOT ATTEMPTED | NO: not attempted |
| refusal-business-benchmark | UNIMPLEMENTED_ROUTE / BUSINESS_MEANING | NOT ATTEMPTED | NO: not attempted |
| refusal-business-intent | UNIMPLEMENTED_ROUTE / BUSINESS_MEANING | NOT ATTEMPTED | NO: not attempted |
| refusal-business-q49 | UNIMPLEMENTED_ROUTE / BUSINESS_MEANING | NOT ATTEMPTED | NO: not attempted |
| refusal-nonexistent-column | NEEDS_INPUT / None | NOT ATTEMPTED | NO: not attempted |
| refusal-two-figures-total | NEEDS_INPUT / None | NOT ATTEMPTED | NO: not attempted |
| refusal-two-figures | NEEDS_INPUT / None | NOT ATTEMPTED | NO: not attempted |
| refusal-unidentified-measure | NEEDS_INPUT / None | NOT ATTEMPTED | NO: not attempted |
| refusal-unidentified-visual | NEEDS_INPUT / None | NOT ATTEMPTED | NO: not attempted |
| refusal-unsupported-filter | NEEDS_INPUT / None | NOT ATTEMPTED | NO: not attempted |
| refusal-unsupported-relative | NEEDS_INPUT / None | NOT ATTEMPTED | NO: not attempted |
| visual-1 | Global card [45e0a944] / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| visual-2 | Handled Quantity - unfiltered [b4e3f661] / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| visual-3 | Handled Quantity - unfiltered [d72c75ad] / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| visual-4 | Handled Quantity - unfiltered [e1b0664f] / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| visual-5 | Handled Quantity - unfiltered [44a8172e] / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| visual-6 | Calculated table card [ae4a2be8] / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| family-A | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | NOT ATTEMPTED | NO: not attempted |
| family-B | Inventory Health [d78c6da0] / METRIC_COMPONENTS | NOT ATTEMPTED | NO: not attempted |
| family-C | Inventory Health [886713d3] / DERIVED_CALCULATION | NOT ATTEMPTED | NO: not attempted |
| family-D | TARGET_AMBIGUOUS / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| family-E | TARGET_AMBIGUOUS / FRESHNESS | NOT ATTEMPTED | NO: not attempted |
| family-F | TARGET_AMBIGUOUS / TRANSFORMATION_MECHANISM | NOT ATTEMPTED | NO: not attempted |
| family-G | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | NOT ATTEMPTED | NO: not attempted |
| family-H | TARGET_AMBIGUOUS / METRIC_COMPONENTS | NOT ATTEMPTED | NO: not attempted |
| family-I | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | NOT ATTEMPTED | NO: not attempted |

## Rebuilt estate — nine families

Current prompt and validator: 0/9 completed records; zero estate reads. A recorded pre-provider budget refusal is labelled separately below.

| Ticket | Expected target / kind | Observed target / kind | Full record match / mismatches |
| --- | --- | --- | --- |
| family-A | Inventory Health [25189fcc] / FIGURE_DIFFERENCE | NOT ATTEMPTED | NO: not attempted |
| family-B | Inventory Health [d78c6da0] / METRIC_COMPONENTS | NOT ATTEMPTED | NO: not attempted |
| family-C | Inventory Health [886713d3] / DERIVED_CALCULATION | NOT ATTEMPTED | NO: not attempted |
| family-D | TARGET_AMBIGUOUS / VISUAL_CONTENT | NOT ATTEMPTED | NO: not attempted |
| family-E | TARGET_AMBIGUOUS / FRESHNESS | NOT ATTEMPTED | NO: not attempted |
| family-F | TARGET_AMBIGUOUS / TRANSFORMATION_MECHANISM | NOT ATTEMPTED | NO: not attempted |
| family-G | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | NOT ATTEMPTED | NO: not attempted |
| family-H | TARGET_AMBIGUOUS / METRIC_COMPONENTS | NOT ATTEMPTED | NO: not attempted |
| family-I | TARGET_AMBIGUOUS / SOURCE_CORRECTNESS | NOT ATTEMPTED | NO: not attempted |
