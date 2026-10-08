# Round Ten B: dated human decisions

2026-10-07. The human reviewed the eight mapping misses: six engine errors,
two expectation errors. Original ticket files, tapes, outputs and grades stay
unchanged. The separate hash-bound expectation correction records the two
authorised changes; it is not a rewrite of the original score.

| Cases / column | Decision | Required action and reason |
| --- | --- | --- |
| D-terse, D-typo / inference enabled; D-noisy, D-terse / inference disabled | Engine error | An explicit no-reported-figure procedure receipt must produce NO_REPORTED_FIGURE, rather than NOT_ANSWERED. Expectations unchanged. |
| F-terse, F-typo / inference enabled | Expectation error | CONSISTENT_TO_BOUNDARY / NOT_ANSWERED. Reason: "boundary consistency does not answer a mechanism question". |
| question-hiding-rows / inference enabled | Engine routing error | Reproduction is appropriate; a pipeline walk is not. Hold after reproduction with UNIMPLEMENTED_ROUTE until a bounded filter-effect route exists. NCP / REPRODUCED remains the placeholder expectation. |
| refusal-business-intent / inference enabled | Engine intake-kind error | A primary business-rule decision is BUSINESS_MEANING and refuses at intake. Technical evidence must never become an answer about business correctness. Expectation unchanged. |

The two saved F business outputs were inspected for the condition on their
expectation correction. Both state that the reachable values agree, but neither
explicitly says the source was unreachable. This is a separate output defect in
both preserved tapes; accepting NOT_ANSWERED does not accept that omission.

The human also explicitly approved whole-config discovery approval for the
240-to-600 daily model-call cap. The prepared manifests change only that cap;
physical allowance, restoration reserve, rolling window and diagnostic cap
remain unchanged. Applying the new approval and recording its context/hash is
recorded below. This is retained-metadata approval, not recollection or a fresh
served-data/snapshot claim. Both discovery results remain PARTIAL.

| Manifest | Approved model context | Whole-config hash |
| --- | --- | --- |
| Inference enabled | 5645a323-e818-495f-af6a-4cb13932ee71 | 36bdc278b70319820cdcbf0d5151433b15932b684e04050035fa19d7e4c92a96 |
| Inference disabled | eff8809d-86c9-4823-92b8-3d790c0dbbc7 | 763fb27472b24ed4669aac29fa1574e934d089267f2a139a5326e973826fe93e |

Approval controls ran at 2026-10-08 00:20 UTC (2026-10-07 locally), with zero
physical requests and zero model calls. The shared store's latest approval is
the inference-disabled one; a later run must explicitly activate and pin its
own manifest's approved context. Approval alone does not establish that old
context-bound code-verification proofs are valid for a new context.

Engine changes in this work item invalidate the earlier Round Ten freeze.
No live rerun or new acceptance claim has been made at this checkpoint.

Offline referent checkpoint: the produced cell is rechecked against the resolved
intake target before dispatch; keyed cells need every grouping key, and TOTAL
requires its own explicit ticket span. The wrong-cell sealed excerpt is a
regression source, not a replacement for the full private tape. Original receipts
remain unchanged. No value-based target selection is permitted.

The intake wire's context cost is 34,758 -> 43,338 characters. Models 6 -> 6,
measures 39 -> 39, columns 97 -> 97; all 52 visual candidates are retained.
This view has zero SQL-object directory entries before and after; it is the
intake catalog, not the investigation planner directory. Opaque handles compact
identities without truncating entries. A test asserts visual and grouping
coverage is conserved. The existing 60,000-character wire bound is unchanged.

Initial full regression on the uncommitted engine ran 2,281 tests: 23 failures
and 12 errors. Recorded failures are preserved. Affected rechecks identify
legacy synthetic producer responses needing the new null visual field, tests
that assumed unnamed-cell fan-out, and tape tests refusing uncommitted engine
bytes. Corrected targeted checks pass 25/25; the committed full regression and
hosted checks remain pending. No live run or improved fifty-ticket score is
claimed. The thirteen-case intake eval and remaining routing, fallback-output,
and lock work remain pending.


