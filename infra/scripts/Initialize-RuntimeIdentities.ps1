$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'RuntimeSql.Common.ps1')
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$credentialRoot = Join-Path $projectRoot '.local/runtime-credentials'
$identities = [ordered]@{
 'orderops_app' = 'orderops_app_role'
 'orderops_fabric' = 'orderops_fabric_role'
 'orderops_investigator' = 'orderops_investigator_role'
}
$conn = Open-OrderOpsConnection (Join-Path $projectRoot '.local/azure-sql.credential.xml')
$tx = $null
try {
 $tx = $conn.BeginTransaction()
 $cmd = $conn.CreateCommand(); $cmd.Transaction = $tx; $cmd.CommandTimeout = 60
 $cmd.CommandText = "DECLARE @r int; EXEC @r=sys.sp_getapplock @Resource='runtime-identities',@LockMode='Exclusive',@LockOwner='Transaction',@LockTimeout=0; SELECT @r;"
 if ([int]$cmd.ExecuteScalar() -lt 0) { throw 'Another identity setup is running.' }
 $cmd.CommandText = Get-Content -LiteralPath (Join-Path $projectRoot 'infra/sql/004_runtime_roles.sql') -Raw
 $null = $cmd.ExecuteNonQuery()
 New-Item -ItemType Directory -Path $credentialRoot -Force | Out-Null
 foreach ($entry in $identities.GetEnumerator()) {
  $path = Join-Path $credentialRoot ($entry.Key+'.credential.xml')
  $cmd.Parameters.Clear()
  $cmd.CommandText = 'SELECT COUNT(*) FROM sys.database_principals WHERE name=@name'
  $null = $cmd.Parameters.Add('@name',[System.Data.SqlDbType]::NVarChar,128)
  $cmd.Parameters['@name'].Value = $entry.Key
  $exists = [int]$cmd.ExecuteScalar() -gt 0
  if ($exists -and !(Test-Path -LiteralPath $path)) { throw "Existing user $($entry.Key) has no saved credential; refusing automatic password rotation." }
  if (!(Test-Path -LiteralPath $path)) {
   $bytes = New-Object byte[] 32
   $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
   try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
   $password = 'aA1!'+[Convert]::ToBase64String($bytes)
   $secure = ConvertTo-SecureString $password -AsPlainText -Force
   $credential = New-Object System.Management.Automation.PSCredential($entry.Key,$secure)
   $credential | Export-Clixml -LiteralPath $path
   $password = $null
  }
  $credential = Import-Clixml -LiteralPath $path
  if ($credential.UserName -ne $entry.Key) { throw 'Credential username mismatch.' }
  if (!$exists) {
   # DDL is composed on the server with QUOTENAME. Password is a bound parameter,
   # never embedded in command text, logs, command-line arguments or source files.
   $cmd.CommandText = "DECLARE @ddl nvarchar(max)=N'CREATE USER '+QUOTENAME(@name)+N' WITH PASSWORD = '+QUOTENAME(@password,CHAR(39))+N', DEFAULT_SCHEMA=app'; EXEC sys.sp_executesql @ddl;"
   $null = $cmd.Parameters.Add('@password',[System.Data.SqlDbType]::NVarChar,128)
   $cmd.Parameters['@password'].Value = $credential.GetNetworkCredential().Password
   try { $null = $cmd.ExecuteNonQuery() } catch { throw "Failed to provision $($entry.Key); SQL details suppressed to protect credentials." }
   finally { $cmd.Parameters.RemoveAt('@password') }
  }
  $cmd.Parameters.Clear()
  $cmd.CommandText = "GRANT CONNECT TO [$($entry.Key)]; ALTER ROLE [$($entry.Value)] ADD MEMBER [$($entry.Key)];"
  $null = $cmd.ExecuteNonQuery()
  Write-Output "Configured $($entry.Key) in $($entry.Value)"
 }
 $tx.Commit(); $tx = $null
 Write-Output 'Runtime identities committed. Credentials saved encrypted under .local/runtime-credentials/.'
} finally {
 if ($tx) { try { $tx.Rollback() } catch {} }
 $conn.Dispose()
}
