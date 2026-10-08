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
