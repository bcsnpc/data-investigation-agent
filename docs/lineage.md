# Lineage backend

The lineage builder derives an evidence-backed graph from a completed metadata scan. It reads the captured definitions, never executes notebook code, and stores each graph build separately in the existing local SQLite inventory.

## Run and query

```powershell
python -m pip install -r scripts/requirements-lineage.txt
python scripts/collect_lineage_evidence.py --config infra/metadata/development.json
python scripts/lineage_graph.py
python scripts/validate_lineage.py
```

`collect_lineage_evidence.py` reads the connection IDs referenced by copy-job definitions and the lakehouse SQL endpoint properties. It retains only connection type/path and lakehouse endpoint metadata, with acquisition times. It does not retrieve or store passwords. The evidence file identifies the inventory scan it enriches; use `--scan` to select an earlier complete scan and `--output` to change the output file. The lookup is live while the inventory is a snapshot, so evidence timestamps remain part of each build.

The builder accepts `--database` and `--evidence` for other environments. Queries use the stored graph and do not call Azure or rebuild it:

```powershell
python scripts/lineage_graph.py --asset "<asset-id-from-inventory>" --direction upstream
python scripts/lineage_graph.py --asset "<asset-id-from-inventory>" --direction downstream
```

Use `--run` to query an earlier build. `--include-filter` includes semantic relationship filter dependencies. Python callers can use `load_graph(database, run).traverse(asset_id, direction, kinds)` directly. Traversal is cycle-safe and returns assets, typed edges, evidence and unresolved dependencies relevant to the visited assets.

## What is derived

- **SQL to Bronze:** source server/database from the connection API; schema/table and destination workspace/lakehouse/table from copy-job mappings. Matching table names alone is insufficient. All ten mappings resolve.
- **Pipeline invocation:** the pipeline definition's explicit copy-job ID. This is an orchestration edge, not a data transformation.
- **Notebook transformations:** Python AST analysis resolves literal containers, bounded loops, string assembly, Spark reads, temporary views, SQL queries, supported dataframe operations and writes. SQLGlot resolves SQL table scopes, so CTE names are not treated as physical tables. No notebook imports, arbitrary functions or Spark code execute.
- **Gold to semantic tables:** entity partitions and M expressions resolve through the captured lakehouse endpoint IDs and hosts. No lakehouse-name guessing is used.
- **Measures:** explicit DAX column/measure references and supported table-function references resolve within the model. Strings/comments are ignored; ambiguous references remain unresolved.
- **Reports:** explicit semantic model IDs, visual/page bindings and static inherited filter fields. Visual/page/report presentation edges make downstream asset discovery possible.

## Persistence and edge meaning

`lineage_runs` stores the metadata scan ID, build time, status and supplemental API evidence. `lineage_edges` stores source, destination, edge kind and supporting definition hashes/details. `lineage_gaps` stores unresolved references and parser limitations. Graph builds do not replace previous runs or mutate inventory assets.

Edges point upstream to downstream. Default traversal includes `data`, `binding`, `presentation` and static `context` edges. `filter` edges describe semantic relationship direction and require opt-in. `produces` and `orchestration` are available through the Python `kinds` argument for execution/ownership tracing; they are excluded from default value lineage so a notebook's unrelated outputs do not become data dependencies.

Notebook edges are conservative table-level derivation, not complete column-level lineage or proof of a runtime query result. SQL temporary views can resolve to their materialized output when the result is published directly or wrapped only in metadata-column additions. Sibling projections are not assumed to depend on one another. Static filter dependencies identify fields that can affect a visual; they do not reproduce a user's active slicer selections, bookmarks or query session.

`COMPLETE` means no unresolved references were detected by the supported parsers for that captured build. It does not certify arbitrary Python/DAX support, data correctness, refresh freshness or root cause. Unsupported writes, conditional dataflow, unknown transforms and unresolved references produce explicit gaps. Dynamic or externally imported transformation code requires additional metadata/runtime evidence. Application-event lineage and the lineage UI remain later work.

## Validation evidence

Inventory scan: `5d11f419-0596-412a-9002-1971b3fed6ad`.

The verified build has 360 edges and zero detected unresolved references. All 41 data-bound visuals trace to SQL; the four remaining visuals are text elements. Net Sales traces to exactly six source tables: `app.orders`, `app.order_lines`, `app.payments`, `app.products`, `app.refunds` and `app.refund_lines`. Downstream traversal identifies Executive Sales and Product Performance. Ten source-to-Bronze mappings and pipeline invocation are verified. Every edge includes supporting metadata hash evidence.

The live-estate regression uses independently specified expectations; it is not used to construct the graph. Offline tests cover CTE scope, joins, unseen table names, materialized intermediate dependencies, sibling projections, unsafe notebook code, unsupported control flow, DAX ambiguity/string handling and cyclic traversal. No source data, pipeline, notebook or report was changed.

API and parser references: [Fabric connection metadata](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/get-connection) and [SQLGlot scope analysis](https://github.com/tobymao/sqlglot/blob/main/sqlglot/optimizer/scope.py).
