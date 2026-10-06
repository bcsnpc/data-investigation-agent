# Install an estate

Optional manifest flags `lineage_proposer` and `assistant_proposer` default to
`false`. Neither is required for an investigation. Approval-time lineage graphs
are platform proposals, not verified bindings; an approver accepts or rejects
proposed code locations. Assistant expressions are untrusted compiler inputs,
and the assistant's own query answers are never evidence. Each assistant call
consumes the client's Fabric capacity as well as a recorded model-call allowance;
the feature's availability also depends on the tenant and capacity. An enabled
flag supplies no permissions. The installed transport must be configured explicitly.

Provide three things. The estate file is validated against
[the manifest contract](../scripts/investigator/estate_manifest.py); only installed
adapters execute. The current registry installs the Microsoft adapter and Azure
model provider. This guide is installation scope, not a claim of other-platform support.

| Client supplies | What the engine does with it | Without it |
| --- | --- | --- |
| **Read-only execution identity**: principal, credential reference outside Git, and explicit per-resource READ/BUILD/QUERY scope as required by the adapter. Several identities may serve different layers. | Resolves the declared reader, enforces scope and budgets, executes guarded reads, records identity and quantity-bound surface attestations. Declared rights never grant permissions. Provider credentials are configured separately. | A missing or refused reader makes that surface unavailable. No publisher/admin fallback or automatic elevation. |
| **One estate file**: environment/storage, installed adapter options, identified layers/resources and readers, reachability ceiling, optional system of record, pipeline audit/history sources, capabilities, accepted limits and budgets. | Approves discovery under the whole manifest/config hash; discovers metadata; walks faithfully comparable boundaries up to the declared ceiling. Reads the load's own audit accounting, never substitutes recounts. Records diagnostic work separately from physical guard/control requests. | No valid approved estate means no execution. Without a declared/reachable application, the walk ends at the deepest established boundary and lists every unchecked hop. A ceiling is never evidence that a layer is reachable. |
| **Where transformation code lives**: read-only Git, local export, or item-definition source with exact location/revision/identity declarations and boundary locations eligible for inference. | Fetches retained code with provenance, extracts supported transformations, compiles proposed bindings, round-trips them and verifies bounded typed profiles as the execution readers. Code-fetch identity remains distinct from data-read identity. | Unsupported/missing code leaves inferred bindings UNVERIFIED and blocks comparisons that require them. Explicit declared bindings may still be usable; names are never guessed across systems. Item APIs requiring write scope need a separate human identity decision; Git/local avoid that scope. |

Install workspace dependencies from `scripts/requirements-workspace.txt`, keep
secrets in the existing external credential mechanism, collect metadata and approve
the current whole-policy hash. A configuration change needs a new matching approval;
do not narrow the hash. Approval-time binding verification has its own manifest
budget, separate from investigation diagnostics. Rolling physical allowance and
expiring batch credits bind estate traffic; reserve restoration capacity for fixture
controls. Review a ticket's scope before explicitly authorizing execution through
the local workspace or `scripts/run_estate_investigation.py`.

The output says what was answered, what was compared and where the walk stopped.
Optional refresh/snapshot capabilities never grant access; snapshot verification
requires aligned reports bound to the actual value queries. **SNAPSHOT_UNVERIFIED**
remains the Microsoft fixture ceiling. Code hashes, standalone timestamps and
agreement of totals cannot establish currency or global equivalence. The demo's
[two-column gate](two-column-replay-gate.md) is known-estate historical producer
replay, including expected refusals, not unfamiliar-domain acceptance.
