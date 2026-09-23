# Local proposal repairs

2026-09-23 UTC. Ordered offline reliability item 4, issue #199.

The dynamic runtime repairs identical duplicate hypothesis updates and bounds
descriptive text before contract validation. Conflicting claims/statuses under one
ID remain invalid: the runtime does not select a truth, invent an ID or merge
evidence. SQL/DAX text, identifiers, citations, classifications and scope are never
truncated or rewritten. Text truncation retains an ellipsis and records omitted
character counts; it is not a certification of the resulting statement.

A parsed, catalog-approved SQL proposal can retrieve its missing referenced object
schemas locally, then recompile and pass the existing dispatch checks. This uses
catalog metadata, not a data read or planner call. At most 16 missing assets can be
fetched per proposal. Unknown objects/columns, stale context, denied readers,
incomplete schemas, query limits and deadline checks remain enforced. SQL proposals
are exposed when source objects are present in the planner's directory; this does
not grant execution. Explicit metadata lookup remains useful for forming a query.

Each repair emits `PROPOSAL_REPAIRED` with `hypothesis_id`, `text_bound` or
`schema_prefetch`, counts/field paths or an observation reference. These events are
distinct from clean proposals, validation rejections and executed data receipts.
The replay ledger counts them separately. Prior recordings and failed attempts
are not modified.

## Offline evidence

Five repair tests passed in 8.839 seconds; the final six-test set passed in 9.451 seconds, adding repair-event retention when the dispatch deadline expires. The recorded-provider test reproduces
the three-consecutive-duplicate-update failure **shape**, not the exact historical
v2 family-A trajectory: that attempt has no item-1 HTTP recording. It completes four
planner calls (three tests and a final question), three mock SQL reads, three
duplicate repairs, four text repairs and one schema prefetch. Full offline replay
matches the recorded request bytes and final state without another provider call.
No NO_PROGRESS stop occurs. This does not claim that a live LLM selects good tests.

The five session-replay tests passed in 16.008 seconds, 36 flexible-query tests in
9.937 seconds and nine projection tests in 6.115 seconds. The golden context
snapshots did not require changing their expected content. Unauthorized-object
tests prove that rejected objects are neither prefetched nor executed. Conflicting
hypotheses and oversized executable text remain rejected.

The first four repair tests passed in 2.243 seconds. The first expanded test run
failed because its synthetic SDK fixture omitted the required usage policy; the
guard correctly rejected it. The policy was supplied. A replay test initially
expected a mismatch after automatic prefetch, but the exact query already had a
saved receipt and was correctly reused; its assertion now verifies reuse without
an unrecorded tool call. Both failed suite runs remain in the append-only ledger.
Validation rows represent suite invocations, not aggregated internal fixture calls.

The first full run executed 978 tests with one engine-fencing error: the deadline-event correction changed engine bytes during the run. This is an invalidated validation run, not a pass. The final tree passed all 979 tests in 246.828 seconds without concurrent edits. A final source-availability assertion passed in the 36-test flexible-query suite (6.805 seconds). Secret scanning and local links passed. No live LLM, SQL or Power BI calls were made; no
permission, SQL limit, daily usage or deployment setting changed. Engine bytes
change, so v4 remains invalidated; a fresh freeze and fresh variant must wait for
all ordered offline gates. Next is conservative read redundancy, separately.
