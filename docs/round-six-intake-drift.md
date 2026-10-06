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

## Section 2 completion checkpoint

The committed `ad47c58` engine passed 2,027 complete regression tests. The initial
failed sweep is preserved: twelve golden prompt mismatches, eleven uncommitted
engine refusals from the recorder, and one transient replay setup count of four
calls rather than six. Removing the unnecessary initial-prompt addition and
committing the engine resolved the known causes; all 42 isolated recorder/replay
tests and the complete committed sweep passed. No refusal was weakened.

Regrading the two preserved intake decisions under the current consumer accepts
declared EMPTY and rejects inferred UNSPECIFIED for correction. This found a false
positive: the dash in the visual's title was also inventoried. The final refinement
requires a dash to be stated as the shown value. A named test asserts that the
exact EMPTY ticket matches only `nothing` (128:135) and `empty` (151:156), not the
title separator. Twelve new tests plus seven quote-retry and four golden tests
pass (23). The final correction input is 35,353 canonical characters, a 224-character
increase; the earlier 284-character measurement above is retained as the
pre-refinement result. Initial input and all catalog coverage remain unchanged.

The initial wire stays byte-exact. No figure is synthesized by this validation,
no tolerance is introduced, and both original runs remain unchanged. Ordinary CI
was six green checks on `ad47c58`; final refinement CI and archived regrade are
tracked separately. No I live request has occurred. Prior freezes invalid;
15x2 unearned, #410 draft. This is the required report before live work.

## Final I result: changed-result stop

The archived declared column regraded 15/15 with zero estate reads. This replays
the original producer revisions, not the new engine. The only I live attempt was
EMPTY against report-14sep using the unchanged stripped manifest and single pin.
Intake `1b844035-f362-40b2-aada-19ceaeb8a811`, sealed tape
`4b2965df-b9cc-49e7-9645-9e2938151f7b`, producer
`c0b3d5b01468b6294d80a4565bc8e9e2c0f1b60a`, stopped NEEDS_INPUT before a session
was created. Tape SHA-256:
`0ae91c97b3a09d05e2dfd3219f34ab11e2aa5a4feef09cf6045353bca1310f46`.

The first response again emitted `reported_candidates: []`. The new validator
rejected it, carrying `nothing` at 128:135 and `empty` at 151:156 into the
independently reserved, recorded retry. The retry emitted:

```json
[
  {"role":"OTHER","quote":"20261001"},
  {"role":"FIGURE","quote":"shows nothing"},
  {"role":"FIGURE","quote":"the visual is empty"}
]
```

Both FIGURE quotes are verbatim, at 122:135 and 137:156. The unchanged reported
figure contract rejects any inventory with more than one FIGURE candidate before
choosing a value. These are two phrases describing the same visual in the ticket,
not two different measured numbers; the current contract nevertheless treats two
candidate spans as ambiguity. This is the next established blocker. It is not a
second omission, so the result is NEEDS_INPUT, not the new omission-specific HELD.
No third call, ambiguity weakening, replacement run or post-failure engine change
was made. The exact refusal is:

> More than one ticket span could be the reported figure. Which figure should be compared?

The explicit-statement rule worked live and both attempts were charged. It did
not earn reproduction. The failed result is independently byte-exact replayed
under its recorded producer with sockets blocked, including both intake responses
and deterministic refusal outputs. Tape replay matched; acceptance failed. Both
full refusal outputs are saved under
`docs/runs/round-six-i-reproduction-empty-business_output.txt` and
`docs/runs/round-six-i-reproduction-empty-technical_output.txt`.

| Authorized case | Result | Physical / diagnostic | Intake / investigation / synthesis calls | Pot |
| --- | --- | --- | --- | --- |
| EMPTY / report-14sep | NEEDS_INPUT; expected reproduction not earned | 0 / 0 of 12 | 2 / 0 / 0 | 265 → 265 |
| numeric16 / report-15sep | NOT_RUN: first changed result | — | — | — |
| source-gap | NOT_RUN: first changed result | — | — | — |
| source-consistent | NOT_RUN: first changed result | — | — | — |

There were no probes, execution surfaces, surface attestations, boundary reads or
comparisons in I. Synthesis did not run; intake rendered refusal outputs. No
prewarm or mutation occurred, so no restoration was required. Reader scopes,
policy, manifest, fixtures and original recordings remain unchanged. The first
live ledger row records the failure; an appended annotation specifies diagnostic
0/cap12 where the generic runner originally emitted null for a missing session.

Final column: archived15/15; inferred9 passed,1 failed,5 not run. H's nine family
attempts and failed EMPTY remain exactly as recorded; this authorized I attempt
has its own row and tape. The current matrix is `docs/runs/round-six-i-column.json`.
Nine family expectations matched on bounded code-derived verified lineage;
this includes C's expected HELD and does not mean nine full answers or global
equivalence. The H binding table remains in the one-context report and original
binding ledger. The [fifteen-binding table](round-six-per-binding-verification.md#preserved-proposals-zero-reads)
names each boundary, column and dependent family; the
[G completion evidence](round-six-last-two-engines.md#eight-remaining-profiles-2026-10-05)
records the final eight bounded witnesses alongside the seven preserved ones.
Every relevant boundary retains SNAPSHOT_UNVERIFIED.

Closing local usage: Round Six265/400,60 restoration reserved, ordinary stop340;
rolling310/1500. I added zero physical requests and two metered intake calls.
The final refinement's targeted/golden23 tests passed; complete local2027 passed
on its immediately preceding engine checkpoint. Final CI is tracked on #410.
No15x2 gate was earned, no new replay bundle or secret was published, and #410
stays draft/unmerged. README and roadmap delivery claims were deliberately not
updated. Prior freezes remain invalid; no unfamiliar-domain acceptance claim.
