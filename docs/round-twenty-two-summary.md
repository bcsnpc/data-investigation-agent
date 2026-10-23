## Reliability fixes

2026-10-22 progress (UTC observations extend into October 23; amended prompt
re-read, completed work retained):

- **1a green:** snapshot deadline 180 -> 300 seconds; assertions unchanged.
  Full frozen129556e suite: 5,019 PASS / 48 skip, zero errors/failures,
  683.747s including the snapshot module inside the parallel run.
- **1b pending:** before run job-dia-worker-2zmlavm finished02:58:52-03:45:03UTC,
  2,771s, Azure Succeeded but actual smoke FAIL/NO_COMPARABLE_PATH. Complete
  output preserved at.local/round-twenty-two/smoke-before.log. Old tape diagnosis proves quantity ALLOW
  occurred after the child deadline. Remote evidence publication is deferred
  outside that handshake, without changing the expectation or read-only checks.
  Corrected smoke1/job-dia-worker-fet4jr7 is running. Three consecutive green
  runs have not been earned.
- **1c cause established (owner duration test):** original execution remained
  active through immutable publication at69s; the live probe at70s. Both
  exceeded the60s enclosing limit; the live child exited0 without a deadline
  expiry. Record the outer job limit as cause, correcting the earlier unknown
  conclusion without altering evidence. Changed only the enclosing limit to
  180s, read back with unchanged image/resources/schedule/identity. Confirmation
  job-dia-collectors-ue92850 Succeeded in56s (03:44:57-03:45:53UTC), child exit0
  without deadline expiry; seal3bd5ece6. Its manual allowance stays4; FETCH exhaustion
  remains a probe limitation. The scheduled six-hour collector is the real
  fresh-load test.
- **1d green:** exact two scanner refresh GETs recorded in decisions.md;
  investigator remains Viewer. Existing scanner guard/transport suite28PASS.
- **1d-2 implemented, live confirmation pending:** closed source failure classes,
  metered transient retry, availability facts and blocked output;12 focused
  tests PASS, including failed-load cause/time checks and comparison blocked
  without inventing a numerical cause. **1d-3 implemented, cloud timings pending:**
  normal/test recording, batched audit, staged replies, current-context-only
  catalog materialization;5 focused audit/catalog tests PASS. The new input
  archive is15,330,618bytes versus116MB previously; originals unchanged, stored
  MD5 verified. These added items precede section2. New ledger investigator is
  the default engine; legacy remains baseline only. The old-config smoke
  monitor was stopped before further admissions; its active cloud execution
  was not interrupted.

Opening shared usage: 749/6,000 requests, investigator$1.817798/$40,
enrichment$5.170482/$25; restoration95 untouched. Corrected smoke1 is in flight.
Section 2 has not started; the reliability gate remains red.

Production reliability source1ac73a4 passed5,026 tests /48skip, zero failures or
errors in688.403s. Later6c6b963 changes only a synthetic child's import path
and documentation; all8container shards plus image publication PASS. Deployed
image604867fc to the same three jobs, preserving schedules/resources/identity.
Fresh ec59eef suite passed5,027/48skip, zero errors/failures in662.537s before
the amended availability/mode additions. It is not their full-suite result.

## Agent-state patterns

All nine patterns are implemented; source `d66432a` full suite is green (5,131 tests,48 skipped,zero failures/errors). Image39978613480 all8shards and publicationPASS; live smoke and cloud harness validation are in progress.

| Pattern | Commit | Regression test | Status |
|---|---|---|---|
| Code-owned case | `2ca2462` | `test_round_trip_preserves_every_code_owned_field` | Focused PASS |
| Recitation | `e34efd4` | `test_matching_recitation_is_silent_mismatch_is_logged_and_cannot_advance` | Focused PASS |
| Just-in-time evidence | `a01d935` | `test_explicit_raw_fetch_is_cleared_after_the_next_model_call` | Focused PASS |
| Visible errors and blocked repeats | `6db6a65` | `test_same_failed_signature_is_blocked_different_arguments_are_allowed` | Focused PASS |
| Code-owned tool scope | `4280a7e` | `test_forbidden_tool_never_dispatches_and_code_advance_changes_tools` | Focused PASS |
| Durable checkpoint | `78da28c` | `test_killed_investigation_resumes_completed_steps_and_identical_case_without_re_reads` | Focused PASS |
| Stable prefix | `d002908` | `test_two_tickets_have_identical_prefix_and_scope_references_expand_before_validation` | Focused PASS; live cache measurement pending |
| Optional clean reader | `f1e9f75` | `test_enabled_reader_returns_summary_to_real_parent_loop_without_raw_growth` | Focused PASS; default OFF |
| End-to-end harness | `79a21a1` | `test_fixture_ticket_submits_polls_and_receives_real_engine_case_log` | Focused PASS; cloud harness pending |

