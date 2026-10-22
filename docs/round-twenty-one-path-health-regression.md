# Bounded graph paths retain code-owner refusals

2026-10-22. Full regression exposed the same failure in the graph asset-catalog
test and its two inherited container-schema variants. A derived column is owned
by its destination lakehouse but its proof comes from notebook `book`. With the
notebook collection marked UNAVAILABLE, the bounded path reader still returned
three DERIVED edges. Its stop reason mentioned unavailable code only after some
edges had already been followed.

The old complete reader hydrated `definition_source_owner` from the approved
asset-catalog ownership index; the new SQL-bounded reader omitted that step and
looked up collection health only for destination node owners. Both readers now
use one ownership/health decorator, applied only to their already-selected
records. The path reader retains SQL adjacency filtering and the node/edge caps.
The source-owner lookup is restricted to provenance source IDs in those returned
nodes and edges. The existing approved ownership index contains owner metadata
and blob references (bounded at construction to 1,000 owners); no referenced
asset CAS bytes, unrelated historical graph bodies, or complete definition
catalog is loaded. No sealed graph body, hash, owner or unavailable observation
is rewritten. Verified edges affected by unavailable proof retain the existing
stale qualification and the API refuses to traverse them.

The permanent regression poisons an unrelated historical node body and forbids
calling `records()` while exercising `path_records()` and GraphAPI. It verifies
that the lakehouse-owned root gains notebook proof ownership, the notebook's
exact unavailable reason survives, and no outgoing edge or upstream node is
returned. Original refusal assertions remain unchanged. Initial targeted asset
catalog, container-schema and facts suite: 70 passed, 1 opt-in PostgreSQL skip;
no live calls or grants.
