# Round Eleven B: fixed conversational oracle

Owner Chiranjeevi Bhogireddy and independent reviewer Claude approval was
confirmed by the human on 2026-10-09. The accepted diff is now sealed. Its exact
reviewed file remains unchanged, including the historical draft labels; approval
is the separate `acceptance/oracle/oracle-seal.json` record.

Approved oracle SHA-256:
`be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c`.
The original 40-development / 28-held-out split and all golden records are
unchanged. No further oracle amendments are permitted in this phase.

The evaluator uses only approved answers, refuses unapproved or non-unique
choices, checks adopted target, cell keys, scope, figure, precision and route,
and counts illegitimate questions separately. Adoption does not prove correctness.
Keyed scope is compared through the consumer's validated singleton filters.
Visual equivalence requires the reviewed complete-definition proof, not merely
a shared measure. Transport and budget holds receive no semantic refusal credit.

Historical responses from frozen 44490b4 are rescored separately in
`round-eleven-oracle-historical-baseline.json`. This is a historical baseline,
not a fresh run of the corrected engine, and its consequential differences are
audit flags rather than silently declared causal harmful errors. Original tapes
and prior scores remain intact. Development work uses development cases only;
held-out is reserved for the final frozen pass.

## Final frozen text evaluation, 2026-10-09

All 68 unchanged tickets completed, development first and held-out once, on
`cc7dfd2`, engine hash
`6c9747075363a79f3141f36098fd5568cb44a845c79409f0c55327a9ce734228`.
No runtime changes were made during the pass, and no fix used held-out results.
The simulator answered only a uniquely offered choice authorized by the sealed
oracle; otherwise its abstention and the resulting hold remain recorded.

| Metric | Development | Held-out | Requirement |
|---|---:|---:|---|
| Settled within one round | 20/40 (50.0%) | 10/28 (35.7%) | Held-out at least 24/28 |
| Questions | 25 | 24 | Mean at most one per ticket |
| Mean questions | 0.625 | 0.857 | At most 1.0 |
| Illegitimate questions | 17 | 24 | Zero |
| Raw consequential admission flags | 1 | 1 | Zero; provenance audit below |

**Quality gate FAILED.** The lower question count meets the average bound,
but it does not excuse unnecessary questions. No general rehearsal, fifty-ticket
investigation batch or screenshot phase follows this result. #423 stays draft.

| Class | Dev settlement | Held-out settlement | Dev questions / illegitimate | Held-out questions / illegitimate |
|---|---:|---:|---:|---:|
| Family variants | 10/26 | 6/22 | 16 / 10 | 18 / 18 |
| Question | 2/3 | 1/1 | 1 / 1 | 0 / 0 |
| Refusal | 4/7 | 1/3 | 8 / 6 | 6 / 6 |
| Visual | 4/4 | 2/2 | 0 / 0 | 0 / 0 |

Under this same oracle the historical 44490b4 responses scored dev15/40 and
held7/28, with question means0.975/1.143 and illegitimate questions31/32.
The fresh result is20/40 and10/28, with means0.625/0.857 and17/24 illegitimate
questions. This is not a controlled attribution to one fix: the fresh evaluation
also supplies independently pinned complete metadata as described below.
The earlier one-shot scores remain a distinct test, not relabelled as this score.

## Development changes and limits

- Matrix addresses use declared Rows/Columns axis order rather than sorted
  identifiers. Exact typed keys become consumer filters; missing axes, wrong
  arity and ambiguous column hints stay unresolved. A named or user-confirmed
  single-axis matrix can supply its declared key; ordinary columnless selections
  on an ungrouped card still remain selection requests.
- Target hints narrow candidate sets without choosing the first shared title.
  A confirmed single-measure card can supply its retained measure binding when
  the model extracted an unresolved label. Competing resolved measures remain
  preserved and cannot be silently discarded.
