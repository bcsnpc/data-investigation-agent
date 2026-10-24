# Blockers and lessons

## Round 22, 2026-10-22: streaming snapshot deadline

Round 21's 96 MiB child-memory test exceeded 180 seconds during the four-way
main suite, then the unchanged complete module passed in 106.893 seconds
alone. Choose a 300-second test deadline (2.8 times the isolated duration),
rather than changing assertions or reducing the database. Source preservation,
concurrent-WAL consistency, unsafe-value refusal and the less-than-96-MiB
peak-growth assertion remain unchanged. Full parallel validation follows.

Validation: frozen `129556e` completed all 5,067 tests in 683.747 seconds:
5,019 PASS, 48 skipped, zero failures/errors. The snapshot module passed inside
its parallel shard; no isolated retry was needed.

## Round 22: daily SQL worker deadline consumed by parent capture

Recovered the immutable Round 21 investigation event journal, SHA-256
`91a868ec379df1a425cbc7c52bcfd854e876101bb9512fe5de30f47aa6368614`.
All three lower workers started with a 150-second deadline. For the first,
identity completed at +7.887s, database guard at +31.752s, object guard at
+94.130s, and the quantity REQUEST arrived at +133.500s. Parent budget/capture
processing delayed ALLOW until +156.476s; flush then raised BrokenPipeError,
and WORKER_END retained -9. The other two repeat that sequence. The query
had not been admitted before the worker deadline. This is evidence of the
parent handshake timing failure, not evidence of an OOM or SQL denial.

Remote publication now waits until the physical worker has closed; the
unchanged original events still serialize, secret-audit and fsync immediately.
Every queued record must be acknowledged before the enclosing step returns or
seals. Published step-start remains evidence of an interrupted incomplete
step. No read-only guard, budget reservation, child timeout, result or expected
classification was relaxed. A real child-pipe test refuses publication while
the child is waiting; failure tests preserve the original error and prevent
an unpublished capture from sealing. Live three-run confirmation is pending.

The first new publication-failure test expected OSError from seal; the existing
seal correctly refused with CAPTURE_PUBLICATION_FAILED_NO_SEAL instead. Corrected
that test assertion to the stronger existing refusal; no implementation bypass.

## Round 22: original audit worker evidence and new diagnostics

Examined original collector capture `0a43cb29-6221-42f0-a119-6acb31ec003d`,
SQL failure receipt SHA-256
`60915ef651f155f0cba18b275bba321f56c976fbecb1361563a7fcff324cf5bd`,
and the retained input/access/physical-read/dispatcher timeline. Database and
object guards passed; the quantity step returned RuntimeError, "Physical read
response unavailable". The two dispatcher observations lasted 26.728 and
27.075 seconds. No SQL permission error or original child exit code survives.

Azure's 21:00 UTC October 22 execution `job-dia-collectors-29878380` has the
matching retained image/input and is Failed; its end time is absent. Replica
listing returns `[]`; log retrieval returns `ERROR: No replicas found for
execution`. These controls cannot establish a child termination reason.
The collector's 60-second container deadline is not proof that it caused this
EOF. Original stderr, child exit code and platform termination reason are
missing. Cause remains UNESTABLISHED; no OOM or permission diagnosis is made.

New bounded, value-free protocol frames report worker start, ten-second
heartbeats and last action. Parent wait separately records the actual exit
code and whether its own deadline fired. The capture publishes these small
diagnostics promptly, without draining the deferred evidence queue, and never
inside a platform transaction. Query text, parameters, tokens and result values
are excluded. Frames do not consume investigation reads or satisfy a value or
identity evidence contract. Launch PID and child-reported interpreter PID remain
distinct: the first real Windows test exposed the venv launcher's separate PID;
requiring them to match was incorrect. Later frames must retain one reported PID.
All 30 lifecycle/publication/managed-worker tests pass. Live audit confirmation
is pending; this item is not yet closed.

The first Linux image run exposed a test-launch error: pytest added scripts to
the parent's import path, but the test's fresh interpreter could not import
managed_sql_worker. Bind that same tracked scripts directory explicitly in the
synthetic child. No production path, permission or expected result changed;
the failed image is not published or deployed.

## Round 22: audit logging live proof, with outer failures retained

The first two logging launches returned NOT_DUE (zero SQL requests); neither
counts as a logging probe. The table-only configuration matched an earlier
collector identity/cursor too. For the actual one-off read, use the existing
direct collect-facts route with a one-second manual listing interval; scheduled
configuration stays at six hours. No cursor or fact was deleted or rewritten.

`round22-audit-lifecycle-03` / `job-dia-collectors-hfpp65n` on tested image
`604867fc` recorded START at03:29:37Z, heartbeats at03:29:48Z (connect) and
03:29:58Z (sql_quantity), CHILD_STOPPING and actual parent-wait EXIT at03:30:02Z:
exit0, deadline_expired=false, last_action=sql_quantity. Four physical SCAN
requests were charged. Seal
`95b17941a5de54ee7c1d134aedda9ef9305081d2e1b10a6987b619b5461cb1d5`.
Full original output: .local/round-twenty-two/audit-lifecycle-03.log.
This satisfies the unknown-cause branch of1c: missing original evidence is
listed, new start/heartbeat/exit/last-action logging is observed live. The
original EOF cause is still UNESTABLISHED.

Do not conflate this with collector success: Azure marked this execution
Failed; its60-second job began03:29:02Z and child completion was after61s.
The outer captured exit intent is0 and sealed; no platform termination reason
establishes why Azure marked it Failed. Also the operator's unnecessarily
narrow four-request allowance was consumed by LIST's guarded SQL read, so
FETCH returned BUDGET_EXHAUSTED and appended no fresh fact. Preserve both.
The scheduled dispatcher still has its original eight-request allowance.
No claim of a new attested load value is made from this logging-only proof.

## 2026-10-22 correction: enclosing audit job limit established

Following the owner's duration test, the original run0a43cb29 began21:00:00Z
and was still publishing its immutable final capture at21:01:09Z: at least69s
against a60s enclosing job. The live probe round22-audit-lifecycle-03 began
03:29:02Z and sealed at03:30:12Z: at least70s against the same60s limit. Its
child exited0, deadline_expired=false. These recorded lower bounds establish
the outer job limit as the failure cause, not the child's own deadline. This
supersedes the earlier UNESTABLISHED conclusion; original receipts stay intact.
Azure's missing endTime still prevents an exact full-duration claim. Evidence:
.local/round-twenty-two/audit-duration-evidence.json and both original sealed
captures. Raise only the enclosing limit to180s, read it back and confirm once.
The runtime preflight regression rejects the obsolete60s configuration when
180s is pinned. Manual4-request FETCH refusal remains a limitation, not a
failed database permission check; scheduled six-hour collection remains the
real load-fact test.

