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
planner projection and runtime coverage. All six CI checks passed and PR #229
merged as `5a5909b`.

## Corrected three-run result

Exactly three identical recorded known-domain G trials ran after the merge, and
the batch stopped. C1, C2 and C3 each reproduced 8,765 with one DAX baseline read,
made zero SQL reads and zero investigation-planner calls, and terminated at step 3
as `NO_COMPARABLE_PATH`. Each reported zero resolved boundaries and zero executed
comparisons. No `NOT_COMPARABLE` event occurred because the first adjacent boundary
could not be resolved at all; the stop was `CAPABILITY_UNAVAILABLE` with the exact
missing stable binding for the `dbo.movement_values` partition label.

All three syntheses validated. All six intake/synthesis request-response tapes
match their recorded byte lengths and SHA-256 hashes, with no exclusions or provider
errors. Daily reservations moved from 121/35/3,722,694/890,000 to
127/38/3,860,454/918,500 for planner calls, cloud reads, input characters and output
tokens. All 165 records are settled. Measured intake/synthesis tokens have a USD
0.128989 reference cost, excluding cloud reads and not representing Azure billing.

This corrects the first smoke's three invalid consistency labels. It does not
improve source reach: the same three DAX reads and no SQL reads occurred. It also
confirms that zero investigation-planner calls are structural here; the deterministic
adapter stops before a transformation definition or divergence can be judged. The
next accepted batch must reach a real comparable divergence and invoke that judgment;
no further run is made at this checkpoint. See the
[machine-readable result](runs/no-comparable-path-corrected-smoke.json).

## 2026-09-25 correction after #232

The structural conclusion above is withdrawn pending a correct-context run. The
three #229/#230 sessions opened the `development` discovery environment, while the
warehouse variant had been discovered under `unknown-domain-v4`. The older context
did not contain the newly collected semantic-endpoint-to-lakehouse relation. Its
failure to bind `dbo.movement_values` therefore does not establish that the binding
was absent from the intended estate, and it cannot establish that zero planner
calls were a structural property of the correct path.

The original runs, receipts, machine-readable result and text remain preserved as
the historical record. They demonstrate the false-consistency correction: a
zero-comparison path no longer claims `CONSISTENT_TO_BOUNDARY`. They also
demonstrate that the engine did not widen scope or join similarly named objects.
Capability gating added later is independently valid. The declared-scope primitive
remains a sound resolution rule, but whether this boundary needs that primitive is
open until a run uses the intended discovery environment.

## 2026-09-25 follow-up in the intended context

The pending check is complete. Of exactly three launched known-domain regressions,
the first failed before intake on a stale usage-policy environment label. After a
counter-preserving policy alignment, the next two opened `unknown-domain-v4`,
resolved the semantic-to-Gold source with `DECLARED_BY_DEFINITION`, and each
executed an equal 8,765 = 8,765 comparison. This confirms that the prior structural
conclusion was an artifact of the wrong context. It does not test transformation
judgment because no comparison diverged. See the
[correct-context record](correct-context-process-three.md).
