-- Small lifecycle fixture; no connection to the cloud business baseline.
CREATE TABLE s_dim_product(product_id VARCHAR,product_name VARCHAR,category VARCHAR,subcategory VARCHAR);
INSERT INTO s_dim_product VALUES ('P','Desk accessory','Office','Accessories');
CREATE TABLE s_fact_order(order_id VARCHAR,customer_id VARCHAR,order_date TIMESTAMP,currency VARCHAR,status VARCHAR,captured_amount DECIMAL(19,4));
INSERT INTO s_fact_order VALUES
('ORD-000001','C','2026-01-01','USD','PARTIALLY_RETURNED',198),
('ORD-000002','C','2026-01-01','USD','PAID',55),
('ORD-000003','C','2026-01-01','USD','PENDING_PAYMENT',0);
CREATE TABLE s_fact_order_line(order_line_id VARCHAR,order_id VARCHAR,product_id VARCHAR,quantity INTEGER,unit_price DECIMAL(19,4),discount_amount DECIMAL(19,4),order_discount_amount DECIMAL(19,4),line_total DECIMAL(19,4),tax_amount DECIMAL(19,4));
INSERT INTO s_fact_order_line VALUES
('L1','ORD-000001','P',2,90,0,0,180,18),
('L2','ORD-000002','P',1,50,0,0,50,5),
('L3','ORD-000003','P',1,100,0,0,100,10);
CREATE TABLE s_fact_refund_line(refund_id VARCHAR,order_line_id VARCHAR,quantity INTEGER,merchandise_amount DECIMAL(19,4),tax_amount DECIMAL(19,4));
INSERT INTO s_fact_refund_line VALUES ('R1','L1',1,90,9);