Confirmation: job-dia-collectors-ue92850 / round22-audit-lifecycle-04 finished
Azure Succeeded,03:44:57-03:45:53UTC,56s, on image604867fc with the180s enclosing
limit. Actual child exit0, deadline_expired=false, last_action=sql_quantity;
exit record0/CHECK_REPORT_DELIVERED. Seal
3bd5ece6215588bd9784ec631b72cc90b9451d6740cb63a77d1e142fd1195a74.
Four SCAN requests, zero model calls. LIST read the Warehouse successfully;
the collector returned UNCHANGED_MARKER and appended no fresh fact. Existing
coverage still names SQL_READ_FAILED:LockNotAvailable:None from03:30:30UTC,
not a successful load observation. Do not treat Azure success as fresh-fact
verification. Keep the earlier four-request FETCH limitation and scheduled
six-hour test unchanged. Local output: audit-lifecycle-04.log; ARM before,
single-field PATCH and after: collector-envelope-{before,patch,after}.json.

## Round22 amendment - availability and amended gates

The amended owner prompt was re-read2026-10-22. Keep completed work; new ledger
investigator is the engine under test. Legacy is comparison only. Add1d-2 and
1d-3 before section2; a gate still blocked after three distinct fixes must be
recorded before proceeding. No safety gate is softened. Collector envelope
confirmation does not turn unavailable facts into successful observations.

