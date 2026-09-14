# Native report definition evidence bundles

report_definition_evidence.py reads one finished retained metadata scan in a read-only SQLite
transaction, verifies asset content hashes, and constructs a report-scoped evidence bundle.
No definition text is executed and no network call or business query occurs.

The supported binding is a unique semanticmodelid in definition.pbir's byConnection connection
string. It must resolve to a SemanticModel under the same workspace in the same scan. Missing,
duplicate, byPath or unavailable model references remain unresolved; names are never a fallback.
A resolved binding means only that the retained explicit ID points to a retained model.

The bundle preserves all native report parts, raw filterConfig and visual queries from report,
page and visual definitions, and model descendants including DAX measure definitions and
relationships. Each asset retains its API source, capture time and content hash. The bundle
has a deterministic hash; this detects local changes, not a Microsoft provenance signature.

```powershell
python scripts/report_definition_evidence.py --database .local/metadata/report-definitions.sqlite --scan SCAN_UUID --report fabric://WORKSPACE_UUID/REPORT_UUID --output .local/report-bundle.json
```

Output creation refuses to overwrite an existing bundle. Missing report/page/model definitions
are explicit gaps. PARTIAL scans may still produce bundles, with scan status preserved. The
current gap list is not an exhaustive assessment of every Power BI feature or missing visual.
Absent filterConfig is not interpreted as unfiltered runtime state. Slicer state, bookmarks,
RLS, interactions, relationships and DAX evaluation remain outside this step. No classification
or routing is promoted; root_cause_verified and snapshot_comparable remain false.

Validation against live-captured scan 93324a35-8a2b-459e-a979-22b9bd75b03e resolved all three
reports by explicit model ID. Executive Sales yielded 15 definition context entries, Order
Operations 23, and Product Performance 14 (52 total, including report/page entries). No current
structural gap checks failed. Bundles are retained under
.local/report-definition-bundles/ae65178f-9d0d-4a81-b27e-3d8baa6831b9.

Five tests cover binding/filter/DAX retention, stable hashes, missing references, tampering,
missing model definitions, unfinished scans and duplicate model IDs with otherwise valid hashes.
Next: evaluate supported native filter and measure semantics against explicit ticket context,
and attach these bundles to the reviewed investigation workflow.
