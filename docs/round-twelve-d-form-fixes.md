# Round Twelve D form fixes and development record

2026-10-10. Draft #423; prior freeze invalid. A1 rescoring is recorded separately. No fresh held-out intake pass is authorized or attempted.

## DECIDED WITHOUT REVIEW

Model-only questions use the existing free-text intake port, selected explicitly by ?It?s about a measure, not a specific report?. The report proof asserts a visual and a complete declared report scope; extending it with fabricated report/page fields would misrepresent authority. Rejected alternative: extending the report-specific proof to model scope in this presentation round. The measure-text route accepts no report/page/visual picks, retains the original form envelope separately, and forwards the original description and supplied value/comparison through the closed text input contract. It performs ordinary interpretation; it does not invent a visual or assert that the text route always succeeds. The UI states the route and requires a question naming the model/measure. No model/measure dropdown is claimed.

Page pictures use retained definition geometry, not rendered screenshots or current values. No estate request is made for geometry. Missing/duplicate geometry refuses preview; the optional title list remains available. Clicks are explicit user visual selections, never automatic scope authority. Form-choice previews now read the persisted form choices instead of incorrectly consulting free-text choice values.

## Generic fixes

Picked visual anchoring no longer treats a generic shape or position word as a different named object. Actual named-object conflicts remain evidence and require one user decision. An unresolved/ambiguous description with a picked visual offers a user confirmation rather than refusing or selecting a substitute.

A fully receipted candidate set with no value match now asks the user to point to the visual. Choosing one preserves the supplied value and archives the prior probes; inability to point holds. No quantity is changed to force reproduction.

Forms and free-text intake share the same predicate admission block. An explicitly unidentified filter, unresolved column, or unsupported relative-date restriction cannot be repaired by asking an unrelated report/page question. The dev unsupported-filter control exposed that the form had bypassed this existing rule.

## Temporary model allowance

Owner replied ?yes go ahead? on2026-10-10 to reserved model output1,500,000 ->2,400,000 for this batch only, restored afterward with counters preserved. Usage before1,422,000; each provider call reserves8,000. Call600, input8,000,000, estate rolling3,000, round pot1,500 and diagnostic12 unchanged. Private before-manifest bytes and approval record retained; counts/hash-only ledger entry appended. No identity or permission change.

## Original nineteen incomplete controls

These are the retained last-pass results, not a fresh held-out evaluation. Genuine missing information may receive one relevant question; capability refusals must name the actual unavailable operation. Model-only records must not be asked for report/page. Nothing in this table is used as a held-out test fixture.