Availability classes are closed and value-free; transient source reads retry
twice through their existing meters. A typed permission refusal is never an
empty result. Source failure appears as a separate blocked status alongside
the supported verdict, with layer/name, times, attempts, reachable conclusion
and owner. A recorded load's source-outage cause stays attached to failed job.
Do not infer a source outage from a generic connection-failure code: Microsoft
also documents session-limit causes for UserErrorFailedToConnectToSqlServer
([SQL connector](https://learn.microsoft.com/en-us/azure/data-factory/connector-sql-server)).
Native failure receipts remain authoritative; no root cause is manufactured.

Access checks can append availability facts only for explicitly bound graph
subjects in their deployment bindings; no source node or permission is
invented. Collector facts retain the failed call separately from unavailable
run history. Old tests that assumed COVERAGE was the last returned fact now
select it by kind, retaining all negative-accounting assertions. Initial new
test failure was ISO formatting in its assertion; compare canonical times.

The first amended image failed one legacy handoff test: it invoked the renamed
default investigation route with a legacy proof/form. Keep that proof test,
explicitly invoking legacy-baseline; a separate registry test enforces the new
default. No expectation, reader scope or proof assertion was loosened. Failed
image39899480797 was not published or deployed. Session-catalog test also
exposed a real Windows open-file leak: a sqlite connection context commits but
does not close; use closing() for the read-only source. Preserve the selected
model's discovery deny/policy fields in the reduced session catalog.

Availability review found two producer/consumer edge cases before new live
admission. Persist only the final reachability after retries (all failed
attempts stay in the run evidence); otherwise equal collection timestamps can
select a failed attempt after recovery. Use recorded actual observation times
in the cloud. Retained continuation nodes may not be current graph members:
retain their availability in the run, but never insert a graph node merely to
make a ledger write pass, or mask a successful native read as a source failure.
Tests cover both.

A failed load may carry a recorded source outage. Report failed job with the
outage cause even when its source quantity cannot be read, while explicitly
blocking the numerical comparison. The source-outage timestamp must lie inside
that failed run, and the producer must be on the admitted target path. A later
diagnostic outage cannot explain an earlier failure. Tests exercise both the
explicit status and comparison paths; no fabricated quantity or scope change.

Normal mode must not bypass the new investigator's inherited projected-capture
limit. Reject a PRIVACY_PROJECTED estate before state/native reads, even when
no tape is requested; do not quietly record raw audit values. The existing
projected engine limitation remains open, with a regression at cloud assembly.
All estates used for this round's current synthetic exact inputs remain EXACT.


### NORMAL smoke witness transport ? 2026-10-23
The sealed first amended-engine smoke reached the measured 8,765/7,661 boundary and a checked native TRANSFORMATION_LOGIC witness. It then failed at the provider-input admission guard: fetching that witness duplicated 58,675 characters of native assessment/observations into the next model request (configured bound48,000). The bound was not raised. The model view now supplies the checked mechanism, classification, support and evidence IDs, excluding duplicated native observations and rendered outputs. Original full witness/tape bytes remain unchanged in evidence storage and consumer validation still uses them. Retained real witness projects to3,587 characters. Regression proves the input witness is untouched and the model receives the proof classification/references. This is a reliability transport repair; the section2 pattern programme has not been declared complete.


### Section1 checkpoint and soft-gate continuation ? 2026-10-23
Full sourceaa409a7: **5,056 PASS /48 skipped**, zero failures/errors,734.374s. Tested source7d9653f imagee93a69cb has all8 offline shards and publicationPASS. All three jobs read back unchanged schedules/identity/resources; worker3600s, graph1800s, collectors180s (the separately recorded60?180 decision).
Corrected-image smoke sequence: h3xzssv PASS280s (05:18:14?05:22:54UTC), wfdgnq0 PASS277s (05:24:18?05:28:55), ibc6h0s FAIL290s (05:29:52?05:34:42). First two retain as-designed verdict and native TRANSFORMATION_LOGIC at8765/7661; third fails provider-input admission, not an estate or model-provider authorization failure. Every original seal remains unchanged. **Three consecutive greens are not earned.**
Under the amended prompt's explicit three-fix soft gate, continue section2 with the gate OPEN: deferred handshake publication, NORMAL batching/path materialization, and compact design-witness transport were three distinct fixes; the request still grows beyond48000 characters after extra definitions and repeated evidence fetches. The exact failed get_evidence signature, seals, results, readbacks and budget are in docs/runs/round-twenty-two-section-one.json. No threshold or expectation is loosened. The code-owned state/JIT/repeat/prefix work directly addresses this remaining blocker; rerun after that work.
Budget at05:35:41UTC: **1003/6000 physical** (INV466/SCAN537/REST0), reserve95 untouched, model**USD2.967361/40**;68 settled and2historical uncertain reservations, no new open reservations. Enrichment remainsUSD5.170482/25. No new identity, grant or secret. Status52s passes the owner's amended<60s job target; standalone full-investigation<120s remains to be established (smoke investigator phase106.36s is not standalone end-to-end timing).


### Pattern validation: rejected model decision must stay in the loop ? 2026-10-23
The Azure adapter validates ticket-specific consumer scope after stable wire-reference expansion. Its ValidationError previously escaped the investigator loop rather than becoming feedback. The model operation now records that known protocol/schema rejection as a completed failed decision and retries within the existing overall run controls. It does not weaken the validator, resend a completed native read, change an expectation, or catch secret/billing/auth failures. Two regressions prove corrected decisions can complete and SECRET_DETECTED still propagates. This is a validation follow-up, not an extra state-pattern commit.

2026-10-23 Section 2 validation: full suite caught a storage-provider URL above the adapter boundary in the new user harness. Moved the cloud CLI port into adapters; generic submit/poll/outcome and the sealed literal ratchet remain unchanged. No allowance or expectation changed.

2026-10-23 Section2 operator control: `az containerapp job execution list` stalled before smoke admission. The same existing-owner GET via `az rest` returned the complete unpaginated execution list in5.75s, with no active worker. Stopped only the stalled local read-only CLI processes; no cloud execution was interrupted. Operator admission now bounds that REST read at45s and refuses unexamined continuation pages.

2026-10-23 pattern smoke PASS: root model_calls8 but embedded cost.model_calls7; shared ledger settles8 actual calls. Preserve original output, inspect the stale display snapshot during Section3 development. Actual cache12.46% does not establish improvement over the historical65.36% sample.

2026-10-23 standalone harness preparation refused before I/O: operator changed template run_id without the exact matching capture grant. Original config/log retained; bind_execution regression assertion reproduced the error offline, complete Azure listing confirmed no new submission. Corrected configuration preserves template/grant binding and lets existing per-execution binding generate a new ID.
2026-10-23 independent evaluation preparation: initial synthetic batch test caught a missing optimistic revision on submission receipt update; explicit revisions now guard both submission and completion, with uncertain submission/duplicate-key tests. No live batch was submitted before repair.

2026-10-23 user harness A:18model steps,1quantity read,not found; consumer refused unsupported refresh-stale verdict, then repeated evidence fetches exhausted the ticket budget without comparing pending layers. No harmful cause delivered. Record as development evidence; do not count as a successful investigation, soften validation, or substitute the earlier smoke answer.

2026-10-23 evaluation packaging: first fairness cloud execution iycpmm5 was AzureSucceeded but HELD/CHECK_ACCESS_FAILED before provider submission because the new input archive omitted the original permission map/bindings. Original capture preserved; shared evaluation namespace confirmed no batch. New immutable archive02 includes the unchanged files and keeps the access preflight. Operator helper filename replacement also altered its read-only ARM API version to unsupported2025-02-02; the400response is retained, no launch occurred, corrected to the supported2025-01-01.

2026-10-23 fairness execution5egjquv failed before provider submission: worker-exit LockNotAvailable/exit1/UNDELIVERED_EXCEPTION at enrichment-batch, access checks3PASS. Exact exception message was not retained; do not invent it. No final run-record seal exists; partial header, steps, tape reference and exit remain on Blob. Read-only reconciliation found no independent evaluation batch and no evaluation reservations, so no model request was issued. An operator reporting process had an idle-aborted PG read and was stopped after all4pipeline definitions/receipts were saved; this does not establish it caused the worker lock error. No further overlapping operator SharedState reporting snapshot will run during the next submission.

2026-10-23 Round22 fairness: first independent batch12/12 returned, but several rejected freshness/definition questions because facts were not in labels. That is not evidence the tickets are unfair. Preserve all judgments, clarify that fairness concerns a grounded investigation request rather than deriving answers from labels, reassess independently before exclusions. No oracle/expectation/engine change.

2026-10-23 Round22 billing fault control: real job failed with fixedTHROW as intended. Restore updateDefinition returnedHTTP200, but original control stalled during final read/report bookkeeping. A separate metered GET confirmed original semantic hash392afac3? exactly; no new mutation. Only then stopped original local process. No open RESERVED physical rows sincecontrolstart; original partial journal kept, no invented exception/rootcause. PG active-statements query foundnone; exact wait cause remains unestablished.

2026-10-23 Round22 control recovery: a no-locals stack dump of the second stalled local controller identifies psycopg wait_select -> SharedUsage.mirror -> build_phase.shared_reserve, before the next Fabric job GET dispatched. It is a local budget-report mirror wait, not proof of Fabric API latency. Original controller stopped; separate existing-publisher control observed the real failed run, restored the original definition and confirmed hashfebc543e?. One original physical reservation remains conservatively charged RESERVED; no authority check was disabled and no other worker reservation was settled. Both cloud reader collectors succeeded,2+4requests within manual4 each.


2026-10-23 Section3 source readiness: cloudprofile jobgi787q3 Failed at sql_database_permissions before value query, childexit1/deadlinefalse, nativeInvalidOperationException/noSQLerrno. All64partial records preserved; rootseal absent, not labelled replayable. Existing principaldb_datareader plusCONNECT/VIEW DEFINITION; no nonread direct grant found in the owner metadata query. Native builtin hierarchy reports VIEW PERFORMANCE DEFINITION/VIEW SECURITY DEFINITION covered by VIEW DEFINITION; old guard omitted both. Corrected recognition and bounded refusal details50focusedPASS; live corrected-image confirmation pending. No permission or credential changed. Old local reader helper also failed at query with noSQLerrno; do not call either failure source outage or substitute owner quantity as investigator evidence. Receipt runs/round-twenty-two-source-guard-diagnosis.json.

2026-10-23 corrected-guard source profile02, jobiv4nd2c, failed earlier at connection with nativeSqlException40613/HY000; it never exercised the corrected guard. Azure subsequently reported ordersops Online/resumed19:58:59UTC.60unsealed partial records retained, no value obtained or mutation. Root retry classifier recognized18456 but omitted40613, so it recorded retry=false. Add connection-stage40613 to the existing bounded30/45second retry; query-stage40613, permission229, model auth/billing and guard refusals stay unretied. Initial runner test invocation was from dirty engine files and correctly hit TAPE_UNCOMMITTED_ENGINE; rerun from committed source, not by disabling the pin.

2026-10-23 sourceprofile03 confirms the SQL40613 retry (attempt1 retry=true), then both read-only permission guards pass. Attempt2 reaches the actual query and returnsSQL529/22018: the profile compiler attempted nvarchar conversion of nativeSQLtimestamp(rowversion). Native metadata pins this column as timestamp. Fix uses complete schema-derived column_types: binary/image/timestamp/rowversion render as binary hex; other supported types retain their prior text SQL; unsupported/missing/extra type entries refuse. Typed profiles require metadata hash references and remain NOT_EQUALITY_PROOF.57focusedtestsPASS. Original93partial records retained; no source value obtained yet.

2026-10-23 waitingpilot02: three actual Wait-only jobs submitted, publisher observedInProgress; local controller then lost its PGtransaction with IdleInTransactionSessionTimeout. Recovery inspected the same terminal jobs and restored all three original served hashes,12ordinaryINV requests, no emergency reserve. Originalcontroller16requests preserved. ReaderRUNNING collection did not occur within this pilot, so three waiting cases are not claimed earned. No source/table/model data mutated; native completedjob history remains. Underlying PGidle cause remains open; do not call it resolved by the earlier report narrowing.

2026-10-23 waitingpilot03: budget PGconnection failed while reading all historical state_usage during job-start admission, before publisher dispatch. Three definition control requests completed; one Wait-only definition was changed, no job submitted. Fresh recovery listed native jobs, found none active, restored original definition/hash (four requests). No readerRUNNING facts earned; original error retained. Budget query now selects only the existing UTC monthly/adoption interval and joins allocations for those rows, under the same serialized transaction. No status/owner/estate filtering, no deletion, no cap, timeout or retry change.32monthly/controltestsPASS, including identical decisions for full-history versus period reads and pending/uncertain/unclassified cross-estate charges. This reduces transfer while locked; the connection failure root cause remains unproven.

## PostgreSQL laptop failures: owner diagnostic steer, 2026-10-23

Confirmed outward IP184.105.12.85. PostgreSQL pg-dia-d5dd7d65 already has OwnerCurrentIp184.105.12.85/32; no firewall change was needed or made. The existing AllowAzureServices0.0.0.0 rule was left unchanged. This was a separate read from the earlier Azure SQL rule replacement.

Last24h Azure Monitor: CPU credits306-313 (latest306); CPU average latest9.7768%, maximum sampled99.9000%; active connections7-11, latest average9.1. The max_connections metric required PT30M rather than PT5M (original native400 retained) and reports50. Read-only SQL confirms max_connections50 and superuser_reserved_connections10. Control-plane activity query returned no events in the window. Native database metadata queries completed in0.018-0.023s; state_usage contains12,130 rows/933,633 reserved-payload bytes versus1,530 rows/113,966 bytes in the governing interval.

Cause is NOT established as firewall mismatch, depleted credits or exhausted connections: the measurements do not support those explanations. The earlier IdleInTransactionSessionTimeout identifies why that particular transaction was killed, not why the client went idle; the latest generic OperationalError cannot distinguish network loss from server termination. Keep this root-cause item open. Monthly query narrowing reduces unrelated historical transfer, with accounting-equivalence tests, but is not a proved fix for the connection losses. No timeout, server tier, role or network range was changed. Exact queries, metric window and hashed receipts: docs/runs/round-twenty-two-postgres-diagnosis.json.

2026-10-23 waitingpilot04:12publisherrequests submitted three Wait300jobs, allcompleted and originalhashesrestored (12recoveryrequests). Fixture reader Failed FACT_COLLECTOR_RUNNER_OPTIONS before any collector dispatch: operator config incorrectly added force at runner options level. All11unsealedpartialrecords retained. New load preflight reuses the same consumer validator before cloud admission; two regressionsPASS. Pilot05 separately exposed another PGconnection loss despite monthly query narrowing; fixture Wait600submitted, billing mutation NOTdispatched. A broad local filename substitution accidentally changed billingworkspace04f6 to05f6; native404 during no-op recovery retained. Correct helper identifiers from declared constants, never global substitutions; no incorrect workspace mutation succeeded. Fixture restoration pending its controlled job completion.

2026-10-23 PostgreSQL follow-up: last24h server-log listing returns zero available files (no logging setting enabled or changed). The monthly query narrowing did not eliminate the next laptop connection failure, so it is not a confirmed disconnect fix. Add bounded30/45second retries only to untaped build-control shared reservation admission, keeping owner/key/request constant and reconciling a lost commit acknowledgement before HTTP dispatch. No settlement of another owner, no timeout/cap/role changes; exact tapes and legacy paths retain their prior behavior.35budget/controltestsPASS, including commit-ack loss -> one charge/one dispatch, bounded exhaustion, and auth/query/policy refusal without retry. Initial new test exposed psycopg idle-timeout inheriting Error rather than OperationalError; classification corrected and all35pass. Independent collector/runtime/runner suite69PASS after correcting one test command that named a nonexistent module. Root cause remains open.

2026-10-23 owner PostgreSQL steer implemented: central connector enforces keepalives1/idle30s/interval10s/count3, connect timeout15s. Shared transactions get fresh connections and close before external work; test verifies closure before the next operation. Safe document reads/list/account snapshots reconnect once; untaped control reservations reconnect once using the same owner/key/request. General writes are not automatically replayed; authentication/permission/query/budget errors are not transport retries. Connect acquisition has one retry and is marked to avoid a second nested operation retry. Each failed SQL/commit/cursor request records client-observed idle-before-request, failed-request duration and connection age, without query text/arguments. No claim that this client interval proves server idle. Historical failures had no idle interval; do not invent one.70tests total:56PASS/14opt-in skips. Fresh live read-only ledger snapshot succeeded with zero connection failures, using the corrected laptop connector:1453/6000(INV675/SCAN778/REST0),modelUSD4.080700/40; emergency95untouched. No tier, network, role or budget changed.

2026-10-23 independent waiting writer preparation failures preserved: first local admission refused a stale platform cost receipt before cloud launch; new config cites the existing actual fresh646485microdollar billing receipt without altering its timestamp. Second cloud attempt failed INVESTIGATOR_INPUT_BOUND before provider dispatch because a template retained the old r17-fairness-tasks path while the sealed archive contained writer-waiting-tasks.json. Third config mechanically verifies every fixed input path and SHA against package members before launch; same batch key, no blind provider resubmission. No billing/auth refusal or investigator outcome occurred.

2026-10-23 source-history control failures retained: pilot01 changed no source data (twoSQLreads: native40613 while resuming, then SQL156 from an unquoted identity alias in the operator prewarm query). Pilot02 inserted three authored back-dated rows, then the investigator query failed at stagequery, SQL1033/42000;76unsealedpartialrecords preserved. Source controller restored only its three native-version-pinned rows and confirmed the complete original rows hash0a78462d4e4dfd7bf66aeda89cd4d4757f2149fb00d61a14a597922216049a0b,360rows/7661units. ZeroPGdrops/retries during insert/restoration, no permission/identity change, zero model calls. Reader observations of the new rows are not earned yet; owner mutation receipts are not promoted to investigator evidence.

Offline diagnosis: managed_sql_worker adds query-bound attestation by wrapping the SELECT as a derived table. The fixture observer had ORDER BY without TOP. Microsoft [documents the derived-table ordering restriction](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-order-by-clause-transact-sql). Fix the fixture compiler with TOP(n+1), retaining one overflow row and exact-ID/row-count validation; do not remove attestation, change permissions or silently truncate to n.58fixture/managed-worker/gatewaytestsPASS. This is a control-query compiler defect, not evidence of a source outage. The native error code/stage plus constructed statement support the diagnosis; the worker intentionally does not retain arbitrary driver message text. SQL database-wide rowversion advanced during the authored inserts and cannot be rewound; original rows and their native versions are restored.

2026-10-23 PostgreSQL completion check: frozen4d7cac3 full suite5196total/5148passed/48skipped, zero failures/errors,696.99s; later TOP fixture repair is covered separately by58focusedtests and hosted CI. Current82470b9 connection/transaction/control-meter checks21PASS; an initial command named a nonexistent test module and was corrected, not hidden. Fresh owner read-only ledger snapshot at2026-10-23T22:32:23.765773+00:00 succeeded with zero connection failures:1516/6000(INV731/SCAN785/REST0), modelUSD4.080700/40, reserve95untouched. No estate/model calls, new permissions or firewall changes. All waiting/source controls restored. Earlier PostgreSQL disconnect cause remains OPEN; successful keepalive operations do not establish causality. No scored dev or sealed60set yet.

2026-10-23 owner source-history steer: choose(b), native system-versioned temporal history on the existing practice source. Existing primary key, no triggers, proposed history absent; native rollback-only DDL probe accepted hidden periods with existing rowversion and restored complete original row/schema hashes. Two physical owner-control requests, zeroPGdrops/retries, zero model calls. Earlier read-only metadata attempt returned SQL40613; Azure then reported Online and the separate retained retry succeeded. No firewall, role or tier changed. Temporal history is not yet enabled by this checkpoint.47fixture/gatewaytestsPASS; initial positive temporal SELECT test exposed the closed AST allowlist, now narrowly admits SYSTEM_TIME ALL only on an independently allowlisted physical table. Red-team tests still refuse writes, external/other objects, AS OF and unknown version forms. Prior freeze invalidated.

2026-10-23 owner option(b) applied: native system-versioning ON for existing practice source1938105945, owned history510624862/app.stock_movements_round22_history. Two hidden generated period columns; complete original360rows/7661units and original eight-column schema hashes match. Native initialhistory0rows; current+history reservedallocation204800bytes (total, not incremental/monthly billed cost). Three publisherSQLcontrols, zeroPGdrops/retries, no grants, identities, tier or free-limit changes. Feature intentionally remains enabled through dependent scored dev/held-out runs; no scored history ticket admitted yet. Native empty-history digest returnedNULL, so cleanup compiler now normalizes emptyJSON to[] before hashing; keep original receipt unchanged. Temporal observation converts datetime2(7) periods to native text, preserving seventh fractional digit. Focused fixture/gateway42testsPASS after removing duplicate imported fixture-test discovery; prior47/48 counts included those duplicate executions. Prior freeze invalid.

2026-10-23 native temporal retention confirmed: cloud investigator executionjob-dia-worker-moadola Succeeded22:50:11-22:52:00UTC, imagec21e46a/source24a56e4. It read three native historical rows900201/900202/900203 after current rows had already been restored and complete original row/schema hashes checked. Native periods22:49:27.1219695-22:49:30.3563391UTC survive as seven-digit text; quantities7/11/13 and native versions44001/44002/44003 match insert receipts. Sealbc27fd8cc92bfb09cb2ba2df393bab205814f448a44bcc2e9aeec6bd6db90f0b,78records. Fourpublishercontrols, zeroPGdrops/retries, zero model calls or grants. Temporal feature/history remains enabled for dependent scores. A bounded fixture point-in-time comparison query is now prepared/tested: matched-row count plus nullableSUM keeps absence separate from0, timestamps bound exactly through7digits.43focusedfixture/gatewaytestsPASS. No scored ticket or HISTORY_CHECK verdict yet; prior freeze invalid.

2026-10-23 native historical comparison succeeded as investigator: executionph830vc22:57:57-22:59:21UTC. For movements900201/900202/900203, at22:49:20UTC matchedrows0/SUMBLANK; at22:49:28UTC matchedrows1/SUM7,11,13. Native retained coverage begins22:43:47.9434148UTC, before both requested times. Current source remains restored and native history remains enabled. This proves before/after data remains queryable after restoration; no scored engine verdict claimed. Existing engine gaps retained for dev: ProcessChecks only installs DESIGN_CHECK; validate_history wraps before_quantity as VALUE, so BLANK-before insertion cannot be silently treated as0. No expectation or contract changed to hide that gap. Receipt docs/runs/round-twenty-two-temporal-before-after.json.

2026-10-23 frozenfcce806 full suite5203total/5155passed/48skipped, zero failures/errors,1122.15seconds. Allfourshards exited0. This covers native temporal enablement/empty-history normalization; later point-in-time fixture compiler is separately43focusedPASS and final cleanup NULL checks7focusedPASS. Cleanup now refuses missing object IDs or NULL native digests explicitly instead of relying on SQL three-valued comparisons. No history cleanup executed. Hosted24a56e4 all8shards+publicationPASS, fcce806 andb396844 hosted checksPASS; no claim of a final release gate. Native history remains enabled, current source restored, no scored60set/dev/held-out yet. Independent drafting currently32tickets:28DEV/4HELDOUT, not a sealed final set. Last ledger1557/6000(INV772/SCAN785/REST0),investigatorUSD4.080700/40,enrichmentUSD5.282409/25,reserve95untouched; diskC27.45/D13.18GiB. All recent owner PostgreSQL reads/controls had zero drops/retries; earlier idle-drop cause remains open.

2026-10-23 different-context preparation: three same-application export comparisons independently derived from committed seed literals before native reads. Warehouse1/2:2948/2084; product7/8:1104/1258; September14/15:923/772. Complete derivation script, row counts and seed hash in docs/round-twenty-two-context-controls.md; no report-total or pipeline-defect claim. Bounded fixture-only grouped compiler uses two bound context values, nativeSUM and a keyed result; no estate mutation, new permission or engine route. Two testsPASS. Initial test wrongly looked for digit2 anywhere in a statement containing a dated table name; corrected to assert the WHERE AST has parameters and no literals. Native values and scored verdicts not earned yet. Prior freeze invalid.

2026-10-23 access-difference preparation: native billingapp metadata confirms existing dia-investigator-round19(EXTERNAL_USER) and orderops_investigator(SQL_USER,DATABASE) both have db_datareader, proposed isolated access objects absent, app schema exists. First metadata readSQL40613, separate retry33seconds later succeeded; no firewall/tier/permission changed, and no quota-exhaustion cause inferred. Existing protected SQL-reader file was checked by username only; no secret printed/copied. Plan uses app.round22_access_rows(6syntheticrows), app.round22_access_readers(3data mappings), app.round22_access_export: CURRENT_USER chooses visible data; this is not a security policy and not an actual permission difference. Same native group query, separate real sign-ins, no impersonation. Existing role scope supplies SELECT; no grant planned. Independent synthetic sums: SQLreader10/20/30, investigatorSP25/45/65. Four new fixture/closed-scope testsPASS. No objects created yet; native paired observations/scoring pending. Prior freeze invalid.

2026-10-23 refresh-stale preparation finding: retained fixture/billing definitions are DirectLake except fixture constant-inline Import/calculated tables. Microsoft documents automatic framing as enabled by default and a portal setting to disable it: https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-how-it-works . An old refresh timestamp alone does not establish stale DirectLake data. No automatic-update setting changed and no refresh-stale control or unsupported-API claim earned; continue investigating a reversible, build-script-based control with actual divergent values/load chronology.

2026-10-24UTC isolated-model reader control02 reached nativeDAX and was refused401/PowerBINotAuthorizedException. Azure wrapperSucceeded is not query success. Expected tokenaudience/tenant/application recorded; publisherportal maps this model to Default:SingleSign-On(EntraID), automatic updatesON. Do not infer tokenexpiry or missingBuild without further evidence. Initial01packaginghold remains separate. No modelsetting/connection/permissionchanged; no refresh-stale quantity or scoredblockedticket claimed. Receipt docs/runs/round-twenty-two-application-refresh-preparation.json.

2026-10-24UTC framing-control proof refused: existingpublisher GETmodelmetadata succeeded, SDKderivedPOST metadata/models/6992510/settings bodydirectLakeAutoSync=false returned401. Reloadedpublisherportal stillshowsON, so no restorePOSTneeded and no retry/escalation. Exactrequest/response/preimage/readback: docs/runs/round-twenty-two-autosync-control-refusal.json. Twoownercontrolphysicalrequests, zero models. Causeunestablished; notcalledexpiredcredentialormissingrole. No stale-state case earned.

2026-10-23 owner date / 2026-10-24 UTC: third native blocked-record control qg5qqdr failed before its DAX request with LockNotAvailable: "canceling statement due to lock timeout". Original 44 partial capture files retained unchanged, not a sealed run and not an access result. Concurrent schedule control overlapped, but the exact lock holder is not established. Code inspection found read-only budget snapshots taking the global reservation writer lock. Read snapshots now use database-enforced read-only repeatable-read transactions; reservation mutations retain READ COMMITTED, the exclusive advisory lock and both lease checks. Replay uses the same read-only contract. No broad lock-timeout/write retry, counter release, limit or permission change. This establishes an avoidable contention path, not the cause of earlier idle drops. Focused core41PASS; clean replay/full regression follows.

2026-10-23 owner date /October24UTC: original read-lock Windows full5224 executed:5175PASS,48skip,1ERROR,0assertion failures,1279.61s. Error retained: old safe-read test mock did not accept _read_only keyword; fixed mock now asserts that flag on both retry calls. Focused51PASS. Add connection/read-only/monthly-allocation regression modules to the published-image offline shard list; prior8shards were a selected foundation suite, not the full Windows suite. No expectation changed. Full final rerun follows.

2026-10-23 owner resume after laptop power loss (UTC24October): clean pushed efbb18b recovered. All5recent cloud worker executions plus01:30collector Succeeded; no cloud operation remained in flight at01:53UTC. Local5227test final rerun interrupted; original partial logs hashed/preserved, not a pass or failure. Affected51tests re-runPASS. No open model/enrichment reservations; interrupted publisher refresh-historyGET remains fully charged1request and is nowUNCERTAIN, originals unchanged. Five older physical reservations are unchanged and conservatively counted; historical orphan is immutable. Current1840/6000 (INV1023,SCAN817,REST0), reserve95; modelUSD4.080700/40. Owner now approves source-correct fixed identity for Appmodel and actual reversible new source rows: prior equal-data loads prove timing only, never a numeric stale discrepancy. Existing blocked-case401captures remain historical and cannot be scored against an accessible model without fresh failure staging.

2026-10-23 owner date /24OctoberUTC: restarted clean full regression completed5227tests,5179PASS/48skip/0failure/0error,744.69seconds, onfa1a405 engine source. The affected51tests alsoPASS. Original mock error and interrupted final run remain preserved. No estate/model read in these tests; no expectation changed. Source connection/data changes are publisher-controlled fixture preparation, not scored findings.

2026-10-23 owner date / October24UTC: hosted47b8 image shard0 exposed an isolated test-environment assumption, not an allowed I/O: global DIA_LIVE_ACCESS_DISABLED=1 correctly refused LIVE_ACCESS_DISABLED before the empty identity policy. The transaction guard assertions already passed. Identity-denial assertion now locally isolates that switch and separately asserts the enabled kill switch refuses; production gateway unchanged. Original workflow40050822183 retained. Affected16 state plus4 read-transaction tests PASS with global live access disabled; no transport call occurs.

2026-10-24UTC latency prototype01: native source reader observed900501/502/503 with17/19/23units, but Bronze control failed before dispatch onSQL_ROW_CAP_EXCEEDED(request4,existingpolicy2). Original44partialfiles retained, unsealed, no latency claim. Guard refused correctly; control now requests oneCOUNT/SUM row within2, preserving NULL for absence, no scope or policy change. Owned future schedule removed; only900501-503 deleted by native-version guards, full363-row/7692 preimage hash matched, stale900401-403 retained.11publishercontrols,0models. InitialSQL40613 resumed on bounded read-only prewarm retry. See docs/runs/round-twenty-two-latency-prototype-failure.json.

2026-10-24UTC scored latency admission: Azure ARM execution-list GET failed with ConnectionResetError(10054) before the fresh source probe launched and before ticket submission. Preserved the BLOCK as INVALID_NOT_AN_ENGINE_RESULT, restored the owned source/schedule, and restaged only the two never-submitted tickets. The private control wrapper retries only idempotent list/show GET transport failures, never a start POST or an uncertain ticket submission. All4submitted latency outcomes remain HELD on the missing raw-calculation route. No expectation changed; receipts docs/runs/round-twenty-two-scored-latency-admissions.json.

2026-10-24UTC scored Wait control restoration encountered native HTTP401 TokenExpired (requestId de39914c-d0a5-490b-80c9-ee94c3f5956a) after both scored outcomes were sealed. FabricCliTokens cached a publisher access token for the entire process without checking exp. A fresh acquisition under the same existing publisher returned the same configured tenant and audience with valid expiry; no identity, permission, sign-in or secret changed. The cache now renews120seconds before expiry and rejects an already-expired acquisition; ten connector tests pass. No failed mutation is retried blindly. Original401/status are preserved; recovery waits the owned job terminal before guarded definition restoration. This is a control finalization failure, not a replacement scored attempt.


### Round22 first dev score and grouped fix loop, 2026-10-24
All40 first-pass outcomes are preserved; independent Claude grade1/40, harmful0. Legacy baseline and held-out are not run. Fixture admission failures before submission remain separate. No expectation was amended.
- R17-01-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Handled Quantity sums the carried additive units, not a count of movement records; the unfiltered card evaluates8765. Preserve the named visual, qualify saved/default and snapshot assumptions, and never judge intended business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-02-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Handled Quantity sums the carried additive units, not a count of movement records; the unfiltered card evaluates8765. Preserve the named visual, qualify saved/default and snapshot assumptions, and never judge intended business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-03-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Handled Quantity sums the carried additive units, not a count of movement records; the unfiltered card evaluates8765. Preserve the named visual, qualify saved/default and snapshot assumptions, and never judge intended business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-04-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Business intent or physical unit meaning is not established by the SUM definition. Recreate the technical figure where possible, state the limit, never invent intended correctness or physical units.","verdict":"not found"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-05-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Handled Quantity sums the carried additive units, not a count of movement records; the unfiltered card evaluates8765. Preserve the named visual, qualify saved/default and snapshot assumptions, and never judge intended business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-06-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Handled Quantity sums the carried additive units, not a count of movement records; the unfiltered card evaluates8765. Preserve the named visual, qualify saved/default and snapshot assumptions, and never judge intended business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-07-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Return the exact model refresh-history facts after path-only refresh; retained last successful API refresh ended2026-10-07T21:15:37.357Z with schedule disabled. Do not claim query-bound snapshot freshness or invent a recent refresh.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-08-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Return the exact model refresh-history facts after path-only refresh; retained last successful API refresh ended2026-10-07T21:15:37.357Z with schedule disabled. Do not claim query-bound snapshot freshness or invent a recent refresh.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-09-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Return the exact model refresh-history facts after path-only refresh; retained last successful API refresh ended2026-10-07T21:15:37.357Z with schedule disabled. Do not claim query-bound snapshot freshness or invent a recent refresh.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-10-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Handled Quantity sums the carried additive units, not a count of movement records; the unfiltered card evaluates8765. Preserve the named visual, qualify saved/default and snapshot assumptions, and never judge intended business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-11-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Business intent or physical unit meaning is not established by the SUM definition. Recreate the technical figure where possible, state the limit, never invent intended correctness or physical units.","verdict":"not found"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- R17-12-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"Business intent or physical unit meaning is not established by the SUM definition. Recreate the technical figure where possible, state the limit, never invent intended correctness or physical units.","verdict":"not found"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- failed-fixture-load-v1 ? answered/failed job ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"PIPELINE","named_cause":"round_two_application_load_audited_20261003: the specifically named native run failed with controlled SQL THROW2011 before original activities; it did not complete. Never attribute the old failure to the restored current definition.","verdict":"failed job"} ? Correct failed-job status but delivery omitted its specific ledger error and run particulars.
- failed-fixture-load-v2 ? answered/failed job ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"PIPELINE","named_cause":"round_two_application_load_audited_20261003: the specifically named native run failed with controlled SQL THROW2011 before original activities; it did not complete. Never attribute the old failure to the restored current definition.","verdict":"failed job"} ? Correct failed-job status but delivery omitted its specific ledger error and run particulars.
- failed-billing-transform-v1 ? answered/failed job ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"PIPELINE","named_cause":"Billing Warehouse transformations: the specifically named native run failed with controlled SQL THROW2011 before original activities; it did not complete. Never attribute the old failure to the restored current definition.","verdict":"failed job"} ? Correct failed-job status but delivery omitted its specific ledger error and run particulars.
- failed-billing-transform-v2 ? answered/failed job ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"PIPELINE","named_cause":"Billing Warehouse transformations: the specifically named native run failed with controlled SQL THROW2011 before original activities; it did not complete. Never attribute the old failure to the restored current definition.","verdict":"failed job"} ? Correct failed-job status but delivery omitted its specific ledger error and run particulars.
- failed-billing-load-v1 ? answered/failed job ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"PIPELINE","named_cause":"Billing application load: the specifically named native run failed with controlled SQL THROW2011 before original activities; it did not complete. Never attribute the old failure to the restored current definition.","verdict":"failed job"} ? Correct failed-job status but delivery omitted its specific ledger error and run particulars.
- failed-billing-load-v2 ? answered/failed job ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"PIPELINE","named_cause":"Billing application load: the specifically named native run failed with controlled SQL THROW2011 before original activities; it did not complete. Never attribute the old failure to the restored current definition.","verdict":"failed job"} ? Correct failed-job status but delivery omitted its specific ledger error and run particulars.
- baseline-S01-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"REFINED -> SERVING","named_cause":"Left join on product_id has two rate matches for product7;1104 carried units repeat,7661+1104=8765. Describe recorded mechanics without judging business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- baseline-S01-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"REFINED -> SERVING","named_cause":"Left join on product_id has two rate matches for product7;1104 carried units repeat,7661+1104=8765. Describe recorded mechanics without judging business correctness.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- baseline-S02-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"REFINED -> SERVING","named_cause":"Invoice101 has two account-plan-history matches;250 repeats,700+250=950. SUM includes all statuses; do not decide whether VOID should count.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- baseline-S02-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"REFINED -> SERVING","named_cause":"Invoice101 has two account-plan-history matches;250 repeats,700+250=950. SUM includes all statuses; do not decide whether VOID should count.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- baseline-S03-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"CALCULATE SUM of Sales[Sales Amount] with USERELATIONSHIP(Sales[DueDateKey],Date[DateKey]); no invented numeric result or business policy.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- baseline-S03-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SEMANTIC","named_cause":"CALCULATE SUM of Sales[Sales Amount] with USERELATIONSHIP(Sales[DueDateKey],Date[DateKey]); no invented numeric result or business policy.","verdict":"as designed"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- access-export-1-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"Case1: orderops_investigator sees10 and1row; investigator principal sees25 and2rows. Same SELECT; CURRENT_USER visibility-group data mapping differs. It is data-based visibility, not a newly enabled native RLS policy or permission grant.","verdict":"access difference"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- access-export-1-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"Case1: orderops_investigator sees10 and1row; investigator principal sees25 and2rows. Same SELECT; CURRENT_USER visibility-group data mapping differs. It is data-based visibility, not a newly enabled native RLS policy or permission grant.","verdict":"access difference"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- different-warehouse-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"The two application exports select different warehouse_id1=2948 versus2=2084; do not compare them as the same scope or claim pipeline loss.","verdict":"different question"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- different-warehouse-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"The two application exports select different warehouse_id1=2948 versus2=2084; do not compare them as the same scope or claim pipeline loss.","verdict":"different question"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- latency-900501-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE -> BRONZE","named_cause":"Movement900501 exists in application after the last completed load but is absent in Bronze; a real enabled future application-load schedule has not run yet. Name the scheduled load and its due time, distinguish missing row/BLANK from zero.","verdict":"latency"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- latency-900501-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE -> BRONZE","named_cause":"Movement900501 exists in application after the last completed load but is absent in Bronze; a real enabled future application-load schedule has not run yet. Name the scheduled load and its due time, distinguish missing row/BLANK from zero.","verdict":"latency"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- latency-900502-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE -> BRONZE","named_cause":"Movement900502 exists in application after the last completed load but is absent in Bronze; a real enabled future application-load schedule has not run yet. Name the scheduled load and its due time, distinguish missing row/BLANK from zero.","verdict":"latency"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- latency-900502-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE -> BRONZE","named_cause":"Movement900502 exists in application after the last completed load but is absent in Bronze; a real enabled future application-load schedule has not run yet. Name the scheduled load and its due time, distinguish missing row/BLANK from zero.","verdict":"latency"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- history-source-900201-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"Retained native temporal history shows movement900201 absent/BLANK before22:49:20UTC and quantity7 at22:49:28UTC on2026-10-23. Native versions persist; do not invent a zero or infer history from removed current rows.","verdict":"source changed history"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- history-source-900201-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"Retained native temporal history shows movement900201 absent/BLANK before22:49:20UTC and quantity7 at22:49:28UTC on2026-10-23. Native versions persist; do not invent a zero or infer history from removed current rows.","verdict":"source changed history"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- older-export-movement-1-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"Requested2026-10-20 snapshot precedes earliest retained native history2026-10-23T22:43:47.9434148. Current movement is known but earlier quantity cannot be established; no zero, change or earlier value invented.","verdict":"not found"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- older-export-movement-1-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"SOURCE","named_cause":"Requested2026-10-20 snapshot precedes earliest retained native history2026-10-23T22:43:47.9434148. Current movement is known but earlier quantity cannot be established; no zero, change or earlier value invented.","verdict":"not found"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- stale-total-v1 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"BRONZE -> SEMANTIC","named_cause":"Application load fixture20261003 model at7661 versus Bronze7692 for total; load completed after model framing, automatic updates are held off. Name that model refresh boundary, no pipeline-loss verdict.","verdict":"refresh stale"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- stale-total-v2 ? HELD/None ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"BRONZE -> SEMANTIC","named_cause":"Application load fixture20261003 model at7661 versus Bronze7692 for total; load completed after model framing, automatic updates are held off. Name that model refresh boundary, no pipeline-loss verdict.","verdict":"refresh stale"} ? Raw calculation admission was not installed; no technical quantity investigation began.
- waiting-fixture-load-v2 ? answered/not found ? expected {"blocked":false,"harmful":false,"layer_or_split_point":"PIPELINE","named_cause":"Named job has a freshly observed active RUNNING/QUEUED Wait-control execution, not a completed historic run. Name that job/run and its pending completion, not a failure or invented SLA.","verdict":"waiting on job"} ? The explicit status validator rejected declarative still-running wording despite a fresh running-job admission.

