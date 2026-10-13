# Bronze cloud authentication follow-up — 2026-10-13

## Owner decision under CLAUDE.md §8

Chaitu approved a read-only correction if the failed Bronze read used an older identity or the existing investigator principal lacked Bronze access, followed by one bounded Bronze check (maximum ten physical requests). Only a successful Bronze check authorizes one additional full verification and family A demo attempt. That attempt must retain the 1,800-second runtime, exclusive writer lease, fresh offline admission and exact replay before the demo. No write rights or other scope changes are authorized. Restore the six-hour schedule and release any lease afterwards. This dated decision supersedes the prior no-further-attempt statement only within those conditions.

## Saved failure and identity comparison

Third-attempt tape SHA-256 `e47da8adbde93ac29737d2498d2466f3052020cfc2c1ae191b1853527bf864a7` retains sixteen SQL worker payloads. All sixteen use `federated_reader`, app `531419ef-1610-415a-b8bf-01a4b6aad751`, Fabric-tenant principal `439ceb25-d200-4f02-95cf-4b1318faca62`, tenant `dff91047-ebc2-4657-8dbe-5af328d57780`. None uses the old SQL login or user sign-in cache. Token-provider code validates those bindings and the SQL audience before connecting; a successful token acquisition is not a successful database login.

The six completed bounded witnesses read Gold targets and Silver sources. The seventh read Silver successfully, then failed on Bronze with retained `LowerReadError`, kind `SqlException`, number `18456`; no underlying causal diagnosis is established by that number. Its receipt is `05b6f722-ec3b-4e41-af3e-bee9c8841f61`. The failed database is `warehouse_bronze_e1b8e1`, lakehouse `09ba0ef9-7342-4179-a49e-1fc8adf48d82`, SQL endpoint `7050f705-e595-4708-b62b-1836dac30741`, in workspace `149f8d99-1c66-4a0a-9624-759be002bb60`.

All three use the same declared server, `i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com`, with distinct explicit database names. The Bronze query is the original compiled key-range comparison over the retained declaration, not a newly invented query or the Azure application database.

## Current permission and endpoint readback

Four separately metered owner control GETs returned HTTP200 between 19:15:40 and 19:16:04 UTC: workspace role assignments, Bronze lakehouse, Silver lakehouse, and Bronze SQL endpoint. Before record: `.local/round-nineteen-b/bronze-access-before.json`. The investigator already holds **Viewer** on this workspace; Bronze's current endpoint ID, server, display name and successful provisioning state agree with the retained route. Silver agrees as well. No role or identity was changed, so there is no grant to quote or artificial after-grant claim.

Microsoft documents that a workspace role including Viewer suffices to connect to Fabric SQL items. It also documents that service principals need Fabric API token initialization. These describe platform requirements, not the cause of this particular failed read; the successful same-principal Silver/Gold reads make an entirely uninitialized principal an insufficient explanation. [Authentication](https://learn.microsoft.com/en-us/fabric/data-warehouse/entra-id-authentication), [service-principal initialization](https://learn.microsoft.com/en-us/fabric/data-warehouse/service-principals).

## Probe admission and retained launcher failure

The approved probe reuses the one sealed Bronze worker request, narrows the job gateway to Bronze, retains its read-only permission guards and quantity-bound surface report, uses the existing investigator federation, and caps physical requests at ten. No model call, new grant or alternative identity is allowed.

Launcher `job-dia-worker-elooltx` failed before importing any platform or SQL code: `ModuleNotFoundError: No module named 'cloud_stage_environment'`. It admitted zero SQL probes. The inline command omitted `/app/scripts` from Python's module path. Original launch input is retained in `.local/round-nineteen-b/bronze-cloud-check-01/`; the corrected launcher explicitly sets that path and retains a new launch record. This is a launcher correction before the single SQL probe, not a successful Bronze check or a full verification retry.

The six-hour job schedule is temporarily Manual, runtime remains 1,800 seconds, and the prelaunch execution listing contained no running job. The corrected launch `job-dia-worker-exoycg8` is pending. The full verification and demo are not admitted.

## Offline replay diagnostic

The original third capture's Windows replay at its recorded revision failed: the recomputed final first reports `VERIFIER_ENGINE_DIFFERS`, followed by the old wrapper's `TAPE_EVENT_DIFFERS:FINAL:CONFIGURATION`. The runtime fingerprint includes `sys.version`; the Linux producer and Windows replay environment differ. This replay is not a pass and is not evidence of a different Bronze result. No tape, receipt or expectation was altered. The independently required same-image replay for any newly successful verification remains mandatory.

## Follow-up result and retention defect, 2026-10-13

The corrected launcher `job-dia-worker-exoycg8` admitted the one Bronze check. Shared PostgreSQL accounting independently records **four SETTLED physical requests, zero pending and zero model calls** in session `round-nineteen-b-bronze-check-01`. It then failed at `Tape.finish` with `TapeError: TAPE_BOOTSTRAP_FIELDS`. The operator wrapper had supplied an incomplete capture header; validation occurred after the producer instead of before it, and the exception prevented its result ZIP upload. The result and partial worker journal were left only on the ephemeral replica. They were not recovered. This is an evidence-retention failure introduced by this session's operator wrapper, not a successfully recorded Bronze result. Four requests alone do not establish the quantity or its attestation, so **Bronze is NOT_VERIFIED and the additional full verification/demo are NOT_ADMITTED**. No replacement SQL read was made.

The successful connections/permission guards implied by dispatch reaching a fourth request narrow the earlier18456 diagnosis, but cannot replace the missing native result. No new role was justified; identities and scopes remain unchanged. The precise reason for the original18456 remains unestablished.

A generic recorder repair now validates the existing seven-field bootstrap header at construction, before any producer can run. Regression tests use this malformed launcher header and prove that the producer is never called and no artifact is created; a valid existing header still seals and replays. The old unpinned-context test is updated to expect the earlier refusal. Original tapes and failures are unchanged. The local operator also requires a valid header and independent failure-safe result upload before any future owner-authorized attempt; no such attempt was started here.

The earlier stdout retained the two exceptions in this session's tool record. A later control log read returned `ExecutionReplicaNotFound`/HTTP404 for the cleaned first replica; its exact response is preserved in `.local/round-nineteen-b/bronze-window-close/`. No fresh query was used to recreate evidence. The independent budget snapshot is `.local/round-nineteen-b/bronze-budget-terminal.json`.

After verifying all executions terminal, the original `0 */6 * * *` schedule was restored and read back, with1800-second runtime and zero retries. Receipt: `.local/round-nineteen-b/bronze-window-close-02/summary.json`. No new writer lease was acquired for the single probe; the previous full attempt's lease remains released. No counter was reset or refunded. Engine freeze invalidated by the fail-before-producer repair.

Dated offline validation correction: e34 full regression returned4,461PASS,2FAIL,46skip,1,557subtests. The privacy-mode error must precede generic field validation; its original test is unchanged. The worker-launch test now provides a valid seven-field header, retaining all original process-policy assertions. Seven targeted tests/five subtests pass. No new live check follows.
