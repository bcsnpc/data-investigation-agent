# Targeted report and model definition refresh

The existing metadata connectors already acquire native report definitions and TMSL model
parts. The new collect_report_metadata.py command selects 1?20 explicit Report/SemanticModel
UUIDs and refreshes only those items into an immutable SQLite scan. It performs no SQL catalog
scan, business query, model refresh, notebook execution or deployment.

Collection discovers workspace items, validates every selection before creating a scan, then
uses the existing definition extraction and model refresh-history paths. Native definition
parts, pages, visuals, model tables, columns, measures (including DAX) and relationships are
retained with source endpoints, timestamps and content hashes. Selecting a report does not
automatically select a model: association must be resolved and verified separately.

Use --item repeatedly and a dedicated output database:

```powershell
python scripts/collect_report_metadata.py --database .local/metadata/report-definitions.sqlite --item REPORT_UUID --item MODEL_UUID
```

The command uses configured Fabric CLI authentication with interactive renewal disabled.
Credentials are not stored in the scan. Existing connector handling records redacted capability
failures; one failed definition yields PARTIAL while other selected definitions remain available.
COMPLETE refers only to the selected metadata capabilities, never full-estate coverage. Repeated
calls append scans and preserve prior snapshots. No latest full-estate scan pointer is changed.

Four tests verify retained measure expressions and call scope, partial failure/redaction,
invalid selections and preservation of prior scans. No production findings are promoted:
snapshot_comparable and report_model_association_verified remain false.

Next: build evidence bundles from these native definitions, resolve report-to-model bindings,
and evaluate report/page/visual filters and measures against explicit ticket context.


Live verification: scan `93324a35-8a2b-459e-a979-22b9bd75b03e` in
`.local/metadata/report-definitions.sqlite` completed with zero unavailable capabilities:
3 reports, 4 pages, 45 visuals, 1 model, 6 semantic tables, 102 columns, 25 measures,
5 relationships and 67 definition parts. All 259 stored asset hashes verified. These are
fresh native API definitions, not simulated lab definitions. The scan did not refresh the
model or query its business data, and does not prove snapshot comparability.