Resume2026-10-23: clean working tree and pushed head `ac042944` confirmed. Its predecessor full suite found one platform-literal ratchet failure in the new harness, retained verbatim. Source `d66432a` moves the provider port under adapters without changing the ratchet or its allowance;10 focused tests PASS. Full suite completed5,131 tests/48skip,zero failures/errors in1000.119s. Image workflow39978613480 completed all8shards and publication successfully; digest8db2ba2d. No new live/model request admitted before the full-suite result.


## Scored ticket set

_pending_

## Validation

_pending_

## Budget

_pending_

## Open items

Inherited unresolved application-source access checks and native replay drift
remain. Daily smoke's expected TRANSFORMATION_LOGIC has not yet been earned
three consecutive times; corrected smoke1 is in flight. Audit enclosing
runtime correction confirmed Azure Succeeded. No fresh load fact is claimed
from the four-request manual probe: UNCHANGED_MARKER and retained unavailable
coverage (SQL_READ_FAILED:LockNotAvailable:None). Scheduled six-hour collection
remains the real test.

## Deferred

_pending_


### Status refresh owner steer ? 2026-10-23 (owner instruction 2026-10-22)
Status questions now attempt `refresh_facts` on stale/missing admitted-path facts before answering. A missing collector is a failed route, classified QUERY_ERROR, rather than permission to return a stale status. Refresh permission/network failures retain the source-availability class, observation time and owner; hard guardrail/budget failures still propagate. Fresh ledger facts require no top-up. On-demand force now reaches the underlying incremental collector, so an unchanged run marker cannot prevent renewing stale observations. The cloud status spec will bind only the fixture pipeline's existing metadata route (no audit SQL, no off-path subjects); existing scheduled/manual audit limits remain unchanged.
The first NORMAL status execution job-dia-worker-rgjhvlg took 38s Azure start-to-end, with 1.793382s admission/path and 1.839225s investigation (engine loop 0.360824s, inclusive). This missed the <30s total target. Startup was not separately recorded in that old sidecar; remaining time is not falsely labelled startup. New observational sidecars include UTC worker timing start for comparison with Azure's execution start, separately from investigation and publication. No old capture or receipt changed.
Full corrected-image 5c25dc6 suite: 5,050 PASS / 48 skipped, no errors, 683.078s. New-engine smoke job-dia-worker-hu1s138 finished Azure Succeeded in 288s but smoke FAIL (family-A check); not a passing smoke. Its sealed capture remains unchanged. Three consecutive new-engine smoke passes are not yet earned.


### NORMAL smoke witness transport ? 2026-10-23
The sealed first amended-engine smoke reached the measured 8,765/7,661 boundary and a checked native TRANSFORMATION_LOGIC witness. It then failed at the provider-input admission guard: fetching that witness duplicated 58,675 characters of native assessment/observations into the next model request (configured bound48,000). The bound was not raised. The model view now supplies the checked mechanism, classification, support and evidence IDs, excluding duplicated native observations and rendered outputs. Original full witness/tape bytes remain unchanged in evidence storage and consumer validation still uses them. Retained real witness projects to3,587 characters. Regression proves the input witness is untouched and the model receives the proof classification/references. This is a reliability transport repair; the section2 pattern programme has not been declared complete.

Status refresh negative-history regression (2026-10-23): a successfully refreshed, complete empty run history is not a failed query or an outage. It remains an honest no-record answer; the refresh failure classifier is used only when collection fails or yields no usable status/history observation. Existing fresh complete negative history needs no repeated top-up.


### Status steer live result ? owner 2026-10-23
`job-dia-worker-hm27jiu` (source7d9653f, tested imagee93a69cb) Succeeded at05:12:27UTC. Stale facts were refreshed only for pipeline3bf74ae1? through two metadata GETs; zero model calls and zero quantity probes. The fresh latest run37b546ca? is SUCCEEDED, so the explicit status question is answered without inventing a failed-job incident or numeric cause. Seal9b0a87c0? and full timing receipt: docs/runs/round-twenty-two-status-refresh.json.
Startup to capture clock27.485616s; investigation10.773940s; capture publication4.102764s (inclusive, overlaps); Azure total52s. Remaining setup/publication/shutdown13.740444s is not relabelled startup. Owner now accepts <60s total for job-based status runs this round: PASS. Original <30s result remains recorded, superseded only as the acceptance target. No startup optimization is planned this round. Full-investigation target remains <120s.
The fba799a full suite passed5,054 tests /48 skipped in807.412s. Final-source full validation and the three-smoke sequence continue. Operator budget reporting stalled before admitting a smoke; its read-only process was stopped with no reservation issued. A direct read-only control-plane snapshot completed and reports880/6000 physical (INV466/SCAN414/REST0), modelUSD2.128512/40, no new reserved model rows, reserve95 intact. Runtime admission, locking and lease guards were not changed.


