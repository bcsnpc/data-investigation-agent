# Pass 1: partial progress, not a final score

Observed 2026-11-21. Pass 1 continues; no pass 2, calibration or v5 run is admitted. Protected calibration allowance is $14.34, plus the existing $3 reserve. The owner requires pass 2 (pass-1 failures plus the fixed 20-ticket regression guard) before calibration.

Independent grading currently covers 33 of 50 main-cohort outcomes: primary 3 correct, strict 3, reviewed 4. One reviewed harmful flag is retained. The separate five plumbing reruns are fully graded: primary 0/5, strict 0/5, reviewed 0/5, harmful 0. These are separate cohorts and must not be combined into one score. Two saved screenshot grading packets remain unsent because they exceed the existing input bound; they have no assigned grade.

Both failed-job cohorts and the waiting-job cohort completed. The subsequent history control was restored to its original source and schema hashes after admission refused before a ticket dispatch. The serial controller inherited the three-worker concurrency buffer; recovery uses the already-existing one-worker buffer. No cap was raised. Fault cohorts remain serialized.

## Retained harm flag and trace follow-up

`form__v2-fixture-quantity-v1`: the primary marked harmful, the secondary did not. The independent reviewer returned harmful=true, but also winning_grader=SECONDARY and a reason saying the answer states a wrong cause. These fields conflict. The reviewed harm flag is retained; the operator has not overwritten the independent review or either grade.

The saved business answer is UNRESOLVED. It incorrectly retains an initial ambiguous-DAX error after a later native recreation returned 8,765. The same saved trace has Bronze/Silver 7,661 and Gold/model 8,765, two product-7 rate rows, product-7 units 1,104 versus 2,208, and 406 Gold rows versus 360 distinct movements. The correct next investigation is to inspect and cite the retained join definition, establish its multiplicity and answer the split. A repaired query must supersede its earlier failed attempt as a remaining blocker; the original failed attempt remains in evidence. This is a substantive conclusion/recovery issue, not permission to relabel the original as a successful run or alter its expectation.

Freeze is blocked until any reviewed harmful cause is addressed and retested without harm. Full per-ticket backtrack and final counts remain in progress.