| Partition | Record | Correct behavior | Retained actual | Explanation |
|---|---|---|---|---|
| dev | original:family-E-noisy | Use model/measure text route; no report/page question | HELD, 1 question(s): USER_INFORMATION_UNAVAILABLE | ILLEGITIMATE: a report/page choice cannot establish a visual for a model-only measure question. |
| dev | original:family-E-terse | Use model/measure text route; no report/page question | HELD, 1 question(s): USER_INFORMATION_UNAVAILABLE | ILLEGITIMATE: a report/page choice cannot establish a visual for a model-only measure question. |
| dev | original:family-E-typo | Use model/measure text route; no report/page question | HELD, 0 question(s): Starting measure/model is unresolved | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:question-change-days | Hold naming the unavailable historical route | HELD, 0 question(s): The earlier-state comparison route is unimplemented; a current-state walk cannot answer a change between states. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:question-stale-no-sla | Use model/measure text route; no report/page question | HELD, 0 question(s): TARGET_UNRESOLVED: Ungrouped scope needs an explicit global request. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:refusal-business-benchmark | Hold / recorded domain-owner handoff; no technical verdict | HELD, 0 question(s): The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:refusal-business-intent | Hold / recorded domain-owner handoff; no technical verdict | HELD, 0 question(s): The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:refusal-business-q49 | Hold / recorded domain-owner handoff; no technical verdict | HELD, 0 question(s): The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:refusal-two-figures | One figure clarification or hold naming figure ambiguity | HELD, 0 question(s): Ambiguous reported figure: more than one resolved value requires clarification: 16 from '16'; 17 from '17' | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:refusal-unidentified-visual | One referent question or hold if genuinely unidentified | HELD, 0 question(s): Starting measure is unresolved from the primary question | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| dev | original:refusal-unsupported-filter | Hold naming unavailable predicate/column; no unrelated question | HELD, 1 question(s): USER_INFORMATION_UNAVAILABLE | ILLEGITIMATE: a report/page choice cannot establish the missing custom predicate. |
| dev | original:refusal-unsupported-relative | Hold naming unavailable predicate/column; no unrelated question | HELD, 0 question(s): TARGET_AMBIGUOUS: Primary-question evidence does not uniquely select a visual. Candidate visuals: Handled Quantity - extra visual predicate, Handled Quantity - page and slicers, Handled Quantity - unfiltered, Saved predicate selections, Top-N verification. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| held_out | original:family-G-noisy | Use model/measure text route; no report/page question | HELD, 0 question(s): TARGET_UNRESOLVED: Ungrouped scope needs an explicit global request. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| held_out | original:family-G-terse | Use model/measure text route; no report/page question | HELD, 1 question(s): USER_INFORMATION_UNAVAILABLE | ILLEGITIMATE: a report/page choice cannot establish a visual for a model-only measure question. |
| held_out | original:family-G-typo | Use model/measure text route; no report/page question | HELD, 0 question(s): Starting measure/model is unresolved | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| held_out | original:question-change-week | Hold naming the unavailable historical route | HELD, 0 question(s): The earlier-state comparison route is unimplemented; a current-state walk cannot answer a change between states. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| held_out | original:refusal-nonexistent-column | Hold naming unavailable predicate/column; no unrelated question | HELD, 0 question(s): TARGET_AMBIGUOUS: Primary-question evidence does not uniquely select a visual. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units. | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| held_out | original:refusal-two-figures-total | One figure clarification or hold naming figure ambiguity | HELD, 0 question(s): Ambiguous reported figure: more than one resolved value requires clarification: 8765 from '8765'; 8766 from '8766' | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |
| held_out | original:refusal-unidentified-measure | One referent question or hold if genuinely unidentified | HELD, 0 question(s): Starting measure is unresolved from the primary question | No unrelated question was asked; any reason mismatch remains separate from correct settlement. |

## Validation and next steps

157 focused tests passed before the final measure-text preflight test; subsequent focused and full regression results will be appended. One invalid mock source lacking its required text was corrected in the test, not defaulted in production. An early full regression was interrupted before source edits; its log is preserved and is not a frozen-source pass. Fresh dev and live work are pending. No billing investigation has run.

## Browser validation and billing preparation, 2026-10-10

A synthetic local server with estate transports absent was exercised in the connected Edge browser. Selecting Report / Overview displayed retained page geometry; clicking the Global card outline selected that target and single-number mode. The measure-text switch disabled report/page/visual fields. No ticket was submitted and no billing tester artifact was created. This verifies interaction, not estate execution or owner-unaided use.

The first fragment-login attempt failed with `TypeError: window.history.replaceState is not a function`. The classic script's global `history()` function shadowed the browser API. It is now named `investigationHistory`; a Node regression runs the actual fragment bootstrap and checks that the native history object survives. Interactive outlines use role `group`, with keyboard-operable button children, instead of a static-image role. Three launcher/UI tests pass.

Nine independent billing answer/evidence contracts are sealed in `acceptance/billing/independent-expectations.json`, SHA-256 `b3a6d225e97855a6a86b5d693763164230cf9ee38989347b5910b63af43d2362`. They specify the relationship to the actual question and the seeded arithmetic, not invented observed outcomes. Undeployed latency states are explicitly not assumed. A test verifies both the seal and every unchanged independent ticket hash. Tickets07-12 remain excluded and await owner/reviewer expectations via `docs/billing-unplanned-tickets-for-review.md`. No billing investigation has run.

Fresh dev is in progress on engine9ef6205 with zero estate reads. Two model-only freshness records so far still ask NUMBER: the form's explicit subject is not conveyed to the text resolver. This is a shared wiring defect, not a reason to change oracle targets. The current pass and its failures are preserved before a dev-only fix. No fresh held-out pass.