### Section1 checkpoint and soft-gate continuation ? 2026-10-23
Full sourceaa409a7: **5,056 PASS /48 skipped**, zero failures/errors,734.374s. Tested source7d9653f imagee93a69cb has all8 offline shards and publicationPASS. All three jobs read back unchanged schedules/identity/resources; worker3600s, graph1800s, collectors180s (the separately recorded60?180 decision).
Corrected-image smoke sequence: h3xzssv PASS280s (05:18:14?05:22:54UTC), wfdgnq0 PASS277s (05:24:18?05:28:55), ibc6h0s FAIL290s (05:29:52?05:34:42). First two retain as-designed verdict and native TRANSFORMATION_LOGIC at8765/7661; third fails provider-input admission, not an estate or model-provider authorization failure. Every original seal remains unchanged. **Three consecutive greens are not earned.**
Under the amended prompt's explicit three-fix soft gate, continue section2 with the gate OPEN: deferred handshake publication, NORMAL batching/path materialization, and compact design-witness transport were three distinct fixes; the request still grows beyond48000 characters after extra definitions and repeated evidence fetches. The exact failed get_evidence signature, seals, results, readbacks and budget are in docs/runs/round-twenty-two-section-one.json. No threshold or expectation is loosened. The code-owned state/JIT/repeat/prefix work directly addresses this remaining blocker; rerun after that work.
Budget at05:35:41UTC: **1003/6000 physical** (INV466/SCAN537/REST0), reserve95 untouched, model**USD2.967361/40**;68 settled and2historical uncertain reservations, no new open reservations. Enrichment remainsUSD5.170482/25. No new identity, grant or secret. Status52s passes the owner's amended<60s job target; standalone full-investigation<120s remains to be established (smoke investigator phase106.36s is not standalone end-to-end timing).

Pattern2a implemented: versioned code-owned case, validated model notes, retained snapshots and final outcome. Module2tests, investigator39tests, image-staging5tests PASS offline. No new live/model call. Pattern2f resume remains pending.


### First three state patterns ? 2026-10-23
2a code-owned case and validated annotations;2b model recitation compared to code state (including definition judgment calls);2c summary-only ordinary context with one-call raw retrieval and hash-bound paging for large evidence. Each pattern has a separate commit, tests and architecture entry. Focused case3, investigator42, ports14 and cloud assembly12 tests PASS; image-staging5PASS. No live/model call during these edits. The section1 smoke blocker stays OPEN until final-pattern validation; no request bound or acceptance expectation changed.


### State patterns2d?2f ? 2026-10-23
Failed exact calls are blocked from retained case errors; tool sets follow code-owned phases; shared checkpoints resume completed logical steps with original evidence/probes and ledger-backed read accounting. The real child-process kill/restart test passes, with identical preserved case state and no completed native rereads. Changed binding/hash and concurrent revision tests refuse reuse. Case3, playbook1, checkpoint3, investigator43, native ports15, source-availability17 and cloud assembly12 focused tests PASS offline. No live read or model call during pattern work. Interrupted-operation charges remain on the shared ledger; no scope, secret or allowance changed. Final full/image/smoke validation remains pending after all nine patterns.


### Final three state patterns ? 2026-10-23
2g stable per-phase system/tool prefixes keep IDs/context/key in dynamic payload and validate expanded references against the original consumer;2h optional clean-context heavy reader stays OFF unless trusted step configuration enables it, returns only an untrusted reading note with checked references;2i submit/poll/outcome harness uses the real dia CLI and verifies the seal/result. All have separate commits and tests/architecture entries. Focused ports17, reader3, harness4, checkpoint3, core43 and staging5 PASS offline. No new live or model call during these edits; last observed physical1003/6000, modelUSD2.967361/40, reserve95 intact. Full/image/harness/smoke validation and a new-prefix live cache measurement remain pending2j. The retained pre-pattern cache baseline is65.36% cached input tokens, explicitly not a new-pattern measurement. Three-consecutive smoke gate remains OPEN after PASS/PASS/FAIL and the documented soft-gate continuation.

### Section2 gate earned, 2026-10-23
Source `d66432a`: full5,131 tests/48skip,zero failures/errors; image workflow39978613480 all8shards and publicationPASS. Tested digest8db2ba2d deployed to all3 jobs with unchanged schedules/resources/identities/timeouts. Smoke `job-dia-worker-wnj7nkc` PASS all6checks, Azure Succeeded,15:49:43?15:55:52UTC(369s), native TRANSFORMATION_LOGIC atSilver7661/Gold8765; new engine verdict as designed. Original seals retained; NORMAL mode has no byte-exact replay claim. This earns2j's daily-smoke gate; it does not earn three consecutive greens.
Actual new-prefix provider usage:7552/60610 cached input tokens(12.46%),4/8call hits,0unknown; lower than retained pre-pattern65.36% baseline, not presented as a speed improvement. Investigation phase180.91s; standalone job timing remains to be measured through the user harness. Root model_calls8 versus embedded cost.model_calls7 is a retained accounting-display discrepancy to inspect during development; shared ledger settled all8.
Shared budget after:1176/6000physical(INV466/SCAN710/REST0), modelUSD3.424084/40,80settled/2historicaluncertain, reserve95untouched. EnrichmentUSD5.170482/25 unchanged. Public receipt: docs/runs/round-twenty-two-patterns-validation.json. ContinueSection3; no scored ticket or injection yet.
