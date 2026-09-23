# Retrieval and test allowances

2026-09-23. Ordered reliability item 6; issue #199.

New dynamic sessions partition the existing planner-call allowance. Two turns (or
all turns when the configured total is smaller) are reserved for test proposals.
LOOKUP has a separate cap of total minus that reserve. Remaining retrieval also
accounts for already-spent calls, including malformed/provider-failed attempts,
so those attempts cannot silently spend the reserve through more retrieval.
A test proposal consumes a planning opportunity even when later rejected; spent
provider calls are never refunded. SQL/cloud, cumulative input/output, deadline,
permission and daily usage limits are unchanged.

The exact allowance is visible in each new session and planner payload. LOOKUP
is removed from the provider action schema when exhausted and independently
rejected by local validation, with RETRIEVAL_BUDGET_REJECTED recorded. Typed and
proposed tests remain subject to their normal admission. Automatic approved-schema
prefetch still requires no extra planner turn and is counted separately. New
sessions record action_budget_version=1; historical sessions are not relabelled
as having enforced the new partition.

Every adaptive session now exposes reads_per_run, retrieval_calls, test_calls and
retrieval_test_ratio. Scoring and newly appended ledger rows expose reads_per_run;
the ledger's existing retrieval/test counters retain their definitions. Retrieval
counts planner LOOKUP decisions, including unavailable/repeated lookups; tests
count RUN/QUERY proposals, including local query rejections. Successful read count
is separate from those attempts. Partial result counts remain separately visible.

## Offline validation and limits

Five focused tests passed (7.940 seconds). A recorded mock-provider pressure case
makes four different context requests, then one native and one source read under
its original six planner calls. Source schema prefetch is local. Full session
replay MATCHED with zero network calls and zero uncached tool execution. The run
ends BUDGET_LIMIT after two reads; it is an allocation check, not a business answer.
The provider fixture follows advertised capabilities, so this does not establish
that a live model will choose a useful test. It does establish that retrieval
cannot dispatch using the protected planning turns.

An out-of-budget injected provider still proposes LOOKUP twice: both are refused
without metadata dispatch and recorded separately; both paid planner attempts stay
charged. Explicit missing-date clarification and an expired deadline still stop
without data reads. The acceptance wording about zero-read stops applies to
retrieval starvation, not a requirement to bypass safety or invent executable
scope. Provider failures, unsupported queries, permission holds, insufficient total
tokens/time and material ambiguity can still yield zero successful reads. These
remain failures/holds where appropriate, not fabricated successes.

Earlier four-test checks passed in 7.118 seconds, nine planner-view goldens in
4.095 seconds, and five session replay checks in 14.303 seconds. No historical
tape or F-paced result was modified; F-paced remains FAILED. Full regression and
CI are pending. All recordings in these tests use mock transport, not a live
investigation. Payload shaping changes invalidate prior exact-request tapes and
v4 remains invalidated. No live tape/run, freeze or new variant until items 5-8
are merged. Intake regressions follow in their own PR.

A retained zero-network proof is saved under
`.local/action-budget-proof-8e591f22-68a4-4111-9a8a-ee8a9753ed4b/` with the disposable
catalog, exact mock HTTP recordings and MATCHED replay result. Its one-test capture
passed in 9.312 seconds. Its separate ledger row contains actual trajectory counts
(four retrieval proposals, two test proposals, two reads, ratio 2, one schema
prefetch); validation-suite rows do not aggregate internal fixture trajectories.

Final local validation: **999 regression tests passed in 236.111 seconds**. CI and
merge follow on the item-6 PR. Engine bytes and planner payloads changed; previous
frozen grading and exact-request tapes cannot be reused as current acceptance.

The clarification fixture now explicitly requests an unspecified reporting period,
so the missing-date question has a concrete ticket basis. All five focused tests
passed again in 5.853 seconds; engine code did not change after the full suite.
[PR #214](https://github.com/bcsnpc/data-investigation-agent/pull/214) tracks final CI
and merge. Secret scanning and 183 local documentation links passed.

## Baseline review decision (2026-09-23)

Keep the reserve based on proposed test turns, including locally rejected proposals.
This deliberately protects opportunities to test rather than guaranteeing admitted
reads. Counting only admitted proposals would let repeated invalid proposals retain
protected turns until a separate no-progress limit intervenes. Every proposal still
spends a planner call; successful reads and rejection counts are reported separately.
A zero-read run remains visible as a failure or hold, never an allocation success.
