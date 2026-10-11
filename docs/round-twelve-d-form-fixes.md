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

## Fresh dev pass D1 and subsequent generic fixes

D1 engine9ef6205 completed all46 attempts:40 base forms and6 visual-skipped forms;48 model calls,613737 input characters,zero estate reads. Complete visual forms:27/28 successful settlements,zero questions,zero harmful admissions. Controls:8/12 successful settlements,2 questions,both illegitimate,zero harmful admissions. Visual-skipped:4/5 measurable settled,1 question,classified illegitimate by the unchanged original oracle; the additional A1 E-mention case was NOT_MEASURABLE because no matching historical candidate receipt exists. No new receipt was invented or read. The value-not-found question is required by this prompt but that altered derived-form condition is not a changed oracle expectation; both facts remain visible.

Rebuilt familyI newly failed: extraction quoted `adjustment reason Q49` as an identifier, which was then processed as numeric precision. The generic repair now rejects a phrase that cannot express one exact identifier token with `IDENTIFIER_QUOTE_INVALID`, using the existing recorded one-retry protocol. It neither strips text nor chooses an identifier. Synthetic X73 tests preserve the rejected phrase and require the next exact-token response; missing page metadata in the first synthetic test was corrected in its fixture, not defaulted in production.

Model-only routing now carries the user choice as `structured.subject=MODEL_MEASURE` in the existing closed input request. The producer receives that subject, code verifies the request/text binding, the original adoption path retains it, and generic global hints cannot create a report visual. Report-context kinds and unresolved report-only selections conflict with that subject and refuse; filters, identifier evidence, named models and measures still pass their existing validators. No fallback visual or global-value match was introduced.

The prior full regression ran2842 tests and failed one historical oracle-diff assertion. That test is now pinned to the preserved pre-A1 seal, and all12 oracle tests pass. A1's own exact-three-field diff test still protects the current oracle. Original run errors and ledger rows remain unchanged. A focused fresh dev rerun will cover the four model-subject records and the identifier record; unaffected D1 results remain historical, not newly generated.

D2 affected-dev rerun engine9914e9d:8 attempts,9 calls,114947 input characters,zero estate reads. Identifier case now settles, with rejected phrase evidence retained in D1. E-noisy/E-terse/stale-no-SLA settle with zero questions. E-typo still asked NUMBER after two calls: its sole named measure has one adjacent transposition, but the old spelling repair was restricted to a picked visual. This is a shared closed-subject defect. The same one-swap rule now applies only within one named model's retained measures; two possible names refuse and no visual is selected. Unknown model/measure subjects now hold with their actual named blocker rather than offering report visuals. Synthetic spelling and ambiguity tests pass. The running full regression9914e9d was stopped before this source change; its partial log is preserved and is not a completed pass. A final frozen-source regression and a fresh E-typo dev-only recheck follow. No acceptance expectation or oracle changes.

## Final dev map and live admission

D3 engine488664b rechecked E-typo once: one recorded model call,12,858 input characters,zero estate reads; settled without a question. The retained D1 map plus affected D2/D3 reruns totals58 model calls,741,542 input characters,zero estate reads. This is an explicitly mixed-revision dev map, not a fresh whole-set or held-out pass.

| Dev group | Records | Correct zero-question settlements | Questions | Illegitimate questions | Harmful errors |
|---|---:|---:|---:|---:|---:|
| Complete visual forms |28|28|0|0|0|
| Unchanged controls |12|10|0|0|0|
| Visual-skipped measurable forms |5|4|1|1|0|

The sixth skipped form, original E-mention newly carrying the A1 figure, is not measurable without a retained candidate-value capture. No receipt was manufactured. The one skipped no-match question follows the newly required click-to-identify route, but remains a mismatch against the fixed oracle. Controls question-change-days and refusal-unidentified-visual hold; the original scorer does not credit their disposition. No expectation was edited. By base class: family26/26, question2/3, refusal6/7, visual4/4. Every selected row retains its source revision and score hash.

Two live harness startups failed before a ticket or estate request: first a private artifact path typo, then rebuilt lineage approval rejected the changed whole-manifest hash. Both logs are retained. DECIDED WITHOUT REVIEW: revalidate and explicitly reapprove the existing sampled lineage witnesses under the approved output-budget-only manifest, instead of repeating estate verification for an allowance change. The script asserts that the output allowance is the only difference; witnesses remain identical and the original approval is archived. No new snapshot or current-data claim. Original installation disables code inference and needs no lineage approval. Rebuilt new approval SHA-256 af64188ae1a1c24af38f5ffa37e69b4fdd01d101ac4e74e199b58311c134a276.

