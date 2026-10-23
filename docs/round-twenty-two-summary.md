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
- **1c cause established (owner duration test):** original execution remained
  active through immutable publication at69s; the live probe at70s. Both
  exceeded the60s enclosing limit; the live child exited0 without a deadline
  expiry. Record the outer job limit as cause, correcting the earlier unknown
  conclusion without altering evidence. Changed only the enclosing limit to
  180s, read back with unchanged image/resources/schedule/identity. One audit
  confirmation is in flight. Its manual allowance stays4; FETCH exhaustion
  remains a probe limitation. The scheduled six-hour collector is the real
  fresh-load test.
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
three consecutive times; the before run remains in flight. Audit enclosing
runtime correction awaits one Azure-success confirmation. No fresh load fact
is claimed from the four-request manual probe.

## Deferred

_pending_
