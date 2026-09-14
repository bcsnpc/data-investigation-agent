# Bounded local background worker

Start the existing local review server with an optional worker. Set the local operator
token as described in [review UI](investigation-review-ui.md), then run:

```powershell
python scripts/serve_investigations.py --enable-tickets --enable-plan-review --enable-planning --enable-worker --worker-max-jobs 1 --worker-max-seconds 900
```

Approve the proposed scope in the UI. The background thread polls the local queue every
five seconds and runs only a queued child ticket linked to a saved approval. The original
narrative ticket remains unchanged. Refresh the child ticket to see RUNNING, COMPLETED,
NEEDS_INPUT or FAILED and its saved evidence. COMPLETED does not mean the issue is resolved.

The default session claims at most one ticket, within a 15-minute window. Limits can be
set to 1–10 jobs and 1–3,600 seconds. The time limit stops new claims; it does not interrupt
an active bounded acquisition. All non-idle outcomes count toward the job limit. Once
the limit is reached, the API stays available and additional approved tickets remain
queued. Restart the server deliberately to begin a new worker session.

Authenticated `GET /api/worker` exposes status, processed count, configured limits and
the last ticket result. It returns 404 when the worker is disabled. Status is local to
the current server process; it is not a durable scheduler history. The ticket timeline
and evidence remain durable. There is no HTTP restart or limit-changing endpoint.

Ctrl+C stops polling and waits for active work to finish. Forced termination can leave
a RUNNING ticket with an uncertain outcome. The background worker never automatically
reclaims expired leases or retries terminal tickets; inspect their evidence before an
operator recovery. The existing one-shot CLI retains its explicit expired-lease recovery
behavior. Existing connection-stage SQL 40613 retry limits still apply within a run.

Worker execution occurs separately from the HTTP thread. Current model planning requests
still occupy the synchronous HTTP server while generating drafts. Explanation generation
remains the explicit operator CLI from [grounded explanations](grounded-explanations.md);
automatic explanation scheduling and parent/child status consolidation are follow-ups.

Run one server instance for a workspace. Claim transactions prevent two workers claiming
the same queued ticket, but session budgets are per process and reset on restart. This
is opt-in local orchestration, not a deployed unattended service. It never changes SQL
free-limit, AutoPause or overage settings and performs no polling queries against Azure
SQL or Fabric while idle.

Validation: approved plan → transactional child → background execution → persisted
completion is tested using the real queue and handoff with a simulated cloud adapter.
Tests also cover job/time limits, unapproved tickets, expired claims, active shutdown,
sanitized failures and status endpoint authentication. No new live SQL/Fabric/LLM calls
were needed for these orchestration tests.
