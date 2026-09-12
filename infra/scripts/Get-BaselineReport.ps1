$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Add-Type -AssemblyName System.Data
$credential = Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/azure-sql.credential.xml')
$credential.Password.MakeReadOnly()
$connection = New-Object System.Data.SqlClient.SqlConnection('Data Source=tcp:sql-orderops-9696025.database.windows.net,1433;Initial Catalog=ordersops;Encrypt=True;TrustServerCertificate=False;Connect Timeout=60')
$connection.Credential = New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
try {
 $connection.Open()
 $cmd = $connection.CreateCommand()
 $cmd.CommandTimeout = 600
 $cmd.CommandText = Get-Content -LiteralPath (Join-Path $projectRoot 'infra/sql/003_validate_baseline.sql') -Raw
 $null = $cmd.Parameters.Add('@cutoff',[System.Data.SqlDbType]::DateTime2)
 $cmd.Parameters['@cutoff'].Value = [datetime]'2026-09-12T00:00:00'
 $null = $cmd.ExecuteNonQuery()
 $cmd.Parameters.Clear()
 Write-Output 'Live SQL reconciliation: PASS'
 $queries = [ordered]@{
  'Dataset' = 'SELECT dataset_id,order_count,status,completed_at FROM app.dataset_runs'
  'Counts' = "SELECT 'customers' table_name,COUNT_BIG(*) row_count FROM app.customers UNION ALL SELECT 'products',COUNT_BIG(*) FROM app.products UNION ALL SELECT 'orders',COUNT_BIG(*) FROM app.orders UNION ALL SELECT 'order_lines',COUNT_BIG(*) FROM app.order_lines UNION ALL SELECT 'payments',COUNT_BIG(*) FROM app.payments UNION ALL SELECT 'shipments',COUNT_BIG(*) FROM app.shipments UNION ALL SELECT 'shipment_lines',COUNT_BIG(*) FROM app.shipment_lines UNION ALL SELECT 'refunds',COUNT_BIG(*) FROM app.refunds UNION ALL SELECT 'refund_lines',COUNT_BIG(*) FROM app.refund_lines UNION ALL SELECT 'audit_log',COUNT_BIG(*) FROM app.audit_log"
  'Order statuses' = 'SELECT status,COUNT(*) orders FROM app.orders GROUP BY status ORDER BY orders DESC'
  'Purchase behavior' = 'SELECT purchase_profile,COUNT(*) customers,MIN(n) minimum_orders,MAX(n) maximum_orders,CAST(AVG(1.0*n) AS decimal(10,2)) average_orders FROM app.customers c JOIN (SELECT customer_id,COUNT(*) n FROM app.orders GROUP BY customer_id) o ON o.customer_id=c.customer_id GROUP BY purchase_profile'
  'Monthly demand' = "SELECT CONVERT(char(7),order_date,126) month,COUNT(*) orders FROM app.orders GROUP BY CONVERT(char(7),order_date,126) ORDER BY month"
  'Example return' = "SELECT TOP(1) o.order_id,o.customer_id,o.total_amount,o.status,r.refund_amount,r.refund_reason FROM app.orders o JOIN app.refunds r ON r.order_id=o.order_id WHERE o.status='PARTIALLY_RETURNED' ORDER BY o.order_id"
 }
 foreach ($entry in $queries.GetEnumerator()) {
  $cmd.CommandText = $entry.Value
  $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($cmd)
  $result = New-Object System.Data.DataTable
  $null = $adapter.Fill($result)
  Write-Output $entry.Key
  $result | Format-Table -AutoSize | Out-String -Width 180 | Write-Output
  $result.Dispose(); $adapter.Dispose()
 }
} finally { $connection.Dispose() }
