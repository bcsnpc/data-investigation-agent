# Round Six I: explicit reported statements at intake

Offline checkpoint, 2026-10-05 America/Chicago. PR #410 remains draft. No I
estate request, provider call or fixture change at this checkpoint.

## Sealed intake comparison

Declared EMPTY session `6575058a-4f86-422a-92ff-2f3def6687c4`, tape
`4b863ffe-09fe-4978-a44c-d93183b05f8d`, used producer
`966ff027d32ce87953bb50bd14a76b02a5343082`. H session
`1f96ab15-e18c-4d5d-9732-0f79a15d072e`, tape
`645941a9-32cd-47e6-827f-34e009fa514e`, used `154b2c2`.

The canonical request arrays hash respectively to
`7a3cb01065749e0f90c3f92fac75d0e4e79e7658ce7a3e0fbd7fb60936baadbd`
and `73048117277a8274cbc6be3496ffb08dd5c8c7c7d2b7f7e0991c30def47af6e6`.
There are eleven leaf differences: five model context IDs and six model revisions.
The selected EMPTY model retains its report-14sep context ID; its revision changes.
Ticket text, initial instructions, response schema, deployment/settings, and the
remaining catalog content are identical. Whole-manifest discovery re-approval and
catalog projection/enablement bookkeeping in #410 account for the input changes.
The intervening #399 quote-retry refactor does not change this initial wire prompt.

The declared response inventories DATE `20261001` and FIGURE
`shows nothing (the visual is empty)`. Consumer extraction yields:

```json
{"state":"EMPTY","source":{"start":122,"end":157,"quote":"shows nothing (the visual is empty)"}}
```

H inventories no reported candidates and yields `{"state":"UNSPECIFIED"}`,
with no reported-figure quote span. It nevertheless classifies VISUAL_CONTENT and
quotes the empty statement elsewhere. Its BLANK read and failed acceptance remain
unchanged. Canonical bodies, original response extractions and the eleven-field
diff are preserved locally under `.local/round-six-i-20261005/`.

Different inputs preclude calling this proven identical-request variance. Neither
tape establishes that bookkeeping differences caused the omission rather than
sampling variance. The established defect is that an accepted interpretation can
omit an explicit reported statement without consumer refusal.

## Consumer rule and correction

`intake_statement_registry.py` owns the closed empty forms and shown-number
recognizer. A PROPOSE carrying UNSPECIFIED is rejected when the ticket explicitly
states a shown empty state or number. Matching preserves exact token spans; it
does not select a figure, invent a tolerance or populate a reported value.
Dates, report identifiers, negative signs and conceptual mentions are distinguished
from reported empty states. The same empty vocabulary validates figure provenance
and is supplied to the producer.

One correction shares intake's existing single retry allowance. Its rejection
reason and matching quotes reach the retry prompt; both attempts have separate
reservations, usage settlement and recording events. A second omission holds with
`INTAKE_OMITTED_EXPLICIT_STATEMENT` and the matching quotes, before data reads.
Exhausted allowance prevents correction without refund. ASK already fences
execution as NEEDS_INPUT; it is not forced to invent an unambiguous figure.

Eleven new tests and seven existing quote-retry tests pass. An old test double that
returned UNSPECIFIED for an explicitly shown 9 was corrected to supply that
figure's exact provenance; the new rule was not bypassed. Initial test failures
and invocation errors remain in local logs. Complete regression and archived
fifteen-tape regrade are pending; no live or 15x2 pass is claimed.

Initial intake instructions and schema remain unchanged. Twelve golden synthetic
requests match exactly; all 22 focused/golden tests pass. H's sealed initial
catalog has six models, 38 measures and 95 columns before and after, with 35,129
canonical input characters unchanged. It has no planner directory or SQL-object
directory (zero before/after). The correction adds 284 canonical input characters
(35,413), retaining every model/member; a test asserts unchanged catalog coverage.
The first full-suite attempt includes the unnecessary initial-prompt addition;
golden-test failures diagnosed it and that addition was removed rather than
changing golden expectations. Only the correction prompt receives the new terms.

## DECIDED WITHOUT REVIEW

Retained the current correct approval and catalog revisions instead of rolling
back context bookkeeping to imitate a historical request. The validator rule is
needed independently of the unknown sampling cause. Shared the existing one-retry
budget instead of allowing a quote retry followed by another omission retry.
Rejected changing the initial prompt: its existing explicit-empty instruction is
sufficient to state the producer's duty; consumer enforcement is the missing part.
No scope, identity, manifest, cap, counter, fixture or expectation changes.

Pot remains 265/400 at the last recorded control read, with 60 reserved and
ordinary work stopping at 340. Rolling last observed 310/1500; investigation cap
12 unchanged. Engine changes invalidate previous freezes. README and roadmap
delivery claims remain unchanged until the actual 15x2 gate merges. The remaining
authorized live list is EMPTY, numeric16, ingestion-gap and source-consistency,
one attempt each, with source prewarm/restoration recorded as controls and a stop
on the first changed result.
