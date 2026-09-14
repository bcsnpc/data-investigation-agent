# Reviewed report-scope API

The local report-scope replay now uses the existing ticket, plan review and finite worker
workflow. This mode is API-only; it does not expose the generic lab UI as a report-scope UI.

The supported report is `Lab All Orders vs Excluded Partial Returns`, with metric Net Cash,
currency USD and all orders. Its distinct report and lineage IDs identify the fixed comparison:
requested all_orders versus simulated exclude_partial_returns. Ticket narrative does not
select arbitrary filters, and no LLM interprets it. Other report names require clarification.

A fresh review folder is bound to this mode and resolved lab path. Reusing two-layer or
three-layer approvals, changing the source path, or selecting conflicting modes is rejected.
Only an approved child ticket executes; the original intake remains queued. Acquisition
reads both projections in one transaction and rejects non-USD rows before storing a finding.

Run with INVESTIGATOR_API_TOKEN already set locally to at least 32 ASCII characters:

```powershell
python scripts/serve_report_scope_review.py --lab .local/defect-lab/lab.duckdb --review-folder .local/report-scope-review --port 8775
```

Use the existing authenticated API sequence: POST /api/tickets, POST /api/tickets/{id}/plan,
GET /api/plans/{id}, POST /api/plans/{id}/approve with the displayed plan_hash and confirm true,
then GET the completed child ticket and /api/investigations/{investigation_run_id}.
POST ticket/plan requests use unique Idempotency-Key values. The worker processes one approved
job within its existing 15-minute session; restart for another session.

The saved result reports MISMATCH and USD -99 for the baseline fixture. Classification remains
UNRESOLVED, root_cause_verified and automatic routing remain false. It proves a local filter
effect, not the behavior or provenance of a deployed Power BI report. No live delivery occurs.

Four tests exercise authenticated plan/approval/execution and evidence retrieval, idle behavior
before approval, mode/source binding, conflicting modes and rejection of unapproved currency.
The lab baseline remains READY after normal execution.

Remaining: dedicated UI/evidence presentation, actual report/measure API acquisition, live
snapshot comparability and deployed cause verification.
