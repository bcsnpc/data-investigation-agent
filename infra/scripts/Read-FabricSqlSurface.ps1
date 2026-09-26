$ErrorActionPreference='Stop'
# Ask a Fabric SQL analytics endpoint who it is serving and which database.
# Self-report only: it accepts no query. A connection always names its
# database; an empty name is refused before connecting.
Add-Type -AssemblyName System.Data
$connection=$null
$stage='setup'
try {
  $request=[Console]::In.ReadToEnd() | ConvertFrom-Json
  $names=@($request.PSObject.Properties.Name | Sort-Object)
  if (($names -join ',') -ne 'access_token,database,server') { throw 'Unexpected request fields' }
  if ([string]::IsNullOrWhiteSpace($request.database)) { throw 'Database name required' }
  if ($request.server -notmatch '^[A-Za-z0-9.-]+$') { throw 'Invalid server' }
  $builder=New-Object System.Data.SqlClient.SqlConnectionStringBuilder
  $builder['Data Source']="tcp:$($request.server),1433"
  $builder['Initial Catalog']=$request.database
  $builder['Encrypt']=$true
  $builder['TrustServerCertificate']=$false
  $builder['Connect Timeout']=30
  $builder['ApplicationIntent']='ReadOnly'
  $connection=New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
  $connection.AccessToken=$request.access_token
  $stage='connect'; $connection.Open()
  $stage='query'
  $command=$connection.CreateCommand()
  $command.CommandTimeout=60
  $command.CommandText='SELECT SUSER_SNAME() AS login_name, DB_NAME() AS database_name'
  $reader=$command.ExecuteReader()
  if (-not $reader.Read()) { throw 'Self-report returned no row' }
  $result=@{status='REACHABLE';stage='complete';login_name=[string]$reader['login_name'];database_name=[string]$reader['database_name']}
  $reader.Close()
  $result | ConvertTo-Json -Compress
} catch {
  $sqlError=$_.Exception
  while($sqlError -and -not ($sqlError -is [System.Data.SqlClient.SqlException])) { $sqlError=$sqlError.InnerException }
  @{status='UNAVAILABLE';stage=$stage;error_type=$_.Exception.GetType().Name;sql_error_number=if($sqlError){$sqlError.Number}else{$null}} | ConvertTo-Json -Compress
  exit 1
} finally { if($connection){$connection.Dispose()} }
