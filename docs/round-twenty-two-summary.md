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

Standalone user harness validation2026-10-23: `job-dia-worker-wvq9ret` AzureSucceeded16:00:15?16:07:44UTC(449s), client472.20s, seal a4cd6ef7?. Exact ticket echo and capture seal PASS. Engine result not found/TICKET_BUDGET_REACHED after18modelcalls/1native read; only the visual was read. A proposed refresh-stale verdict was correctly rejected for missing divergent equivalent-context reads; subsequent evidence fetches did not measure pending boundaries. No established cause or successful fixture investigation is claimed. Full retained outputs: docs/runs/round-twenty-two-user-harness.json. This is unscored validation, not a Section3 dev or held-out record. The <120s standalone target is missed. No injection has been applied.

Owner frontier steer2026-10-23 implemented before any scored dev run: v2 case retains successful exact results, duplicates return the saved result plus evidence-ID feedback and a blocked event. Rejected verdicts and3exploratory model steps without quantity/proof progress transfer control to the first unmeasured boundary, then unchecked hypotheses. The deterministic continuation retains a one-tool phase record, preserves exact scope/key, and reuses the unchanged native/evidence validators. No-progress phases advance; exhaustion reports not found and furthest measured point.133focused tests PASS, including5new frontier regressions. Image build and one replacement A harness validation pending; original18-call result preserved. Section3 set is not yet sealed or run;12old-ticket fairness tasks prepared, no injection applied.

Section3 preparation: scoring contract committed separately before set admission;40dev and20+held-out, strict verdict/layer/cause scoring and independent grading, with per-batch physical allowance40per ticket under the unchanged6000monthly ceiling. Twelve original Round17 fairness inputs are prepared using visible labels only; provider calls not yet admitted. Original question files are unchanged. Routine platform input archive1a3066c2? uploaded without overwrite and stored-MD5 verified; secret references only. No controlled injection applied and no scored set sealed yet.

Owner frontier confirmation2026-10-23: exactly one A rerun, `job-dia-worker-6u1avrg`, source8611703/tested image9ecb3fec, AzureSucceeded16:30:31?16:35:09UTC(278s), client318.87s. **As designed**, native **TRANSFORMATION_LOGIC**, evidence-proven code frontier. **4provider calls versus18before**; original not-found capture remains unchanged. Seal f744a1b9?. The correct finding is earned; the<120s full-investigation target is still missed. This is unscored validation, not a dev or held-out ticket. Full outputs, measured values, case errors/blocks and exact budget delta: docs/runs/round-twenty-two-frontier-family-a.json. Continue Section3; no scored run or injection yet.


Frontier source8611703 full regression:5,143 tests/48skip,zero failures/errors,1116.59s; all4local shards exit0. Independent fairness batch completed12/12 schema-valid judgments atUSD0.041762 enrichment,0estate reads. Several judgments confuse the ability to investigate with answering from labels alone; originals retained and independent criteria clarification pending. No exclusions adopted or scored tickets admitted.


Section3 control checkpoint2026-10-23: three real failed-job controls acrossfixture/billing now collector-confirmed with matchingrunIDs/error2011. Original pipeline definitions restored and servedhashes match; no originaldata activity ran or history was removed. Readercollectors used2fixture+4billing SCAN requests, within unchangedmanual4perjob. Two local reporting stalls preserved; secondstack establishes SharedUsage.mirror wait before nextAPI dispatch, notFabric latency. One originalphysical reservation stays conservativelycharged RESERVED. Bothfairnessreviews preserved; all12oldquestions remaininset dueunsupported/inconsistentexclusions, notrewritten. EnrichmentUSD5.259538/25 before ticketwriter. Otherverdictcontrols/setseal/scoringstillpending. Receipt docs/runs/round-twenty-two-failure-controls.json.

Independent writer firstbatch completed3tasks/6unchanged ticketdrafts,USD0.006052enrichment. Fullset is not sealed/scored; drafts in tests/tickets/independent-drafts-real-failures.json. As-of17:37UTC physical1262/6000(INV538/SCAN724/REST0),investigatorUSD4.080700/40;95reserveuntouched. EnrichmentafterwriterUSD5.265590/25. PlatformactualobservationUSD0.646485at17:35UTC,CostManagement429twice thenbackoffsuccess; oldlaunchconfigsnotretimestamped. No next-class fault is applied.

