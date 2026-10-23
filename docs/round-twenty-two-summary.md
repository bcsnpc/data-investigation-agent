## Reliability fixes

2026-10-22 progress (UTC observations extend into October 23):

- **1a green:** snapshot deadline 180 -> 300 seconds; assertions unchanged.
  Full frozen129556e suite: 5,019 PASS / 48 skip, zero errors/failures,
  683.747s including the snapshot module inside the parallel run.
- **1b pending:** current smoke admitted as job-dia-worker-2zmlavm; its complete
  original output will be preserved. Old tape diagnosis proves quantity ALLOW
  occurred after the child deadline. Remote evidence publication is deferred
  outside that handshake, without changing the expectation or read-only checks.
  Three consecutive green runs have not been earned.
- **1c instrumentation green:** original logs/replica/exit evidence cannot
  establish the audit EOF cause. New live capture has start, two heartbeats,
  actual exit0 and last_action=sql_quantity. Original cause stays unknown.
  The enclosing60-second Azure job was Failed and the manual fetch allowance
  was exhausted; these remain open, not a successful fresh-load observation.
- **1d green:** exact two scanner refresh GETs recorded in decisions.md;
  investigator remains Viewer. Existing scanner guard/transport suite28PASS.

Opening shared usage: 749/6,000 requests, investigator$1.817798/$40,
enrichment$5.170482/$25; restoration95 untouched. Current smoke is in flight.
Section 2 has not started; the reliability gate remains red.

Production reliability source1ac73a4 passed5,026 tests /48skip, zero failures or
errors in688.403s. Later6c6b963 changes only a synthetic child's import path
and documentation; all8container shards plus image publication PASS. Deployed
image604867fc to the same three jobs, preserving schedules/resources/identity.

## Agent-state patterns

_pending_

## Scored ticket set

_pending_

## Validation

_pending_

## Budget

_pending_

## Open items

Inherited unresolved application-source access checks and native replay drift
remain. Daily smoke's expected TRANSFORMATION_LOGIC has not yet been earned
three consecutive times; the before run remains in flight. Audit logging
diagnoses the next occurrence but does not establish the original EOF cause.
The audit logging probe exposed a separate enclosing-job status/runtime issue
and a manual fetch allowance mistake, both retained above.

## Deferred

_pending_
