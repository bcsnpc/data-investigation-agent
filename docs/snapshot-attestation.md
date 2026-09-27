# Optional snapshot attestation

2026-09-27. Item 2; #277 merged after six green checks at `6c15b76`.
Implementation and offline validation only. No live run or freshness fixture.

## What changed

Every completed cross-surface comparison now carries a versioned
`snapshot_attestation` with both reports, their identity provenance, a reason,
and the sides lacking query-bound versions. Its honest default is
`SNAPSHOT_UNVERIFIED`. Execution-surface independence remains a separate fact;
`CROSS_SURFACE_VERIFIED` never implies snapshot verification.

For each unverified comparison, the outcome carries a mandatory, deterministic
limit. Agreement explicitly does not establish currency. Divergence explicitly
states that different update timing was not excluded. Business prose identifies
the affected comparison and whether the missing version belongs to the check
nearer the report or further back. Technical output retains the same warning and
both complete attestation reports. These clauses are appended by the renderer,
not delegated to the model or silently truncated to a prose bound. The structured
status is present in both outputs; technical identifiers remain outside business
prose. Existing bounded model text remains subject to its original limits.

Synthesis validates against original observations and additionally asserts that
the digest preserves the complete snapshot attestation. Dropping or changing any
of its fields is rejected. Historical observations remain unchanged and default
to unverified when projected; they are not retroactively relabelled as verified.

## Verification rule and its limits

An adapter may attach `snapshot_identity` to a quantity's evidence or expose the
optional `snapshot_identity(probe)` capability. A usable report must identify its
own evidence, the exact quantity receipt, the same engine/connection/object, a
native dataset identity and nonempty opaque version, and its identity provenance.
Its binding must be `QUERY_BOUND`: the adapter must obtain the version from the
actual quantity execution or a platform guarantee that binds it to that execution.
An execution-reader report must name the execution reader; a metadata-identity
report must identify a different account. These are adapter evidence contracts,
not fields the model can populate as an interpretation.

`SNAPSHOT_VERIFIED` requires both bound reports to name the same dataset and
version. Equal version numbers on different datasets do not verify alignment.
Two known but different snapshots remain unverified for alignment with the explicit
`DATASET_OR_VERSION_DIFFERS` reason. This does not assert that their individual
version reports are absent. Transformed layers need a future declared input/output
snapshot manifest; same-number versions are never guessed equivalent.

Matching snapshots establish alignment, not that either is the latest committed
state. No outcome is selected or refused based on snapshot status. Enrichment
runs only after the deterministic procedure has selected its outcome, caches a
report per quantity receipt, and retains optional-read failures without changing
the classification. Tests compare absent, verified, mismatched, malformed-binding,
metadata-only and failed enrichment for equal and divergent cases.

## Optional Microsoft metadata identity

An estate may add this secret-free section to its approved Fabric configuration:

```json
"snapshot_identity_reader": {
  "account": "metadata@example.com",
  "profile": ".local/snapshot-metadata"
}
```

It must be distinct from quantity-reader accounts and their profiles. Existing
whole-file discovery approval still applies to configuration changes. Nothing was
added to the live configuration, and no identity, scope or permission was granted.
The execution reader is never elevated and there is no implicit publisher fallback.

The Microsoft adapter uses the configured identity's isolated Azure CLI profile,
validates token account/tenant/audience, and performs one fixed read-only metadata
query per supported compared surface after the walk. DAX uses the configured
ADOMD library and model identity for `INFO.DELTATABLEMETADATASTORAGES()`; SQL uses
the approved server and compared database for `sys.dm_db_external_tables_log_status`.
Each request is metered through the existing governor. Results are bounded at
20 rows (a 21st detects truncation) and 64 KiB; refusals/empty/truncated responses
remain explicit. Credential-bearing exception text is not retained.

**These separate Microsoft metadata queries are `METADATA_ONLY`, not query-bound.**
Even if an administrator can read them, their success alone cannot establish the
version served by an earlier quantity query. They retain versions and provenance
as enrichment but cannot promote today's estate to `SNAPSHOT_VERIFIED`. Promotion
is supported for genuine query-bound adapter reports and tested offline; it has
not been demonstrated live on this platform. The tested least-privilege reader
constraints in CLAUDE.md still stand. This avoids implementing false attestation
under the guise of an optional identity.

## Context cost and validation

This changes the synthesis evidence view, not the investigation planner directory.
The offline one-comparison golden view grows from 440 to 610 serialized characters
for the default unverified report. Directory entries remain 0 to 0, SQL object
entries 0 to 0, and evidence entries 1 to 1 in that view. The planner's existing
directory is untouched. Metadata-bearing reports cost more and are bounded as
above; no context is removed to pay for them. The complete attestation survives
projection, with tests rejecting dropped fields rather than silently compacting
it away.

Final validation: **1,286 regression tests passed** in 268.277 seconds; the initial full pass had 1,285 passing tests before the final inline-report test was added. PowerShell syntax and `git diff --check` passed. An earlier focused run exposed a trailing-space sentence-validation failure in the revised summary; it was corrected before both full passes. No browser or live transport session was run. Focused tests
cover default status, query binding, dataset/version identity, provenance,
unchanged outcomes, optional failure, no identity fallback, configuration checks,
projection integrity and the mandatory text in both rendered outputs. No cloud
calls or LLM calls are part of these tests.

Engine bytes changed, invalidating prior freezes. No new freeze, unfamiliar-domain
claim, budget redesign or freshness-fixture attempt. Item 3 remains separate work.