Raw operational entry wiring, offline before scoreddev: exact graph-name admission preserves original ticket and source span; optional run_selector is inside the FACTrequest and selects a unique retained historical run at stated precision, never latest fallback. Native timestamps retain seventh-ninth digits; missing/finer/ambiguous references refuse or ask one combined essentials question. Both outputs state selection precision. Raw calculation admission explicitly remains unsupported; no default visual or expected target fills it. Selector8/intake7/cloudassembly13/factproducer23/core45/frontier5 targeted tests passed. Newfull/image pending. Independently derived fixture7661->8765 andbilling700->950 arithmetic committed separately from current value verification. Sample196-byte DueDate definition hash8b542b83 verified through approvedCAS restoration. Six more baseline wordings are being independently authored. README legacy encoding prevented UTF8 decoding; checkpoint appended asASCII without transcoding existing bytes.


Owner frontier completion, 2026-10-23: one A validation reached as designed/native TRANSFORMATION_LOGIC with 4 provider calls versus 18; original preserved. Six frontier tests plus core/cloud tests pass (64 total), including short evidence-only feedback on successful raw retrieval repeats. Pre-score source9c770d3 full5168/48skip/zero failures and all8 image shards pass; final feedback change separately focused-tested. Full evidence and limits: docs/round-twenty-two-frontier-confirmation.md. No scored dev run yet. Prior freeze invalid.


Section3 continuation2026-10-23: six independently written baseline drafts preserved unchanged as DEV only; three provider messages,USD0.006628,zero estate reads. Full set/held-out sealing and scoring still pending. Owner approved and verified one existing SQL laptop /32 firewall replacement, no other scope change; original40613/40615 controls preserved.


Source before-state completed2026-10-23T19:09:44UTC: existing owner control read360syntheticrows,7,661units, complete row/schema preimage retained. One INV physical request,zero diagnostic/model calls or source mutations. Firewall replacement readback verified. A later40613 occurred during serverless resumption; after Azure reported Online, the bounded retry completed in8.47s. Two earlier report-preflight connection failures dispatched no SQL and remain preserved. Source receipt docs/runs/round-twenty-two-source-baseline.json; pre-writer40/20allocation in docs/round-twenty-two-set-construction.md. Not a scored result.


Source readiness update2026-10-23: corrected guard/source-resume image19bd668 passes all8hostedshards/publication. Sourceprofile03 retried40613 at30s, passed both permission guards, then exposedSQL529 for generic timestamp-to-text profile conversion. Complete schema-driven binary-hex correction57focusedtestsPASS; no data or permission changes. NativeSourceProfile has not yet produced values. All3Wait-only pilot jobs completed and originaldefinitions restored/hashconfirmed after localPGIdleInTransactionSessionTimeout; publisherobservations only, no readerRUNNING facts earned. All failures retained; source-profile-attempts and wait-pilot-recovery receipts in docs/runs. Set sealing/scoring stillpending.

2026-10-23 source profile04 Succeeded (20:55:34-20:58:35UTC), sealed24ffa60f3705aadab6e65313b02ce1b7a94bcc719642a31e2eef8b78a319211f. Schema-typed compiler54e8a91 query executed through tested cloud transport19bd668: row_count360, eight checksums, read_only_verified=true, VALUE_QUERY self-report identifies expected investigator531419ef@aeb4d0a9, ordersops and Microsoft SQL Azure. Startup access audit and probe are counted separately in the capture (all physical results recorded); zero model calls or source mutations. This confirms typed-query transport, not end-to-end collector wiring, semantic equality or the units sum. Prior failed captures remain unchanged. Receipt docs/runs/round-twenty-two-source-profile-success.json.

2026-10-23 waitingpilot03: budget PGconnection failed while reading all historical state_usage during job-start admission, before publisher dispatch. Three definition control requests completed; one Wait-only definition was changed, no job submitted. Fresh recovery listed native jobs, found none active, restored original definition/hash (four requests). No readerRUNNING facts earned; original error retained. Budget query now selects only the existing UTC monthly/adoption interval and joins allocations for those rows, under the same serialized transaction. No status/owner/estate filtering, no deletion, no cap, timeout or retry change.32monthly/controltestsPASS, including identical decisions for full-history versus period reads and pending/uncertain/unclassified cross-estate charges. This reduces transfer while locked; the connection failure root cause remains unproven.

2026-10-23 PostgreSQL follow-up: last24h server-log listing returns zero available files (no logging setting enabled or changed). The monthly query narrowing did not eliminate the next laptop connection failure, so it is not a confirmed disconnect fix. Add bounded30/45second retries only to untaped build-control shared reservation admission, keeping owner/key/request constant and reconciling a lost commit acknowledgement before HTTP dispatch. No settlement of another owner, no timeout/cap/role changes; exact tapes and legacy paths retain their prior behavior.35budget/controltestsPASS, including commit-ack loss -> one charge/one dispatch, bounded exhaustion, and auth/query/policy refusal without retry. Initial new test exposed psycopg idle-timeout inheriting Error rather than OperationalError; classification corrected and all35pass. Independent collector/runtime/runner suite69PASS after correcting one test command that named a nonexistent module. Root cause remains open.