Dated intake checkpoint, 2026-10-07 America/Chicago. The sealed business-intent
proposal already carried `BUSINESS_MEANING`: the defect was admission ignoring
that kind, rather than the model returning the wrong kind. The new admission
rule refuses before a procedure; the original `TRANSFORMATION_LOGIC` result
and human decision remain preserved. Its exact proposal excerpt and full-tape
hash are a regression case. Mixed business-rule requests are conservatively
refused; no technical finding answers their intent component.

Explicit saved-context reproduction, discrepancy, primary business-rule,
filter-effect and earlier-state wording now have consumer checks. A returned
contradiction or invalid consumer record receives one separately recorded and
metered correction; another invalid response HOLDs. Exact provenance, figure
precision and selection-versus-mention checks remain. Missing visual evidence
is not repaired by choosing a candidate. Closed wording checks cannot certify
all human intent: ambiguous paraphrases remain model-quality risks measured by
the eval, not an asserted completeness proof.

Thirteen misses are goldens in
`acceptance/model_steps/intake-round-ten-misses.json`. Five report questions
without a named visual now expect `TARGET_UNRESOLVED`, two unavailable historical
comparisons expect `UNIMPLEMENTED_ROUTE`, and six visual cases retain their
named cells, keys and quantities. No target was authored into an original
ticket. Retained fixture metadata excerpts supply the evaluation names/shapes;
the adapter derives all 52 visual candidates, with no parallel inventory.
The original captured intake records score 0/13 full records and 0.6442307692
field accuracy under these new admission requirements. This is an intake eval
baseline, not a restatement of the 41/64 historical end-to-end batch score.
The corrected model eval has not run, so no after score is claimed.

Filter-effect intake is a distinct subject. Its current route preserves
reproduction receipts then HOLDs `UNIMPLEMENTED_ROUTE` without reading a lower
layer. The requested one-restriction-at-a-time attribution implementation is
still pending; the placeholder expectation stays unchanged. The two earlier
state questions cannot silently substitute a present-state walk.

Context measurement on this eval view: six models, 39 measures, 97 columns,
52 visual directory entries and zero SQL-object entries before and after.
Wire payload 36,492 -> 36,530 characters; new instruction text 653 characters.
No truncation or coverage reduction. This excludes native definition excerpts
which stay out of the planner payload. The earlier referent inventory cost
measurement is separate and preserved.

Validation: 100 focused tests passed. An intermediate check failed because it
expected the business-intent tape to be misclassified; inspecting the actual
sealed proposal corrected the test to assert the admission defect. Another
intermediate decoder check exposed admission being applied before pure decoding;
that check was moved to intake admission, preserving decoded roles and rejecting
business measurement scope. A test command also named a nonexistent test module;
this was operator error, not a passing check.

The prior committed 2,281-test regression had four synthetic tape-provider
failures; the provider fixture lacked the newly required nullable visual field.
The test-only correction subsequently passed all 28 process-tape tests and is
on #423. A final integrated full regression remains required. No new estate
request, fixture change, identity scope or live model call in this checkpoint.
Original failures remain unchanged. #423 is draft; the freeze remains invalid.

Dated Round Ten B offline route/output/transaction checkpoint, 2026-10-07
America/Chicago. The intake commit passed 2,292 regression tests. The filter
question now has an optional declared_filter_effects route: reproduce the named
cell, then compile one evaluation per ACTIVE restriction removed. It never walks
the pipeline. Conditional alternatives stay excluded; cell keys and all remaining
restrictions are retained, including empty intersections. Original quantities,
complete inventory, query scope, context/revision and attestation validate every
variant. BLANK is a result. A cap or failed probe prevents a complete effect
finding; no approximation or pipeline substitution follows. The original D
filtered-lower-layer refusal is unchanged.

The new DECLARED_FILTER_EFFECTS outcome reports value changes, not individual
missing records or intended business correctness. Both output paths render its
restriction/value facts and CONFIRM_SCOPE_INTENT action. Saved-default and
snapshot qualifications remain; no aligned-version claim is added. The authorized
placeholder expectation correction is hash-linked and append-only; the authored
original ticket and its old result remain unchanged. The adapter capability is
not yet enabled in the prepared live manifests, so no live result is claimed.