Live plan: eighteen fixture-authored forms, one base family per original/rebuilt estate, with fixed expectations preserved. Starting shared pot1,150/1,500, restoration reserve95, ordinary remainder255; diagnostic cap12. Upper physical estimate288 exceeds that remainder, so the batch can stop and preserve a partial map rather than spend restoration capacity. Model-output allowance2.4M is temporary and will return to1.5M with charges intact. No billing run.

## Once-per-family live record, engine488664b

These are actual form attempts, not successful end-to-end investigations. No replacement attempt or gate bypass. Fixed expectations remain unchanged. A hold before procedure earns no expected technical outcome.

| Estate / family | State | Reason | Physical | Model calls | Input characters | Seconds |
|---|---|---|---:|---:|---:|---:|
|original:family-A|HELD|Selected report is absent or ambiguously bound|0|0|0|29.91|
|original:family-B|HELD|Selected report is absent or ambiguously bound|0|0|0|26.44|
|original:family-C|HELD|Selected report is absent or ambiguously bound|0|0|0|27.39|
|original:family-D|HELD|Selected report is absent or ambiguously bound|0|0|0|28.15|
|original:family-E|HELD|Selected report is absent or ambiguously bound|0|0|0|26.83|
|original:family-F|HELD|Selected report is absent or ambiguously bound|0|0|0|27.5|
|original:family-G|HELD|Selected report is absent or ambiguously bound|0|0|0|28.78|
|original:family-H|HELD|Selected report is absent or ambiguously bound|0|0|0|27.77|
|original:family-I|HELD|Selected report is absent or ambiguously bound|0|0|0|27.38|
|rebuilt:family-A|HELD|Dynamic investigation needs current approved discovery policy|0|1|11843|55.43|
|rebuilt:family-B|HELD|Dynamic investigation needs current approved discovery policy|0|1|11838|41.88|
|rebuilt:family-C|HELD|Dynamic investigation needs current approved discovery policy|0|1|11823|39.19|
|rebuilt:family-D|HELD|Dynamic investigation needs current approved discovery policy|0|1|11897|34.37|
|rebuilt:family-E|HELD|Dynamic investigation needs current approved discovery policy|0|1|11893|36.28|
|rebuilt:family-F|HELD|Dynamic investigation needs current approved discovery policy|0|1|11876|33.4|
|rebuilt:family-G|HELD|Dynamic investigation needs current approved discovery policy|0|1|11932|32.88|
|rebuilt:family-H|HELD|Dynamic investigation needs current approved discovery policy|0|1|11905|34.96|
|rebuilt:family-I|HELD|Dynamic investigation needs current approved discovery policy|0|1|11831|33.78|

Completed investigations: 0/18. Physical requests 0; model calls 9; reserved input characters 106838. No probe, surface attestation, boundary comparison, investigation planner call or synthesis output exists for a pre-procedure hold. No business/technical output is invented for it. Original ticket histories, provider bodies, sealed forms, failure logs and per-attempt ledger rows are preserved.

Original models are disabled in the shared catalog after the rebuilt collection. Both manifests share that catalog; the current enabled set contains only the two rebuilt models. Original definitions remain retained. This is a catalog activation/state mismatch, not evidence that the original platform reports vanished. Rebuilt forms reach scope adoption, but their preview refuses current discovery-policy approval. The separate sampled-lineage budget reapproval did not reapprove discovery. No model was enabled and no discovery gate was bypassed.

The upper physical estimate was288; actual estate requests0. The shared pot stays1,150/1,500, remaining restoration reserve95, ordinary remainder255. Rolling allowance3,000 and diagnostic cap12 are unchanged. No billing run, owner-unaided demo, latency finding or general capability verification is earned. The blocked demo command and terminal requirements are recorded in [the handoff](round-twelve-d-demo-handoff.md).

Validation: frozen488664b full regression ran2,855 tests in1,003.166 seconds and failed one obsolete expected exception. All other2,854 passed. The identifier test now requires IDENTIFIER_QUOTE_INVALID and verifies the input is untouched; all44 extraction tests pass after that test-only correction. Production engine hash is unchanged. The failed full-run log remains retained; no second complete full-run claim is made.


Temporary output allowance restored on both manifests:2,400,000 ->1,500,000. Shared daily counters preserved:274 model reservations,3,466,493 input characters,1,899,500 output tokens. The restored output limit is already exceeded; further calls must hold until reset or a new explicit approval. The overrun guard remains on. Original sampled-lineage approval restored after archiving the batch approval. No counter reset or identity/permission change.
