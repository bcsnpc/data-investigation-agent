-- Executed inside the provisioning script's transaction.
IF DATABASE_PRINCIPAL_ID('orderops_app_role') IS NULL CREATE ROLE orderops_app_role AUTHORIZATION dbo;
IF DATABASE_PRINCIPAL_ID('orderops_fabric_role') IS NULL CREATE ROLE orderops_fabric_role AUTHORIZATION dbo;
IF DATABASE_PRINCIPAL_ID('orderops_investigator_role') IS NULL CREATE ROLE orderops_investigator_role AUTHORIZATION dbo;

-- Explicit object grants avoid automatically exposing future tables.
DECLARE @table sysname, @sql nvarchar(max);
DECLARE objects CURSOR LOCAL FAST_FORWARD FOR SELECT name FROM (VALUES
 ('customers'),('products'),('orders'),('order_lines'),('payments'),
 ('shipments'),('shipment_lines'),('refunds'),('refund_lines'),('audit_log')) t(name);
OPEN objects;
FETCH NEXT FROM objects INTO @table;
WHILE @@FETCH_STATUS=0
BEGIN
 SET @sql=N'GRANT SELECT ON OBJECT::app.'+QUOTENAME(@table)+N' TO orderops_app_role, orderops_fabric_role, orderops_investigator_role;';
 EXEC sys.sp_executesql @sql;
 IF @table<>'audit_log'
 BEGIN
  SET @sql=N'GRANT INSERT, UPDATE ON OBJECT::app.'+QUOTENAME(@table)+N' TO orderops_app_role;';
  EXEC sys.sp_executesql @sql;
 END;
 FETCH NEXT FROM objects INTO @table;
END;
CLOSE objects;
DEALLOCATE objects;
GRANT INSERT ON OBJECT::app.audit_log TO orderops_app_role;
DENY UPDATE, DELETE ON OBJECT::app.audit_log TO orderops_app_role;
DENY DELETE, ALTER, EXECUTE ON SCHEMA::app TO orderops_app_role;
DENY INSERT, UPDATE, DELETE ON OBJECT::app.dataset_runs TO orderops_app_role;

GRANT VIEW DEFINITION ON SCHEMA::app TO orderops_investigator_role;
DENY INSERT, UPDATE, DELETE, ALTER, EXECUTE ON SCHEMA::app TO orderops_fabric_role, orderops_investigator_role;
DENY CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, ALTER ANY USER, ALTER ANY ROLE TO orderops_app_role, orderops_fabric_role, orderops_investigator_role;
