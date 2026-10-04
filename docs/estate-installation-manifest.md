# Estate installation and readiness manifest

One file is the installation configuration. `infra/estates/fixture.json` expresses
the existing fixture; `infra/estates/databricks.json` is a hypothetical installation
that validates without an installed transport. Validation is not reachability,
permission, faithful equivalence, evidence currency or a capability acceptance.
No identity or permission is created by a manifest.

The root and neutral nested structures are closed. The installed adapter/provider
registry owns its native options and rejects unknown options. An uninstalled
adapter may validate the neutral document, but execution refuses it. This keeps
provider credential discovery (including the existing secret mechanism) outside
the neutral contract. Secrets themselves never belong in the file.

| Field | Client declares | Engine behaviour |
| --- | --- | --- |
| version, environment, storage | Contract version, isolation namespace and existing catalog/inventory paths | No fallback environment or secondary config file. Catalogs are evidence, not configuration. |
| adapters | Registry key, implementation and adapter-owned connection options | Installed adapter validates native options. The fixture uses the already approved transport accounts and profiles. |
| layers | Ordered inventory; stable asset ID, closed role, readable business role name, adapter/address/reader and reachable flag | Reachability is a ceiling. Undeclared or configured-unreachable layers are not probed; actual reads still require scope, compiler proof and attestation. |
| resources | Explicit audit, history or code resources with address and reader | References must resolve to an inventoried resource; native execution still needs current discovery. |
| system_of_record | A layer reference or null | Without one, the walk ends at its deepest declared comparable layer. Declaring a source does not make it reachable. |
| identities | Existing principal, secret-mechanism reference and exact resource rights | A layer/resource reader must have exactly one declared READ scope. The installed adapter rejects conflicting account, credential or address declarations; it grants nothing. |
| pipelines | Boundary endpoints, producer/delivery identities, audit PRESENT/resource or UNAVAILABLE/reason, history location or null | Audit declarations become the consumer's load-audit contract. Missing PRESENT resources refuse installation. Existing audit/history evidence gates remain. |
| lineage | Declared endpoint bindings with provenance, code-inference permission and locations, optional source capture fields | Declarations are carried as distinct evidence, conflict with an observed path refuses, and a declaration alone never manufactures quantity equivalence. Inference is a ceiling for an adapter that can produce it, not a new transformation reader. |
| capability_ceiling | Sorted closed operation list | Intersected with adapter capabilities. Configuration cannot declare a stub or unavailable operation operational. |
| model | Provider/deployment/endpoint, governed generation limits, provider-owned credential lookup and recovery ceiling | Consumer validators remain authoritative; no ticket-driven model/budget changes or provider fallback. |
| budgets | Diagnostic cap, input bound, path-depth ceiling, rolling 24-hour physical allowance, daily planner bounds, round start/pot/restoration reserve | Physical requests remain charged; round exhaustion refuses before dispatch and protects unused restoration capacity. Credits still require separately recorded approval. No counter reset or refund. |
| accepted_limits | Explicit known limitation code/resource/plain statement | Relevant claims name the limitation "By configuration". Acknowledgement cannot waive attestation, scope, snapshot or refusal rules. |

The active runner (`run_estate_investigation.py`, also the adaptive CLI), local
workspace host and discovery CLI accept `--manifest`. They do not accept legacy
config/profile/policy/estate files. Typed diagnostic tools and historical evidence
utilities remain developer tools; they are not alternate installation runners.
Historical configs, receipts and tapes stay intact and are not migrated in place.

Example: `python scripts/run_estate_investigation.py --manifest infra/estates/fixture.json
--ticket ticket.txt --request-key unique-attempt --output .local/attempt.json --approve`.
Discovery uses the same manifest and pins the entire validated installation in
its approval. **The fixture manifest has not been recollected/re-approved or
live-executed:** the retained approval pins the older config and must refuse the
new installation until an explicitly recorded current approval exists. This PR
spends no estate reads and does not reinterpret Round Five's historical tapes.

The fixture audit is in the approved ops Warehouse. The lakehouse audit remains
historical lag evidence, not the configured audit source. Optional snapshot and
refresh timing stay unavailable by default; native transport access and query-bound
snapshot limits are unchanged. The application grant remains one table only;
dia-reader retains no scope. Client readiness means usable declared bindings,
typed quantities, an attested audit if available and approved isolated readers;
it does not mean every estate exposes an application or synchronized surfaces.

Synthetic validation exercises unknown keys, missing roles/audits, bad references,
undeclared scopes, conflicting credentials/addresses, consumer bounds, round
restoration reservation, configured unreachability and lineage conflicts. The
Databricks document contains no Microsoft-specific vocabulary; its transport and
provider are intentionally uninstalled, so no connection or cloud call is made.
Engine bytes changed; all previous freezes remain invalid. No investigation run
or ledger row is claimed for these unit tests.

Legacy execution entry points cannot bypass this installation. The typed-action
CLI now reads saved status only, with `--manifest`; the historical evidence server
is read-only and also takes the manifest. Its former planning/worker switches
are removed. New investigations run through the budgeted manifest workspace.
Synthetic tests reject the old configuration/execution switches and verify that
status reading cannot execute a saved run. Historical receipts are unchanged.

Discovery uses this same installation and budget governor. HTTP requests, nested
OneLake requests, each SQL catalog command, and Warehouse catalog guards are
admitted and counted individually. A logical discovery operation is not one
physical request. Exhaustion prevents sending another request; partial coverage
remains unavailable rather than silently becoming a complete context. Synthetic
raw protocol tests establish two-request accounting and refusal before transport.
