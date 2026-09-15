# Catalog-driven source diagnostics

This grouped Phase D continuation follows merged PR #156 and is tracked by [#157](https://github.com/bcsnpc/data-investigation-agent/issues/157). It adds actual upstream Azure SQL observations through resolved metadata IDs. It does not certify equivalence between a SQL aggregate and a semantic measure.

## Implemented contract

- Resolve SQL objects and columns from the model context's pinned scan. Verify retained metadata hashes and SQL catalog visibility. Require the configured workspace, SQL server/database and allowed schema.
- Admit only user tables, `count_rows`, and `sum` of exact numeric columns. Reject views, computed columns, unknown objects, foreign columns and arbitrary query fields. SUM casts to decimal(38, captured scale), with supported scale 0-18.
- Require 1-8 explicit string-column filters, up to 50 values each. Values use SqlClient parameters, never SQL string interpolation. Unicode values are bounded by UTF-16 parameter capacity. SQL numeric/date/boolean filters are not yet implemented; native Power BI typed filters are a separate contract.
- Execute one SELECT aggregate with MAXDOP 1, a 30-second connection timeout, 30-second command timeout and 90-second worker timeout. There are no joins, stored procedures, remote functions, writes or automatic retries. These limits do not guarantee a fixed scan cost or remaining Azure quota.
- Keep credentials in the configured local credential file. The PowerShell helper is an internal compiler transport, not an exposed arbitrary-query API. ApplicationIntent is ReadOnly; actual permission enforcement still depends on the configured database identity.
- Persist RUNNING before dispatch, then typed value, row count and nonblank count. SUM over no nonblank rows remains BLANK; count remains an integer value. Reject inconsistent responses. Context changes during a read hold its result.
- Preserve interrupted/failed reads without inventing numbers. Timeouts, including SQL timeout code -2, are INTERRUPTED. Error records include only a bounded error type and optional SQL number, never exception text or credentials. A crashed RUNNING receipt is not automatically resumed.

The receipt pins scan, object/catalog/context/scope and configured-connection hashes. These are metadata/request references, **not remote data-version proof**. Remote schema changes since the scan remain possible. Every result leaves snapshot comparability, measure equivalence and root cause false.

## Use

Discover eligible object and column IDs without querying business rows:

```powershell
python scripts/run_source_diagnostic.py --config infra/metadata/development.json --database .local/catalog.sqlite --environment development --catalog-model-id YOUR_REGISTERED_MODEL_ID
```

Save a plan under `.local/` using the returned IDs and current model revision/context:

```json
{
  "model_id": "registered-model-id",
  "revision": 5,
  "context_id": "current-context-id",
  "object_id": "retained-sql-object-id",
  "operation": "count_rows",
  "column_id": null,
  "filters": [{"column_id": "retained-currency-column-id", "values": ["USD"]}]
}
```

For SUM, set `operation` to `sum` and supply the exact numeric column's ID. Invoke one read explicitly:

```powershell
python scripts/run_source_diagnostic.py --config infra/metadata/development.json --database .local/catalog.sqlite --environment development --plan .local/source-plan.json --approve
```

The catalog database's `source_diagnostics` table retains receipts. Admin-only GET routes under `/api/v2/admin/models/{id}/source-diagnostics` list the latest 100 receipts; append `/{receipt_id}` for one historical result. Model/environment scoping is enforced. The API does not dispatch SQL.

## Verification

The full regression suite passed: **427 tests**. The focused source suite also passed after the timeout/error detail update. Ten tests cover parameterization, metadata/connection gates, invalid plans, SUM null semantics, response validation, UTF-16 bounds, pre-dispatch receipts, stale context, timeout classification and evidence authorization. The PowerShell script passed syntax validation.

Live Azure SQL validation used the existing local diagnostic test catalog:

- Initial count attempt failed: receipt `407497d8-0c0f-4397-8b75-bb722fe04527`. Its original error detail was insufficient to determine the cause; it is not relabeled as confirmed auto-pause.
- A separate count invocation succeeded: **100000** orders for currency USD, receipt `165f9905-8bcc-4021-bf16-0c6910695535`.
- SUM of `total_amount` for that scope succeeded: **69713713.6800**, with 100000 rows/nonblank values, receipt `12026488-edc3-4116-9601-c3d53a3dc3c3`.

These receipts are retained in `.local/model-admin-verify/native-diagnostics.sqlite`. No SQL data, schema, tier or quota settings were changed. No LLM call was needed. No claim of comparison to Power BI or business correctness follows from these reads.

## Still pending

Authoritative measure-to-source mappings, aligned grains/filter/date/BLANK contracts, wider typed source scope, schema/version proof, cross-system snapshot comparability, key/record diagnostics, equivalence verification, durable budget/recovery and the adaptive planner remain open. This tool supplies source observations for that work; it does not close D/E.
