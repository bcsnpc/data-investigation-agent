"""Reporting SQL shared by the Fabric notebook and local adversarial fixtures.

Sales cohorts use original order_day. Refund events retain refund_day separately.
"""
MONEY = (
    "gross_sales_amount", "discount_amount", "sales_amount", "tax_amount",
    "captured_amount", "refunded_sales_amount", "refunded_tax_amount",
    "refund_amount", "net_sales_amount", "net_tax_amount", "net_cash_amount",
)
UNITS = ("units_ordered", "units_sold", "units_returned", "net_units")
ADDITIVE = MONEY + UNITS

QUERIES = {}
QUERIES["order_line_summary"] = """
WITH returned AS (
 SELECT order_line_id, SUM(quantity) returned_quantity,
 SUM(merchandise_amount) returned_merchandise, SUM(tax_amount) returned_tax
 FROM s_fact_refund_line GROUP BY order_line_id
), amounts AS (
 SELECT l.order_line_id,l.order_id,o.customer_id,l.product_id,p.product_name,
 p.category,p.subcategory,CAST(o.order_date AS DATE) order_day,o.currency,o.status,
 CASE WHEN o.captured_amount>0 THEN 1 ELSE 0 END is_funded,
 CAST(l.quantity AS BIGINT) units_ordered,
 CAST(CASE WHEN o.captured_amount>0 THEN l.quantity ELSE 0 END AS BIGINT) units_sold,
 CAST(COALESCE(r.returned_quantity,0) AS BIGINT) units_returned,
 CAST(CASE WHEN o.captured_amount>0 THEN l.quantity*l.unit_price ELSE 0 END AS DECIMAL(28,4)) gross_sales_amount,
 CAST(CASE WHEN o.captured_amount>0 THEN l.discount_amount+l.order_discount_amount ELSE 0 END AS DECIMAL(28,4)) discount_amount,
 CAST(CASE WHEN o.captured_amount>0 THEN l.line_total ELSE 0 END AS DECIMAL(28,4)) sales_amount,
 CAST(CASE WHEN o.captured_amount>0 THEN l.tax_amount ELSE 0 END AS DECIMAL(28,4)) tax_amount,
 CAST(CASE WHEN o.captured_amount>0 THEN l.line_total+l.tax_amount ELSE 0 END AS DECIMAL(28,4)) captured_amount,
 CAST(COALESCE(r.returned_merchandise,0) AS DECIMAL(28,4)) refunded_sales_amount,
 CAST(COALESCE(r.returned_tax,0) AS DECIMAL(28,4)) refunded_tax_amount,
 CAST(COALESCE(r.returned_merchandise,0)+COALESCE(r.returned_tax,0) AS DECIMAL(28,4)) refund_amount
 FROM s_fact_order_line l JOIN s_fact_order o ON o.order_id=l.order_id
 JOIN s_dim_product p ON p.product_id=l.product_id
 LEFT JOIN returned r ON r.order_line_id=l.order_line_id
)
SELECT *,units_sold-units_returned net_units,
 CAST(sales_amount-refunded_sales_amount AS DECIMAL(28,4)) net_sales_amount,
 CAST(tax_amount-refunded_tax_amount AS DECIMAL(28,4)) net_tax_amount,
 CAST(captured_amount-refund_amount AS DECIMAL(28,4)) net_cash_amount
FROM amounts
"""

line_sums = ",".join(f"SUM({c}) {c}" for c in ADDITIVE)
line_columns = ",".join(f"l.{c}" for c in ADDITIVE)
QUERIES["order_summary"] = f"""
WITH lines AS (
 SELECT order_id,COUNT(*) line_count,{line_sums}
 FROM g_order_line_summary GROUP BY order_id
)
SELECT o.order_id,o.customer_id,c.customer_name,c.customer_segment,c.state_code,
 c.country_code,CAST(o.order_date AS DATE) order_day,o.order_date,o.currency,o.status,
 o.total_amount order_amount,o.coupon_code,o.dataset_id,
 CASE WHEN o.captured_amount>0 THEN 1 ELSE 0 END is_funded,
 CASE WHEN o.status='CANCELLED' THEN 1 ELSE 0 END is_cancelled,
 CASE WHEN o.refunded_amount>0 THEN 1 ELSE 0 END has_return,
 l.line_count,{line_columns}
FROM s_fact_order o JOIN lines l ON l.order_id=o.order_id
JOIN s_dim_customer c ON c.customer_id=o.customer_id
"""

order_measures = "COUNT(*) order_count,SUM(is_funded) funded_order_count,SUM(is_cancelled) cancelled_order_count,SUM(has_return) returned_order_count"
QUERIES["sales_daily"] = f"""
SELECT order_day,currency,{order_measures},{line_sums}
FROM g_order_summary GROUP BY order_day,currency
"""
QUERIES["sales_by_customer"] = f"""
SELECT order_day,currency,customer_id,customer_name,customer_segment,state_code,
 country_code,{order_measures},{line_sums}
FROM g_order_summary
GROUP BY order_day,currency,customer_id,customer_name,customer_segment,state_code,country_code
"""
QUERIES["sales_by_product"] = f"""
SELECT order_day,currency,product_id,product_name,category,subcategory,
 COUNT(DISTINCT order_id) order_count,
 COUNT(DISTINCT CASE WHEN is_funded=1 THEN order_id END) funded_order_count,
 {line_sums}
FROM g_order_line_summary
GROUP BY order_day,currency,product_id,product_name,category,subcategory
"""
QUERIES["refund_summary"] = """
WITH lines AS (
 SELECT refund_id,COUNT(*) returned_line_count,SUM(quantity) units_returned,
 CAST(SUM(merchandise_amount) AS DECIMAL(28,4)) refunded_sales_amount,
 CAST(SUM(tax_amount) AS DECIMAL(28,4)) refunded_tax_amount
 FROM s_fact_refund_line GROUP BY refund_id
)
SELECT r.refund_id,r.order_id,r.payment_id,o.customer_id,o.currency,
 CAST(o.order_date AS DATE) order_day,CAST(r.refund_date AS DATE) refund_day,
 r.refund_date,r.refund_reason,l.returned_line_count,l.units_returned,
 l.refunded_sales_amount,l.refunded_tax_amount,
 CAST(r.refund_amount AS DECIMAL(28,4)) refund_amount
FROM s_fact_refund r JOIN s_fact_order o ON o.order_id=r.order_id
JOIN lines l ON l.refund_id=r.refund_id
"""

KEYS = {
    "order_line_summary": ["order_line_id"], "order_summary": ["order_id"],
    "sales_daily": ["order_day", "currency"],
    "sales_by_customer": ["order_day", "currency", "customer_id"],
    "sales_by_product": ["order_day", "currency", "product_id"],
    "refund_summary": ["refund_id"],
}