F's two original business outputs established reachable agreement but omitted
an explicit unreached-source statement. That separate output defect is preserved.
The engine now renders both facts for a mechanism question ending at boundary
consistency, while conservatively mapping it NOT_ANSWERED. The two expectation
corrections retain the human's exact reason.

The original family-A-terse and family-G-mention synthesis failures were schema
pattern rejections: A used "matching rows may multiply" and "operation may
 duplicate"; G used "matching rows may multiply" and "can exceed". Their sealed
responses and absent outputs remain. One separately reserved/recorded composition
retry now runs within the original synthesis deadline and existing governor. No
retry of uncertain transport completion. After rejected prose or exhausted retry
capacity, an unchanged, revalidated original assessment renders both outputs and
an explicit "Mechanism not stated" limitation. Unsupported assessments and changed
source evidence still refuse; fallback cannot invent a classification. Tests cover
one rejection followed by success, two rejections followed by deterministic outputs,
and unchanged support. Earlier bounded-spine rendering now uses this same engine
fallback instead of manufacturing model prose.

Gate lock cause: the gate's own copied-database writer, after cache spill,
opened a second ModelStore read connection to the same file during load/admission.
Catalog reads now borrow that caller-owned transaction under an explicit path
scope; they never commit or close it, and another file cannot borrow it. The
regression appends fifty 32-KiB records under EXCLUSIVE with cache_size=2, reloads
and admits each, then confirms all fifty committed. No journal mode or timeout
increase.

Intermediate checks are preserved: generic new-outcome fixtures lacked real
per-restriction receipts; fixing them exposed reproduction-action substitution
and a business early-return dropping effect findings. Both were fixed. A display
check expected a capitalized synthetic field despite the evidence carrying a
lowercase identity; the assertion was corrected. A retry-accounting assertion
forgot the existing planner plus baseline-read reservations; the corrected check
asserts four settlements. Targeted integrated checks pass; the committed complete
regression and thirteen-case model eval are next. No estate request, live model
call, fixture change, scope change, reset or cap increase in this checkpoint.
Prior freezes remain invalid; #423 stays draft. No improved batch score or enlarged
gate is claimed.

Dated model-eval checkpoint, 2026-10-07 America/Chicago. All thirteen goldens
executed once against the synthetic retained-metadata catalog, with zero estate
reads and fourteen recorded model calls (one normal validation retry). Full-record
matches 0/13 -> 11/13; field score 0.6442307692 -> 0.9134615385. The baseline-v2
adds only the required step label to the evaluation suite; the earlier baseline
artifact and original captured records remain. This is not an updated fifty-ticket
end-to-end score.

Two findings remain. The two-level matrix responses supplied a single combined
"North / Component 1" target value with no column and no filters, rather than two
address keys. Both responses are retained; the validator HOLDs INTAKE_RECORD_INVALID
instead of reading the wrong cell. The saved-bookmark case returned the correct
visual and VISUAL_CONTENT subject but BUSINESS_QUESTION/NONE rather than the
authored MISMATCH_COMPLAINT/VERTICAL pair. Both are valid wire pairs; the existing
validator has no rule establishing that this reproduction question must use the
latter pair. This is recorded field variance, not silently changed expectation
or an asserted false reproduction. No ticket-specific repair or replacement
attempt was made.

The first CLI invocation stopped at KeyError: step before building an installation
or dispatching a provider. The suite now carries that required format field and a
regression assertion. This operator/setup failure is recorded separately from the
thirteen model attempts.

Historical gate replay requires the old decision code, which also contains the
old second-connection I/O defect. A scoped replay-only connection shim now reuses
the caller's writer during historical load/admission, never patches a fact,
request, response, clock or output, and is skipped on current producers. The sealed
family-A-mention replay now matches all events and final outputs under its original
2ec18bdc8148e99a33adfb667c2d473f4ac95615 revision: COMPLETED,
TRANSFORMATION_LOGIC, synthesis COMPLETED, zero network/estate/model requests.
Both current and legacy fifty-append tests pass. The first failed diagnostic and
its database-is-locked error remain unchanged. This confirms one repaired gate
path, not an expanded passing roster or a new engine acceptance.
