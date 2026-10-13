# Estate lineage graph: offline foundation

This implementation supplies the Round Nineteen static foundation. It does not claim a live scan, cloud PostgreSQL migration, complete dependency graph, or a verified path. The engine freeze is invalidated by these new modules.

## Contract and storage

`estate_graph_contract` defines closed node/edge records. Every edge has DECLARED, INFERRED, VERIFIED or UNKNOWN confidence, an exact source identity, raw-definition SHA-256, observation time and JSON pointer or text span. UNKNOWN requires a reason and remedy. A model proposal can only be INFERRED. VERIFIED requires query-verification provenance, evidence IDs and a scope hash; repository writes additionally resolve those IDs and reject mismatched producer, edge, definition or scope. That receipt resolver must be supplied by the governed verification service, never model input.

Graph IDs derive from estate, owner, kind and stable declaration locator. Names are labels, not global identities. Edges are oriented from a consumer toward its dependency for traversal; CONTAINS is the explicit structural parent-to-child relation. No estate name, source layer convention or metric is encoded in the engine.

`GraphRepository(SharedState)` reuses the existing current graph tables and adds history, owner-fingerprint and change tables. Live authority is the existing PostgreSQL backend; SQLite remains an explicit offline test backend. Replacements and history closing are transactional. Validity intervals are half-open: `valid_from <= time < valid_to`. Unchanged fingerprints skip updates. A source change invalidates affected verification, while an unrelated title change does not. Removed cross-owner dependencies become named UNKNOWN stopping boundaries; deleted objects remain available as-of their earlier time. Their dependent definitions need recollection before restoring a link. The current graph is a projection of history, not a second independently computed artifact.

The static extractor currently reconciles one retained catalog as one owner. Metadata recollection can be incremental upstream; this adapter still rebuilds that owner's in-memory graph from the complete retained catalog. A scheduled modified-item scanner and deployment are not supplied here.

## Raw definitions

`graph_definitions.DefinitionSink` uses the existing immutable Files store. It writes one content-addressed definition, verifies it, returns its SHA-256/size/URI, and deduplicates subsequent identical bytes. With the approved Blob Files adapter, this uses the existing private platform storage and its gateway; tests use local CAS. No implicit backend or credential is selected. Projected capture refuses explicitly rather than storing raw definitions under a projected label.

The extractor requires a sink. It cannot silently claim raw definitions were stored without receiving the matching digest and byte count. Native PBIR bytes are preferred over expanded catalog metadata only after checking equality. Any provided retained metadata hash is verified before extraction. No collector, estate or model request is made by static extraction.

## Static coverage and named limits

| Retained form | Extracted now | Explicit remaining boundary |
|---|---|---|
| Expanded report/page/visual catalog and PBIR | Visible/hidden flags, native measure/column references, report-model binding, saved slicer filter predicates, report/page/visual filters and declared interactions | Missing/ambiguous binding or unsupported visual reference is UNKNOWN; runtime selections are not established |
| Saved bookmark parts | Conditional bookmark step and stored filters | No claim that a bookmark was invoked |
| Model metadata / model.bim | Tables, columns, measures, relationship endpoints/active flag/filter direction, RLS role filters, calculation groups, field parameters and partition M steps | DAX dependency resolution requires served engine dependency rows; RLS user membership and dynamic parameter selection remain unknown |
| TMDL | Supported declaration headers and exact source spans | Not a complete TMDL grammar; expressions/relationships require engine resolution |
| SQL catalog, views and text | Exact-database object binding and column dependencies for one explicit-column SELECT, WHERE filters, join conditions | Multi-statement procedures, dynamic SQL, CTEs, nested SELECTs, star expansion or ambiguous references stop explicitly |
| Notebook Python | Supported data-operation call spans and possible filter calls | Receiver types and dataframe dataflow are UNKNOWN; notebook source is never executed |
| Power Query | Named steps and directly called Table.SelectRows filters | Step dataflow, source identity and arbitrary M semantics are UNKNOWN |
| Pipeline / Copy | Activities and explicit mapping text | Connection/object/column binding is UNKNOWN; mapping text is not mistaken for a resolved path |
| Refresh schedule catalog objects | Declared schedule nodes, when collected | Runtime refresh/load timestamps are not invented from schema modification dates |

No existing fixture-specific notebook special case is reused. No inferred name match is marked declared or verified. Unsupported code remains a named boundary for a later bounded interpreter; this commit makes no model calls. Engine dependency collection, an inference proposer, on-demand live path verification, runtime timing import and scanner API integration remain later work.

## Guarded compact API

`GraphAPI` exposes `path_to_source`, `visual_context`, `filters_on`, `table_columns`, `definition_of`, `freshness`, and `as_of(time)` variants. The caller supplies a trusted exact object slice through `Gateway.graph_objects`; missing scope, wildcard scope and outside-slice roots refuse. Unauthorized adjacent nodes/edges are not returned. Limits default to 100 nodes, 250 edges and 128,000 serialized bytes; hard maxima are 200/500/256,000. Count truncation is explicit and an oversized serialized result refuses. Source completion is never inferred from a leaf column: the system-of-record flag must come from the explicit source-asset declaration.

The gateway policy addition is `identities[reader].graph[estate] = [exact object IDs]`. This grants only graph reads. It adds no SQL, HTTP, workspace or identity scope. The API is a Python service surface, not a deployed HTTP endpoint. The repository scan is bounded at 10,000 historical records per internal read; estates exceeding it refuse rather than silently return an incomplete graph. More selective database-side traversal remains an optimization.

`coverage(graph)` returns counts by kind/confidence plus all explicit UNKNOWN reasons and remedies. It is ready for the operator's preflight composition; existing preflight output is not changed in this commit.

## Operator integration

1. Supply a hash-checked retained asset catalog and its explicit system-of-record asset IDs.
2. Construct `DefinitionSink` with the approved immutable Files adapter and location. No default local-to-cloud fallback exists.
3. Call `adapters.estate_graph_static.extract(estate, assets, sink, observed_at=..., source_asset_ids=...)`.
4. Construct `GraphRepository` from the configured SharedState; migrate its additive tables and replace the retained-catalog snapshot.
5. Obtain coverage for the operator; construct a GraphAPI with an admitted exact node allowlist for each agent.

These are implemented entry points, not evidence that the live steps occurred.

## Validation

Parallel offline graph/gateway/shared-state/neutrality/literal tests: 72 passed, 14 skipped, 47 subtests passed before the final serialized-byte-bound test; final graph/static tests: 33 passed. The skipped shared-state tests require a PostgreSQL test server; no PostgreSQL connection was opened in this work. Tests cover original definition restoration, no projected-to-raw fallback, unknown predicate forms, metadata hash tampering, identity-sensitive deletion fingerprints, SQL/filter extraction, hard API bounds, unauthorized objects, history tampering, unrelated-change proof preservation and cross-owner deletion.
