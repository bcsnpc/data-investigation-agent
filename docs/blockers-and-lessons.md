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
