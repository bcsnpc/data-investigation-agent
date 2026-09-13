# Gold reporting contract

Tracking: FAB-003 (#13). Gold is published by `nb_ordersops_silver_to_gold` into
`lh_investigator_gold`. Source SQL lives in `infra/fabric/gold_models.py`; the
Spark execution and validation code is `infra/fabric/silver_to_gold.py`.

## Reporting tables and grains

| Table | Unique key | Purpose |
|---|---|---|
| order_summary | order_id | Order-level totals, customer, status, funding and return indicators |
| order_line_summary | order_line_id | Product drill-through and original-line financial/quantity reconciliation |
| sales_daily | order_day, currency | Daily order-cohort totals and order counts |
| sales_by_customer | order_day, currency, customer_id | Customer/day cohorts with location and segment |
| sales_by_product | order_day, currency, product_id | Product/day cohorts with category and subcategory |
| refund_summary | refund_id | Refund event, original order, payment, refund date and merchandise/tax split |

The five reporting tables from the specification are implemented; the additional
line summary preserves a direct route from product aggregates to source lines.
No Power BI semantic model or report is created by this notebook.

## Metric definitions

An order is funded when Silver captured_amount is positive. Validation requires
funded captures to equal the original order total. Unpaid cancellations and
PENDING_PAYMENT orders contribute zero sales/cash but remain in order counts.
Paid cancellations preserve their original capture and full refund; their net
sales, tax, cash and units must all be zero. Gross funded activity includes these
orders, so cancellation does not erase actual payment/refund history.
Payment attempts are not joined to raw order lines; failed attempts cannot
inflate sales. Refund lines are aggregated before joining to order lines.

| Metric | Definition |
|---|---|
| gross_sales_amount | Funded merchandise before item/coupon discounts, excluding tax |
| discount_amount | Both source discounts for funded purchases |
| sales_amount | Funded merchandise after discounts, excluding tax and before returns |
| tax_amount | Original tax on funded purchases |
| captured_amount | Funded payable amount including tax |
| refunded_sales_amount | Original discounted merchandise returned |
| refunded_tax_amount | Original tax refunded |
| refund_amount | Refunded merchandise plus refunded tax |
| net_sales_amount | sales_amount minus refunded_sales_amount |
| net_tax_amount | tax_amount minus refunded_tax_amount |
| net_cash_amount | captured_amount minus refund_amount |
| units_ordered | All original line quantities, including cancelled/unpaid orders |
| units_sold | Original quantities on funded orders, before returns |
| units_returned | Sum of refunded line quantities, including paid cancellations before shipment |
| net_units | units_sold minus units_returned |

`order_summary.order_amount` is the original application total, including tax
and including cancelled/unpaid order values. It is retained for investigation,
not used as sales. These explicit names replace the draft's ambiguous Revenue /
Net Revenue aliases. The project has not defined accounting revenue recognition.
Money uses SQL decimals, with no floating-point percentages or reallocation.

Sales tables use original order_day (UTC): subsequent refunds are attributed back
to that order cohort. They are not a calendar cash-flow statement. For refund-date
reporting, aggregate refund_summary.refund_day and do not also add the sales-table
refund measure. There is no daily payment-date cash-flow table in this release.

Order counts are additive across sales_daily and sales_by_customer keys within
a currency. Product order counts are distinct within a product/day only; an order
containing multiple products can appear in multiple product rows. Never sum these
to get overall order count. Compute averages as ratios of relevant totals (for
example sales_amount / funded_order_count), not averages of group averages. Keep
currencies separate; no exchange-rate conversion is provided.

`has_return` and `returned_order_count` mean an order has a refund, including a
paid cancellation. Likewise, `units_returned` includes cancelled quantities
refunded before shipment; these fields do not claim a physical warehouse return.

## Readiness and provenance

The notebook requires the Silver latest report to be READY, checks all seven
consumed tables for expected counts, non-null unique keys and a single matching
Silver run ID, and pins each table to a Delta version. It checks that Silver's
report and versions remain stable before publication.

Before writing Gold, it verifies each output grain, per-order financial identities,
refund totals, nonnegative line amounts/quantities, full cancellation reversal, all
aggregate money/quantity totals by currency, additive order counts, and independent
captured-payment totals. After each write it compares persisted row counts and the
full row multiset with the intended output, including provenance columns.

Every Gold row has `_gold_run_id`, `_silver_run_id`, `_processed_at_utc` and a
`_silver_versions` map. Reports in `Files/validation/<run_id>.json` and `latest.json`
record source/processing run IDs, versions, counts, currency totals and checks.

Delta overwrite is atomic per table, not across all six. The latest report becomes
RUNNING before writes, READY after all checks, and FAILED if publication fails.
Consumers must require READY and matching row run IDs. Run serially; no distributed
job lock or recurring refresh schedule is implemented. A failed partial publication
must not be treated as a valid reporting snapshot.
Prepublication reconciliation failures save sample records in
`Files/validation/<run_id>-failure.json` and `last-failure.json`; they do not
replace an earlier valid snapshot's READY report.

## Deploy, run and test

```powershell
python scripts/deploy_gold_notebook.py
& ".local/fabric-cli-env/Scripts/fab.exe" job start "ws-investigator-dev.Workspace/nb_ordersops_silver_to_gold.Notebook"
```

This uses the existing enterprise Fabric login and environment IDs. No SQL admin
credentials are used, and Silver/Bronze business records are not changed.

Local tests execute the same SQL using DuckDB and independently calculated
fixtures, including multiple refunds against one line, repeated products within
an order, both discount types, cancelled/unpaid orders, separate currencies, and
refund dates different from original order dates. These deliberately include more
complex return shapes than the current baseline. Fabric execution verifies the
queries and decimals on the actual Spark engine and data.

```powershell
python -m pip install -r scripts/requirements-fabric-tests.txt
python -m unittest discover -s scripts -p test_gold_models.py
```

For an independent comparison against the unchanged SQL baseline, run
`infra/scripts/Get-GoldSourceTotals.ps1`, download Gold's READY
`Files/validation/latest.json` to `.local/fabric-gold-report.json`, then run
`python scripts/compare_gold_source.py`. It compares all 15 money/quantity totals
by currency using exact decimals. The SQL query uses order headers, successful
payments and refunds independently of the Gold line aggregation. Run this while
the source is unchanged from the ingested snapshot; live operational mutations
would require another ingestion before comparing.

## Verified execution ? 2026-09-13 UTC

- Notebook job `99c62fbc-9ed3-40fe-8120-e605c37d8139`: Completed,
  05:15:56?05:19:24 UTC.
- Gold validation run `f4e5f3e9-455b-4f99-9a55-408268444b8c`: READY;
  all 59 checks passed, including six complete persisted-row comparisons.
- Source Silver run `55cdeeb3-0772-494a-8e7f-f0df4da03353`;
  seven source Delta versions pinned and checked unchanged.
- Independent Azure SQL query: all 15 currency totals match exactly.
- Six local SQL fixtures and two generator tests passed; notebook/Python and
  PowerShell syntax checks passed.

| Table | Rows |
|---|---:|
| order_summary | 100,000 |
| order_line_summary | 286,652 |
| sales_daily | 365 |
| sales_by_customer | 97,782 |
| sales_by_product | 50,610 |
| refund_summary | 7,270 |

USD captured amount is 68,017,043.14; refunds are 3,124,218.65;
net cash is 64,892,824.49. Net merchandise sales are 60,665,933.51 and
net tax is 4,226,890.98. Order `ORD-000002` retains its two lines,
1,682.64 capture, 153.00 refund and 1,529.64 net cash.

Initial execution caught an incorrect validation assumption that all cancelled
orders were unpaid. The generator also produces paid cancellations with full
refunds. The final check requires complete net reversal, preserving actual
captures and refunds; a regression fixture verifies that lifecycle. No source
records were changed to make validation pass.
