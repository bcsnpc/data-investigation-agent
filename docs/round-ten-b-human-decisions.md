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
