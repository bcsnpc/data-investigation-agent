# Round Twenty: bounded shared state and daily smoke

Implemented offline, 2026-10-21. Live deployment and scheduling are owned by the round operator.

## Shared state

All production PostgreSQL connections in tracked code now open through `investigator.postgres_connection.connect`: `configured_state()` in `shared_state.py`, and the platform health reader in `platform_health.py`. Every open sets a 15-second connect bound, a 30-second startup statement timeout and idle-in-transaction timeout, and a five-second lock timeout. Only acquisition timeouts are retried, at most twice, after 30 and 60 seconds. Failed queries and transactions are never retried by this helper. No credentials or driver exception text are logged.

Budget admission and settlement remain separate short transactions. A context marker now makes a gateway request fail before dispatch when it is attempted inside a shared-state transaction. The parent worker launcher checks this too, so child-process isolation cannot hide its parent's lock. The existing gateway still checks identity, object, read-only guards, query and bounds.

Long writer leases are retired from the new runner. The gateway refuses external requests while a legacy exclusive writer lease is installed. Existing legacy `finally` releases survive for historical wrappers; a process crash can bypass `finally`, so persisted lease expiry remains authoritative. The crash regression uses a subprocess that exits without cleanup and confirms another writer proceeds after expiry. PostgreSQL transaction-scoped advisory locks are released on close/rollback; a disconnected process cannot retain a permanent session lock. The idle transaction timeout bounds a stalled live connection.

## Daily smoke integration

The fixed runner registry uses `daily_smoke.handler(plan, context)`. `plan.target` is deployment configuration: `version`, a unique `run_id`, `reader_authentication`, a guarded Gold worker `gold_payload`, own-platform `platform_blob`, and `demo_earned`. The Gold payload must use that same reader. It carries the already-allowed table, SQL and result columns; existing SQL permissions and read-only guards run normally. Its physical calls draw from the monthly collectors line selected by the caller, not the investigation allocation.

Each step is recorded through `context.step`: audience/identity-bound sign-in, one Gold value query, write/read of a challenge in the tool PostgreSQL `daily_smoke` namespace, and upload/readback of a small own-platform CAS Blob challenge. No estate database write exists. The final record is one line: run ID, DAILY_SMOKE, PASS or FAIL. The full structured result retains individual checks. Driver messages are excluded from errors because they may contain credentials. A family A callback is required when `demo_earned` becomes true; until the demo succeeds it remains false. This is health evidence, not a verified source-path claim.

`daily_smoke.schedule_plan()` emits a plan for the existing `job-dia-worker`, pinned image, UTC cron `0 6 * * *`, parallelism/completion one and 1,800-second runtime. It creates no resource and applies no ARM mutation. The root operator applies it only after integration tests, using the same runner command. No second launcher is introduced.

## Cost estimate before scheduling

Sources checked 2026-10-21: [Microsoft Learn billing](https://learn.microsoft.com/en-us/azure/container-apps/billing) and [Container Apps pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/). Jobs incur active compute while executing, no idle or inbound-request charges. Monthly per-subscription free grants are 180,000 vCPU-seconds and 360,000 GiB-seconds, shared with other consumption workloads.

A public [Azure Retail Prices query](https://prices.azure.com/api/retail/prices?%24filter=serviceName%20eq%20%27Azure%20Container%20Apps%27%20and%20armRegionName%20eq%20%27southcentralus%27&currencyCode=USD) returned South Central US Standard active prices USD0.000024/vCPU-second and USD0.000003/GiB-second, effective 2022-06-01 (query time 2026-10-21). The existing template allocates 0.5 vCPU and 1 GiB.

At 31 daily executions taking a conservative full 1,800 seconds each, gross compute is 27,900 vCPU-seconds and 55,800 GiB-seconds: **USD0.837/month before free grants**. At a 120-second light-health duration, gross compute is **USD0.0558/month**. If free grant headroom remains, compute is zero, but that is not assumed. Allow USD0.02/month for small retained challenge/receipt storage and requests (estimate, not measured bill). Adding the gross worst case USD0.857 to the last platform estimate USD14.822133 gives **USD15.679133/month**, below USD20. This excludes model and estate consumption, which have separate monthly lines. When family A is added, its model usage must be costed against USD40/month before enabling that flag. Root must confirm the current platform baseline and actual job size before applying this estimate.

No live read, scheduling change, grant, resource provisioning or credential migration was performed by this helper.

## Owner correction: independent graph job (2026-10-21)

Daily smoke must not remove graph change detection. The owner approved the separate consumption job `job-dia-graph-scan` in the same existing environment, image, managed identity,0.5vCPU/1GiB and1,800-second runtime. Azure readbacks confirm daily `0 6 * * *` and graph `0 */6 * * *`; the shared pair validator refuses either missing schedule. Both now use the tested2230c90 image006c847. No identity or role changed. Graph gross compute at124 full-duration executions is$3.348/month plus$0.05 retained storage; combined platform estimate$19.077133/month, with free grants not assumed. These jobs scale to zero between executions; the estimate is not an invoice. Exact receipts: docs/runs/round-twenty-schedule-pair-image-02.json.
