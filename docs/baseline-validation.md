# Loaded baseline verification

Verified against Azure SQL database `ordersops` on 2026-09-12.
Dataset `retail-v1-s42-n100000-20260912` is READY.

| Table | Committed rows |
|---|---:|
| app.customers | 20,000 |
| app.products | 150 |
| app.orders | 100,000 |
| app.order_lines | 286,652 |
| app.payments | 105,047 |
| app.shipments | 95,545 |
| app.shipment_lines | 273,805 |
| app.refunds | 7,270 |
| app.refund_lines | 12,680 |
| app.audit_log | 509,550 |
| **Total business rows** | **1,410,699** |

All local relational checks and live SQL reconciliation passed. A 1,000-order
SQL dry run was validated and rolled back before the full load. A fresh SQL
connection verified the committed data. Rerunning the full loader returned
`Dataset already loaded with matching manifest; no changes made.`

Generator tests passed for exact reproducibility, cent allocation, and rejection
of corrupted line amounts, missing customer references, excessive refunds and
incorrect current statuses. The manifest and raw SQL verification output are
stored under `.local/baseline-100k-v1/` and excluded from source control.

## Observed behavior

- 8,000 one-time customers have exactly one order each.
- 9,000 repeat-profile customers have 1–16 orders (mean 4.83).
- 3,000 business customers have 5–32 orders (mean 16.19).
- 88,588 orders are DELIVERED, 3,913 CANCELLED, 3,837 PARTIALLY_RETURNED,
  1,993 RETURNED, 1,127 SHIPPED and 542 PAID at cutoff.
- Example: ORD-000002 belongs to CUST-018515, has a $1,682.64 order total,
  and a $153.00 refund for an unsuitable item. Status: PARTIALLY_RETURNED.

## Inspect in Azure Portal query editor

```sql
SELECT * FROM app.dataset_runs;

SELECT TOP (20) order_id, customer_id, order_date, status, total_amount
FROM app.orders
ORDER BY order_date DESC, order_id;

SELECT * FROM app.orders WHERE order_id = 'ORD-000002';
SELECT * FROM app.order_lines WHERE order_id = 'ORD-000002';
SELECT * FROM app.payments WHERE order_id = 'ORD-000002';
SELECT * FROM app.shipments WHERE order_id = 'ORD-000002';
SELECT * FROM app.refunds WHERE order_id = 'ORD-000002';
SELECT * FROM app.audit_log
WHERE entity_type = 'order' AND entity_id = 'ORD-000002'
ORDER BY [timestamp], event_id;
```

See [business rules and limitations](synthetic-data.md) for the exact meaning of
amounts and lifecycle states. These are simulated business histories, not real
customer transactions.