2026-10-23 owner PostgreSQL steer implemented: central connector enforces keepalives1/idle30s/interval10s/count3, connect timeout15s. Shared transactions get fresh connections and close before external work; test verifies closure before the next operation. Safe document reads/list/account snapshots reconnect once; untaped control reservations reconnect once using the same owner/key/request. General writes are not automatically replayed; authentication/permission/query/budget errors are not transport retries. Connect acquisition has one retry and is marked to avoid a second nested operation retry. Each failed SQL/commit/cursor request records client-observed idle-before-request, failed-request duration and connection age, without query text/arguments. No claim that this client interval proves server idle. Historical failures had no idle interval; do not invent one.70tests total:56PASS/14opt-in skips. Fresh live read-only ledger snapshot succeeded with zero connection failures, using the corrected laptop connector:1453/6000(INV675/SCAN778/REST0),modelUSD4.080700/40; emergency95untouched. No tier, network, role or budget changed.

2026-10-23 fixture waiting case observed by actual investigator collector at21:23:13.832107Z: job605f92df-b2e4-4851-8263-51d7ade0ad1e RUNNING, twoSCANreads within manual4, zero model calls. Azure reader executionSucceeded21:22:45-21:23:28, sealed capture retained. Original pipeline definition restored/hashconfirmed after nativeCompleted21:30:14.2933333. One waiting case now backed by reader facts; billing waiting cases remain pending. Prior metadata/configuration failures retained. No data activity executed and no source row changed. Receipt docs/runs/round-twenty-two-waiting-fixture-observed.json.

2026-10-23 waiting controls completed: native investigator collected fixtureRUNNING(twoSCAN) and both billingRUNNING(fourSCAN), each within its unchanged manual4allowance. Allthree originaldefinitions restored/hashconfirmed; source data unchanged and controlled history retained. Billing publisher stage8ordinaryINV and recovery8ordinaryINV completed with zero reservation retries/read connection failures using new laptop keepalives/short-lived transactions. These are three actual scenario cases, not scored engine verdicts. Waiting wording is still pending independent batch completion, with DEV2/heldout2 allocation fixed before inspection; restage the same named controlled case for future live scoring rather than calling a historical completed job running. Full80d0940 regression5192total/5144passed/48skipped, zero failures/errors,742.40seconds. Later structured failure-journal/cursor-context/keyed-settlement follow-up48focusedtestsPASS; do not claim the prior full result covers that follow-up.

2026-10-23 independent waiting writer completed three provider messages/four unchanged drafts (DEV2,heldout2 mechanically partitioned without displaying text). AddedUSD0.003998; enrichmentUSD5.276216/25. No engine/expectation/ledger inputs to writer,zero estate reads or investigator calls. These are drafts, not the final sealed60set. Every future scored waiting case must re-stage its named real control and readerRUNNING facts; completed historic runs never substitute. Hashes/seal in docs/runs/round-twenty-two-independent-waiting.json.

2026-10-23 source-history control preparation: existing fixture builder now emits a bounded, parameterized SELECT for only the planned new synthetic IDs, including native rowversion converted to bigint. Managed SQL reader still enforces existing table-only scope, read-only guards and query-bound attestation; no arbitrary ticket SQL or new permission.44fixture/control/apply/gatewaytestsPASS. No source row has been changed. Before any mutation: durable insert/restoration recipe, sealed original preimage, current budget/disk, and a reader observation route must be ready.

2026-10-23 source-history control failures retained: pilot01 changed no source data (twoSQLreads: native40613 while resuming, then SQL156 from an unquoted identity alias in the operator prewarm query). Pilot02 inserted three authored back-dated rows, then the investigator query failed at stagequery, SQL1033/42000;76unsealedpartialrecords preserved. Source controller restored only its three native-version-pinned rows and confirmed the complete original rows hash0a78462d4e4dfd7bf66aeda89cd4d4757f2149fb00d61a14a597922216049a0b,360rows/7661units. ZeroPGdrops/retries during insert/restoration, no permission/identity change, zero model calls. Reader observations of the new rows are not earned yet; owner mutation receipts are not promoted to investigator evidence.

