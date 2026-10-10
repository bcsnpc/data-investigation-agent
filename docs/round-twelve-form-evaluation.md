# Round Twelve form evaluation — 2026-10-10 UTC

**The form quality gate failed.** This is a completed controller evaluation of
all68 unchanged sealed records, not a model-quality or live-investigation result.
Source bc79db9, engine hash
`6ca6954dc213b44bc4a446df31c26d47062da639217485793cdf30436acc6e54`.
Oracle seal `be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c`
and dev40/held28 split are unchanged.

| Column | Evaluated | Correct one-round settlements | Questions | Mean | Illegitimate questions | Harmful admissions |
|---|---:|---:|---:|---:|---:|---:|
| Development |40|1/40|35|0.875|35|0|
| Held-out |28|1/28|28|1.000|28|0|

| Class | Dev settled / tickets | Dev questions | Held settled / tickets | Held questions |
|---|---:|---:|---:|---:|
| Family |0/26|21|0/22|22|
| Question |0/3|3|0/1|1|
| Refusal |1/7|7|1/3|3|
| Visual |0/4|4|0/2|2|

All68 stopped:63 after an offered question the sealed oracle did not authorize
answering, with USER_INFORMATION_UNAVAILABLE retained; five at
TARGET_NOT_EXECUTABLE. No scope was adopted. Zero harmful admissions therefore
does not establish useful accuracy. Every failure and refusal has its own ledger
row and tape, including the question and original description.

## What this actually tests

Form selections came from determined oracle fields; the description is the
original ticket byte-for-byte. No target or comparator was substituted for an
unknown, inapplicable or unrepresentable field. Runtime metadata came from the
independently preserved catalog/context, never from oracle proof material.
The simulator answers only legitimate questions with a single authorized choice.

The current form has no fully determined report-visual-plus-external-comparator
case in this oracle. Thirty-four tickets determine MEASURE_AT_SCOPE rather than
a visual. Fifteen determine a visual but need DECLARED_SUBJECT, an internal route
the form does not offer. Remaining targets are not applicable or undetermined.
Zero-question settlement for fully representable forms is **not assessable (no
cases)**, not a passing zero denominator. These are coverage failures; the oracle
and expected dispositions have not changed.

The controller requires a bound visual and comparison before interpreting the
description. Consequently these68 never reach its provider path: **zero new
model calls and zero input characters**. The configured deployment in the plan
is investigator-quality-54 with manifest options; no unadopted F55 override was
used. This run provides no evidence about description extraction accuracy.
Model-only subjects, declared-subject routing and description handling before
redundant clarification need to be resolved before this form covers the oracle.
Description conflicts currently hold rather than offer the required one-click
choice; additional text restrictions are preserved as refusals, not erased.

## Retention and controls

Private artifacts are in `.local/round-eleven/round-twelve-forms-bc79db9-v3/`:
forms.json, plan.json, results.json and68 individual audit.tape.json files.
Results SHA256 `7d71bdddd10d7f38e54f52f6429f35c52900d4ad447346cbd23922fdb399bf2a`;
derived forms SHA256 `abeda4436eefdeffc57fc2431956c41f9ec75d3d169475c111c1676ef834f09d`.
Public per-case scores: [development](evals/round-twelve-form-dev.json) and
[held-out](evals/round-twelve-form-held.json). Ledger experiment ROUND_TWELVE_FORMS
has68 rows. Two earlier runner preparation failures are preserved separately:
preflight incorrectly used the raw synthetic catalog without report cells; the
second exposed an oracle route not in the form enum. Neither dispatched a model
or estate request. The final runner uses the actual retained snapshot and records
unrepresentable fields explicitly; it invents neither a route nor a tolerance.

Browser check used a loopback host with execution disabled: report, page and
visual selectors loaded; the unsupported route is visibly coming soon; manual
refresh retained the entered16 but reset report selection. The list explicitly
said retained approved context, not live Fabric. No form submission, report edit,
tester ticket or estate request was made by that browser check. This is not the
live end-to-end demo.

New estate physical requests0, diagnostics0, model calls0. Round pot remains
1,142/1,500, restoration reserve95; rolling usage129/3,000 at this checkpoint.
The existing UTC-day model charges remain32 calls/400,030 input characters;
counters were neither reset nor increased. Live form investigations and billing
scoring have not run. Independent tester15 and owner-authored18 remain separate;
six independent unplanned-rendering tickets remain pending owner/reviewer
expectations. No invented combined score. Draft #423 remains draft; freeze
invalid. Full regression on bc79db9 passed2,788 tests in625.746s, native exit0;
retained log `.local/round-twelve-form-integrated-full.txt`. This is the required
after-form-scoring report, not round completion.
