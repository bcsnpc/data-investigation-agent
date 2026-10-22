# Independent daily smoke and six-hour graph schedules

Owner direction, 2026-10-21: retain the daily 06:00 UTC smoke job and provision a
second Container Apps job, `job-dia-graph-scan`, for the existing six-hour graph
change detection. This is approved resource provisioning under §8, with no new
identity, role, estate permission or secret. This document records the prepared
implementation; a plan is not a deployed schedule.

The new job inherits the existing managed identity, Container Apps environment,
region, pinned worker image, 0.5 vCPU / 1 GiB size, and 1,800-second runtime.
Parallelism and completion count are one, native retry limit zero. Its cron is
`0 */6 * * *`; the existing worker's daily cron remains `0 6 * * *`.

`runner_graph_schedule.plan` reads the graph configuration and gateway from the
retained `job-before.json`, preserves their scopes and moves them into a typed
`dia run graph` scan check. Only the already approved per-execution capture grant
is added to that gateway. Each run receives a distinct capture ID. The retired
`graph_scan_bootstrap.py` launcher and its two inline graph environment payloads
are absent from the new container command/environment.

Worst gross 31-day estimate, without free grants: 124 graph executions × 1,800
seconds × 0.5 vCPU = 111,600 vCPU-seconds; memory = 223,200 GiB-seconds. At the
provided estimate this adds $3.348 compute and $0.05 storage/control allowance.
Existing platform $14.822133 + daily $0.857 + graph $3.348 + allowance $0.05 =
**$19.077133/month**, below the $20 cap. This assumes each graph execution remains
within its 1,800-second runtime; it is an estimate, not a bill. Model or estate
requests use the separate monthly scan line, not the investigation line.

After updating the runner estate's image to the current immutable image, the
prepared command for the root operator is:

```powershell
& .local/llm-env/Scripts/python.exe scripts/graph_job_schedule.py --existing-job .local/round-twenty/job-before.json --runner-estate .local/round-twenty/runner-smoke-template.json --output .local/round-twenty/independent-graph-job-applied.json --apply
```

The command uses the existing `deployment.cli` array. It performs exactly one
PUT on the approved new job ID, then reads both jobs. Async creation polls with
bounded waits without repeating PUT. It does not mutate the daily job, create an
environment, assign a role or start an investigation. Apply records both full
control-plane readbacks and validates the pair before returning APPLIED. Failed
or pending provisioning cannot be reported as success.

`validate_pair(daily, graph, image=...)` is the shared preflight/readback contract.
It refuses either missing schedule, a manual trigger, wrong cron, failed
provisioning, mismatched image/environment/identity/resources, or retired/untyped
launcher. A single cron on one job cannot satisfy it. Tests exercise missing
daily and missing graph schedules independently, unchanged inherited scope,
unique captures, failed provisioning and one-PUT async polling. The root
integration must invoke this pair check with fresh readbacks during admission
and record the actual provisioning result; no live call was made by this helper.