- Redundant visual clarification is avoided only when every candidate has a
  complete, validated declaration inventory, the same pinned context and empty
  equivalent restriction sets. The result is a measure-at-scope, not an invented
  visual target. A shared measure or missing definition is insufficient.
- Explicit application asks and internal definition questions carry their own
  evidenced route; configured defaults cannot override required confirmation,
  competing external comparisons or business intent.
- Scope proofs are code evidence. Adding them initially made a legacy wire view
  exceed its60,000-character bound. Removing code-only proofs from that model
  view preserves directory coverage and the previous wire bytes; the actual
  ticket-only model request remains bounded at20,000 characters.

Runtime still does not express the oracle's figure-only and report-or-screenshot
question forms. Some holds ask NUMBER/COMPARISON instead of resolving facts from
the retained definitions, and some genuinely unsafe/unsupported tickets receive
unrelated clarification instead of their specific refusal. Those remain scored
failures. The visual class passing six cases is not a general intake claim.

The runtime catalog definitions came from the existing read-only local
`unknown-domain-v4/catalog.sqlite`: exact stored context hashes were checked,
with native ownership copied from those retained control records. No definition,
scope proof or answer was copied from oracle truth into runtime. Original ticket,
golden and split hashes are unchanged. This enriches the earlier synthetic name
catalog with independently retained definitions; it is not an estate recollection
or proof of current data values. Context IDs/revisions and full capture bytes
are in the sealed private plan/tapes.

## Admission flag audit; no score changes

| Ticket | Raw flag | Retained ticket evidence | Finding |
|---|---|---|---|
| original:family-E-mention, dev | reported_figure | “The global Handled Quantity currently shows 8765.”; exact span169:173 | Oracle says NOT_STATED; proposed8765 is genuinely quoted. |
| original:family-G-mention, held-out | reported_figure | Same sentence; exact span218:222 | Same fixed-oracle discrepancy; inspected for reporting, not tuning. |

Both proposals retain EXACT precision and choose8765, not the separately labelled
tracking reference4182. The audit did not establish an invented number or wrong
referent. Nevertheless both raw mismatches remain failures under the approved
fixed test. No oracle edit, score override, expectation change or deliberate
discarding of a supplied figure was made to force a pass. This audit is not a
claim that the engine has proven general zero harmful error.

## Recording and validation

Fresh intake evaluation:82 recorded model calls,1,026,165 transmitted input
characters, zero physical estate requests, zero diagnostic or guard reads, no
transport exceptions and no early stop. Model reservations before/after were
436→518 of600 calls and6,373,491→7,399,656 of8,000,000 input characters;
output reservations ended777,000 of1,500,000. No allowance or counter changed.
The fixture demo's usage is recorded separately.

Every ticket has a sealed tape, retained request/response/history and one ledger
row. Original tapes remain unchanged. Sanitized complete per-case grades and
capture hashes are in [the result map](round-eleven-oracle-final-results.json).
Raw captures stay local under `.local/round-eleven/oracle-final-cc7dfd2`; the
runner is pinned by SHA256
`b5e03c075f516ac5b74b9eb42132b58e6f6da3e8256dbfc01bcccae8fa6fdd33`.

The first full suite reported2,702 tests with two failures asserting superseded
behavior. Test-only commit`d3feb29` retains the ordinary unbound-selection
refusal and asserts an explicit application route is evidence, not a configured
default; required confirmation still refuses. Fifty-three focused tests passed,
and the corrected full suite reports2,702 tests OK. The runtime fingerprint is
byte-identical to the scored revision. The PowerShell tool wrapper returned1
despite the latter unittest OK report; the native child exit was not separately
captured, so no native-exit0 claim is made. Earlier interrupted, dirty-source and
fixture failures remain in private logs; none counts as a passed full suite.
Eighty focused intake/oracle tests passed before freezing the evaluation, and
the clean synthetic auto-start/tape lifecycle suite passed33 tests on82b8582.

Zero-new-call development audits using historical responses are retained
separately. They are not fresh quality samples. The initial catalog-size failure
and its failed attempts remain visible. All earlier freezes are invalid.

