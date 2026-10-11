# Round Ten B: first-divergence audit

2026-10-07. Read-only inspection of the original64 recorded attempts. Zero estate reads and zero provider calls. No engine/adapter fix or ticket rerun has occurred. #423 remains draft; its existing15?2 hosted check passed on3e40a9b, which is not the blocked enlarged gate.

## Misses grouped by first divergence

| First divergence | Misses |
| --- | ---: |
| synthesis | 2 |
| intake | 13 |
| outcome mapping / question account | 8 |

There are23 misses across attempted columns:19 inference-enabled and4 inference-disabled. These group into three entry points, not nineteen independent patches. The grouping names the earliest evidenced divergence, not a proven root cause for every held response. An ambiguous or under-specified ticket is not authorization to invent a target or broaden scope.

## Per-ticket table

Expected and observed columns show status/outcome/answer category. A matching outcome with failed synthesis is a miss. "Not attempted" is distinct from a refusal. Original tape hashes and precise stage accounting are pinned in [the score artifact](runs/round-ten-fifty-score.json).

| Ticket / class | Column | Expected | Observed | Match | First divergence |
| --- | --- | --- | --- | --- | --- |
| family-A-mention / second-numeral-mention | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-A-noisy / forwarded-noisy | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-A-terse / terse | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | no | synthesis |
| family-A-typo / typo-informal | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-B-noisy / forwarded-noisy | stripped | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-B-terse / terse | stripped | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-B-typo / typo-informal | stripped | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-C-noisy / forwarded-noisy | stripped | HELD / ? / NOT_ANSWERED | HELD / ? / NOT_ANSWERED | yes | none under sealed checks |
| family-C-terse / terse | stripped | HELD / ? / NOT_ANSWERED | HELD / ? / NOT_ANSWERED | yes | none under sealed checks |
| family-C-typo / typo-informal | stripped | HELD / ? / NOT_ANSWERED | HELD / ? / NOT_ANSWERED | yes | none under sealed checks |
| family-D-noisy / forwarded-noisy | stripped | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | HELD / ? / ? | no | intake |
| family-D-terse / terse | stripped | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | COMPLETED / NO_COMPARABLE_PATH / NOT_ANSWERED | no | outcome mapping / question account |
| family-D-typo / typo-informal | stripped | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | COMPLETED / NO_COMPARABLE_PATH / NOT_ANSWERED | no | outcome mapping / question account |
| family-E-mention / second-numeral-mention | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | NEEDS_INPUT / ? / ? | no | intake |
| family-E-noisy / forwarded-noisy | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-E-terse / terse | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-E-typo / typo-informal | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-F-noisy / forwarded-noisy | stripped | COMPLETED / CONSISTENT_TO_BOUNDARY / PARTLY_ANSWERED | COMPLETED / BUSINESS_QUESTION / NOT_ANSWERED | no | intake |
| family-F-terse / terse | stripped | COMPLETED / CONSISTENT_TO_BOUNDARY / PARTLY_ANSWERED | COMPLETED / CONSISTENT_TO_BOUNDARY / NOT_ANSWERED | no | outcome mapping / question account |
| family-F-typo / typo-informal | stripped | COMPLETED / CONSISTENT_TO_BOUNDARY / PARTLY_ANSWERED | COMPLETED / CONSISTENT_TO_BOUNDARY / NOT_ANSWERED | no | outcome mapping / question account |
| family-G-mention / second-numeral-mention | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | no | synthesis |
| family-G-noisy / forwarded-noisy | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-G-terse / terse | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-G-typo / typo-informal | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-H-noisy / forwarded-noisy | stripped | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-H-terse / terse | stripped | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-H-typo / typo-informal | stripped | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-I-noisy / forwarded-noisy | stripped | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | yes | none under sealed checks |
| family-I-terse / terse | stripped | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | yes | none under sealed checks |
| family-I-typo / typo-informal | stripped | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | yes | none under sealed checks |
| question-change-days / new-question | stripped | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | no | intake |
| question-change-week / new-question | stripped | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | NEEDS_INPUT / ? / ? | no | intake |
| question-hiding-rows / new-question | stripped | COMPLETED / NO_COMPARABLE_PATH / REPRODUCED | COMPLETED / TRANSFORMATION_LOGIC / REPRODUCED | no | outcome mapping / question account |
| question-stale-no-sla / new-question | stripped | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| refusal-business-benchmark / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| refusal-business-intent / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | no | outcome mapping / question account |
| refusal-business-q49 / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| refusal-nonexistent-column / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | NEEDS_INPUT / ? / ? | yes | none under sealed checks |
| refusal-two-figures-total / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | NEEDS_INPUT / ? / ? | yes | none under sealed checks |
| refusal-two-figures / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | NEEDS_INPUT / ? / ? | yes | none under sealed checks |
| refusal-unidentified-measure / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | NEEDS_INPUT / ? / ? | yes | none under sealed checks |
| refusal-unidentified-visual / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | HELD / ? / ? | yes | none under sealed checks |
| refusal-unsupported-filter / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | HELD / ? / ? | yes | none under sealed checks |
| refusal-unsupported-relative / refusal | stripped | Refuse: HELD, NEEDS_INPUT, CAPABILITY_REFUSAL | NEEDS_INPUT / ? / ? | yes | none under sealed checks |
| visual-1 / visual-variety | stripped | COMPLETED / NO_COMPARABLE_PATH / REPRODUCED | COMPLETED / TRANSFORMATION_LOGIC / REPRODUCED | no | intake |
| visual-2 / visual-variety | stripped | COMPLETED / NO_COMPARABLE_PATH / REPRODUCED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | no | intake |
| visual-3 / visual-variety | stripped | COMPLETED / NO_COMPARABLE_PATH / REPRODUCED | HELD / ? / ? | no | intake |
| visual-4 / visual-variety | stripped | COMPLETED / NO_COMPARABLE_PATH / REPRODUCED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | no | intake |
| visual-5 / visual-variety | stripped | COMPLETED / NO_COMPARABLE_PATH / NOT_REPRODUCED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | no | intake |
| visual-6 / visual-variety | stripped | COMPLETED / NO_COMPARABLE_PATH / REPRODUCED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | no | intake |
| family-A-mention / second-numeral-mention | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | NEEDS_INPUT / ? / ? | no | intake |
| family-A-noisy / forwarded-noisy | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-A-terse / terse | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-A-typo / typo-informal | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | yes | none under sealed checks |
| family-B-noisy / forwarded-noisy | declared | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-B-terse / terse | declared | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-B-typo / typo-informal | declared | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | yes | none under sealed checks |
| family-C-noisy / forwarded-noisy | declared | HELD / ? / NOT_ANSWERED | HELD / ? / NOT_ANSWERED | yes | none under sealed checks |
| family-C-terse / terse | declared | HELD / ? / NOT_ANSWERED | HELD / ? / NOT_ANSWERED | yes | none under sealed checks |
| family-C-typo / typo-informal | declared | HELD / ? / NOT_ANSWERED | HELD / ? / NOT_ANSWERED | yes | none under sealed checks |
| family-D-noisy / forwarded-noisy | declared | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | COMPLETED / NO_COMPARABLE_PATH / NOT_ANSWERED | no | outcome mapping / question account |
| family-D-terse / terse | declared | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | COMPLETED / NO_COMPARABLE_PATH / NOT_ANSWERED | no | outcome mapping / question account |
| family-D-typo / typo-informal | declared | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | COMPLETED / NO_COMPARABLE_PATH / NO_REPORTED_FIGURE | yes | none under sealed checks |
| family-E-mention / second-numeral-mention | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | NEEDS_INPUT / ? / ? | no | intake |
| family-E-noisy / forwarded-noisy | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-E-terse / terse | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-E-typo / typo-informal | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-F-noisy / forwarded-noisy | declared | COMPLETED / CONSISTENT_TO_BOUNDARY / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-F-terse / terse | declared | COMPLETED / CONSISTENT_TO_BOUNDARY / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-F-typo / typo-informal | declared | COMPLETED / CONSISTENT_TO_BOUNDARY / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-G-mention / second-numeral-mention | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-G-noisy / forwarded-noisy | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-G-terse / terse | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-G-typo / typo-informal | declared | COMPLETED / TRANSFORMATION_LOGIC / PARTLY_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-H-noisy / forwarded-noisy | declared | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-H-terse / terse | declared | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-H-typo / typo-informal | declared | COMPLETED / NO_KNOWN_PATTERN / NOT_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-I-noisy / forwarded-noisy | declared | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-I-terse / terse | declared | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | not attempted | ? | daily model cap before dispatch |
| family-I-typo / typo-informal | declared | COMPLETED / TRANSFORMATION_LOGIC / NOT_ANSWERED | not attempted | ? | daily model cap before dispatch |

