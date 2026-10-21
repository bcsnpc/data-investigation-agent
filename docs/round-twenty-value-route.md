# Practical value route

`scripts/cloud_value_verifier.py` compiles retained declarations, not a supplied
SQL string. `build(model, measure_id, target_id, layer_mappings, tolerance=...)`
uses the report adapter's complete declaration inventory, the engine's
conservation validation, and the selected visual's native cell address. ACTIVE
saved slicer defaults enter the same composed scope as page and visual filters;
conditional bookmarks remain evidence, not active predicates.

The native DAX query runs first through the runner's governed reader. A failed
native read is retained with its original status, HTTP error and provider body;
the path returns `REFUSED`, naming SEMANTIC, before any lower read. No source
value substitutes for a failed visual read. This is an attempted path, not a
complete value proof. Missing lower mappings remain explicit and cannot earn a
vacuous success.

Each layer mapping has `layer_id`, `endpoint`, physical `objects` keyed by graph
table identity (`schema`, `table`, discovered `columns`), `columns` keyed by
semantic column identity (`object_id`, exact `column`), and the admitted semantic
`relationships` identities. The DirectLake/producer bridge supplies these
coordinates from retained definitions. The compiler never guesses a numeric key
from a dimension name, a physical table from its display name, or a source
column from a ticket family. Unknown propagation or unmapped scope refuses.

Supported quantity semantics are additive `SUM(column)` and the closed
`CALCULATE(SUMX(FILTER(table,column="literal"),RELATED(lookup[column])),
REMOVEFILTERS(lookup))` subset. The latter requires a unique declared active
many-to-one relationship, uses LEFT JOIN to preserve unmatched-row BLANK,
includes a measured duplicate-lookup-key guard, and records the removal of
lookup-table predicates. An absent guard is a refusal. Other DAX expressions
are named unsupported, never rewritten as a naive join. IN predicates are
intersected once per semantic column; empty intersections remain `1=0`.

The executor returns an observational result, never `VALUE_VERIFIED` itself.
The independent engine resolver must validate native receipts, attestation,
explicit tolerance, scope/mapping/definition/endpoint pins and any numerical
explanation before awarding that confidence. An unexplained difference stops
with both values preserved. Measured BLANK is distinct from zero, a failed read,
and a successful response with no value field. Snapshot alignment is not
asserted; saved-default and snapshot qualifications remain in the plan.

The offline CLI accepts a retained `--model`, exact `--measure-id` and definition
part `--target-id`, optional bridge `--mappings`, and explicit `--tolerance` plus
`--tolerance-source`. It creates a new `--output` and performs no calls. With no
mapping file it marks `lower_mapping_complete=false`; this is a native-first
attempt plan, not evidence that the full path is supported.

Offline retained fixture check (2026-10-21): the selected definition part
`a32b6a48db655ac8a4f2` yields nine declarations: four ACTIVE, five CONDITIONAL,
zero UNSUPPORTED. Two ACTIVE entries assume saved slicer defaults. Native DAX
contains day `2026-09-15`, movement type `RECEIPT`, product name `Component 1`
and warehouse name `North`. Graph visual IDs use `/visual/`; the retained
definition part uses `/part/`. An exact part binding is required; this compiler
does not resolve a different visual as a fallback. These are retained metadata
observations, not live verification results.
