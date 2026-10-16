# Interpreter source addressing — 2026-10-13

The retained second interpreter batch stopped on task 1 at `EDGE_VALIDATION`,
with `GRAPH_INTERPRETER_SPAN_DIFFERS`. All six proposed edges cited offsets
`235:400`. Their copied quote did not equal that slice of the retained source:
the slice began with the preceding statement's semicolon and ended inside
`[invoices]`. This was model character-counting error, not a changed definition.
The original batch, provider bytes and failed status remain unchanged.

The regression fixture contains the exact synthetic source and six failed
span fields, with original request and response SHA-256 references. It excludes
provider identifiers, encrypted reasoning, credentials and unrelated response
metadata. Its definition hash is checked by the test.

Future calls use `SOURCE_LINE_REFERENCES_V2`. The model selects the first and
last IDs from numbered source lines. Code derives the Unicode code-point
offsets and quote from those lines, verifies the slice against the original
hash-checked source, and emits the existing graph TEXT-span evidence shape.
Neither Unicode nor CRLF is normalized. Bad, reversed or out-of-range IDs
refuse; there is no substring search, offset repair or hidden retry.

## Decided without review

Use contiguous source-line references instead of asking the model to supply
both numerical character offsets and a copied quote. The rejected alternative
was finding the copied quote somewhere in the source and silently repairing
its offsets: repeated text makes that ambiguous and would alter the meaning of
the failed proposal. The owner accepted the line-reference approach during
this round. Historical captures keep their original contract and remain failed.

This fixes addressing, not semantic truth. An exact source span can still
support a wrong interpretation. Accepted edges remain INFERRED; code marked
fixture-authoring-only remains `execution_established: false` and cannot earn
deployed-procedure verification. No estate or model calls were made for this
fix. Live interpretation results belong to the later recorded batch.

## Live result, 2026-10-13

Batch `round-nineteen-b-interpreter-01` completed four retained procedure tasks with 6, 7, 6, and 7 proposed edges. All four exact-span validations passed. Four model calls cost USD0.074710; zero estate reads, zero graph mutations, no publication or settlement error. Result SHA256 `1361336e80ca0905514c6a6c9140b30e7d096a3d532462bb360c56e9f83435df`; four captures retained. These are INFERRED proposals for review, not verified or deployed transformation evidence. Original failed captures remain unchanged.
