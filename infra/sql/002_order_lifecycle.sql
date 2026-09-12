SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF COL_LENGTH('app.customers','purchase_profile') IS NULL
 ALTER TABLE app.customers ADD purchase_profile nvarchar(40) NULL;
IF COL_LENGTH('app.products','available_from') IS NULL
 ALTER TABLE app.products ADD available_from datetime2(3) NULL, compatibility_family nvarchar(40) NULL;
IF COL_LENGTH('app.orders','currency') IS NULL
 ALTER TABLE app.orders ADD currency char(3) NOT NULL DEFAULT 'USD', coupon_code nvarchar(40) NULL,
 tax_rate decimal(7,4) NULL, dataset_id nvarchar(64) NULL;
IF COL_LENGTH('app.order_lines','order_discount_amount') IS NULL
 ALTER TABLE app.order_lines ADD order_discount_amount decimal(19,4) NOT NULL DEFAULT 0,
 tax_amount decimal(19,4) NOT NULL DEFAULT 0, promotion_code nvarchar(40) NULL;
IF COL_LENGTH('app.refunds','payment_id') IS NULL
 ALTER TABLE app.refunds ADD payment_id nvarchar(40) NULL REFERENCES app.payments(payment_id);
IF OBJECT_ID('app.shipments','U') IS NULL
BEGIN
 CREATE TABLE app.shipments (
 shipment_id nvarchar(40) NOT NULL PRIMARY KEY,
 order_id nvarchar(40) NOT NULL REFERENCES app.orders(order_id),
 carrier nvarchar(40) NOT NULL,
 tracking_number nvarchar(60) NOT NULL UNIQUE,
 shipped_at datetime2(3) NOT NULL,
 delivered_at datetime2(3) NULL,
 CHECK(delivered_at IS NULL OR delivered_at >= shipped_at)
 );
 CREATE INDEX IX_shipments_order ON app.shipments(order_id);
END;
IF OBJECT_ID('app.shipment_lines','U') IS NULL
 CREATE TABLE app.shipment_lines (
 shipment_id nvarchar(40) NOT NULL REFERENCES app.shipments(shipment_id),
 order_line_id nvarchar(40) NOT NULL REFERENCES app.order_lines(order_line_id),
 quantity int NOT NULL CHECK(quantity > 0),
 PRIMARY KEY(shipment_id, order_line_id)
 );
IF OBJECT_ID('app.refund_lines','U') IS NULL
 CREATE TABLE app.refund_lines (
 refund_id nvarchar(40) NOT NULL REFERENCES app.refunds(refund_id),
 order_line_id nvarchar(40) NOT NULL REFERENCES app.order_lines(order_line_id),
 quantity int NOT NULL CHECK(quantity > 0),
 merchandise_amount decimal(19,4) NOT NULL CHECK(merchandise_amount >= 0),
 tax_amount decimal(19,4) NOT NULL CHECK(tax_amount >= 0),
 PRIMARY KEY(refund_id, order_line_id)
 );
IF OBJECT_ID('app.dataset_runs','U') IS NULL
 CREATE TABLE app.dataset_runs (
 dataset_id nvarchar(64) NOT NULL PRIMARY KEY,
 seed int NOT NULL,
 as_of datetime2(3) NOT NULL,
 order_count int NOT NULL,
 manifest_sha256 char(64) NOT NULL,
 status nvarchar(20) NOT NULL,
 completed_at datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME()
 );
COMMIT TRANSACTION;
