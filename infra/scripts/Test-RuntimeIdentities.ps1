$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'RuntimeSql.Common.ps1')
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$tables = @('customers','products','orders','order_lines','payments','shipments','shipment_lines','refunds','refund_lines','audit_log')
$checks = 0
function Test-Operation {
 param($Connection,[string]$Sql,[bool]$Allowed,[string]$Label)
 $tx = $Connection.BeginTransaction()
 $cmd = $Connection.CreateCommand(); $cmd.Transaction = $tx; $cmd.CommandText = $Sql; $cmd.CommandTimeout = 30
 try {
  $denied = $false
  try { $null = $cmd.ExecuteNonQuery() }
  catch [System.Data.SqlClient.SqlException] {
   if ($_.Exception.Number -notin @(229,262,15151,15247)) { throw }
   $denied = $true
  }
  if ($Allowed -eq $denied) { throw "Unexpected permission result: $Label (allowed=$Allowed, denied=$denied)" }
  $script:checks++
 } finally { $tx.Rollback(); $cmd.Dispose() }
}
foreach ($user in @('orderops_app','orderops_fabric','orderops_investigator')) {
 $conn = Open-OrderOpsConnection (Join-Path $projectRoot ".local/runtime-credentials/$user.credential.xml")
 try {
  $cmd = $conn.CreateCommand()
  $cmd.CommandText = 'SELECT CURRENT_USER'
  if ($cmd.ExecuteScalar() -ne $user) { throw 'Incorrect authenticated identity.' }
  $checks++
  foreach ($table in $tables) {
   Test-Operation $conn "SELECT TOP (1) * FROM app.[$table]" $true "$user SELECT $table"
   foreach ($permission in @('INSERT','UPDATE','DELETE')) {
    $expected = $user -eq 'orderops_app' -and $permission -ne 'DELETE' -and ($table -ne 'audit_log' -or $permission -eq 'INSERT')
    $cmd.CommandText = "SELECT HAS_PERMS_BY_NAME('app.$table','OBJECT','$permission')"
    if ([int]$cmd.ExecuteScalar() -ne [int]$expected) { throw "$user unexpected $permission permission on $table" }
    $checks++
   }
  }
  # Successful write probes are always rolled back; denied probes select no rows.
  $isApp = $user -eq 'orderops_app'
  Test-Operation $conn "UPDATE app.orders SET status=status WHERE order_id='ORD-000002'" $isApp "$user UPDATE orders"
  Test-Operation $conn "INSERT INTO app.customers(customer_id,customer_name) VALUES('PERMISSION-PROBE','Permission probe')" $isApp "$user INSERT customer"
  Test-Operation $conn "INSERT INTO app.audit_log(event_id,entity_type,entity_id,operation,user_id) VALUES('PERMISSION-PROBE','order','PERMISSION-PROBE','TEST','permission_test')" $isApp "$user INSERT audit"
  Test-Operation $conn 'DELETE FROM app.orders WHERE 1=0' $false "$user DELETE orders"
  Test-Operation $conn 'UPDATE app.audit_log SET operation=operation WHERE 1=0' $false "$user UPDATE audit"
  Test-Operation $conn 'DELETE FROM app.audit_log WHERE 1=0' $false "$user DELETE audit"
  Test-Operation $conn 'UPDATE app.dataset_runs SET status=status WHERE 1=0' $false "$user UPDATE manifest"
  Test-Operation $conn 'CREATE TABLE app.permission_probe(id int)' $false "$user CREATE TABLE"
  $cmd.CommandText = "SELECT HAS_PERMS_BY_NAME('app','SCHEMA','ALTER')+HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','ALTER ANY USER')+HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','ALTER ANY ROLE')+HAS_PERMS_BY_NAME('app','SCHEMA','EXECUTE')"
  if ([int]$cmd.ExecuteScalar() -ne 0) { throw "$user has excessive administrative/execute permissions" }
  $checks++
  if ($user -eq 'orderops_investigator') {
   $cmd.CommandText = "SELECT HAS_PERMS_BY_NAME('app','SCHEMA','VIEW DEFINITION')"
   if ([int]$cmd.ExecuteScalar() -ne 1) { throw 'Investigator metadata permission missing.' }
   $cmd.CommandText = "SELECT COUNT(*) FROM sys.columns WHERE object_id=OBJECT_ID('app.orders')"
   if ([int]$cmd.ExecuteScalar() -lt 10) { throw 'Investigator cannot discover order columns.' }
   $checks+=2
  }
  Write-Output "PASS: $user authenticated; reads, write boundaries and administrative restrictions verified."
 } finally { $conn.Dispose() }
}
Write-Output "PASS: $checks live permission checks; all write probes rolled back."
