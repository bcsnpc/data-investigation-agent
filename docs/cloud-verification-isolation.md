# Isolated cloud verification admission

Owner amendment, 2026-10-13: one additional cloud attempt is authorized only
after runtime, isolation and offline admission conditions pass, with unchanged
model, estate, verification and restoration caps. The earlier two failed
attempts remain unchanged. This supersedes the earlier no-third-attempt stopping
decision, not its recorded failures. The fixture4 pending reservation was
subsequently settled UNCERTAIN by the owner controller at 18:01:59 UTC, with its
charge preserved in `.local/round-nineteen-b/fixture4-interrupted-reservation.json`.

## Enforcement boundary

`SharedState.transaction` checks an expiring writer lease in the existing
`state_documents` table before waiting for the application advisory lock, then
rechecks after acquiring it using READ COMMITTED. Another worker refuses before
acquisition; a worker that was waiting when a lease appeared refuses afterward.
PostgreSQL lock waits are bounded at five seconds, statements at thirty seconds,
and idle transactions at thirty seconds. Errors roll back and close connections.
These changes create no schema, permission, identity or secret.

The worker ID and an explicit lease ID are inherited through the child process
environment. A child with the same pair is allowed; a different or missing pair
is refused. The lease ID is a process-coordination label, **not a database
credential or security boundary**. Anyone already able to issue raw administrative
SQL can bypass this cooperative guard. Old images also lack it. All old workers
must be drained, the sole scheduled job switched to Manual for the window, and
the owner must refrain from raw writes. Read-only owner queries that do not take
the application advisory lock remain possible.

Expiry refuses further normal transactions by the admitted worker; it never
silently runs without isolation. The owner controller releases the exact lease
after terminal status. The supplied `isolated(...)` context manager also releases
on exceptions for operator-managed operations, preserving the original exception
if cleanup itself fails. A hard kill may leave the lease ACTIVE until expiry;
the controller must record and release it. Charges are never reset or released
by lease handling.

## Operator sequence and exact inputs

No live action is performed by these helpers. Before the authorized attempt:

1. Drain all executions and pause the old schedule. Retain control-plane GETs
   proving terminal execution statuses and `triggerType: Manual`.
2. Confirm no holder of application advisory lock `183746812` in PostgreSQL.
3. Read the existing job after its owner-approved runtime change. Its
   `properties.configuration.replicaTimeout` must be at least 1,800 seconds
   and equal the stage's `required_runtime_seconds`.
4. Install the lease using the existing owner control path and new code:

```python
from investigator.shared_writer_lease import acquire, release
lease = acquire(state, owner=worker_id, lease_id=unique_attempt_label,
                expires_at=unix_expiry, approval=dated_owner_decision)
# Retain lease and the transaction result; expiry must cover the full runtime
# plus launch delay, and cannot exceed one hour from acquisition.
```

5. Add to the stage config:

```json
{
  "required_runtime_seconds": 1800,
  "finalization_reserve_seconds": 600,
  "run_admitted_at": 0,
  "overall_run_deadline": 0,
  "deadline": 0,
  "exclusive_writer": {"owner": "same-worker-id", "lease_id": "unique-attempt-label", "expires_at": 0}
}
```

The zeroes are placeholders, never admissible values. Supply actual finite Unix
timestamps from one admission epoch: `overall_run_deadline = run_admitted_at +
1800` and the inner `deadline <= run_admitted_at + 1200`. The total configured
run duration must equal the observed job runtime; an integer runtime label alone
is insufficient. Admission cannot be older than five minutes. Leave
at least 600 seconds for capture packaging and upload: work admission is capped
at the earlier of 1,200 seconds or job runtime minus that reserve. The stage
checks before readiness and demo. The same inner deadline is inherited by
child workers, and PostgreSQL application-state admission refuses after it,
before any new budget reservation. Existing in-flight bounded calls can finish
after the admission cutoff. This is not a hard kill of arbitrary Python work
and does not predict packaging duration; it preserves headroom rather than
guaranteeing the final ZIP arrives.

6. Pass two fresh observations to `cloud_stage_environment.build` or its CLI:

```python
job_observation = {"observed_at": unix_observed_at, "job": unmodified_job_get}
isolation_observation = {
    "observed_at": unix_observed_at,
    "executions": execution_get_records,  # all Succeeded, Failed or Stopped
    "scheduled_job": unmodified_paused_job_get,
    "advisory_lock_holders": 0,           # measured, not assumed
    "lease": lease                       # exact installed body, status ACTIVE
}
```

Observations older than five minutes refuse. The builder refuses active/unknown
execution states, an unpaused schedule, lock holders, a mismatching lease, or a
lease too short for the full runtime. It includes hashes of the observations
in `DIA_CLOUD_JOB_ADMISSION` and passes `INVESTIGATOR_EXCLUSIVE_LEASE_ID` to
the worker, along with `INVESTIGATOR_CLOUD_WORK_DEADLINE`. CLI flags are
`--job-observation` and `--isolation-observation`.
The worker calls `require(...)` against actual PostgreSQL before publication or
any estate read. Each subsequent application-state transaction rechecks expiry
and ownership. The controller retains terminal status, then calls
`release(state, lease)` and reads back RELEASED. Restore the existing schedule
only after the isolation window has ended, with before/after receipts.

The guard does not preserve a partial tape across a hard container kill. That
known retention gap remains; no complete verification or replay is claimed from
settled ledger entries alone.
