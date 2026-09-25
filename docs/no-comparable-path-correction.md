# No-comparable-path correction and binding proposal

Updated 2026-09-25. Related #224, #227 and #228. This is a known-domain
reliability correction. It makes no freeze, variant or unfamiliar-domain claim.

## Finding from the first smoke

The evidence supports the distinction hypothesis, not a missing `measure_path`
call. Each saved process run contains a context observation produced by
`context_search.measure_path`. It resolves Handled Quantity to `Activity[units]`,
retains the semantic table and column, and records the DAX-derived identity edges.
It also retains the Direct Lake partition source as a definition label and reports
`UNRESOLVED_PARTITION_IDENTITY` and `UNRESOLVED_EXTERNAL_SOURCE_BINDING`.

The #224 audit reached the Gold item, notebook and Silver inputs through additional
item-relation and definition surfaces. Those asset relationships do not establish
that a scoped aggregate at one asset is faithfully equivalent to a scoped aggregate
at the next. The Microsoft adapter therefore correctly did not invent a lower-layer
query. Its defect was reporting that distinction as `NO_LINEAGE` and allowing a
zero-comparison run to claim `CONSISTENT_TO_BOUNDARY`.

For the current model the first missing binding is specific: the Activity semantic
table's partition carries the source label `dbo.movement_values`, but that label has
no stable discovered asset identity. The engine cannot compile a lower-layer
quantity under the declared scope from a name label alone.

## Contract correction

`NO_COMPARABLE_PATH` is a thirteenth closed outcome. It requires an established
presentation baseline, the attempted path-resolution receipt and a specific missing
binding or access description. Its action is to name what would make comparison
possible. It never says that a lower layer agreed.

`CONSISTENT_TO_BOUNDARY`, `INGESTION_GAP` and `BUSINESS_QUESTION` now require at
least one successful equal boundary comparison. The baseline is no longer tagged
as flow-consistency evidence. Refresh/load/presentation/transformation/defect
claims require an observed unequal comparison. The refresh branch also tags its
comparison evidence correctly when using it as the baseline. Boundary attribution
also proves that the cited baseline layer is immediately above the unequal
comparison; a lower divergence reached after an earlier gap uses its own observed
upper quantity rather than the presentation baseline. This audit found no other
implemented verification claim lacking its corresponding comparison. Horizontal
outcomes remain proposal-only and already require both definitions, scopes or paths.

`NOT_COMPARABLE` remains a boundary event. The walker records the two layer IDs and
specific reason, then continues. A later divergence can still terminate normally.
If no comparison connected to the presentation baseline succeeds, the result is
`NO_COMPARABLE_PATH`. If one or more contiguous comparisons succeed before a later
uncomparable boundary, `CONSISTENT_TO_BOUNDARY` names only the deepest continuously
verified layer and stops with `NOT_COMPARABLE`.

Technical output now reports resolved boundary count, executed comparison count and
each uncomparable boundary. The current adapter reports the partition-label binding
gap as `CAPABILITY_UNAVAILABLE` rather than erasing the asset lineage as
`NO_LINEAGE`.

## Proposal only: comparable-quantity binding

A comparable-quantity binding is a versioned, provenance-bearing contract for one
adjacent process boundary. It contains:

- stable upper and lower asset IDs and their definition-version hashes;
- the upper measure or quantity expression and a lower-layer expression plan;
- aggregation, grain, filter, time-window, null and sign semantics;
- the scope fields that translate exactly and any field that cannot translate;
- the transformation or partition evidence that establishes the mapping;
- authority (`DISCOVERED`, `DETERMINISTICALLY_DERIVED` or `DECLARED_CONTEXT`),
  validity dates and an invalidation fingerprint.

A binding may be derived only from identity-backed partition metadata, deterministic
column/expression lineage, or reviewed declared context. Model inference may explain
a retrieved definition but cannot authorize equivalence. Similar names cannot form
a binding. A definition change invalidates the binding until it is re-derived or
reconfirmed.

At runtime the adapter compiles both quantities under the declared scope and either
returns comparable probes or a per-boundary `NOT_COMPARABLE` reason naming the
missing identity, column correspondence, grain rule, scope translation, permission
or reader capability. The engine continues walking other resolved boundaries but
never substitutes an approximation.

This proposal is not implemented here. In particular, the current partition label
is not joined to the discovered Gold object, and no Gold/Silver or Azure SQL query
is added.

## Context cost and validation

The change adds no investigation-planner payload content. The four golden projected
payloads remain byte-for-byte equal: 0/0/1,460, 50/0/7,212, 0/0/4,722 and
0/0/31,851 for directory entries, SQL objects and payload characters. Only response
schema hashes change for the thirteenth outcome.

**1,052 local regression tests pass**, including process, synthesis, intake,
planner projection and runtime coverage. CI, followed by exactly three recorded
known-domain G trials, remains before this checkpoint is complete.
