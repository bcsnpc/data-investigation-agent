# Pass 1: partial progress, not a final score

Observed 2026-11-21. Pass 1 continues; no pass 2, calibration or v5 run is admitted. Protected calibration allowance is $14.34, plus the existing $3 reserve. The owner requires pass 2 (pass-1 failures plus the fixed 20-ticket regression guard) before calibration.

Independent grading currently covers 33 of 50 main-cohort outcomes: primary 3 correct, strict 3, reviewed 4. One reviewed harmful flag is retained. The separate five plumbing reruns are fully graded: primary 0/5, strict 0/5, reviewed 0/5, harmful 0. These are separate cohorts and must not be combined into one score. Two saved screenshot grading packets remain unsent because they exceed the existing input bound; they have no assigned grade.

Both failed-job cohorts and the waiting-job cohort completed. The subsequent history control was restored to its original source and schema hashes after admission refused before a ticket dispatch. The serial controller inherited the three-worker concurrency buffer; recovery uses the already-existing one-worker buffer. No cap was raised. Fault cohorts remain serialized.

## Retained harm flag and trace follow-up

`form__v2-fixture-quantity-v1`: the primary marked harmful, the secondary did not. The independent reviewer returned harmful=true, but also winning_grader=SECONDARY and a reason saying the answer states a wrong cause. These fields conflict. The reviewed harm flag is retained; the operator has not overwritten the independent review or either grade.

The saved business answer is UNRESOLVED. It incorrectly retains an initial ambiguous-DAX error after a later native recreation returned 8,765. The same saved trace has Bronze/Silver 7,661 and Gold/model 8,765, two product-7 rate rows, product-7 units 1,104 versus 2,208, and 406 Gold rows versus 360 distinct movements. The correct next investigation is to inspect and cite the retained join definition, establish its multiplicity and answer the split. A repaired query must supersede its earlier failed attempt as a remaining blocker; the original failed attempt remains in evidence. This is a substantive conclusion/recovery issue, not permission to relabel the original as a successful run or alter its expectation.

Freeze is blocked until any reviewed harmful cause is addressed and retested without harm. Full per-ticket backtrack and final counts remain in progress.

## Operational status versus value difference: pass-1 trace observation

The new-image failed-application-load case has native failed run 08a16ae6-71fa-4acd-90b2-bd10bc57a4ba, with start/end/error evidence. The evaluator's second attempt is structurally valid and rejects the failed-job verdict partly because source, Bronze and model totals all equal 7,661. This is separate from attempts 1 and 3, which have schema failures. Investigate generically whether the evaluator incorrectly requires a numeric mismatch for operational/freshness questions, or whether the answer failed to distinguish a failed latest load from demonstrated stale values. The correct fix must preserve that distinction: a failed job is observed; a stale numeric value requires its own evidence. Do not alter the expectation to settle this issue. No engine edit made during pass 1.

## Saved-review worklist (partial)

For the 26 reviewed failures available at this checkpoint, overlapping reviewer-reason symptoms are: target_or_scope 9, missing_definition_or_cause 26, intake_or_question 14, evaluator_or_delivery 15, budget_or_incomplete 2. These are search categories, not established first-wrong-step counts; a grader label such as intake is not substituted for a trace backtrack. The private worklist links each outcome/image, both graders and independent review, evaluator diagnostics, and possible earlier query failures followed by same-layer/same-purpose successful reads. Those recovery candidates require scope comparison before concluding they supersede an error. No new model or estate calls were used to produce this worklist.

Round27 2026-11-21: Nova Pro primary grading returned BEDROCK_AccessDeniedException on screenshot packet form-batch14; the later history batch also stopped its primary dispatch. Saved secondary outputs and original dispatches remain. Read-only STS confirms the existing IAM user dia-bedrock; read-only IAM simulation itself is AccessDenied. Cause beyond provider authorization refusal is not established. No model resend, IAM/identity/secret change or score substitution. Owner action: check existing dia-bedrock Amazon Nova Pro invocation entitlement and AWS billing/account status, retaining the Amazon-only/Claude-denied policy; report any required change before applying it. Opus investigations and offline work continue independently.

## Preliminary pass-2 affordability (not a final ticket selection)

At 2026-11-21 17:27 UTC, Anthropic headroom was $24.005655 after the separately protected $3 reserve; protecting calibration $14.34 leaves $9.665655. The current reviewed-failure plus fixed-guard union already contains at least 38 tickets. Based on 36 saved main outcomes, mean actual usage times that minimum union times 1.3 estimates $50.37. It does not fit. This is preliminary: pass 1 continues within its existing admission allowance; final selection/cost gate follows complete grading. No pass-2 or calibration Opus run is admitted. Offline fixes, tests, grading preparation, backtracks and restores continue under the owner order.
