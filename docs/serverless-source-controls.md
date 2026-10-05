# Serverless source controls and worker diagnostics

Dated 2026-10-05 UTC. Round Five E section 4; known-domain evaluation only.

Source policy is resolved from exact compiled asset IDs against manifest layers.
`serverless` defaults false. Application workers retain the existing 90-second
fallback; this fixture declares 240 seconds. Fabric SQL retains its existing
150-second fallback unless the layer explicitly declares a worker deadline.
Neither deadline changes the investigation's total deadline or any read cap.

Only connect-stage SQL 40613 on a declared serverless source enables the new
resume path: waits of 5, 10, 20 and 25 seconds, at most five attempts. Each attempt
needs fresh physical admission and remains in the connection receipt, labelled
"source paused; waiting for resume". Query failures and arbitrary OSError are
not retried. Undeclared sources retain the existing published-transient policy.
Microsoft documents the initial 40613 and typically approximately one-minute
resume latency; these waits do not guarantee availability or distinguish free
quota exhaustion from every other reason for 40613.
[Serverless FAQ](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-faq?view=azuresql)
and [auto-pause/resume](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-auto-pause-resume?view=azuresql).

The connection-only pre-warm has no SQL statement. Its physical attempts and
resume waits are explicit controls, never investigation diagnostic reads. It
uses the existing source reader, not an owner or publisher. The batch controller
must supply admission and ledger callbacks; a source without a declaration is
refused before connecting. All physical attempts still consume the rolling and
Round Five allowances; waits consume no physical slot.

Worker failures now preserve type, safe OS reason, errno, module and line.
Filename attributes and exception locals are not serialized. Stream pipe failures
and actual timer expiry have distinct recorded events and replay without new
workers/timers. Every new streaming worker records its configured deadline.
Legacy streaming tapes lacked that field: replay retains their original bytes
and cannot assert a retrospective timer-expiry event. The old source failure's
90-second timer is established from the transport used, not proof it fired.
It followed successful guards; its missing OS reason remains unknown.

Six dedicated offline tests cover bounded waits, connect-only eligibility,
control-only accounting, exact asset policy, OSError retention/replay and timer
expiry/replay. Other focused checks passed: 8 SQL retries, 24 tapes, 19 manifest,
6 process failures, 6 physical binding and 18 read-budget tests. Context coverage
remains 2 entries / 1 SQL entry / 7,540 characters in the golden-view test.
No live run or cloud request in the implementation milestone. Round Five remains
218/400; diagnostic cap12 and rolling1500 unchanged. The manifest change requires
current discovery approval before the list; no gate bypass. Engine bytes changed,
invalidating previous freezes. #376 remains draft until strict 15/15 acceptance.
