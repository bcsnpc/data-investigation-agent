# Collector schedule preparation

The owner-approved new job is `job-dia-collectors`, in the existing Container
Apps environment and using its existing worker managed identity and pinned
image. `collector_schedule.plan(existing_worker, runner)` produces a PUT body;
it performs no Azure call. Root deployment must read the resulting job back and
apply `collector_schedule.preflight`, and must separately confirm the existing
daily `0 6 * * *` and graph `0 */6 * * *` jobs remain unchanged. No role or
database grant is part of this plan.

The collector cron is `*/30 * * * *`. Its approved maximum is 0.25 vCPU, 0.5 GiB,
60 seconds, one replica, zero retries. In 31 days this is 1,488 executions,
22,320 vCPU-seconds and 44,640 GiB-seconds. With no free allowance assumed, using
the previously recorded consumption rates ($0.000024/vCPU-second and
$0.000003/GiB-second), compute is at most $0.6696/month. Adding $0.02 storage to
the prior $19.077133 platform estimate gives **$19.766733/month**. This is a
bound from configured runtime, not a measured invoice or a guaranteed API
completion time. Deploying longer runtime or larger resources requires a new
combined estimate. Storage growth needs watching.

The typed route is `facts-dispatcher`, options `{configs: [fixture, billing,
sample]}`. It calls `cloud_facts_dispatcher.execute`. Each wake chooses **one**
estate by a durable shared PostgreSQL cursor, then the existing collector chooses
at most two graph subjects for that estate. No more than eight physical requests
are admitted for that wake, all through the shared monthly SCAN account. Every
subject's listing interval remains at least six hours. Thirty-minute wakes do
not imply all facts are thirty minutes fresh. The graph/facts tools continue to
report observed time, as-of cutoff, stale fields and unavailable coverage.

Cursor advance happens after collection. An exception leaves it unchanged;
neither a failed collection nor an exhausted SCAN allowance becomes a false
success. A failed estate may delay later estates until the cause is resolved.
The job parallelism is one; the plan does not claim exclusion against an owner
manually launching another collector. The shared monthly budget remains the
authority under concurrent attempts.

Runtime SQL profile observations keep both the query-bound receipt and the
hash-verified retained schema metadata reference. The consumer field is named
`key_columns`, but it means checksum columns here: no uniqueness is asserted.
The additive SHA-256-prefix checksum is expressly labelled NOT_EQUALITY_PROOF;
the count/checksum observations cannot promote a lineage link to verified.

This helper prepared code and configurations only: **zero deployments, new
grants, estate reads and model calls**.

Applied and readback2026-10-22: job-dia-collectors exists with exact plannedcron/resources/runtime/managedidentity. UTC-labelledtimestamp normalization fixed the two preserved firstwake failures; laterwakes sealed andstored boundedfacts. Live coverage is partial: fixture/billing jobhistory, selected schedules/durations observed; all3estates refreshhistory403UNAVAILABLE; fixtureaudit/load SQLRuntimeErrorUNAVAILABLE. Counts of rows are not proof of availability. See runs/round-twenty-one-collector-live-coverage.json for separate OBSERVED/UNAVAILABLE counts. No refresh/job was triggered, no guessedrowcount or SQLmodifiedtime substituted.