Waiting fixture finalization: the same-publisher token recovery waited the owned run terminal, restored the original pipeline definition and matched its preimage hash; docs/runs/round-twenty-two-dev1-fixture-restoration.json. The original TokenExpired response is preserved. Persistent stale-refresh/history/access injections remain intentionally active for subsequent dependent scores.


2026-10-24 owner focus steer: remaining Round22 work is calculation intake, deterministic answer detail and investigation reasoning. Dev remains NORMAL only; no scored-dev byte-exact replay gate. Attestation is a warning, not a dev admission condition. Non-safety blockers are logged and bypassed for dev without changing read-only/secret/monthly-cap enforcement or sealed held-out/independent grading. No new guard/receipt/attestation/admission framework is authorized.

2026-10-24 intake integration fix: the graph name query filtered by node IDs and therefore lost all edge IDs; explicit report/page names could not constrain a visual. Enriched intake now retrieves the actual bounded containment/measure edges. Installation graph authority and the names shown to intake are separate: up to200 named candidates, with existing upstream graph objects available to the selected path (each runtime slice remains200nodes/500edges). This removes a metadata-scope configuration obstacle, not an estate permission boundary. A real SQLite graph regression proves report/page/visual/measure edges survive; no lookup uses expectations or values. Provider schema enums now explicitly carry string type.

