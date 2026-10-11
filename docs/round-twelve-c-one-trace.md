# Round Twelve C: one admission trace

Recorded 2026-10-09 America/Chicago / 2026-10-10 UTC. Source: a0c5f49. No engine, adapter, test, policy, oracle or expectation was changed for this investigation. No new model call or estate request was made.

## Dev pass: still blocked, not completed

At 2026-10-10 04:50:44 UTC, a reservation using the corrected 8,000-output-token bound still raised `UsageHold: Provider usage exceeded reservation`. This was a reservation-only check inside a transaction that was rolled back; no provider request was dispatched and no reservation was added.

The governor checks for any `VIOLATION` in the current environment and UTC day before admitting further non-restoration work. The preserved 2026-10-10 row is `intake:e655922d-4502-4d67-b448-d68bf794e324`, reservation `resolve`: 1,500 output tokens reserved, 2,504 actually used. Correcting the bound for subsequent calls does not clear that day's latch. The original row remains unchanged. This latch ceases to apply to new work on the next UTC day, 2026-10-11; no clock, environment or counter was changed to bypass it.

The only fresh dev evidence remains the stopped pass: eight attempted records out of forty, four provider calls, 50,812 input characters, zero estate reads. Seven attempts retained a ticket outcome and one failed before provider dispatch. Thirty-two records were not attempted.

| Metric | Observed partial dev pass |
|---|---:|
| Correct settlements with zero questions | 0 |
| Questions offered | 3 |
| Illegitimate questions | 3 |
| Harmful admissions | 0 |
| Not measurable because definitions were missing | 0 |

These are partial observations, not completed forty-record scores. Two attempts stopped on the reservation problem; those are budget failures, not missing-definition cases. The retained-definition audit found no missing definitions across the dev inputs. The thirty-two unattempted records have no measured outcomes. Held-out was not run.

## Which record can honestly be traced

There is no saved evaluation form with report, page, visual, comparison and value all supplied: inspection found zero in the original 68 inputs and zero in the later 40 dev inputs. A known subject is not necessarily one of the form's five comparison choices. In particular, a reproduction question leaves that comparison field blank rather than inventing an application, freshness or discrepancy comparison.

To avoid fabricating a scored record, this document separates two traces: the existing complete-form regression fixture, which exactly matches the requested input shape, and the closest actual retained estate record, which shows where scoring really stopped. The fixture is not added to the oracle or counted in dev accuracy.

## Complete-form regression fixture: admission succeeds

Source: `scripts/test_form_controller.py`, `test_complete_form_adopts_without_model_or_fake_confirmation`. Its existing setup and submission were executed unchanged in a temporary test workspace. The saved trace is `.local/round-twelve-c-one-trace.json`.

### 1. What was submitted

```json
{
  "version": "estate-form-input-v1",
  "request_key": "form-submit",
  "report_id": "report",
  "page_id": "page",
  "target_id": "card",
  "cell_mode": "UNGROUPED",
  "value_seen": "16",
  "comparison": "LOOKS_WRONG",
  "description": ""
}
```

### 2. What definitions were loaded

This is a synthetic regression catalog, not a discovery of the live estate. It binds Report / Overview / Global card to the Quantity measure. The card has no grouping columns, is supported, and has a `COMPLETE` declared scope with an explicitly empty restriction list. The test supplies context and inventory seals. It does not supply or fetch a DAX measure expression: admission here consumes the catalog's binding and complete-scope declaration, not an executed measure or its numeric result. That is the limit of this fixture's evidence.

### 3. Admission checks, in execution order

1. **Host admission:** the form controller checks that this host permits intake. The test workspace permits it. Passed.
2. **Input shape:** the closed form schema requires the declared fields and valid enums. All fields and the ungrouped mode satisfy it. Passed.
3. **Preserve input:** the ticket store retains the exact form and the current catalog hash. This is a new request, not a changed resubmission. Passed.
4. **Comparison availability:** `LOOKS_WRONG` must be one of the estate's configured choices. It is. Passed.
5. **Report binding:** exactly one retained model must bind the selected report. Model does. Passed.
6. **Page binding:** the picked page must contain retained visuals belonging to that report. Overview does. Passed.
7. **Visual binding:** the selected visual must be exactly one visual on that report and page. Global card is. Passed.
8. **Executable measure:** the visual must be supported and declare a starting measure. It declares one, Quantity, so no measure ambiguity remains. Passed.
9. **Cell scope:** an ungrouped card must use ungrouped mode. There are no row keys to type-check or supply. Passed.
10. **Reported figure:** the value field is parsed as the exact number 16, with its source span in the submitted value field. No tolerance or query result is substituted. Passed.
11. **Description interpretation:** the description is empty, so there is no model interpretation to obtain and no conflicting description to settle. Skipped by the declared empty-input branch, not treated as model agreement.
12. **Complete declared scope:** `form_scope.build` requires this visual's scope to be marked complete and its restrictions to be composable. The explicit empty list passes. Missing scope evidence would refuse here; an absent list is not treated as an empty one.
13. **Authority proof:** the engine constructs and schema-validates hashes of the request, catalog and generated document, plus report, page, visual, measure, mode and declared-scope evidence. Passed.
14. **Provenance and subject:** the figure source points to the value field; the question subject points to the configured selected-comparison text. Passed.
15. **Adoption freshness:** `_adopt_form` compares the current catalog hash to the submission's saved hash. They agree. Passed.
16. **Consumer recomputation:** `question_intake.validate` rebuilds the proposal from the form and metadata, and requires exact proposal and document equality. It then checks completeness of any keyed cell; this card is ungrouped. Passed.
17. **Route admission and save:** the existing question-kind route accepts this figure-difference request. The intake is saved as `PROPOSED`, with `SAVED_USER_SUPPLIED_FORM` provenance and zero provider calls. Passed.