Owner-authored folder was empty before sealing: no owner tickets exist to grade. Refusals are ten separately authored cases, not all held outcomes.

## Evidence for each miss

- **stripped/family-A-terse ? synthesis:** Quantity outcome matches; sealed mechanism rejected for repeated hedging. No outputs emitted.
- **stripped/family-G-mention ? synthesis:** Quantity outcome matches; sealed mechanism rejected for repeated hedging. No outputs emitted.
- **stripped/family-D-noisy ? intake:** RESOLUTION_UNCERTAIN before a proposed target or any probe; exact unresolved choice needs proposal-response inspection, not a guessed grouping fix.
- **stripped/visual-3 ? intake:** RESOLUTION_UNCERTAIN before a proposed target or any probe; exact unresolved choice needs proposal-response inspection, not a guessed grouping fix.
- **stripped/family-E-mention ? intake:** Explicit displayed integer and tracking reference reach intake; model asks for precision instead of supplying an exact reported figure.
- **declared/family-A-mention ? intake:** Intake refuses asking for stated precision; no target/procedure dispatch.
- **declared/family-E-mention ? intake:** Intake refuses asking for stated precision; no target/procedure dispatch.
- **stripped/family-F-noisy ? intake:** Resolved measure and TRANSFORMATION_MECHANISM agree with terse variant; BUSINESS_QUESTION/NONE rather than MISMATCH_COMPLAINT/VERTICAL selects different terminal branch.
- **stripped/question-change-days ? intake:** Temporal-state question classified BUSINESS_MEANING; no pair of date states carried into the procedure.
- **stripped/question-change-week ? intake:** Model asks which metric to compare; no metric/procedure dispatch. Ticket/expected-answer sufficiency is still an authoring question.
- **stripped/visual-1 ? intake:** Correct report, but definition target and cell address absent despite named Global card. Reproduction subsequently selects Warehouse/product matrix TOTAL; requested card is unevaluated.
- **stripped/visual-2 ? intake:** Explicit saved-context reproduction request classified FIGURE_DIFFERENCE; target/cell address absent; capability undeclared by kind. No evidence yet for intersection or calculated-lineage defect as the first cause.
- **stripped/visual-4 ? intake:** Explicit saved-context reproduction request classified FIGURE_DIFFERENCE; target/cell address absent; capability undeclared by kind. No evidence yet for intersection or calculated-lineage defect as the first cause.
- **stripped/visual-6 ? intake:** Explicit saved-context reproduction request classified FIGURE_DIFFERENCE; target/cell address absent; capability undeclared by kind. No evidence yet for intersection or calculated-lineage defect as the first cause.
- **stripped/visual-5 ? intake:** Named page/bookmark target absent; compound North product one selection remains UNSEPARATED. Procedure then refuses VALUE_EXISTENCE_RESULT restriction; bookmark promotion is not established as the cause.
- **stripped/family-D-terse ? outcome mapping / question account:** Procedure retains No reported figure supplied, but header maps to NOT_ANSWERED instead of sealed NO_REPORTED_FIGURE.
- **stripped/family-D-typo ? outcome mapping / question account:** Procedure retains No reported figure supplied, but header maps to NOT_ANSWERED instead of sealed NO_REPORTED_FIGURE.
- **declared/family-D-noisy ? outcome mapping / question account:** Procedure retains No reported figure supplied; header maps to NOT_ANSWERED instead of sealed NO_REPORTED_FIGURE.
- **declared/family-D-terse ? outcome mapping / question account:** Procedure retains No reported figure supplied; header maps to NOT_ANSWERED instead of sealed NO_REPORTED_FIGURE.
- **stripped/family-F-terse ? outcome mapping / question account:** CONSISTENT_TO_BOUNDARY matches; matching totals do not answer the mechanism question, so NOT_ANSWERED differs from authored PARTLY_ANSWERED. Oracle may be too permissive; unchanged.
- **stripped/family-F-typo ? outcome mapping / question account:** CONSISTENT_TO_BOUNDARY matches; matching totals do not answer the mechanism question, so NOT_ANSWERED differs from authored PARTLY_ANSWERED. Oracle may be too permissive; unchanged.
- **stripped/question-hiding-rows ? outcome mapping / question account:** VISUAL_CONTENT and reported16 reach reproduced saved-context result; walk then finds TRANSFORMATION_LOGIC instead of authored NO_COMPARABLE_PATH. Whether walk should proceed is separate from number reproduction.
- **stripped/refusal-business-intent ? outcome mapping / question account:** BUSINESS_MEANING reaches technical walk; TRANSFORMATION_LOGIC with NOT_ANSWERED/domain-specialist action does not meet the authored refusal commitment.

