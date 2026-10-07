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
