# Connected retail baseline

The baseline simulates a fictional US office-electronics retailer over
2025-09-12 through 2026-09-11, with a fixed cutoff of 2026-09-12 00:00 UTC.
Generator version: retail-v1. Seed: 42. Target: 100,000 orders.

## Relationships and purchase behavior

20,000 synthetic customers comprise 40% one-time shoppers, 45% repeat shoppers,
and 15% small businesses. Every customer has at least one order; additional
orders are weighted toward businesses. Account creation precedes purchases.
Customer names are fictional combinations, without real contact details.

150 products span keyboards, mice, monitors, docks, webcams, headsets, cables,
stands, chargers and hubs. Customers have a persistent USB-A or USB-C preference.
Previous paid purchases influence subsequent baskets: monitor owners favor
accessories and consumer monitor reorders are less likely. These are simplified
compatibility families, not a complete hardware compatibility catalog.

Baskets contain 1–5 distinct products. Consumer quantities are usually 1–3;
business quantities range from 2–15 per line. Category weights make inexpensive
accessories more popular. Purchase dates use a shared promotional calendar,
August uplift and lower weekend demand. Recently introduced products cannot
appear in older orders. Shipping and return dates are clipped at the cutoff.

## Financial contract

All calculations use integer cents with explicit half-up rounding. Azure SQL
stores amounts as decimal(19,4), with generated values rounded to two decimals.
All orders are USD. There is no shipping fee in v1.

- `orders.subtotal`: sum of quantity times purchase unit price, before discounts.
- `order_lines.discount_amount`: item promotion discount.
- `order_lines.order_discount_amount`: allocated order coupon discount.
- `order_lines.line_total`: merchandise value after both discounts, excluding tax.
- `orders.discount_amount`: sum of item and allocated order discounts.
- `orders.tax_amount`: sum of line taxes after discounts.
- `orders.total_amount`: discounted merchandise plus tax, the amount payable.
- November 24–30: 15% off keyboards, mice and headsets.
- WELCOME10: selected customers with no prior captured purchase get 10% off
  post-promotion merchandise. Selected business orders otherwise get OFFICE5.
- Order coupons are allocated by largest remainder, preserving every cent.
- State-associated tax rates are **simulated demo rates, not actual tax advice**.
  No jurisdiction, exemption, nexus or effective-date tax engine is implemented.
- Product list prices remain stable in v1; historical purchase prices are stored
  on lines. Promotions are separate discounts rather than hidden price changes.

## Lifecycle

Orders begin PENDING_PAYMENT. A failed payment attempt can precede a successful
capture; failed attempts retain the attempted amount but are excluded from cash
received. Unpaid cancellation has no refund. Paid pre-shipment cancellation is
fully refunded. Otherwise paid orders ship in 1–7 days and deliver in 2–9 more.
Recent orders can remain PAID or SHIPPED at cutoff.

Some delivered orders have a return 2–21 days after delivery. A partial return
means returning selected full order lines; partial quantities within a line,
split shipments, multiple captures and multiple returns per order are not yet
simulated. Refunds include discounted merchandise and its original tax and
reference both the captured payment and original lines. This ensures returns
cannot invent new amounts. Every line in a shipment references the same order.

The audit log captures order creation/status changes, payment attempt outcomes
and refunds. It does not claim to contain field-level snapshots of every insert.
The final order status and updated_at are derived from the final lifecycle event.

## Analytics contract

Order total is not revenue. Recognize discounted merchandise on shipment,
excluding tax. Net revenue subtracts merchandise refunds for shipped orders.
Paid pre-shipment cancellations never recognize revenue. Revenue-by-date must
use shipment dates; refund adjustments use refund dates. A Gold order-level
trace should retain order IDs and show both order total and net revenue.

## Generate and load

```powershell
python -m unittest discover -s scripts -p test_generate_orders.py
python scripts/generate_orders.py --orders 100000 --output .local/baseline-100k-v1
powershell -NoProfile -ExecutionPolicy Bypass -File infra/scripts/Load-OrderBaseline.ps1 -DatasetDirectory .local/baseline-100k-v1
```

Python writes a local SQLite baseline for independent relational checks, then
TSV artifacts and a SHA-256 manifest. Existing output directories with a baseline
are rejected so generation cannot accidentally overwrite an earlier run.
The generator requires only the Python standard library.

The PowerShell loader uses .NET SqlBulkCopy with constraint checks, named column
mappings, batches of 5,000, and one external SQL transaction. Data moves directly
from this machine to Azure SQL over TLS. Credentials remain in the existing
Windows-encrypted local credential file. No password appears in generated files.
The bulk-copy transaction pattern follows Microsoft's
[ADO.NET documentation](https://learn.microsoft.com/en-us/sql/connect/ado-net/sql/transaction-bulk-copy-operations).

Schema migration 002 is applied first and persists separately. Data is committed
only after SQL reconciliations and manifest counts pass. A dataset_runs row then
records READY, the seed, cutoff and manifest hash. Concurrent loads use an
application lock. Rerunning the identical manifest is a no-op; nonempty unrelated
tables or a conflicting manifest cause an error, never an automatic deletion.

`-ValidateOnly` exercises the SQL load and checks, then rolls the sample data
back. The migration remains. A fresh directory can be used for another sample.

## Verification and limits

Checks cover key uniqueness, parent linkage, customer/product chronology,
line and order arithmetic, line taxes, payment reconciliation, refund linkage
and caps, shipment linkage, return eligibility, audit chains, current status
and cutoff dates. SQL foreign keys are checked during bulk copy. Mutation tests
prove the validator catches broken values, references and state.

This is a clean baseline. Do not mix intentionally defective records into it;
future defect scenarios should explicitly identify the changed layer and values.
Stock procurement/inventory, real carriers, chargebacks and real payment/tax
services are outside v1. This dataset is synthetic, not a statistical model
calibrated against a real retailer.