2026-10-24 owner focus bypass: in build-phase investigator reads, a successful native quantity is no longer erased solely by failed surface attestation. Original attestation result and contradiction stay in native evidence, with an explicit warning and no attestation claim. Native query failures and NOT_COMPARABLE scope refusals remain failures.59focused port/cloud/intake tests PASS. Existing read-only gateway, secret checks and budget cap unchanged; no new admission or receipt mechanism.

2026-10-24 validation error retained: I edited/committed source during calculation-causes-full, invalidating its engine revision.3failures/20errors include TAPE_UNCOMMITTED_ENGINE and ENGINE_VERSION_MISMATCH; this is not a clean-source regression result. Affected148tests subsequentlyPASS. Fresh frozen4b2ad42 full5274total/5226PASS/48skip, zero failures/errors,854.98seconds, all4shards0; docs/runs/round-twenty-two-intake-causes-full.json. No safety guard was relaxed to make replay tests pass.

2026-10-24 dev2 first launch stopped before model dispatch: existing gateway correctly refused IDENTITY_NOT_ALLOWED for alias model. The dev configuration had reused an enrichment-only writer template. Original run e1c0ca76/job-dia-worker-tyi5hjk, exact console and missing final blob404 are preserved. Corrected configurations reuse the existing daily model/investigator/federated aliases verbatim; no new identity, permission, audience or secret. This is a configuration correction, not a provider billing/auth refusal or a new scored finding.

