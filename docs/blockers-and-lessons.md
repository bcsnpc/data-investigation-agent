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
