# Typed diagnostic scope

This grouped D/E continuation follows merged PR #154, tracked by [#155](https://github.com/bcsnpc/data-investigation-agent/issues/155). Native diagnostics now accept metadata-bound date, integer, fixed-decimal, boolean and explicit BLANK filters in addition to the existing string-list format. No metric names or table paths were added to runtime dispatch.

## Request contract

The existing plan fields and budgets still apply. A typed filter has exactly `column_id`, `operator` and `values`; the column ID must resolve inside the pinned model context. The caller cannot override its type.

| Catalog data type | `in` values | `range` endpoints |
| --- | --- | --- |
| `string` | JSON strings; null explicitly selects BLANK | Unsupported |
| `int64` | JSON integers within +/- (2^53 - 1), or null | Two increasing integers |
| `decimal` | Decimal strings, up to four decimal places and absolute value 1,000,000,000, or null | Two increasing decimal strings |
| `boolean` | JSON true/false, or null | Unsupported |
| `dateTime` | ISO `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`, or null | Two increasing model-local dates/times |

Example filter list (replace the illustrative IDs with discovered IDs):

```json
[
  {"column_id": "currency-column-id", "operator": "in", "values": ["USD"]},
  {"column_id": "date-column-id", "operator": "range", "values": ["2026-01-01", "2026-02-01"]},
  {"column_id": "amount-column-id", "operator": "range", "values": ["0.0000", "1000.0000"]},
  {"column_id": "flag-column-id", "operator": "in", "values": [true]}
]
```

Ranges include their lower endpoint and exclude their upper endpoint. They explicitly exclude BLANK, avoiding DAX comparison coercion. One predicate contains both bounds, and duplicate filters on one column are rejected. `in` uses TREATAS; range uses FILTER over ALL of the single resolved column. Parent/dependency and dimension requests share this compiler.

Ambiguous/localized dates, timezone offsets, fractional seconds, invalid calendar dates, reversed/equal ranges, implicit numeric conversions, duplicate values and unknown types fail admission. Dates before 1900 are unsupported. No timezone, date role or business period is inferred.

Fixed-decimal input uses CURRENCY with tighter diagnostic literal limits than the model's storage capacity, avoiding precision loss from large literals. Microsoft documents [CURRENCY conversion and rounding](https://learn.microsoft.com/en-us/dax/currency-function-dax) and the distinction between [Power BI numeric types](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-types). Binary floating-point (`double`) columns remain unsupported by this filter contract.

## Discovery, compatibility and evidence

`GET /api/v2/admin/models/{id}/scope` returns column IDs, metadata types, supported operators and literal limits. Existing admin role/environment boundaries apply. The existing dry-run `/assess` route validates typed plans without running a query. Execution continues through the explicit operator CLI.

Typed requests retain `filter_scope_version=typed-scope-v1` in their receipt and request hash. Legacy `{column_id,values}` string filters keep their existing query/request shape; old evidence remains readable. The v2 ticket workflow and browser controls are unchanged.

All reads still leave visual-context reproduction, date-role/effective-identity certification, remote definition stability, snapshot comparability and root cause unverified. A valid filter is not proof that it represents the user's intended report context.

## Validation

The full regression suite passed: **417 tests**. Ten focused tests cover type boundaries, exact inputs, date validation, BLANK distinctions, half-open ranges, duplicate rejection, escaping, scalar/dimensional integration, legacy compatibility and scope API access. CI includes the suite.

Two live Power BI calls on the existing local diagnostic test catalog succeeded:

- Date window 2024-01-01 through exclusive 2027-01-01, USD, units [1,1000) and sales amount [0,1000000): Average Order Value 651.9948, Funded Orders 97527, Sales Amount 63587096.7. Receipt `279c9209-0f05-4ce8-856c-d0e2e4bfa8a6`.
- Replacing that date window with [2040-01-01,2041-01-01): all three native values were BLANK and retained as BLANK. Receipt `60be0fa1-1f1e-42e9-9dea-ebc3569a7ae2`.

These test receipts remain under `.local/model-admin-verify/native-diagnostics.sqlite`. They demonstrate observed scoped reads, not a certified business result. No SQL query, model mutation or LLM call was made by these checks. Boolean/explicit-BLANK filter construction is unit-tested; it was not separately live-tested against a boolean column.