### 4. Where it ended

The scope was admitted. There were zero questions, zero model calls and zero estate reads. The ticket remains `NEW` with an attached admitted intake because this test explicitly has automatic investigation start disabled. That state is not an admission refusal. No reproduction or investigation result is claimed.

## Actual retained estate record: original:visual-1

The saved request picked Round Ten Visual Variety, page Global card, visual Handled Quantity - unfiltered, ungrouped mode, and value `8765`. It left comparison null. Its description was:

> In Round Ten Visual Variety, on page Global card, the Handled Quantity shows 8765. Can the saved declared context reproduce that figure?

The exact request and saved history are retained in `.local/round-eleven/round-twelve-forms-bc79db9-v3/`; the inspection extract is `.local/round-twelve-c-real-trace.json`. No field was filled in retrospectively.

The retained model context is `0bbcfa54-2023-4f59-87ce-9f62662f4a98`, SHA-256 `beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6`. The context seal was checked against the stored body. It contains the selected page at `definition/pages/99d9ca357e3792ad6f70/page.json` and selected visual at `definition/pages/99d9ca357e3792ad6f70/visuals/45e0a944d0425fec09d0/visual.json`, alongside the report/model definitions. There were no parse errors in the collected report parts.

The selected card declares one measure, Handled Quantity. The retained measure expression is `SUM('Activity'[units])`. The card has no grouping columns; its declared scope is complete with no restrictions. Its inventory hash is `c2b1e2d94dea8733546219d91ab7d1ba5075c08c6043c8839cfd300d5b8832ab`. These facts establish the declared measure and scope, not that its current live result equals 8,765.

In the saved older evaluation, report, page, visual, supported single measure and ungrouped mode passed preflight. There were no cell keys to check. **The exact stop was the missing-comparison check in `form_intake.resolve`, before parsing the supplied value and before reading the description.** It returned `NEEDS_INPUT` for `COMPARISON`. The old controller immediately asked “What are you comparing against?” with the five public choices. The oracle could not authorize one: this was a reproduction question, not an external comparison. The simulated user marked comparison unavailable; the ticket became `HELD`, reason `USER_INFORMATION_UNAVAILABLE`. No scope was adopted, no model was called and no value was queried.

That is a form-routing failure, not missing definitions, a failed query or a non-matching value. Current code now interprets the description before asking from this preflight result and can represent the internal declared-subject route. This particular record has not had a fresh corrected dev pass; the present budget latch prevents one. Its historical result is unchanged.

## Answers

**What must be true to admit scope?** The supplied report/page/visual must bind to current retained metadata, the starting measure and cell must be unambiguous and supported, all keyed dimensions must be supplied and typed, the declared restriction set must be complete and renderable, the question must have a supported comparison or declared-subject route, and any reported value must retain its stated precision and provenance. A nonempty description must have a validated interpretation consistent with the picks, or an explicit user decision resolving the conflict. The consumer must be able to recompute the same proposal from unchanged inputs and metadata.

**Does admission require live data or a value match?** Not for an explicitly picked visual with a complete retained scope. The supplied number is an allegation to investigate; it does not have to equal a live result before intake can admit it. Live evaluation belongs to reproduction and investigation. A different, unfinished route for an omitted visual selected by numeric matching would require value probes; it is not a universal admission requirement and was not used here.

**Is zero admission one shared cause?** In the old completed 68-form evaluation, the shared ordering defect was asking from form preflight before interpreting the description; its target/comparison questions prevented defined subjects from reaching admission. There were additional target-shape refusals, so it was not the sole reason for every hold. In the later eight-attempt dev pass there is no single common cause: three B records asked for a target, three D records hit the old multi-measure target refusal, and two E attempts hit the reservation violation/latch. Narrow fixes now exist, and three retained B proposals rebuild under the corrected contract, but that is not a fresh dev score. Scope admission is possible, as the complete-form fixture shows; zero observed admissions does not establish that live data is required.

Stopped after this trace and report. No held-out, live, billing, fixture or scope change followed.
