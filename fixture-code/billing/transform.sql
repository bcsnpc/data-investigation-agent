-- Fixture-authoring code only. Not executed or asserted to be deployed.
-- Bronze tables are Dataflow Gen2 destinations; no literal-row staging here.
CREATE PROCEDURE [silver].[build_invoices]
AS
BEGIN
 DELETE FROM [silver].[invoices];
 INSERT INTO [silver].[invoices] (invoice_id,account_id,invoice_date,amount,status)
 SELECT invoice_id,account_id,invoice_date,amount,status FROM [bronze].[invoices];
END;
GO
CREATE PROCEDURE [gold].[build_billing]
AS
BEGIN
 DELETE FROM [gold].[invoice_activity];
 INSERT INTO [gold].[invoice_activity] (invoice_id,account_id,plan_id,invoice_date,amount,status)
 SELECT i.invoice_id,i.account_id,h.plan_id,i.invoice_date,i.amount,i.status
 FROM [silver].[invoices] AS i
 LEFT JOIN [bronze].[account_plan_history] AS h ON i.account_id=h.account_id;
END;
GO
