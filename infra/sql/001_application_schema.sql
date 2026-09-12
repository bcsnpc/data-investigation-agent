SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF SCHEMA_ID(N'app') IS NULL EXEC(N'CREATE SCHEMA app AUTHORIZATION dbo');

IF OBJECT_ID(N'app.customers', N'U') IS NULL
CREATE TABLE app.customers (
 customer_id nvarchar(40) NOT NULL PRIMARY KEY,
 customer_name nvarchar(200) NOT NULL,
 customer_segment nvarchar(50) NULL,
 state nvarchar(100) NULL,
 country nvarchar(100) NULL,
 created_at datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME()
);
IF OBJECT_ID(N'app.products', N'U') IS NULL
CREATE TABLE app.products (
 product_id nvarchar(40) NOT NULL PRIMARY KEY,
 product_name nvarchar(200) NOT NULL,
 category nvarchar(100) NULL,
 subcategory nvarchar(100) NULL,
 unit_price decimal(19,4) NOT NULL CHECK (unit_price >= 0),
 active_flag bit NOT NULL DEFAULT 1
);
IF OBJECT_ID(N'app.orders', N'U') IS NULL
BEGIN
 CREATE TABLE app.orders (
  order_id nvarchar(40) NOT NULL PRIMARY KEY,
  customer_id nvarchar(40) NOT NULL REFERENCES app.customers(customer_id),
  order_date datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
  status nvarchar(40) NOT NULL,
  subtotal decimal(19,4) NOT NULL,
  discount_amount decimal(19,4) NOT NULL DEFAULT 0,
  tax_amount decimal(19,4) NOT NULL DEFAULT 0,
  total_amount decimal(19,4) NOT NULL,
  created_at datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
  updated_at datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME()
 );
 CREATE INDEX IX_orders_customer ON app.orders(customer_id);
 CREATE INDEX IX_orders_updated ON app.orders(updated_at, order_id);
END;
IF OBJECT_ID(N'app.order_lines', N'U') IS NULL
BEGIN
 CREATE TABLE app.order_lines (
  order_line_id nvarchar(40) NOT NULL PRIMARY KEY,
  order_id nvarchar(40) NOT NULL REFERENCES app.orders(order_id),
  product_id nvarchar(40) NOT NULL REFERENCES app.products(product_id),
  quantity int NOT NULL CHECK (quantity > 0),
  unit_price decimal(19,4) NOT NULL,
  discount_amount decimal(19,4) NOT NULL DEFAULT 0,
  line_total decimal(19,4) NOT NULL
 );
 CREATE INDEX IX_order_lines_order ON app.order_lines(order_id);
 CREATE INDEX IX_order_lines_product ON app.order_lines(product_id);
END;
IF OBJECT_ID(N'app.payments', N'U') IS NULL
BEGIN
 CREATE TABLE app.payments (
  payment_id nvarchar(40) NOT NULL PRIMARY KEY,
  order_id nvarchar(40) NOT NULL REFERENCES app.orders(order_id),
  payment_type nvarchar(40) NOT NULL,
  amount decimal(19,4) NOT NULL,
  payment_status nvarchar(40) NOT NULL,
  payment_date datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME()
 );
 CREATE INDEX IX_payments_order ON app.payments(order_id);
END;
IF OBJECT_ID(N'app.refunds', N'U') IS NULL
BEGIN
 CREATE TABLE app.refunds (
  refund_id nvarchar(40) NOT NULL PRIMARY KEY,
  order_id nvarchar(40) NOT NULL REFERENCES app.orders(order_id),
  refund_amount decimal(19,4) NOT NULL,
  refund_reason nvarchar(500) NULL,
  refund_date datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME()
 );
 CREATE INDEX IX_refunds_order ON app.refunds(order_id);
END;
IF OBJECT_ID(N'app.audit_log', N'U') IS NULL
BEGIN
 CREATE TABLE app.audit_log (
  event_id nvarchar(40) NOT NULL PRIMARY KEY,
  entity_type nvarchar(50) NOT NULL,
  entity_id nvarchar(40) NOT NULL,
  operation nvarchar(30) NOT NULL,
  field nvarchar(128) NULL,
  old_value nvarchar(max) NULL,
  new_value nvarchar(max) NULL,
  user_id nvarchar(100) NOT NULL,
  [timestamp] datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME()
 );
 CREATE INDEX IX_audit_entity ON app.audit_log(entity_type, entity_id, [timestamp]);
END;
COMMIT TRANSACTION;
