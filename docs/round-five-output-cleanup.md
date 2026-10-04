# Round Five output cleanup

## Round Five output cleanup and baseline regressions

Source-consistency business composition now recognizes its existing same-moment
caveat and does not append another timing sentence. A single expected-record
presence/absence shared by all checked layers becomes one sentence listing the
declared business role names. Mixed presence remains a separate per-layer account;
quantity, evidence contracts and outcome gates are unchanged.

The three named baseline failures were stale tests, not reasons to weaken the
consumer: test_evidence_prose expected pre-role wording; test_refresh_comparison
omitted the required boundary citation and supplied the forbidden path account as
the model mechanism; test_retained_job_history bypassed the constructor without
initializing its required cache. The fixtures now satisfy the current contracts
and retain their original value, missing-timestamp and failed-job assertions.
These files and narrative composition are explicitly added to CI. 46 focused
tests pass (10 narrative, 11 record-presence, 6 prose, 15 refresh, 4 job-history).
The original broad failed run remains in private part-a-tests.txt. Its platform
literal failure was already corrected before #380 merged; the ratchet now passes.
Its separate distinct-read failure is preserved and not declared resolved by a
standalone pass. The subsequent combined suite passed all 1,795 tests, including
that distinct-read test. Its earlier cause remains unestablished; the original
failure is preserved. The full private log also contains ResourceWarnings, so
this is a test pass, not a claim that the process emitted no warnings.

This output change does not revise any historical narrative or ledger row. No
live replacement run or additional credit. Engine bytes changed; prior freezes
remain invalid. Round Five's original acceptance expectations remain unchanged.
