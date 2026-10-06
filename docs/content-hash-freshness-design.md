# Content-hash freshness at conclusion — design

2026-10-06 America/Chicago. **Design only; no implementation or estate read.**

Two different things can move: the definition used to interpret a layer, and
the data a query sees. Keep separate evidence kinds. Neither is a served-version
report, and neither removes SNAPSHOT_UNVERIFIED.

**Definition hash.** At the first read retain SHA-256 of the exact definition
bytes plus their declared location/identity: the model definition for the
presentation quantity; the transformation definition for each derived layer;
the declared source schema/load mapping for the application boundary. Share one
definition receipt where several layers genuinely use the same definition.
At conclusion retrieve those same declared locations, with the same code identity,
and compare the hashes. No global search, cached answer described as a new read,
or newly inferred replacement binding. A changed definition makes its earlier
binding stale: “The definition changed during these checks. This finding applies
to the retained definition; the current cause has not been established.” The
engine renders that limitation in both outputs. An unavailable recheck is named.

**Data observation hash.** Separately, a repeat of the identical compiled probe
can hash its complete typed quantity result and cell scope. That detects a
changed checked quantity, not unchanged table content: compensating row changes
can leave a sum unchanged. A full data-content hash requires an adapter's faithful
complete-row renderer, including scope, multiplicity, types, nulls and string
semantics. The current model adapter has no such renderer. Do not call an
aggregate fingerprint a table-content hash. A truncated sample cannot substitute.

| Route | Extra physical work at conclusion | Evidence ceiling |
| --- | --- | --- |
| Local code export | One content read plus a sidecar read when identity metadata is present | Definition bytes at a declared local location |
| Git code | One content GET; notebook identity needs another GET; a mutable ref can need a third | Definition at the resolved revision, not served data |
| Fixture definition API | POST plus bounded polling/result GETs when202; potentially more than one | Definition at the declared item, not its data version |
| Identical quantity probe | One value request per previously guarded object; any necessary new guard remains counted separately | Checked quantity at two observations; no full content/snapshot proof |

**Decision: do not implement this round.** The fixture's definition route cannot
guarantee one physical request per layer; code_definition.fetch() follows202
with status/result GETs. A full-data hash also lacks a faithful native renderer.
Even quantity-only repeats would take the ten-diagnostic source case to thirteen
for three layers, above the unchanged12 cap. Nothing is silently raised or
relabelled as overhead. The implementation criterion is therefore not met.
Later work needs a one-response definition/identity route or an explicitly
approved cost change, plus a distinct data-content capability where supported.

DECIDED WITHOUT REVIEW: keep definition, quantity-observation and full-content
claims distinct. Reject hashing only the old cached bytes, a standalone metadata
timestamp, or an aggregate and calling that freshness or snapshot verification.
