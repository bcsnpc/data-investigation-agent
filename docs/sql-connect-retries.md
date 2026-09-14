# SQL auto-resume connection retries

Issue #57 diagnoses recurring 40613 failures. Azure activity logs showed the
database resuming at the same time as failed investigations. The unchanged
restricted SQL query succeeded after resume (100,000 orders, USD 64,892,824.49).
The original worker made one connection attempt and moved on during wake-up.
Microsoft describes this behavior in the
[serverless FAQ](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-faq?view=azuresql).

The SQL worker now makes at most three attempts, waiting 10 then 20 seconds,
only when the fixed SQL helper reports `SQL_READ_FAILED`, stage `connect`,
SQL error 40613. Each attempt starts a fresh PowerShell process/SQL connection.
Queries cannot have executed when this connection-stage failure is reported.
Query failures, authentication/firewall errors, malformed responses and unknown
timeouts are not retried. Fabric SQL and semantic calls are unchanged.

Each helper invocation retains its 150-second process timeout (30-second
connection timeout and 90-second query timeout). The three-attempt theoretical
bound is 480 seconds plus small process overhead; the outer SQL worker timeout
is 510 seconds. Most 40613 errors return earlier. This fits the 30-minute ticket
lease alongside the other bounded layer calls. A hard outer timeout still
reports unavailable; it may lose in-progress attempt details.

`connection_attempts` on saved SQL observations records attempt numbers,
start/end timestamps, success/failure, SQL error number, stage and retry delay.
Raw errors and credentials are not logged. Recovery yields the actual query
result; exhaustion retains UNAVAILABLE. Snapshot comparability and classification
gates remain unchanged. Completed historical tickets are not auto-requeued.

Five deterministic tests cover recovery, exhaustion, immediate success,
non-retryable errors and malformed/timeout responses, including persistence of
attempt details in metric observations. Existing cross-layer and generator tests
also run. Mocked recovery does not claim a live cold-start reproduction.

Database auto-pause and free-offer/overage settings are unchanged. This fix
handles connection warm-up; it cannot recover a database paused because its
monthly free allowance is exhausted or another sustained outage.

Live verification: run `5a161256-05a0-4f81-9fdb-ab3c238284b4` read all five
layers successfully, each returning 100,000 orders and USD 64,892,824.49. SQL was
already online and succeeded on its first attempt; that history was verified in
the saved observation. Classification remains UNRESOLVED and live snapshot
comparability is not promoted by connection recovery. No forced database pause
or business write was performed. Five retry tests, twelve cross-layer tests and
two generator tests passed.

User constraint: SQL must stay on the free allowance. Reverified useFreeLimit=true and freeLimitExhaustionBehavior=AutoPause. No change to paid overage or free-limit settings is authorized. If the allowance is exhausted, preserve unavailability and wait for renewal; do not change billing settings to make retries succeed.
