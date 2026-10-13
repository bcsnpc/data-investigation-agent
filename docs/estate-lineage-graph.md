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

## Round 19 Part B: bounded producers and scoped verification

`adapters/graph_dependencies.py` admits only four fixed metadata queries, an
exact model/workspace/identity grant, a bounded result (with truncation sentinel),
and the existing caller-owned metadata meter. Each physical attempt goes through
`bounded_call`. Permission failures preserve their returned receipt; unsupported
routes and omitted calculation rows remain UNKNOWN. No retry or privilege fallback
is hidden in this collector. The XMLA transport is an injected installed adapter;
this commit does not claim one has run or been installed in the cloud image.

Microsoft Learn explicitly says that [INFO.CALCDEPENDENCY requires semantic-model
write permission](https://learn.microsoft.com/en-us/dax/info-calcdependency-function-dax).
The investigator cannot receive that permission. The [ExecuteQueries API excludes
INFO and DMV queries](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group).
[INFO.VIEW.RELATIONSHIPS](https://learn.microsoft.com/en-us/dax/info-view-relationships-function-dax)
documents active state and filter direction, but does not override this REST
restriction. These are dated 2026-10-13 documentation findings, not estate probes.
The fixed XMLA operation requires its own exact gateway grant and cannot be sent
through the ordinary DAX operation by this collector. Relationship/column view
rows can be retained; only calculation dependency rows currently have the graph
edge conversion function. An empty response does not remove static coverage gaps.

`graph_interpreter.py` accepts at most 24,000 code characters and 128 admitted
objects. One governed provider call returns up to 64 proposals. Each proposal must
cite a byte-preserving Unicode text span and existing graph IDs. Unknown fields,
invented quotes and out-of-slice endpoints refuse. Every edge is INFERRED; static
gaps remain, because a proposal list does not establish completeness. The installed
provider adapter returns its metadata separately for caller retention. There is
no code execution and no model-selected tool or retry path.

The existing sqlglot static reader handles single explicit-column SELECTs and
CREATE VIEW SELECTs, including WHERE/JOIN dependencies. It now handles the actual
WarehouseTable/WarehouseColumn catalog kinds as well. CTEs, stars, procedural
control flow and dynamic SQL still produce named gaps, not a partial complete path.

`graph_verification.VerificationResolver` requires a trusted retained compiler
binding, a non-numeric dependency witness, and two successful read receipts bound
to the exact endpoints, statements, scope and definition. All four attestation
fields must match. BLANK is distinct from zero, missing value and failed query.
Equal values alone cannot verify an edge. The resulting claim is explicitly
**scoped query agreement only**, not semantic correctness or global equivalence.
Missing aligned query-bound snapshot reports retain SNAPSHOT_UNVERIFIED.
`verify_path` admits a connected edge slice and its two-reads-per-edge budget
before sending anything. Its compiler, query-reader and evidence-store adapters
must be installed by the runtime; no live path verification is earned by these
offline contract tests. `GraphRepository.verify_edges` appends proof/history
without falsifying a changed definition hash. The consumer refuses arbitrary
self-reported VERIFIED dictionaries and requires the receipt resolver.

### Retained catalog audit correction

The first billing import refused nine content hashes. Inspection established
that all nine exactly match compact JSON: enrichment used `onboarding.digest`,
while initial `Collector.asset` used sorted JSON with spaces. This was **not**
evidence of tampering or a stale metadata body. Both exact historic encodings are
now explicitly recomputed and recognized, with the encoding recorded on each
node; neither retained body nor retained hash is rewritten. Unknown hashes still
refuse. Future enrichment uses the initial capture serializer and updates the
expanded byte budget transactionally before mutation. Original scans stay intact.

Freeze invalidation: graph contract/producers, gateway vocabulary and discovery
hash production changed. No estate/model calls, recorded-run changes, new scope,
secret changes, or live verification were performed by these tests.

### Item-owned seed and incremental identity

`extract_partitioned` uses the retained parent-ID chain to assign each graph node
to its Fabric item or SQL database; edge ownership follows the consumer node.
Graph IDs are constructed with that owner at extraction, so an item re-extracted
with the same retained external symbol table has the same IDs. No prefix/name
heuristic chooses an owner. `replace_many` validates and replaces all seed owners
in one transaction and reads the current nodes and edges only once. Cross-owner
references can be inserted in either order; a missing endpoint rolls the whole
batch back. Unchanged owner hashes are skipped. Re-extraction preserves prior
query proof as STALE when its underlying edge changes.

A changed report needs its retained external model symbols for re-extraction.
Passing only the report definition cannot resolve external model fields and
continues to emit UNKNOWN. This is a coverage boundary, not a justification for
silently guessing those symbols. The caller can supply the approved retained
symbol table, replace the changed item's assets in it, extract partitions and
apply only the changed owner. No new estate read is implicit in that operation.

Local retained-material validation (2026-10-13, zero estate/model reads):

| Estate | Retained scan | Owners | Nodes | Edges | DECLARED / UNKNOWN edges | Visual/slicer paths |
|---|---|---:|---:|---:|---:|---:|
| Fixture | 942ae95f-367f-4d11-bb1a-701bb955930c | 40 | 851 | 980 | 855 / 125 | 76 |
| Billing | e2c81334-17c6-474f-957b-53ff5bf1565b | 9 | 270 | 294 | 277 / 17 | 7 |

All 83 paths return named stopping points; none are truncated or claimed verified.
Source-of-record declarations were not inferred into this material. The fixture
scan hash is `87ec081a1433990e99757a954634bd674c6015fda78eea569395e867c7974493`;
billing is `1c07c0c75098efe5b2ede369cd92498b7c8160405a0c6991c81ef91e54139c56`.
The local staging directory contains `partitions.json`, `owner-manifest.json`,
`coverage.json`, `visual-paths.json`, and `definitions-manifest.json`; exact raw
bytes are at `definitions/<sha256>`. The portable `cas://retained-definition/`
references require an explicit configured resolver when published; local staging
is not itself Blob publication. Fixture definitions are 567 objects / 540,032
bytes; billing definitions 189 objects / 132,158 bytes. Earlier semantic-only and
intact-earlier-billing staging outputs are separate and are not the publication
seed.