## Wrong-cell evidence

Visual1 asks for **Global card**, page99d9ca357e3792ad6f70. The sealed intake proposal has `definition_target = null` and `cell_address = null`. Its chosen reproduction cell targets **Warehouse and product matrix**, page5b9bd0d258d6c51b5929, visuald72c75adb19cf1cb1f15, modeTOTAL, grouping columnsItems/product_name andLocations/warehouse_name, empty key restrictions, value8,765. Neither grouping column was dropped from that TOTAL address; the defect is substitution of a different visual after the requested referent was not carried. The requested card is expressly unevaluated with Diagnostic read cap reached.

No claim is made yet that the six visual failures were caused by six separate compilation bugs. The earliest evidence is intake target/kind/selection loss. Before changing bookmark disposition, intersections, total keys or calculated-table lineage, each must be inspected under the intended target. A missing field must not be replaced by a number match elsewhere.

## Next checkpoint

Section1 is reported before fixes. Sections2?5 require independently tested invariants and a separate report before any live attempt. Model allowance600 is explicitly authorized; physical pot800, reserve100, rolling3000 and investigation diagnostics12 stay unchanged. Original50+14 artifacts and oracle seals remain untouched.

## Approved allowance control

Separate Part B manifests now declare daily model calls600 instead of240. Before/after files were re-read and compared: that single budget field is the only difference; pot800, reserve100, rolling3000 and diagnostics12 are unchanged. Original frozen-run manifest files/approvals remain untouched. New whole-config approval is required before any live run. Control hashes:

- estate-visuals.json: before `f1a30a91ae6f05645304c1e6cdc8522b03147bda378e6abf22c0e10c46212e32`; after `655561c689be3e3b5b38332706ecd900ccebade4c4469f686003bf50151fd300`.
- estate-declared.json: before `469ae027f52fdbe5b49bde99eb404e67f7fbffe0afa1285f4ab75f09d59af57d`; after `da712d35b209279a93c92ba3ea88f893ebcbd6a4ca7dcf170ac4ad8554ee30f3`.
