# Planner-view golden tests — offline reliability item 2

Date: 2026-09-22. Tracking: #199. Prerequisite: item 1 merged as PR #209.

Four synthetic recorded-input shapes now have checked-in exact projected and wire
context snapshots, schema hashes and handle mappings. These are purpose-built test
fixtures, not exported business data, stored live receipts or evaluator answers.
The inputs reproduce the structures implicated by the historical trials; no tests
run against pre-fix commits. Local trial artifacts remain under `.local/`.

| Shape | Explicit invariant |
| --- | --- |
| Dense profile with long workspace/model/member identities | Selected-table numeric and measure hints survive the 2,500-character view; dropped tables/members remain counted. |
| Large definition parent with a definition child beyond ten other children | The definition link survives compaction and is admitted by the content-lookup wire schema. |
| Three older paged content receipts and a later lookup | The recent source excerpt survives; retained/omitted characters are counted per receipt, with original page offsets and continuation preserved. |
| Individually bounded schemas, candidates, directory, measures and source content whose assembly exceeds 32,000 characters | Lower-priority directory/history/metadata excerpts are shed deterministically before runtime reservation and dispatch. |

Projection omission is labelled RETAINED, TRUNCATED or OMITTED, with an explicit
statement that it is not catalog removal. Nested excluded metadata fields/items
are counted. Stored receipts are not changed. Protected question/scope, result
receipts, source schemas and execution authority are not silently removed to fit;
an irreducible view still fails the existing admission check without dispatch.
The character ceiling applies to the assembled projected context, as in the
existing policy. Provider instructions/schema overhead is retained in item 1's
wire-body recordings and must be included in item 8's capacity analysis.

The fitting order is a context-budget policy, not a prescribed investigation
route. It does not change tool permission, introduce proposal repair, execute a
query, allocate new budgets or grade business correctness. The engine identifies
new dynamic payloads as `dynamic-investigation-v8`.

## Offline findings and verification

The initial seven tests passed with a single oversized excerpt. That input was
then replaced by an assembly of realistically bounded sections. The revised
fixture failed offline: schema compaction added bookkeeping without reducing
already bounded schemas, leaving the protected input above the ceiling. The
correction retains original metadata when compaction would enlarge it. No live
LLM call was used to find or fix this defect.

Expanding the definition fixture to include a full optional directory exposed a
second offline failure: the wire-handle cap removed the content operation despite
retaining the child in metadata. Observed definition references now precede
optional directory identities, and excluded handles are explicitly counted.
The failing run is preserved in the ledger alongside the corrected check.

The final nine focused projection tests passed, including recording actual SDK
request bodies for all four goldens through mock transport and checking the
wire input and schema against the snapshots. Nine profile, nine navigation and
36 flexible-runtime tests also passed. The representative assembly is 44,844 characters before
projection and 31,851 after fitting, under its 32,000-character ceiling. Its
cumulative remaining allowance models the historical 69%-consumed case, so it
specifically exercises the per-call boundary. Exact expected views and independent
invariant assertions both gate changes; removing the corresponding projection
logic makes the assertions fail. Full regression passed 968 tests in 281.688
seconds. Six CI checks passed on the implementation head; PR #210 records the
final documentation-head checks and merge state.

The [append-only ledger](runs/ledger.jsonl) preserves the failed and successful
offline checks. Validation-suite rows count no real provider or cloud calls;
they do not aggregate every internal unit-test mock invocation. These tests are
not unfamiliar-domain acceptance and do not establish investigation quality.

## Freeze discipline

This item changes engine bytes. V4 remains invalidated, and its original artifacts
and evidence remain untouched. A fresh freeze and fresh variant are required only
after all ordered offline gates pass. Next is item 3, full-session simulation with
recorded providers; no new variant is published for this item.
