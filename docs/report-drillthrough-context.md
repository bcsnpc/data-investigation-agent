# Native order drillthrough context check

The retained Order Operations report has a drillthrough page bound to FactOrder.order_id.
report_drillthrough_context.py checks that supported page requirement against explicit order
context. It uses a hash-verified native definition bundle and never evaluates DAX or executes
Power BI queries.

Supported shape: a single Drillthrough parameter whose boundFilter matches a single
Categorical filter, with both fields exactly FactOrder.order_id and no additional predicate.
The selected page must be present, the model binding resolved, and bundle gaps empty. Unknown
pages, unsupported definitions, missing binding and incomplete evidence return UNSUPPORTED.
Changed bundles and malformed order IDs are rejected.

Missing order context returns NEEDS_INPUT with required_context order_id. An explicit
ORD- plus six-digit ID returns CONTEXT_SUPPLIED. It does not establish that the order exists,
that the report received the filter, or that the resulting numbers are correct. Classification
remains UNRESOLVED and runtime_filter_verified/root_cause_verified remain false. Other
report/page filters, slicers, bookmarks, inherited context, relationships and RLS remain outside
this check. This is a context requirement check, not general native filter evaluation.

```powershell
python scripts/report_drillthrough_context.py --database .local/metadata/report-definitions.sqlite --scan SCAN_UUID --report fabric://WORKSPACE_UUID/REPORT_UUID --page definition/pages/PAGE_ID/page.json --output .local/drillthrough-check.json
```

Add --order-id ORD-000001 to supply order context. Output creation refuses overwriting.
Ticket planning can opt into this check with --page; native page selection in the review UI remains pending.

Validation: five tests cover missing/provided context, changed bundles, invalid order IDs,
unsupported page/binding, extra predicate and invalid filter shape. Against retained live scan
93324a35-8a2b-459e-a979-22b9bd75b03e, Order Operations page
53658f326e3e5e8790b3 produced NEEDS_INPUT without an order and CONTEXT_SUPPLIED with
ORD-000001. Artifacts: .local/drillthrough-context/8a40b268-9318-4b42-a27d-be11803660a2.
No new cloud calls, SQL, LLM or delivery occurred.

Next: attach this check to reviewed ticket context and broaden supported native filter/measure
semantics, retaining unresolved outcomes for unsupported definitions.