Offline diagnosis: managed_sql_worker adds query-bound attestation by wrapping the SELECT as a derived table. The fixture observer had ORDER BY without TOP. Microsoft [documents the derived-table ordering restriction](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-order-by-clause-transact-sql). Fix the fixture compiler with TOP(n+1), retaining one overflow row and exact-ID/row-count validation; do not remove attestation, change permissions or silently truncate to n.58fixture/managed-worker/gatewaytestsPASS. This is a control-query compiler defect, not evidence of a source outage. The native error code/stage plus constructed statement support the diagnosis; the worker intentionally does not retain arbitrary driver message text. SQL database-wide rowversion advanced during the authored inserts and cannot be rewound; original rows and their native versions are restored.

2026-10-23 source control03 succeeded: existing read-only investigator returned allthree authored back-dated rows, matching IDs/business fields/native versions, with query-bound self-report on ordersops and read_only_verified=true. Same tested cloud transport19bd668, fixture query compileraf9eb5f TOP overflow fix. Source controller restored only its three rows, then verified the complete original row hash and schema hash:360rows/7661units. FourownerSQLcontrolrequests, noPGdrop/retry, zero model calls or permission changes. Native source observations are NOT a completed HISTORY_CHECK witness or scored verdict; no arbitrary old row values are inferred from source_modified_at. Separate native audit/version proof is required for the full history producer. DB-wide rowversion advances are explicitly not rewound. Receipt docs/runs/round-twenty-two-source-history-native-observation.json.

2026-10-23 PostgreSQL completion check: frozen4d7cac3 full suite5196total/5148passed/48skipped, zero failures/errors,696.99s; later TOP fixture repair is covered separately by58focusedtests and hosted CI. Current82470b9 connection/transaction/control-meter checks21PASS; an initial command named a nonexistent test module and was corrected, not hidden. Fresh owner read-only ledger snapshot at2026-10-23T22:32:23.765773+00:00 succeeded with zero connection failures:1516/6000(INV731/SCAN785/REST0), modelUSD4.080700/40, reserve95untouched. No estate/model calls, new permissions or firewall changes. All waiting/source controls restored. Earlier PostgreSQL disconnect cause remains OPEN; successful keepalive operations do not establish causality. No scored dev or sealed60set yet.

2026-10-23 owner source-history steer: choose(b), native system-versioned temporal history on the existing practice source. Existing primary key, no triggers, proposed history absent; native rollback-only DDL probe accepted hidden periods with existing rowversion and restored complete original row/schema hashes. Two physical owner-control requests, zeroPGdrops/retries, zero model calls. Earlier read-only metadata attempt returned SQL40613; Azure then reported Online and the separate retained retry succeeded. No firewall, role or tier changed. Temporal history is not yet enabled by this checkpoint.47fixture/gatewaytestsPASS; initial positive temporal SELECT test exposed the closed AST allowlist, now narrowly admits SYSTEM_TIME ALL only on an independently allowlisted physical table. Red-team tests still refuse writes, external/other objects, AS OF and unknown version forms. Prior freeze invalidated.

2026-10-23 owner option(b) applied: native system-versioning ON for existing practice source1938105945, owned history510624862/app.stock_movements_round22_history. Two hidden generated period columns; complete original360rows/7661units and original eight-column schema hashes match. Native initialhistory0rows; current+history reservedallocation204800bytes (total, not incremental/monthly billed cost). Three publisherSQLcontrols, zeroPGdrops/retries, no grants, identities, tier or free-limit changes. Feature intentionally remains enabled through dependent scored dev/held-out runs; no scored history ticket admitted yet. Native empty-history digest returnedNULL, so cleanup compiler now normalizes emptyJSON to[] before hashing; keep original receipt unchanged. Temporal observation converts datetime2(7) periods to native text, preserving seventh fractional digit. Focused fixture/gateway42testsPASS after removing duplicate imported fixture-test discovery; prior47/48 counts included those duplicate executions. Prior freeze invalid.

2026-10-23 native temporal retention confirmed: cloud investigator executionjob-dia-worker-moadola Succeeded22:50:11-22:52:00UTC, imagec21e46a/source24a56e4. It read three native historical rows900201/900202/900203 after current rows had already been restored and complete original row/schema hashes checked. Native periods22:49:27.1219695-22:49:30.3563391UTC survive as seven-digit text; quantities7/11/13 and native versions44001/44002/44003 match insert receipts. Sealbc27fd8cc92bfb09cb2ba2df393bab205814f448a44bcc2e9aeec6bd6db90f0b,78records. Fourpublishercontrols, zeroPGdrops/retries, zero model calls or grants. Temporal feature/history remains enabled for dependent scores. A bounded fixture point-in-time comparison query is now prepared/tested: matched-row count plus nullableSUM keeps absence separate from0, timestamps bound exactly through7digits.43focusedfixture/gatewaytestsPASS. No scored ticket or HISTORY_CHECK verdict yet; prior freeze invalid.
