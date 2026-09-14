# Bounded categorical filter replay

categorical_filter_replay.py executes explicit choices over an isolated Silver/Gold capture.
It accepts a verified native definition bundle and complete selections for one page, restricted
to FactOrder.order_id, currency and status. Every slicer must use one of those fields, including
all-values choices. No SQL comes from a model, report definition or user selection.

Silver and Gold reconciliation rows plus Silver status attributes are read in one DuckDB
transaction. The full capture is validated before filtering, so excluded malformed records do
not disappear from validation. Predicates use exact case-sensitive strings: OR within a slicer's
values, AND across slicers. Explicit all adds no predicate. Status values come from Silver and
are applied to both compared sides; this is a local contract, not semantic relationship inference.

Selected rows are reconciled by order/currency. Empty matches return NO_MATCHES/UNRESOLVED,
not success or expected behavior. Currency totals stay separate. Missing source attributes for
a requested predicate, duplicate records, unknown fields or incomplete selections fail closed.
Results, full capture, status attributes, selected row indices, native context and an evidence
hash are persisted in investigation_runs. Root cause and Power BI runtime verification remain
false. Existing production planning/worker slicer holds remain active.

```powershell
python scripts/categorical_filter_replay.py --lab .local/defect-lab/lab.duckdb --metadata .local/metadata/report-definitions.sqlite --scan SCAN_UUID --report fabric://WORKSPACE_UUID/REPORT_UUID --page definition/pages/PAGE_ID/page.json --selections .local/selections.json --database .local/categorical-evidence.sqlite
```

Use only an isolated lab. This command does not acquire live rows, apply Power BI collation,
evaluate DAX, resolve dimension relationships, reproduce RLS or prove snapshot comparability.

Seven tests cover OR/AND behavior, selected defect impact, empty results, evidence persistence,
unsupported/missing choices, currency separation and duplicate records before filtering.
Retained native Order Operations detail definitions selected ORD-000001/USD from a fresh local
lab: baseline MATCH at 99/99; injected double-refund MISMATCH at 99/0, impact -99. Reset READY.
Artifact: .local/categorical-replay/7368a4ca-5354-49a1-9454-71aa5139c014/report.json.
No new cloud, SQL business queries, LLM or delivery calls.

Next: connect this bounded replay to an explicitly reviewed local execution mode, then establish
live acquisition/filter equivalence before enabling production slicer execution.
