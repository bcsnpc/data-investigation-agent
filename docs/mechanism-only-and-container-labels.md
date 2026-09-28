# Mechanism-only synthesis and discovered container labels

2026-09-28 UTC. #285 merged after six successful checks at
`e6c507885db5109aae0d11f75840409e8e3eb362`.

## Ownership of prose

The synthesis response has no `limitations` field. Its technical statement is
mechanism-only; business wording remains the exact deterministic allowed text.
A shared schema/validator pattern rejects evidence caveats (including snapshot,
attestation, unknown intent and unconfirmed matches) in the mechanism. Assembly
also rejects a repeated retained limitation sentence. Violations are rejected
intact, never stripped, truncated or retried for presentation. The engine renders
the original assessment limits, structured surface fields and snapshot status.
A narrowly recognized trailing clause saying that both sides may not use the
same snapshot is coalesced into the canonical snapshot limitation when every
comparison is unverified. Other judge qualifications remain in the limits block;
unrecognized clauses and all original receipt/mandatory-limit text remain intact.
This is duplicate-clause display consolidation, never a length cut. Synthesis
cannot create a second set of qualifications in either a separate field or its
mechanism paragraph. Output version is now 4; historical saved outputs are intact.

This is a structural responsibility split with syntactic validation, not a claim
that a keyword pattern proves arbitrary English semantic equivalence. Tests cover
the observed failure and paraphrases. Original limit strings and judge receipts
remain intact; this change does not silently delete unknown qualifications.

## Container names

The adapter follows each resolved asset's exact `parent_id` into the retained
discovery context. Its name and the parent's name travel in a display-only map
with `DISCOVERED_PARENT_ID` provenance. The neutral engine carries that map into
the technical record; no layer convention is encoded into the engine.

The current retained context distinguishes:

- L2: stock movements e1b8e1 in warehouse silver e1b8e1.
- L3: stock movements e1b8e1 in warehouse bronze e1b8e1.

Those container names come from discovery. They are not inferred from similar
object names or treated as surface self-attestation. Missing/nonunique container
names get an explicit L-term disambiguator rather than a guessed layer name.
Tests use identically named Sales tables in Regional reporting and Operational
capture, with different discovered parent IDs.

## Context cost and validation

On the saved 778bcd6f evidence, synthesis payload characters are 15,108 before and
after; directory entries 0/0, SQL directory entries 0/0. Synthesis has no directory.
Container names are rendered after the provider call and are not added to model
context. The wire schema is 4,402 -> 4,433 characters; the mechanism exclusion
pattern replaces the old free limitations field. The investigation planner
payload is unchanged. A test requires byte-identical synthesis payloads when only
display labels are added.

All 1,316 regression tests passed in 423 seconds on the final unchanged engine
(SQLite ResourceWarnings, no test failures). Focused schema/rendering tests cover
rejection of model-written caveats, rejection of the removed limitations channel,
distinct container labels, preservation of evidence and unchanged payload coverage.
Engine changes invalidate prior freezes. No live run, model call, estate read,
credit grant, cap change or policy change was made. Resolver inspection used the
local catalog opened read-only, with execution callbacks that raise if invoked.
No investigation was run, so no new investigation ledger row is appropriate.

See the separate [nine-family cost proposal](nine-family-batch-cost.md). It is a
proposal only, not an approved grant or a promise that all families can complete.


The initial 1,314-test invocation retained three failures: one obsolete assertion
for the removed limitations field, plus ADMISSION_CHANGED and an interrupted
replay call-count assertion while engine files were still being edited. The
obsolete contract test was updated; no admission or replay safety check was
weakened. The final full rerun above held engine files unchanged and passed.
`git diff --check` also passed. No live validation was requested or performed.
