# Native drillthrough context in ticket plans

The planner accepts an optional native page path. It checks the supported order drillthrough
requirement using the same metadata scan referenced by the ticket's lineage run, then retains
the result and bundle hash inside the saved draft. This option is explicit; existing planners
without a selected page keep their prior behavior. The hosted UI does not select a page yet.

Only an explicit ticket order_id satisfies the requirement. An LLM-inferred ID does not:
the saved plan remains NEEDS_INPUT and cannot be approved. Unsupported page definitions also
remain NEEDS_INPUT with the check reason. Invalid/missing metadata fails planning closed.
The original ticket remains unchanged, so supplying missing context requires a new ticket/plan.

With explicit valid context, the plan remains DRAFT_REQUIRES_REVIEW. Approval rebuilds the
native check from the configured metadata database and lineage scan and compares it with the
saved check before creating a child. Changed or unavailable evidence requires a new plan.
The existing reviewed-plan hash and transaction checks remain in place.

```powershell
python scripts/ticket_planner.py --ticket-id TICKET_UUID --config infra/metadata/development.json --page definition/pages/PAGE_ID/page.json
```

This command retains the planner's existing opt-in Azure LLM call. Configure its credentials
locally as before. The tests in this step inject a deterministic provider; no LLM was called.
The page must exist in the ticket lineage's scan. A newer targeted definition scan is not
silently substituted for that scan.

Approval authorizes the existing bounded metric/order data checks. It does not execute the
Power BI report, apply its full filters, verify order existence or establish DAX correctness.
The check is revalidated at approval, not continuously at worker execution. Runtime report
verification and dedicated page selection in the UI remain pending.

Five tests cover missing explicit context, inferred context, explicit order approval, changed
metadata after planning and incorrect lineage scan. No cloud, SQL business query, LLM or
external delivery was performed. Next: expose native page selection in the reviewed workflow
and expand native filter/measure evaluation with retained evidence.