2026-10-24 dev2 intake failures drive generic fixes, without consulting held-out: R17-01 model enumerated contiguous tokens instead of endpoints; the span parser now accepts that identical unambiguous span and prompts explicitly for endpoints. Noncontiguous lists still retry/refuse. R17-02 visual names were opaque PBIR identifiers despite literal visible titles in retained definitions; static graph extraction now uses the existing literal-title reader, with node IDs and original definitions unchanged. Dynamic titles are not guessed. R17-03/05 named a current page as context; target lookup now uses that location to disambiguate a measure, without adding page-wide filters or borrowing a comparator's page.133focused tests PASS; these are next-iteration fixes, not an improved dev2 score. Existing dev2 executions remain pinned to4b2ad42 and the original graph until its cohort closes.

2026-10-24 same span-parsing fix also accepts a single listed token as the identical one-token span; dev2R17-08 returned [6] for a numeral, which is not user ambiguity.133focused testsPASS, including exact950 and noncontiguous-reference refusal; no precision, expectation or held-out change.

2026-10-24 legacy comparison wiring: the cloud legacy-baseline handler now forwards a raw id/text file to the existing SmartIntake.submit port, not a fabricated measure-only form. No legacy interpretation/reasoning algorithm changed.115cloud form/proof/intake/investigator testsPASS. The first new test was placed before the tail of an existing test, producing a test-only NameError; corrected placement retained all prior assertions. Native library ResourceWarnings remain visible; no new read or model call was used by these tests.

