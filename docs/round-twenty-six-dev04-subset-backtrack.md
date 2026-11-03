# Dev04 pre-steer subset backtrack

Three already-submitted tickets completed on e41e803b / image 118253a7 before further admissions were paused. Primary, strict and independently reviewed saved-evidence scores are each 1/3, harmful 0. This is not a complete dev pass. No score, expectation, original tape or delivered output was changed.

| Ticket | First incorrect step | What happened | Correct next action |
|---|---|---|---|
| R17-04 | Target | The run stopped at report ambiguity and returned unavailable candidate-scope checks. It never established the requested semantic/business-meaning limit. | Check the actual candidate scopes where possible; otherwise retain those failures and route the meaning decision with the calculation evidence that is available. |
| R17-05 | Conclusion | It reproduced and explained the additive measure, but concluded not found because the current visual state was unverified. The secondary grader credited layer and cause; neither grader credited the verdict. | Distinguish the retained declared calculation and scope that were proved from the unavailable current interactive state, and limit each conclusion accordingly. |

R17-01 was correct according to both independent graders. Its earlier dev02 harmful answer remains recorded; this new result does not overwrite it. R17-05's disagreement was assessed by a separate reviewer, which retained the overall incorrect, non-harmful result.

Sources: dev04 saved outcomes and the primary/secondary grading tasks, plus the independently retained disagreement decision. These are saved evidence projections, not a claim of inspecting byte-exact provider tapes. This backtrack used no new estate reads or model calls beyond the recorded independent grading/review.
