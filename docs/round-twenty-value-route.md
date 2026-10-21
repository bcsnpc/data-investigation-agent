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

`declared_producers(graph, table_ids)` follows every `DERIVED_IN_STEP` edge to
QUERY_STEP and preserves owner, expression, definition hash and JSON pointer.
It never chooses a last writer from static alternatives. On the retained billing
graph, both `gold.subscriptions` and `gold.plans` have two Script CTAS writers:
pipeline `62eb1a7f-19c2-466f-85ec-cda6bc231fb9` and pipeline
`76c60248-b830-433b-9880-90593da28e7e`. Their retained expressions read directly
from `bronze.subscriptions` and `bronze.plans`; no Silver stage or stored
procedure is invented. Definition hashes are respectively
`b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09`
and `6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf`.
Both have `execution_established=false`; which one last ran remains unestablished.
The retained MRR All Plans expression parses into the supported SUMX/RELATED
subset using the actual Subscriptions-to-Plans relationship and exact source
column identities. This is compiler support, not a live value-verification claim.

Native date literals are delegated to the existing catalog-typed DAX compiler.
The retained fixture event_day is declared `string`, so its ISO day is correctly
rendered as text. If the current definition instead declares dateTime, that
compiler refuses this unsupported literal representation rather than silently
applying a string predicate. The string/dateTime regression records that bound.

## Concrete mapping derivation

`cloud_value_mapping.py` checks each retained owner payload against its indexed
SHA-256 before parsing. It derives only the columns required by the measure,
ACTIVE restrictions and their relationship keys. DirectLake mappings follow
exact graph edges and physical asset/container identities; no display-name
search creates a bridge. Notebook continuation uses the existing static
`DeclaredQuantities` parser's per-column origins and exact retained ABFSS table
locations. It never executes notebook code or uses seeded rows as live values.

The retained filtered fixture produces three compilable mappings, each with nine
semantic columns: Gold, Silver and Bronze. All four predicates remain applied
in every query. Original Bronze is literal initialized, with no declared
upstream read. The application binding from the separate round-two fixture is
not attached to it.

Billing produces an exact Gold mapping and an explicitly labelled mapping onto
the Warehouse's declared Bronze views. Script activity endpoint, artifact ID
and database declarations bind the CTAS expressions. Both matching producers
remain alternatives; neither is asserted as the last execution. The Bronze
views are retained CREATE VIEW declarations, not catalog-observed tables.
Their cross-catalog reference to `billing_bronze` needs an exact endpoint-to-
Lakehouse binding before continuing to the physical lakehouse or application.
A matching display name is insufficient. The application Copy definitions are
retained, but this missing hop is not silently crossed.

These are offline mappings with recorded provenance, not earned confidence or
fresh estate verification. Live query failures and numerical differences still
determine what can be concluded.
