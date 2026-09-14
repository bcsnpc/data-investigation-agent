# Automatic explanations and related tickets

The local background worker can generate an explanation after completing an approved
investigation. Enable it explicitly when starting the server:

```powershell
python scripts/serve_investigations.py --enable-tickets --enable-plan-review --enable-planning --enable-worker --enable-explanations --worker-max-jobs 1 --worker-max-seconds 900
```

Set the operator token first as described in [review UI](investigation-review-ui.md).
The worker performs at most one automatic explanation attempt per completed run.
It reuses a validated saved explanation when one already exists. Otherwise the existing
Azure launcher makes one model call with a 130-second subprocess timeout. The configured
SQL investigation budget is unchanged: explanation generation uses saved evidence only.

Automatic request state is durable in `explanation_requests` in workflow.sqlite.
Concurrent requests share the same run key. FAILED requests are not retried automatically;
a crash can leave RUNNING, which is held for operator inspection. Explicit operator CLI
generation remains available for recovery after inspecting uncertain provider outcomes.
That manual action does not rewrite the original automatic request history.

The returned explanation ID must match a persisted, locally validated explanation for
the saved evidence. Model failures do not alter the ticket's completed evidence or
classification. Worker status includes `last_explanation`; the UI displays the validated
explanation after refreshing the completed ticket. Completion can appear before its
explanation is ready. Disabled automatic explanations leave the existing workflow intact.

This callback applies to runs completed by the current worker session. There is no
automatic historical backfill or restart recovery of explanations missed between job
completion and request creation. Graceful shutdown finishes the active investigation
and its explanation callback; forced shutdown can leave an uncertain request.

Ticket detail now includes up to 20 recent related approval links with their current
statuses. The UI lets operators navigate from an original ticket to each investigation,
and back. It retains each ticket's own status and timeline: an original NEEDS_INPUT or
QUEUED ticket is not relabeled COMPLETED when its child completes. Multiple approved
scopes remain visible as separate investigations. Older links remain accessible through
the paginated draft list when the related list is truncated.

Validation covers concurrent and interrupted requests, reuse, failure isolation,
persisted-result verification, noncompleted jobs, and linked ticket history. Browser
verification uses saved real tickets; an existing validated explanation was reused
without another model call. Automatic cloud generation itself continues to use the
previously live-validated Azure launcher; this step does not claim a new end-to-end
cloud acquisition run.
