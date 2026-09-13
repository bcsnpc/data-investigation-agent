-- Read-only independent check against the operational source at the same baseline.
WITH captured AS (
 SELECT order_id,SUM(amount) amount FROM app.payments
 WHERE payment_status='CAPTURED' GROUP BY order_id
), refunds AS (
 SELECT order_id,SUM(refund_amount) amount FROM app.refunds GROUP BY order_id
), returned AS (
 SELECT r.order_id,SUM(l.merchandise_amount) merchandise,SUM(l.tax_amount) tax,
 SUM(CAST(l.quantity AS bigint)) units
 FROM app.refunds r JOIN app.refund_lines l ON l.refund_id=r.refund_id
 GROUP BY r.order_id
), units AS (
 SELECT order_id,SUM(CAST(quantity AS bigint)) quantity FROM app.order_lines GROUP BY order_id
)
SELECT o.currency,
 SUM(CASE WHEN c.amount>0 THEN o.subtotal ELSE 0 END) gross_sales_amount,
 SUM(CASE WHEN c.amount>0 THEN o.discount_amount ELSE 0 END) discount_amount,
 SUM(CASE WHEN c.amount>0 THEN o.subtotal-o.discount_amount ELSE 0 END) sales_amount,
 SUM(CASE WHEN c.amount>0 THEN o.tax_amount ELSE 0 END) tax_amount,
 SUM(COALESCE(c.amount,0)) captured_amount,
 SUM(COALESCE(t.merchandise,0)) refunded_sales_amount,
 SUM(COALESCE(t.tax,0)) refunded_tax_amount,
 SUM(COALESCE(r.amount,0)) refund_amount,
 SUM(CASE WHEN c.amount>0 THEN o.subtotal-o.discount_amount ELSE 0 END-COALESCE(t.merchandise,0)) net_sales_amount,
 SUM(CASE WHEN c.amount>0 THEN o.tax_amount ELSE 0 END-COALESCE(t.tax,0)) net_tax_amount,
 SUM(COALESCE(c.amount,0)-COALESCE(r.amount,0)) net_cash_amount,
 SUM(u.quantity) units_ordered,
 SUM(CASE WHEN c.amount>0 THEN u.quantity ELSE 0 END) units_sold,
 SUM(COALESCE(t.units,0)) units_returned,
 SUM(CASE WHEN c.amount>0 THEN u.quantity ELSE 0 END-COALESCE(t.units,0)) net_units
FROM app.orders o
LEFT JOIN captured c ON c.order_id=o.order_id
LEFT JOIN refunds r ON r.order_id=o.order_id
LEFT JOIN returned t ON t.order_id=o.order_id
JOIN units u ON u.order_id=o.order_id
GROUP BY o.currency;
