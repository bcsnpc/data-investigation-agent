IF EXISTS (
 SELECT 1 FROM app.orders o
 LEFT JOIN (SELECT order_id, SUM(quantity*unit_price) gross,
 SUM(discount_amount+order_discount_amount) discount,
 SUM(tax_amount) tax, SUM(line_total+tax_amount) total
 FROM app.order_lines GROUP BY order_id) l ON l.order_id=o.order_id
 WHERE l.order_id IS NULL OR o.subtotal<>l.gross OR o.discount_amount<>l.discount
 OR o.tax_amount<>l.tax OR o.total_amount<>l.total
 OR o.total_amount<>o.subtotal-o.discount_amount+o.tax_amount
) THROW 51000, 'Order amounts do not reconcile to lines', 1;
IF EXISTS (SELECT 1 FROM app.order_lines WHERE line_total<>quantity*unit_price-discount_amount-order_discount_amount OR line_total<0)
 THROW 51001, 'Line arithmetic invalid', 1;
IF EXISTS (SELECT 1 FROM app.order_lines l JOIN app.orders o ON o.order_id=l.order_id WHERE l.tax_amount<>ROUND(l.line_total*o.tax_rate,2))
 THROW 51015, 'Line tax rounding invalid', 1;
IF EXISTS (
 SELECT 1 FROM app.orders o LEFT JOIN
 (SELECT order_id,SUM(amount) amount FROM app.payments WHERE payment_status='CAPTURED' GROUP BY order_id) p ON p.order_id=o.order_id
 WHERE (o.status NOT IN ('CANCELLED','PENDING_PAYMENT') AND ISNULL(p.amount,0)<>o.total_amount)
 OR ISNULL(p.amount,0)>o.total_amount
) THROW 51002, 'Captured payments do not reconcile', 1;
IF EXISTS (
 SELECT 1 FROM app.refunds r JOIN app.payments p ON p.payment_id=r.payment_id
 WHERE p.order_id<>r.order_id OR p.payment_status<>'CAPTURED' OR r.refund_date<p.payment_date
) THROW 51003, 'Refund payment linkage invalid', 1;
IF EXISTS (
 SELECT 1 FROM app.payments p JOIN (SELECT payment_id,SUM(refund_amount) total FROM app.refunds GROUP BY payment_id) r ON r.payment_id=p.payment_id WHERE r.total>p.amount
) THROW 51004, 'Refunds exceed payment', 1;
IF EXISTS (
 SELECT 1 FROM app.refunds r LEFT JOIN (SELECT refund_id,SUM(merchandise_amount+tax_amount) total FROM app.refund_lines GROUP BY refund_id) l ON l.refund_id=r.refund_id
 WHERE l.refund_id IS NULL OR r.refund_amount<>l.total
) THROW 51005, 'Refund lines do not reconcile', 1;
IF EXISTS (
 SELECT 1 FROM app.refund_lines r JOIN app.refunds f ON f.refund_id=r.refund_id JOIN app.order_lines l ON l.order_line_id=r.order_line_id
 WHERE f.order_id<>l.order_id
) THROW 51006, 'Refund line belongs to a different order', 1;
IF EXISTS (
 SELECT 1 FROM app.order_lines l JOIN (SELECT order_line_id,SUM(quantity) qty,SUM(merchandise_amount) net,SUM(tax_amount) tax FROM app.refund_lines GROUP BY order_line_id) r ON r.order_line_id=l.order_line_id
 WHERE r.qty>l.quantity OR r.net>l.line_total OR r.tax>l.tax_amount
) THROW 51007, 'Return quantities or amounts exceed purchase', 1;
IF EXISTS (
 SELECT 1 FROM app.orders o JOIN app.customers c ON c.customer_id=o.customer_id WHERE o.order_date<c.created_at
) THROW 51008, 'Order predates customer', 1;
IF EXISTS (
 SELECT 1 FROM app.order_lines l JOIN app.orders o ON o.order_id=l.order_id JOIN app.products p ON p.product_id=l.product_id WHERE o.order_date<p.available_from
) THROW 51009, 'Product not available at purchase', 1;
IF EXISTS (
 SELECT 1 FROM app.shipments s LEFT JOIN app.payments p ON p.order_id=s.order_id AND p.payment_status='CAPTURED'
 WHERE p.payment_id IS NULL OR s.shipped_at<p.payment_date
) THROW 51010, 'Shipment precedes payment', 1;
IF EXISTS (
 SELECT 1 FROM app.shipment_lines sl JOIN app.shipments s ON s.shipment_id=sl.shipment_id JOIN app.order_lines l ON l.order_line_id=sl.order_line_id
 WHERE s.order_id<>l.order_id OR sl.quantity<>l.quantity
) THROW 51011, 'Shipment line mismatch', 1;
IF EXISTS (
 SELECT 1 FROM app.refunds r LEFT JOIN app.shipments s ON s.order_id=r.order_id
 WHERE r.refund_reason<>'Cancelled before shipment' AND (s.delivered_at IS NULL OR r.refund_date<s.delivered_at)
) THROW 51012, 'Return precedes delivery', 1;
IF EXISTS (
 SELECT 1 FROM app.orders o LEFT JOIN app.audit_log a ON a.entity_type='order' AND a.entity_id=o.order_id AND a.[timestamp]=o.updated_at
 WHERE a.event_id IS NULL OR a.new_value<>o.status
) THROW 51013, 'Current status disagrees with audit history', 1;
IF EXISTS (
 SELECT 1 FROM (SELECT old_value,LAG(new_value) OVER(PARTITION BY entity_id ORDER BY [timestamp],event_id) prev FROM app.audit_log WHERE entity_type='order') a
 WHERE ISNULL(old_value,'<NULL>')<>ISNULL(prev,'<NULL>')
) THROW 51014, 'Broken audit chain', 1;
IF EXISTS (
 SELECT 1 FROM app.orders o LEFT JOIN app.shipments s ON s.order_id=o.order_id
 WHERE (o.status IN ('DELIVERED','RETURNED','PARTIALLY_RETURNED') AND s.delivered_at IS NULL)
 OR (o.status='SHIPPED' AND (s.shipment_id IS NULL OR s.delivered_at IS NOT NULL))
 OR (o.status IN ('CANCELLED','PAID','PENDING_PAYMENT') AND s.shipment_id IS NOT NULL)
) THROW 51016, 'Shipment disagrees with order status', 1;
IF EXISTS (
 SELECT 1 FROM app.orders o JOIN app.payments p ON p.order_id=o.order_id AND p.payment_status='CAPTURED'
 LEFT JOIN (SELECT order_id,SUM(refund_amount) amount FROM app.refunds GROUP BY order_id) r ON r.order_id=o.order_id
 WHERE o.status='CANCELLED' AND ISNULL(r.amount,0)<>p.amount
) THROW 51017, 'Paid cancellation was not fully refunded', 1;
IF EXISTS (
 SELECT 1 FROM app.payments p JOIN app.orders o ON o.order_id=p.order_id WHERE p.payment_date<o.order_date
) THROW 51018, 'Payment precedes order', 1;
IF EXISTS (
 SELECT 1 FROM app.orders WHERE updated_at>@cutoff
 UNION ALL SELECT 1 FROM app.audit_log WHERE [timestamp]>@cutoff
 UNION ALL SELECT 1 FROM app.payments WHERE payment_date>@cutoff
 UNION ALL SELECT 1 FROM app.refunds WHERE refund_date>@cutoff
 UNION ALL SELECT 1 FROM app.shipments WHERE shipped_at>@cutoff OR delivered_at>@cutoff
) THROW 51019, 'Events occur after dataset cutoff', 1;
