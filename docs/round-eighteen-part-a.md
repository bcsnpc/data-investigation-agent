# Round Eighteen ? Part A

Completed 2026-10-12 local / 2026-10-13 UTC. Draft #424 targets #423; neither is merged. Prior freeze is invalid.

The installed live paths now require an exact endpoint/method or SQL object policy before transport. Missing policy denies. SQL parsing rejects writes/multiple statements/comments/SELECT INTO; DAX permits EVALUATE only. Existing permission checks, bounded reads and accounting remain. The kill switch also blocks provider calls. Platform persistence is a separate code-owned channel, even when the same managed identity authenticates it; the agent cannot select that channel.

Integrated A gate: **43 tests and 47 subtests passed** (gateway, literal audit, MI auth, Linux worker). The gateway branch additionally passed two disjoint groups of **230 and 120 tests** before integration. Full inherited baseline stopped at 4 failures/2,751 passes: three missing crypto packages (now installed), and an intermittent aggregate test returning no outcome. A later focused aggregate pass failed a different case; ten isolated repetitions did not reproduce it. This is retained, not counted as green. Integrated shared-budget tests exposed a synthetic transport grant issue being repaired in Part B.

The product literal scan covers 358 installed engine/adapter/CLI/UI files. One fixture-specific prompt example was removed; two validated example manifests are published. Historical fixture builders remain explicitly non-product tools, listed in the audit. No golden ticket or expected finding changed.

Explicit boundaries: this is an application gateway, not an OS firewall. Authentication and authorized operator deployment commands are trusted control operations. Manual legacy PowerShell is not an agent capability. Unsupported KQL/legacy SQL paths refuse. Linux MI quantity transport is implemented and tested; MI SQL catalog collection is still unavailable. No cloud permission is inferred from a valid manifest.

The approved estimate was committed before deployment. East US created the private storage account/containers, RBAC vault and MI with the two approved platform grants; PostgreSQL refused regional provisioning. Owner approved the fallback order; South Central US availability and regional pricing were checked, and deployment is in progress. No estate grant, estate write, investigation or model call occurred.

Evidence: local `round-eighteen/a-final.log`, baseline and integrated logs, deployment operations and resource/role listings. New code and configuration invalidate the previous freeze. Part B follows; no owner wait requested.
