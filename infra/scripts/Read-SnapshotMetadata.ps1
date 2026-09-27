$ErrorActionPreference='Stop'
$connection=$null
try {
 $request=[Console]::In.ReadToEnd() | ConvertFrom-Json
 if($request.kind -eq 'POWER_BI_DAX') {
  $assembly=[System.Reflection.Assembly]::LoadFrom($request.library)
  $connection=[Activator]::CreateInstance($assembly.GetType('Microsoft.AnalysisServices.AdomdClient.AdomdConnection',$true))
  $builder=New-Object System.Data.Common.DbConnectionStringBuilder
  $builder['Data Source']='powerbi://api.powerbi.com/v1.0/myorg/'+$request.workspace_name
  $builder['Initial Catalog']=$request.model_name
  $builder['User ID']='';$builder['Password']=$request.access_token
  $connection.ConnectionString=$builder.ConnectionString
  $query='EVALUATE TOPN(21, INFO.DELTATABLEMETADATASTORAGES())'
 } elseif($request.kind -eq 'FABRIC_SQL') {
  Add-Type -AssemblyName System.Data
  $builder=New-Object System.Data.SqlClient.SqlConnectionStringBuilder
  $builder['Data Source']='tcp:'+$request.server+',1433';$builder['Initial Catalog']=$request.database
  $builder['Encrypt']=$true;$builder['TrustServerCertificate']=$false
  $builder['ApplicationIntent']='ReadOnly';$builder['Connect Timeout']=30
  $connection=New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
  $connection.AccessToken=$request.access_token
  $query='SELECT TOP (21) object_id, latest_log_version, latest_checkpoint_version, last_update_time_utc, is_blocked FROM sys.dm_db_external_tables_log_status ORDER BY object_id'
 } else {throw 'Unsupported metadata surface'}
 $connection.Open();$command=$connection.CreateCommand();$command.CommandTimeout=60;$command.CommandText=$query
 $reader=$command.ExecuteReader();$rows=@()
 while($reader.Read()) {
  $row=[ordered]@{}
  for($i=0;$i -lt $reader.FieldCount;$i++) {
   $value=$reader.GetValue($i)
   if($value -is [DBNull]){$value=$null}
   if($value -is [datetime]){$value=$value.ToString('o')}
   $row[$reader.GetName($i)]=$value
  }
  $rows+=,$row
  if($rows.Count -ge 21){break}
 }
 $reader.Close()
 @{status=if($rows.Count -gt 20){'TRUNCATED'}elseif($rows.Count -eq 0){'EMPTY'}else{'SERVED'};rows=$rows} | ConvertTo-Json -Depth 8 -Compress
} catch {
 # Never retain exception text: connection failures can embed token-bearing strings.
 @{status='UNAVAILABLE';error_type=$_.Exception.GetType().Name} | ConvertTo-Json -Compress
} finally {if($connection){$connection.Dispose()}}