DECIDED WITHOUT REVIEW: retain exact approved artifact bytes and attach approval
in a hash-checking sidecar rather than rewriting historical draft metadata. This
keeps the reviewed hash and every substantive record immutable.

DECIDED WITHOUT REVIEW: enrich the synthetic name catalog only from separately
sealed local discovery definitions so the engine can independently establish
scope equivalence. Rejected copying the approved oracle's proofs into runtime,
which would make the evaluator supply the answer it is meant to test. Keep the
historical baseline and disclose the changed metadata input.

DECIDED WITHOUT REVIEW: replace the two obsolete unit assertions with tests of
the intended new declaration/route rules while preserving unresolved-selection
and must-confirm safety checks. No golden or acceptance expectation changed,
and no runtime edit was made while held-out scoring was in progress.

## Separate post-score demo defects

After all68 scores were complete, the fixture demo exposed two defects outside
intake. They do not alter, invalidate or replace the recorded cc7dfd2 scores,
but the broader current engine has changed and is not a newly passed quality
sample.

The engine echoed an appended structured report-link field into business prose,
which correctly failed identifier validation. Commits1c0a9f8/53005e4 render the
business question without that appended block only where the existing declared
reference's document hash and exact span prove it. Raw input, original question,
reference and full URL remain in evidence and technical output. No heuristic
identifier stripping or vocabulary-rule relaxation is used; unsupported user
identifiers still refuse. Completed-cell refusal delivery uses the same view.
Eighty focused output/refusal/input tests passed. The original mechanism and
observations were separately re-composed offline with zero reads or model calls;
the original live failure remains unchanged.

The original fallback crash also rolled back final model-reservation settlement,
leaving a finished provider call RESERVED. Commit7d52c10 commits non-refundable
provider accounting independently before fallible final rendering, and records
a fallback failure rather than letting it escape. A regression proves both
attempts remain charged, no planner slot stays reserved, and another legitimate
call can reserve normally. Sixty-six synthesis/question tests and32 governance
tests passed with native exit0. The initially invalid synthetic output reservation
and mistaken test-module invocation are retained as test failures.

DECIDED WITHOUT REVIEW: reconcile only the stranded completed demo reservation
from its sealed provider receipt through the existing governor.settle API.
No conservative charge, cap or counter changes. Rejected raising concurrency,
resetting usage, rewriting receipts or silently inserting offline output as live
synthesis. Its ledger control states exact before/after and receipt provenance.
The same unstarted NEW ticket can resume without a replacement. See
[the separate demo record](round-eleven-demo-flow.md) for live/offline/UI limits.

DECIDED WITHOUT REVIEW: make the post-score renderer and accounting corrections
against the fixture demo's retained evidence, independently of the failed
held-out intake cases. The original oracle and every score remain fixed.

## Final validation and independent demo

Frozen source `7d52c10` passed all 2,707 regression tests in560.516 seconds,
with separately captured native exit0. ResourceWarnings about unclosed test
databases remain visible in the preserved log; no failing test was suppressed.
This validates the implementation regressions, not the failed quality gate.

The independent fixture-link API demo reached validated synthesis, shared
findings, a retained-explanation reply and fixture-author simulated closure.
Its final run used4 diagnostic reads,11 physical requests and4 model calls.
The result was TRANSFORMATION_LOGIC, partly answering the application question:
semantic/serving8,765 versus refined7,661. Snapshots remain unverified; LANDING
and application were unchecked. Browser interaction and the screenshot smart
bridge remain incomplete. Both final outputs are quoted verbatim in
[the demo record](round-eleven-demo-flow.md); all earlier failures are preserved.

Final usage: model527/600 calls and7,480,697/8,000,000 input characters;
read pot1,035/1,500, rolling22/3,000, restoration reserve95 unchanged.
No identity, permission, secret, fixture or budget changes. #423 remains draft.
