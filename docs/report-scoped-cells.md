# Report-scoped cell addressing (PR B)

Date: 2026-10-02. Follows the report-scoping contract in [PR A](report-scoping-contract.md).
This is implementation and local test evidence, not a live reproduction claim.

The procedure now receives the ticket's exact report binding and a separate,
reviewed selection request. Intake performs no estate reads and cannot emit an
OBSERVED or EVIDENCE resolution. Report-name absence, nonmatch and ambiguity
remain explicit refusals. Historical records are preserved unchanged.

The adapter extracts conserved inventories within that report. The active set
comes only from ACTIVE entries. Empty saved slicer selection is an explicit
ACTIVE FULL_DOMAIN declaration. A predicate on another report is never admitted;
a saved selection on another page is a conditional alternative for this cell.
Unknown declaration containers retain UNSUPPORTED and block reproduction through
the consumer's validation. Bookmark invocation remains unknown.

A bare value resolves from exactly one ACTIVE declaration, or from original,
complete, query-bound value-existence receipts covering every candidate grouping
column. Existence reads use the same bounded compiler, reader and diagnostic
admission as quantity reads. Zero or several matching columns refuse; inadequate
read capacity refuses before attempting a partial search. Explicitly stated column
names require exact catalog matching and still incur a value lookup. A mismatch
retains its receipt rather than being treated as a usable selection.

After resolution, projected measures and grouping roles determine scalar cells:
ungrouped, keyed and totals. Missing keys name the missing column; a total can
still be evaluated. Visual calculations and unfamiliar visual types are named
refusals. Keys do not enter the inventory and are composed with ACTIVE restrictions
only at execution. No-report-figure checks may compute quantities, but have no
reproduction label or presentation verdict. Each unevaluated candidate is named.
The lower-layer filtered-scope refusal is unchanged.

Within this optional reproduction check, a prior successful read with exactly the
same compiled expression, resolved references, context, policy, connection and
reader is reused budget-free. A distinct duplicate-refusal event carries the
original receipt/result. No result-containment or semantic-equivalence reasoning
exists. Equal results from distinct compiled reads never block admission. Cache
entries are run-local and require complete results with matching surface evidence.
Original receipts are never rewritten to manufacture separate reads or independence.

The engine validates selection resolution again against its original inventory
and original value-existence receipts during synthesis. Both outputs distinguish
OBSERVED row-value evidence from EVIDENCE declared restrictions. Saved-default
qualifications remain engine-rendered, and the non-reproduction open set explicitly
names a moved slicer and an invoked bookmark. Every comparison is within-layer;
undeclared-context values are never called unrestricted totals.

## Local retained-context inspection

The pinned context remains `3ae7607b-5a5e-46c6-8e1b-195dbabc9cae`.
Inventory Health has two projecting visuals and one conserved full-domain saved
slicer declaration per visual, ACTIVE=1, CONDITIONAL=0, UNSUPPORTED=0. The saved
absence fragment is quoted in [the contract evidence](report-scoping-contract.md).
Warehouse Performance has no visual projecting this measure. The separate predicate
fixture has three projecting visuals, each conserving nine declarations:
ACTIVE/CONDITIONAL/UNSUPPORTED counts are 0/9/0, 3/6/0 and 4/5/0. Declarations are evaluated per (page, visual),
never unioned into a query. This inspection read local retained definitions only.

## Context cost and validation

The twelve immutable intake fixture payloads remain byte-identical: 1,050?1,952
characters, including Family D at 1,103. Model, measure and column counts do not
fall. Wire-schema size changes from 2,193 to 2,163 characters for single-model
fixtures and from 2,261 to 2,217 for the two-model fixture. Combined instruction
constants change from 4,317 to 4,442 characters. Golden directory coverage remains
28 entries and 11 SQL objects. No directory content or compaction budget changes.
Historical synthetic intake cases without a named report now explicitly refuse
rather than manufacturing STATED provenance; their immutable tapes are unchanged.

The first full suite ran 1,548 tests and found five failures: three wording
assertions and two read-accounting tests exposed an overly broad report gate.
The gate was corrected so optional reproduction is report-scoped while ordinary
global process reads remain possible; the changed wording assertions were updated.
Focused contract, scoped-cell, compiler, intake, projection and procedure tests
pass after those corrections. The final full suite passed all 1,550 tests in 286.814 seconds. The duplicate-quote amendment is still PR C. No investigation run,
ledger row, cloud read, provider call, fixture mutation, permission or budget
change was performed for this implementation. Engine bytes changed; all earlier
freezes remain invalid. The three exact saved tickets wait until PR C merges.
