# Reviewed plan handoff and evidence summaries

Issue #55 builds on live planning from PR #54, merged at
`06ceda3dcfeb76ab78afe0514499ea87c063399d`.

The operator inspects a stored draft and explicitly approves its complete scope:

```powershell
python scripts/review_ticket_plan.py --plan-id <plan-uuid>
python scripts/review_ticket_plan.py --plan-id <plan-uuid> --approve --reviewer <operator-label>
python scripts/ticket_worker.py
```

Approval validates the draft again against the pinned report catalog, verifies
its input hash and prompt version, and requires the configured lineage to still
match. Failed drafts, unanswered questions and changed context are rejected.
The reviewer must assess semantic correctness, including filters the model may
have missed. The reviewer label is an operator assertion, not an authenticated
identity; production identity and review UI remain pending.

One SQLite transaction creates a new explicit-scope ticket, its provenance event
and a `plan_approvals` row linking the original ticket, plan hash and reviewer.
Repeated or concurrent approval of the same unchanged draft returns the same
child ticket. The original ticket and evidence are retained. The existing worker
claims queued tickets separately and still applies deterministic lineage and
comparison gates. Approval does not invoke the model or execute a query itself.
It is local CLI only; the HTTP API does not expose approval yet.

Investigation detail responses now include a deterministic `summary` containing
the recorded classification, exact observed values, boundary statuses and JSON
pointer references into the original evidence. Unavailable values remain null;
NOT_COMPARABLE and INSUFFICIENT_EVIDENCE remain explicit. This rendering adds no
root-cause conclusion and never enables defect routing. It is generated from
stored evidence on read, without a model call. LLM-written narrative explanations
are deferred until their factual claims can be validated; this release provides
the evidence-grounded summary and reviewed execution handoff.

Validation covers concurrent approval, stale lineage/catalog rejection,
unanswered-question rejection, exact decimals, partial-evidence summaries and
existing HTTP evidence endpoints. Existing worker and generator checks also run.
SQL transient retries and automatic requeue remain separate follow-ups.

## Live verification

Approved existing reviewed draft 23bb6549-aebf-404d-87d9-cc3adb940d43 as local session operator, creating child ticket af8d5a78-e7cb-433f-82ef-23f63bc0bde5. Repeating approval returned that same ticket. Worker run d70036f1-9288-4f52-9a0a-411ee57b5c03 completed. A real authenticated HTTP request retrieved all ten observations and eight boundary references in the summary; the temporary server was stopped. Bronze, Silver, Gold and semantic observed 100,000 orders and USD 64,892,824.49. SQL returned connection error 40613; partial evidence stays UNRESOLVED. Six handoff/summary tests, six API tests, six workflow tests and two generator tests passed. No business writes occurred.
