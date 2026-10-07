# Model-step evaluation inputs

`intake.json` contains 60 explicitly authored synthetic texts and structured
expectations: six phrasings per family plus six expected semantic holds. The
catalog is synthetic; neither fixture query answers nor model responses supplied
the expectations. No expected record is sent to the model.

Scoring consumes saved intake records, including their original attempt list:

```powershell
python scripts/score_model_steps.py --model-version <recorded-version> --golden acceptance/model_steps/intake.json --records <recorded-intakes.json> --thresholds acceptance/model_steps/thresholds.json --previous <prior-score.json> --output <score.json>
```

Each recorded entry has `case_id`, `model_version` and the saved `intake` body.
Unknown IDs, duplicates and mixed model versions refuse. Missing cases reduce the
score and fail completion. Provider/budget/transport HELD is not a correct
semantic hold; NEEDS_INPUT on a should-hold case is reported separately. Retry
rate uses recorded attempt counts, never a clean replacement response. The golden set is hash-pinned in every score; a changed expectation set cannot
be compared to the old baseline. Non-semantic provider failures score zero,
including fields whose expected value happens to be null. Threshold
changes require a reason. The provisional two-percentage-point drop limit is a
regression ratchet, not a statistically calibrated accuracy guarantee.

The four scorer tests use synthetic records and do **not** establish any model's
accuracy. Actual first scores, reader/synthesis/translation suites and the ten
human readability grades are pending. AI-generated flags must not be labelled
human grades. This is not yet the complete four-step CI quality gate.


`reader.json` carries three Round Six synthetic code examples and six newly
written dynamic-name/UDF examples, with hand-authored pre-verification bindings.
Two new constant-name examples are also successful static controls; four require
fallback. No row values or query answers enter this set. Reader scores report
binding precision/recall and semantic refusals separately, with invalid and
duplicate proposals counted against precision. They do not verify a binding.
The same offline CLI selects the scorer using the golden set's `step`.

`synthesis-recorded.json` contains the fifteen inferred-column cases' sealed
composition excerpts, exact wire schemas, supplied role tokens, boundary facts
and source hashes. It contains fourteen model responses; family C has no model
mechanism and is explicitly unscored. Under current validation, thirteen of
fourteen responses pass (92.857% token/form validity, 7.143% rejection rate).
The source-latency response uses an unqualified "semantic layer"; its completed
output used deterministic delivery wording. This score neither certifies causal
truth nor changes any historical gate expectation or receipt. It is the first
recorded-response score, not a new provider benchmark; no prior delta exists.

[Ten exact paragraphs with their checked facts](synthesis-human-review.md) are
ready for human readability grading. The structured booleans remain null and
have no grader. `score_human` refuses missing or nonboolean grades and requires
an attributed human grader on each of ten distinct items. AI flags are not
substituted. `export_synthesis_eval.py` extracts such examples read-only from
fifteen sealed tapes; private complete requests remain outside the repository.

All model-step integration is still incomplete: intake/reader/translation first
provider scores and human readability grades are pending. CI currently tests the
scorers and their invariants; it is not yet the requested four-step score gate.