2026-10-24 native-reader selection fix: a resolved measure keeps its own installed reader even when its declared expression depends on other measures. For a visual, select only its unique direct COMPUTED_FROM measure; multiple direct measures remain unresolved.111focused cloud/intake/native-port/inventory testsPASS. This fixes referent preservation without any ticket-id, value or expected-outcome lookup.

2026-10-24 dev2 controller resumed the existing R17-09 execution after a failed ARM poll; no repeated investigation. First failed-fixture-load-v1 execution had no final capture and no remaining replicas/logs. Its retained retry exposed local gateway ENDPOINT_METHOD_NOT_ALLOWED for the exact native Copy Job jobs/instances GET (digest72a5a039...). Existing status/fact reader policies already authorize that GET. Dev configurations now reuse those exact existing read entries; no role/audience/permission/secret changed. Both undelivered attempts and exact second console remain local, no successful score claimed for them. No extra guard or receipt framework added.

2026-10-24 referent/scope correction for the next dev iteration: a reported number located on a named report/page cannot silently become a bare model-wide measure read. A unique declared visual showing that measure at that location supplies the visual target with an explicit assumption; multiple visual candidates ask once, never choose by a matching value. Negated page mentions do not constrain the target.165focused testsPASS, including a two-visual same-measure wrong-cell regression and the unchanged sealed-set/inventory checks. Current frozen dev2 outcomes remain unchanged.

