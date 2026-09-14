# Slicer context in reviewed planning

Tickets may now carry native_slicers alongside native_page. The map uses retained visual IDs
and explicit all or categorical string selections, with bounded size and strict validation.
It is persisted as part of the existing immutable ticket body and idempotency hash; changing
choices under the same request key conflicts. The authenticated ticket API accepts it, while
UI controls for entering slicer choices remain pending.

```json
{
  "title": "Cash discrepancy",
  "report": "Order Operations",
  "description": "Investigate the selected report context",
  "native_page": "definition/pages/PAGE_ID/page.json",
  "native_slicers": {"VISUAL_ASSET_ID": {"mode": "values", "values": ["2026-09"]}}
}
```

For a selected native page, planning now retains slicer-context evidence from the lineage scan
in addition to the drillthrough check. Missing choices produce clarification. Supplied choices
are retained but the draft remains NEEDS_INPUT: existing workers do not execute native slicer
filters. Unsupported native definitions are also held. No selection is silently translated
into a query or inferred as all values.

Approval rejects plans containing slicer requirements or explicit nonempty selections. The
worker independently rejects a ticket with nonempty native_slicers before any acquisition,
including direct queued tickets. Existing no-slicer page workflows retain their prior behavior.
This is context intake and an execution guard, not completed native filter execution.

Five tests cover missing context, retained supplied context, approval holds, direct worker
rejection before execution, bounded validation and idempotency conflicts. No cloud, SQL
business queries, LLM, delivery or browser operations occur in this step.

Next: implement supported categorical filtering with comparable evidence, then enable approval
for that explicitly supported execution scope. Add slicer entry controls to the review UI.
