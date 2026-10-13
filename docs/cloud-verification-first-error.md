# Verification replay preserves its first error

The original cloud verification completed live but its offline replay failed.
Its original capture and failed result remain unchanged. A replay-time TapeError
is now re-raised as the same exception immediately after the captured program
fails. Before re-raising, the replay writes a private `*-recomputed-final.json`
diagnostic with `matched: false` and `exact_final_compared: false`, retaining the
original error type, message and event index. It does not claim a recomputed final.

Snapshotting, accounting finalization and `tape.finish` are not attempted after an
event-stream mismatch: they could only mask the original cause with a later error.
Failure to persist the diagnostic also cannot replace the original exception.
Live capture's existing failure-recording contract is unchanged. This alters only
the standalone capture/replay script, not engine fingerprint inputs, sealed bytes,
approval pins or event comparison. The separate shared-budget replay correction
changes engine code and therefore requires fresh preparation and verification;
this diagnostic correction does not authorize reusing the old approval.

Tests: an original CLOCK/BUDGET error escapes by object identity, appears in the
private diagnostic and never calls snapshot/finalize/finish; ordinary live failure
capture retains its prior schema. Existing success/failure exact-capture tests pass.