2026-10-24 Round22 dev definition questions: `definition_of` exposed only a content-addressed reference, leaving the investigator unable to read the retained calculation. Reused the existing immutable Files reader on the existing platform snapshot channel; the tool now returns the exact UTF-8 definition with its original provenance, including historical views. No native data read, identity, scope, new receipt or admission mechanism. The descriptive-definition verdict route remains an open reasoning item; this wiring alone is not claimed to fix the two scored results. Focused graph/cloud/investigator tests: 102 passed, 13 subtests. Existing dev2 cohort stays on its frozen image.
2026-10-24 Round22 retained-definition wiring follow-up: use the existing worker storage declaration even when a sample estate has no facts collector. FACT-only status runs do not initialize this reader. The first focused run exposed a test assembly with an empty mocked storage declaration; restricting initialization to non-FACT requests preserves the status path. Corrected focused run: 102 PASS plus 13 subtests; no safety/red-team failure and no live retry admitted for this change.
2026-10-24 Round22 dev latency holds: intake searched a report/model-only candidate installation (147 fixture names), while the retained graph also contains the explicitly named Bronze source and application table outside that candidate closure. No native read or expectation is needed to establish this configuration omission. Fixing extraction alone cannot bind absent candidates. A separate generic lexical defect treated underscore names as single words; name search now treats spaces, underscores and hyphens consistently, preserves every suffix, and still asks when normalized names collide. Focused calculation/cloud/investigator tests: 98 PASS plus 13 subtests. The current cohort remains frozen; complete candidate discovery and table-start quantity execution remain open for the next dev iteration.
2026-10-24 Round22 definition reasoning repair: DEFINITION previously rejected every proposed answer and spent model turns reaching generic not-found. It now reads the resolved target implementation once through the existing tool and returns the exact retained content as `as designed`, explicitly scoped to RETAINED_DEFINITION_ONLY: no numerical result, numerical cause, intended policy or business correctness is claimed. Existing verdict validation uses the retained static content and its immutable reference; missing contents, a proposal, a different target or changed bytes remain not-found. No new evidence type, guard framework, native query or expectation change. Focused calculation/cloud/investigator tests: 100 PASS plus 18 subtests. Independent dev grading remains pending; this is not a scored-success claim.
