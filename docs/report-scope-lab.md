# Local report-filter scope lab

This step simulates a report filter over the shared Gold lab. It does not execute DAX,
read Power BI report definitions, or verify a deployed semantic model.

`report_scope_lab.py` reads both supported projections in one read-only DuckDB transaction:
all orders and orders excluding PARTIALLY_RETURNED. Requested scope is explicit operator
input; missing scope is never inferred. SQL comes only from the fixed repository mapping.
The existing record reconciler compares keys, currencies, presence and four-decimal amounts.
The module saves captured projections, scope, evidence hash and result in investigation_runs.

| Requested scope | Simulated report | Result | Cash gap USD |
| --- | --- | --- | --- |
| All | All | MATCH | 0 |
| All | Exclude partial returns | MISMATCH | -99 |
| Exclude partial returns | Same exclusion | MATCH | 0 |
| Missing | Exclude partial returns | NOT_COMPARABLE | Not calculated |
| Exclude partial returns | All | MISMATCH | +99 |

A replayed scope mismatch sets local_filter_mismatch_verified, but classification remains
UNRESOLVED and root_cause_verified remains false. This establishes a local filter effect,
not deployed report provenance or business intent. Matching scope also does not establish
full business correctness. Automatic routing remains false. The fixed all-orders versus excluded-partial-returns comparison is also available through
the reviewed ticket API; a dedicated report-scope UI remains pending.

Run against an existing isolated lab (never a live SQL connection):

```powershell
python scripts/report_scope_lab.py --lab .local/defect-lab/lab.duckdb --database .local/report-scope/evidence.sqlite --requested-scope all_orders --report-scope exclude_partial_returns
python -m unittest discover -s scripts -p test_report_scope_lab.py
```

Five tests cover missing/invalid context, matched and mismatched scopes, reverse impact,
persisted evidence and unchanged baseline. The five-case local evaluation passed with
baseline READY in `.local/report-scope-evaluations/e635cd79-4660-43c4-9185-c457784a569a/report.json`.
No cloud, LLM or delivery calls were made.

Next: ingest actual report/measure definitions and context through the connected APIs,
then establish provenance and snapshot comparability before promoting a live cause.
