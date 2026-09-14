# Native slicer context

report_slicer_context.py identifies supported column slicers from one retained page's native
visual definitions. It verifies the bundle hash, resolves each slicer's single Column projection
to a retained semantic table/column, and preserves the visual identity and definition hash.

Each selection is keyed by visual asset ID. An absent selection means unknown context and
returns NEEDS_INPUT, not an implicit all-values filter. Supported explicit choices are:

```json
{"VISUAL_ASSET_ID": {"mode": "all"}}
```

or categorical strings:

```json
{"VISUAL_ASSET_ID": {"mode": "values", "values": ["2026-09"]}}
```

Null, empty/duplicate values, unknown visual IDs and unsupported selection modes are rejected.
Multi-field, unresolved-column and unsupported field projections return UNSUPPORTED. Explicit
context returns CONTEXT_SUPPLIED, never runtime verification. A page without captured native
slicers returns NO_SLICERS_CAPTURED, which does not prove an unfiltered report.

```powershell
python scripts/report_slicer_context.py --database .local/metadata/report-definitions.sqlite --scan SCAN_UUID --report fabric://WORKSPACE_UUID/REPORT_UUID --page definition/pages/PAGE_ID/page.json --output .local/slicer-check.json
```

Optionally add --selections with a local JSON file. Output never overwrites an existing file.
This CLI is not yet connected to ticket planning or the UI. It does not validate value existence,
convert data types, apply filters or execute DAX. Other filters, custom visuals, bookmarks,
relationships and RLS remain outside scope; classification stays UNRESOLVED.

Six tests cover missing and explicit context, invalid choices, unresolved columns, no slicers,
wrong page and tampered evidence. Evaluation against retained native scan
93324a35-8a2b-459e-a979-22b9bd75b03e found 14 slicers across four pages (4/2/4/4).
Every page returned NEEDS_INPUT with missing choices and CONTEXT_SUPPLIED with explicit all
choices. These all choices were evaluation inputs, not observed user selections. Artifact:
.local/slicer-context/3ac50f22-2594-46e4-b153-6a0ac16b4b7a/report.json.
No new cloud, SQL business queries, LLM or delivery calls.

Next: collect explicit slicer choices in the reviewed ticket workflow and evaluate supported
native filter/measure semantics against comparable observations.
