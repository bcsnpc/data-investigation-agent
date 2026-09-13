# Fixed read-only templates. Request and optional Entra token arrive over stdin.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Data
$connection=$null
$stage='setup'
try {
 $request=[Console]::In.ReadToEnd() | ConvertFrom-Json
 if($request.layer -notin @('sql','bronze','silver','gold')) { throw 'Unsupported layer' }
 if($request.currency -cnotmatch '^[A-Z]{3}$') { throw 'Invalid currency' }
 if($request.order_id -and $request.order_id -cnotmatch '^ORD-[0-9]{6}$') { throw 'Invalid order ID' }
 $builder=New-Object System.Data.SqlClient.SqlConnectionStringBuilder
 $builder['Data Source']="tcp:$($request.server),1433"
 $builder['Initial Catalog']=$request.database
 $builder['Encrypt']=$true
 $builder['TrustServerCertificate']=$false
 $builder['Connect Timeout']=30
 $builder['ApplicationIntent']='ReadOnly'
 $connection=New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
 if($request.layer -eq 'sql') {
  $credential=Import-Clixml -LiteralPath $request.credential_file
  $credential.Password.MakeReadOnly()
  $connection.Credential=New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
 } else { $connection.AccessToken=$request.access_token }
 $command=$connection.CreateCommand()
 $command.CommandTimeout=90
 if($request.layer -in @('sql','bronze')) {
  $command.CommandText=@'
WITH captured AS (SELECT order_id,SUM(amount) amount FROM app.payments WHERE payment_status='CAPTURED' GROUP BY order_id),
refunded AS (SELECT order_id,SUM(refund_amount) amount FROM app.refunds GROUP BY order_id)
SELECT COUNT_BIG(*) order_count,CAST(COALESCE(SUM(COALESCE(p.amount,0)-COALESCE(r.amount,0)),0) AS DECIMAL(28,4)) net_cash
FROM app.orders o LEFT JOIN captured p ON p.order_id=o.order_id LEFT JOIN refunded r ON r.order_id=o.order_id
WHERE o.currency=@currency AND (@order_id IS NULL OR o.order_id=@order_id)
'@
 } elseif($request.layer -eq 'silver') {
  $command.CommandText=@'
SELECT COUNT_BIG(*) order_count,CAST(COALESCE(SUM(net_amount),0) AS DECIMAL(28,4)) net_cash
FROM dbo.fact_order WHERE currency=@currency AND (@order_id IS NULL OR order_id=@order_id)
'@
 } else {
  $command.CommandText=@'
SELECT COUNT_BIG(DISTINCT order_id) order_count,CAST(COALESCE(SUM(net_cash_amount),0) AS DECIMAL(28,4)) net_cash
FROM dbo.order_line_summary WHERE currency=@currency AND (@order_id IS NULL OR order_id=@order_id)
'@
 }
 $null=$command.Parameters.Add('@currency',[System.Data.SqlDbType]::VarChar,3)
 $command.Parameters['@currency'].Value=$request.currency
 $null=$command.Parameters.Add('@order_id',[System.Data.SqlDbType]::VarChar,20)
 $command.Parameters['@order_id'].Value=[DBNull]::Value
 if($request.order_id) { $command.Parameters['@order_id'].Value=$request.order_id }
 $stage='connect'
 $connection.Open()
 $stage='query'
 $reader=$command.ExecuteReader()
 if(-not $reader.Read()) { throw 'Aggregate result missing' }
 $values=@{}
 for($i=0;$i -lt $reader.FieldCount;$i++) {
  $values[$reader.GetName($i)]=$reader.GetValue($i).ToString($null,[System.Globalization.CultureInfo]::InvariantCulture)
 }
 $reader.Dispose()
 @{values=$values;query=$command.CommandText;captured_at=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Depth 4 -Compress
} catch {
 # Do not return exception bodies, which may include connection/request details.
 $sqlError=$_.Exception
 while($sqlError -and -not ($sqlError -is [System.Data.SqlClient.SqlException])) { $sqlError=$sqlError.InnerException }
 $code=$null
 if($sqlError) { $code=$sqlError.Number }
 @{error='SQL_READ_FAILED';error_type=$_.Exception.GetType().Name;stage=$stage;sql_error_number=$code} | ConvertTo-Json -Compress
 exit 1
} finally { if($connection) { $connection.Dispose() } }
