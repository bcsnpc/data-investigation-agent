# Repeated UNKNOWN declarations collided

On 2026-10-13 the billing scan retained `GRAPH_NODE_IDENTITY_COLLISION` at
`estate_graph_static.py:88` for the model and report owner refreshes. The error
record has no reference to the failed refresh's uploaded asset payload. The
exact live input therefore remains unavailable to this offline investigation;
the generic cause below is reproduced, but its attribution to those two live
failures is provisional until a new scan or the original payload confirms it.

The static extractor assigned an UNKNOWN boundary the identity
`[origin, reason]`. Two unresolved occurrences in one visual can have identical
wording but different source pointers. The second occurrence reached the
identity-collision guard because its provenance differed. A repeated unsupported
Power Query partition could also collide; the outer definition handler caught
that error and emitted a broader parsing gap, losing the second precise gap.

The boundary identity now includes source asset and span:
`[origin, reason, source_id, span]`. Both locations remain UNKNOWN, with their
original provenance. Repeated processing of the identical location remains
idempotent. Conflicting records at the same identity still refuse. Collection
time and definition content hash do not enter the identity, so a declaration
location keeps its identity across observations and content revisions.

The new identity rule changes UNKNOWN boundary IDs on the next extraction;
normal graph history must record those revisions. Historical graph versions,
scan failures, input definitions and expectations are unchanged. This repair
does not add a parser, invent a dependency, or turn a gap into a verified edge.

Validation: both new occurrence regressions fail before the fix; afterward the
static extraction, partition, asset-catalog, engine-dependency integration and
code-column suites pass **45/45**. A third regression checks identical-location
deduplication and continued refusal of conflicting same-location records. No
estate, platform or model calls were made for this repair.
