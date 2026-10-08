# Round Ten B: once-only reruns

Recorded 2026-10-07 America/Chicago. PR #423 remains draft. Prior freezes are invalid. These are fixture-authored known-domain tickets, not unfamiliar-domain acceptance.

All 23 original misses and 16 unattempted cases ran once under `round-ten-b-regression-20261008` (`8d7f118158f4e7b4bd6ad95baed38c92010d1908`). No replacement run or mid-batch engine/configuration change. All 39 tapes validated.

| Column | Before | After | Current-engine attempts |
| --- | --- | --- | --- |
| Inference enabled | 31/50 | 32/50 (64%) | 19 |
| Inference disabled | 10/14 attempted; 16 unattempted | 10/30 (33.33%) | 20 |

Composite total: 42/80 (52.5%). Untouched original passes retain their original engine provenance; this is not a fresh full-column evaluation. Only one of the 39 new attempts matched its complete sealed expectation: the business-rule refusal. None of the other expectations was changed to fit a new result.

## Score by phrasing class

| Column / class | Before matched / attempted | After matched / attempted |
| --- | --- | --- |
| declared/second-numeral-mention | 0/2 | 0/3 |
| stripped/second-numeral-mention | 1/3 | 1/3 |
| declared/forwarded-noisy | 3/4 | 3/9 |
| stripped/forwarded-noisy | 7/9 | 7/9 |
| declared/terse | 3/4 | 3/9 |
| stripped/terse | 6/9 | 6/9 |
| declared/typo-informal | 4/4 | 4/9 |
| stripped/typo-informal | 7/9 | 7/9 |
| stripped/new-question | 1/4 | 1/4 |
| stripped/refusal | 9/10 | 10/10 |
| stripped/visual-variety | 0/6 | 0/6 |

## What happened

- 22 TARGET_UNRESOLVED: the required target did not resolve unambiguously. Candidates are retained in each refusal; no visual was selected from its number. This prevents testing the later D mapping or filter-effect route on those original tickets.
- Eight UNIMPLEMENTED_ROUTE refusals, including the correctly refused business-rule decision and earlier-state comparisons. Technical current-state evidence is not substituted for those questions.
- One two-level matrix refused INTAKE_RECORD_INVALID after its single recorded retry. A returned selection was not validly quoted; the incomplete key address was never read.
- Three NEEDS_INPUT responses: E/G second-numeral tickets asked for stated precision; H typo asked which starting measure was intended. The exact responses and questions remain in the tapes.
- Global card, matrix total and six-filter card all reproduced the authored figure and synthesized, but returned CONSISTENT_TO_BOUNDARY against sealed NO_COMPARABLE_PATH expectations. Those mismatches remain.
- Bookmark and calculated-table tickets completed NO_KNOWN_PATTERN / NOT_ANSWERED without the expected reproduction finding. Bookmark intake returned VISUAL_CONTENT and figure149, but BUSINESS_QUESTION/NONE plus a selection request for the quoted bookmark name. The procedure tried a selection-scope target and found no scoped grouping column. This is a retained routing/selection finding, not another per-ticket repair.
- No case reached DECLARED_FILTER_EFFECTS: its original ticket stopped at TARGET_UNRESOLVED, with two candidates. The new route has compiled-adapter and hostile-receipt tests; live execution is unverified.

## Usage and gates

Batch: 37 charged physical requests, 15 diagnostic reads, nine guard requests, 47 recorded intake calls, zero investigation planner calls and four synthesis calls. Five investigations completed; four provider composition calls do not mean only four outputs. Every completed investigation retains both outputs; exact outputs remain with the run artifacts. No cap increased or counter reset.

Pot572 ->609/800, ordinary stop700, restoration reserve100 (five already spent historically). Rolling697 ->734/3,000 at closing read. Diagnostic cap12 unchanged. Today65/600 model calls includes14 offline intake-eval calls plus51 batch intake/composition calls; it is not a reset of the prior UTC day.

Hosted run37714499671 passed archived15/15 and inferred15/15 with zero estate/network requests. Forty-two strict-match Round Ten records are candidates for gate growth; exact replay is pending and no enlarged earned gate is claimed.

## Every once-only attempt

| Ticket | Column | Status | Reason/outcome | Matches sealed expectation | Physical / diagnostic / guards |
| --- | --- | --- | --- | --- | --- |
| question-hiding-rows | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-A-terse | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-D-noisy | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-D-terse | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-D-typo | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-E-mention | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-F-noisy | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-F-terse | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-F-typo | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-G-mention | stripped | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| question-change-days | stripped | HELD | UNIMPLEMENTED_ROUTE | no | 0 / None / 0 |
| question-change-week | stripped | HELD | UNIMPLEMENTED_ROUTE | no | 0 / None / 0 |
| refusal-business-intent | stripped | HELD | UNIMPLEMENTED_ROUTE | yes | 0 / None / 0 |
| visual-1 | stripped | COMPLETED | CONSISTENT_TO_BOUNDARY | no | 11 / 5 / 3 |
| visual-2 | stripped | COMPLETED | CONSISTENT_TO_BOUNDARY | no | 11 / 5 / 3 |
| visual-3 | stripped | HELD | INTAKE_RECORD_INVALID | no | 0 / None / 0 |
| visual-4 | stripped | COMPLETED | CONSISTENT_TO_BOUNDARY | no | 11 / 5 / 3 |
| visual-5 | stripped | COMPLETED | NO_KNOWN_PATTERN | no | 2 / 0 / 0 |
| visual-6 | stripped | COMPLETED | NO_KNOWN_PATTERN | no | 2 / 0 / 0 |
| family-A-mention | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-D-noisy | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-D-terse | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-E-mention | declared | NEEDS_INPUT | NEEDS_INPUT | no | 0 / None / 0 |
| family-E-noisy | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-E-terse | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-E-typo | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-F-noisy | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-F-terse | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-F-typo | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-G-mention | declared | NEEDS_INPUT | NEEDS_INPUT | no | 0 / None / 0 |
| family-G-noisy | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-G-terse | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-G-typo | declared | HELD | TARGET_UNRESOLVED | no | 0 / None / 0 |
| family-H-noisy | declared | HELD | UNIMPLEMENTED_ROUTE | no | 0 / None / 0 |
| family-H-terse | declared | HELD | UNIMPLEMENTED_ROUTE | no | 0 / None / 0 |
| family-H-typo | declared | NEEDS_INPUT | NEEDS_INPUT | no | 0 / None / 0 |
| family-I-noisy | declared | HELD | UNIMPLEMENTED_ROUTE | no | 0 / None / 0 |
| family-I-terse | declared | HELD | UNIMPLEMENTED_ROUTE | no | 0 / None / 0 |
| family-I-typo | declared | HELD | UNIMPLEMENTED_ROUTE | no | 0 / None / 0 |

Original tickets, figures, expectation seals, prior tapes and ledger rows are unchanged. F corrections are hash-bound overlays with the human reason; the filter-route placeholder correction is separately authorized and does not make its blocked live run pass. Original F tapes lack an explicit source-unreachable sentence; that separate output defect is fixed by deterministic rendering, not by editing their outputs.
