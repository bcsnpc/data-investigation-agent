# Round Twelve E questionnaire dev, 2026-10-10

Fresh dev only; held-out, oracle, goldens and live expectations unchanged. Each pass attempted the same46 mapped records. No estate requests. Unmappable required report/page or comparison picks are not measurable; none were invented. Original descriptions stayed verbatim.

| Pass / group | Measured | Zero-question settled | Questions | Illegitimate | Harmful | Not measurable |
|---|---:|---:|---:|---:|---:|---:|
|first / complete|28|5|6|3|16|12|
|first / visual-skipped|6|0|1|1|3|0|
|corrected / complete|28|24|1|1|0|12|
|corrected / visual-skipped|6|4|0|0|0|0|

## Why the first pass failed

Nothing was converted to LOOKS_WRONG regardless of the description. Definition questions acquired a discrepancy route; D received conflicting-comparison questions. The corrected mapper leaves this route unset when a description supplies the subject, using the existing validated extraction and preserving the picked target. Blank descriptions retain the generic complaint route. An explicit application comparison remains fixed. The old pass and every tape are preserved.

The mapper also refuses unknown/unrepresentable comparator picks. It cannot turn a missing pick into an authored Nothing selection. The description is not edited to make extraction pass.

## Model usage

- first: 38 calls, 487,665 transmitted input characters;46 attempts, zero estate reads.
- corrected: 38 calls, 487,240 transmitted input characters;46 attempts, zero estate reads.

## Corrected per-class score

| Group / class | Measured | Settled within one round | Questions | Illegitimate | Harmful |
|---|---:|---:|---:|---:|---:|
|complete / family|23|20|1|1|0|
|complete / question|1|1|0|0|0|
|complete / visual|4|3|0|0|0|
|visual-skipped / family|1|1|0|0|0|
|visual-skipped / question|1|0|0|0|0|
|visual-skipped / visual|4|3|0|0|0|

## Not measurable and remaining failures

- complete: original:family-E-noisy. See unchanged input construction and refusal in the retained attempt.
- complete: original:family-E-terse. See unchanged input construction and refusal in the retained attempt.
- complete: original:family-E-typo. See unchanged input construction and refusal in the retained attempt.
- complete: original:question-change-days. See unchanged input construction and refusal in the retained attempt.
- complete: original:question-stale-no-sla. See unchanged input construction and refusal in the retained attempt.
- complete: original:refusal-business-benchmark. See unchanged input construction and refusal in the retained attempt.
- complete: original:refusal-business-intent. See unchanged input construction and refusal in the retained attempt.
- complete: original:refusal-business-q49. See unchanged input construction and refusal in the retained attempt.
- complete: original:refusal-two-figures. See unchanged input construction and refusal in the retained attempt.
- complete: original:refusal-unidentified-visual. See unchanged input construction and refusal in the retained attempt.
- complete: original:refusal-unsupported-filter. See unchanged input construction and refusal in the retained attempt.
- complete: original:refusal-unsupported-relative. See unchanged input construction and refusal in the retained attempt.
- complete: original:family-H-noisy; state HELD; harmful fields []; illegitimate questions ['COMPARISON']. No expected answer changed.
- complete: original:visual-3; state HELD; harmful fields []; illegitimate questions []. No expected answer changed.
- complete: original:family-D; state HELD; harmful fields []; illegitimate questions []. No expected answer changed.
- complete: rebuilt:family-D; state HELD; harmful fields []; illegitimate questions []. No expected answer changed.
- visual-skipped: original:question-hiding-rows; state HELD; harmful fields []; illegitimate questions []. No expected answer changed.
- visual-skipped: original:visual-3; state HELD; harmful fields []; illegitimate questions []. No expected answer changed.

## Exact retained refusal reasons

- complete / original:family-E-noisy: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:family-E-terse: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:family-E-typo: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:family-H-noisy: USER_INFORMATION_UNAVAILABLE
- complete / original:question-change-days: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:question-stale-no-sla: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:refusal-business-benchmark: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:refusal-business-intent: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:refusal-business-q49: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:refusal-two-figures: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:refusal-unidentified-visual: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:refusal-unsupported-filter: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:refusal-unsupported-relative: QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented
- complete / original:visual-3: TARGET_UNRESOLVED: Every grouping column requires a stated cell key.
- complete / original:family-D: No executable retained choice for NUMBER
- complete / rebuilt:family-D: No executable retained choice for NUMBER
- visual-skipped / original:question-hiding-rows: TARGET_AMBIGUOUS: Primary-question evidence does not uniquely select a visual. Candidate visuals: Handled Quantity - extra visual predicate, Handled Quantity - page and slicers, Saved predicate selections.
- visual-skipped / original:visual-3: TARGET_UNRESOLVED: Every grouping column requires a stated cell key.

The first full accounting regression had one obsolete assertion (2,860 total); corrected governance tests passed. The frozen questionnaire source passed2,877 tests. Final routing correction passed158 focused tests including wrong-cell guards. The requested successful owner-unaided demo remains gated on the failed live expectations; see round-twelve-e-demo-handoff.md. Draft423 stays draft.

## Final picked-comparator guard and affected dev

Affected-dev combined:45 unchanged records from frozen1e1fb33; one fresh H-noisy from02cff87. Not a new full frozen pass. Originals remain superseded, not edited.

The model nominated a discrepancy for H-noisy despite its definitions ask; no admissible route followed. Asking for the already-picked comparator was wrong. The engine now holds DESCRIPTION_SUBJECT_UNRESOLVED without reasking it. Actual selection-versus-description conflicts retain their separate question route. A test checks the selected facts remain byte-identical. The fresh affected attempt is recorded separately.

| Group | Measured | Zero-question settled | Questions | Illegitimate | Harmful | Not measurable |
|---|---:|---:|---:|---:|---:|---:|
|complete|28|25|0|0|0|12|
|visual-skipped|6|4|0|0|0|0|

Affected attempt: 2 model calls, 26,574 input characters; zero estate reads. State NEW. All earlier passes and their failures are preserved.

Final focused159 tests passed; the prior frozen full suite2877 passed. No fresh held-out or billing run.

## Final affected-dev per class

| Group / class | Measured | Settled | Questions | Illegitimate | Harmful |
|---|---:|---:|---:|---:|---:|
|complete / family|23|21|0|0|0|
|complete / question|1|1|0|0|0|
|complete / visual|4|3|0|0|0|
|visual-skipped / family|1|1|0|0|0|
|visual-skipped / question|1|0|0|0|0|
|visual-skipped / visual|4|3|0|0|0|
