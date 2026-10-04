# Exact declared application quantity hop

2026-10-03 America/Chicago. Follow-up to merged #353. This is implementation
validation, not a live application-boundary investigation.

The Microsoft adapter can now extend a whole-entity integral SUM through a
collected Copy Job into its exact approved application table. It requires the
served Batch/Overwrite declaration, no source predicate/query or partitioning,
explicit one-to-one name mappings, disabled truncation, a current connection
record, exact source/destination scopes and noncomputed source columns. Unknown
selection or conversion forms, stale connections, multiple producers and schema
gaps remain refusals. The mapping is derived from the inventory's definition and
connection, never configured as a metric route. A notebook may obtain the copied
input's physical schema from that same declared mapping. Filtered/grouped lower
scope remains NOT_COMPARABLE; `_lower_quantity`'s existing refusal is unchanged.

Application reads compile against the approved current SQL catalog. The new
transport preserves every existing read-only session/object guard, uses the
existing DPAPI credential and issues one quantity statement with CURRENT_USER,
DB_NAME and SERVERPROPERTY EngineEdition. Edition 5 identifies this adapter's
Azure SQL product; any other edition refuses attestation. Surface description
columns are removed from the quantity and retained separately with VALUE_QUERY
binding. No read retry, publisher fallback or extra grant is introduced. The
application reader's account must be explicitly declared in `sql.auth.account`;
absence is an unavailability. Existing configurations retain their old behavior.
The transport is included in the engine fingerprint.

Seven new adversarial/integration tests passed: exact source mapping, unknown
predicate and incremental/append/conversion refusal, stale/computed/ambiguous
evidence refusal, real governed catalog admission with retained report, filtered
scope and missing-identity refusal, same-statement guards, and missing/wrong
self-description refusal. The existing depth/independent-lower tests plus these
passed 36; flexible investigation passed 39 and fingerprint tests passed four.

Planner directory entries and SQL-object counts are unchanged by this quantity
path extension; the new module adds no planner directory or prompt content. The
connection evidence change in #353 measured 28 entries / 11 SQL objects / 5,543
characters before and after and requires byte-identical projected payloads.
No live read, fixture mutation, allowance change or ledger row in this change.
Engine bytes changed; prior freezes are invalidated.

Remaining Part B work: declare and consume the attested audit source, add guarded
delivery/freshness producers without inventing a capture cut, wire the isolated
loaded estate to an executable presentation path, recollect/re-approve once those
declarations are complete, then preserve all four authored scenarios and family E.
The original fixture's literal Bronze does not acquire an application dependency
merely because another Copy Job exists. No CONSISTENT_TO_SOURCE, LOAD_LATENCY or
INGESTION_GAP live result is claimed here.
