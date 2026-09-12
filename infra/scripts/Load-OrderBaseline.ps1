param([Parameter(Mandatory=$true)][string]$DatasetDirectory, [switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$datasetPath = (Resolve-Path -LiteralPath $DatasetDirectory).Path
$manifestPath = Join-Path $datasetPath 'manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.validation -ne 'passed') { throw 'Dataset has not passed validation.' }
$tables = @('customers','products','orders','order_lines','payments','shipments','shipment_lines','refunds','refund_lines','audit_log')
foreach ($table in $tables) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $datasetPath "$table.tsv") -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $manifest.files.$table) { throw "Checksum mismatch: $table" }
}
Add-Type -AssemblyName System.Data
# Compiled streaming TSV reader avoids holding the complete dataset in RAM.
Add-Type -ReferencedAssemblies System.Data,System.Xml -TypeDefinition @'
using System;
using System.Data;
using System.Data.SqlClient;
using System.IO;
using System.Globalization;
public static class OrderBaselineBulk {
 public static long Load(SqlConnection conn, SqlTransaction tx, string table, string path) {
  using(var cmd = new SqlCommand("SELECT TOP (0) * FROM app.[" + table + "]", conn, tx))
  using(var adapter = new SqlDataAdapter(cmd))
  using(var data = new DataTable())
  using(var input = new StreamReader(path)) {
   adapter.FillSchema(data, SchemaType.Source);
   string[] columns = input.ReadLine().Split('\t');
   using(var bulk = new SqlBulkCopy(conn, SqlBulkCopyOptions.CheckConstraints, tx)) {
    bulk.DestinationTableName = "app.[" + table + "]";
    bulk.BatchSize = 5000;
    bulk.BulkCopyTimeout = 600;
    foreach(string col in columns) bulk.ColumnMappings.Add(col,col);
    long count = 0;
    string line;
    while((line = input.ReadLine()) != null) {
     string[] values = line.Split('\t');
     if(values.Length != columns.Length) throw new Exception("Invalid TSV row in " + table);
     DataRow row = data.NewRow();
     for(int i=0;i<columns.Length;i++) {
      Type type = data.Columns[columns[i]].DataType;
      row[columns[i]] = values[i] == "\\N" ? DBNull.Value :
       type == typeof(bool) ? (object)(values[i] == "1") :
       Convert.ChangeType(values[i],type,CultureInfo.InvariantCulture);
     }
     data.Rows.Add(row);
     count++;
     if(data.Rows.Count == 5000) { bulk.WriteToServer(data); data.Clear(); }
    }
    if(data.Rows.Count > 0) bulk.WriteToServer(data);
    return count;
   }
  }
 }
}
'@
$credential = Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/azure-sql.credential.xml')
$credential.Password.MakeReadOnly()
$connection = New-Object System.Data.SqlClient.SqlConnection('Data Source=tcp:sql-orderops-9696025.database.windows.net,1433;Initial Catalog=ordersops;Encrypt=True;TrustServerCertificate=False;Connect Timeout=60')
$connection.Credential = New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
$transaction = $null
try {
 $connection.Open()
 $cmd = $connection.CreateCommand()
 $cmd.CommandTimeout = 600
 $cmd.CommandText = Get-Content -LiteralPath (Join-Path $projectRoot 'infra/sql/002_order_lifecycle.sql') -Raw
 $null = $cmd.ExecuteNonQuery()
 $transaction = $connection.BeginTransaction()
 $cmd.Transaction = $transaction
 $cmd.CommandText = "DECLARE @result int; EXEC @result = sys.sp_getapplock @Resource=N'order-baseline-load', @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=0; SELECT @result;"
 if ([int]$cmd.ExecuteScalar() -lt 0) { throw 'Another baseline loader is active.' }
 $cmd.CommandText = 'SELECT manifest_sha256 FROM app.dataset_runs WHERE dataset_id=@id AND status=''READY'''
 $null = $cmd.Parameters.Add('@id',[System.Data.SqlDbType]::NVarChar,64)
 $cmd.Parameters['@id'].Value = $manifest.dataset_id
 $existing = $cmd.ExecuteScalar()
 $manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
 if ($existing) {
  if ($existing -ne $manifestHash) { throw 'Dataset ID already exists with a different manifest.' }
  $transaction.Rollback(); $transaction = $null
  Write-Output 'Dataset already loaded with matching manifest; no changes made.'
  return
 }
 $cmd.Parameters.Clear()
 foreach ($table in $tables) {
  $cmd.CommandText = "SELECT COUNT_BIG(*) FROM app.[$table]"
  if ([long]$cmd.ExecuteScalar() -ne 0) { throw "app.$table is not empty. Refusing to overwrite existing data." }
 }
 foreach ($table in $tables) {
  $loaded = [OrderBaselineBulk]::Load($connection,$transaction,$table,(Join-Path $datasetPath "$table.tsv"))
  if ($loaded -ne $manifest.counts.$table) { throw "Unexpected row count for $table" }
  Write-Output "Loaded app.${table}: $loaded rows (pending commit)"
 }
 $cmd.CommandText = Get-Content -LiteralPath (Join-Path $projectRoot 'infra/sql/003_validate_baseline.sql') -Raw
 $null = $cmd.Parameters.Add('@cutoff',[System.Data.SqlDbType]::DateTime2)
 $cmd.Parameters['@cutoff'].Value = [datetime]$manifest.as_of
 $null = $cmd.ExecuteNonQuery()
 $cmd.Parameters.Clear()
 foreach ($table in $tables) {
  $cmd.CommandText = "SELECT COUNT_BIG(*) FROM app.[$table]"
  if ([long]$cmd.ExecuteScalar() -ne $manifest.counts.$table) { throw "SQL row count mismatch: $table" }
 }
 if ($ValidateOnly) {
  $transaction.Rollback(); $transaction = $null
  Write-Output 'VALIDATED: SQL reconciliation and row counts passed; sample data rolled back.'
  return
 }
 $cmd.CommandText = 'INSERT INTO app.dataset_runs(dataset_id,seed,as_of,order_count,manifest_sha256,status) VALUES(@id,@seed,@asof,@count,@hash,''READY'')'
 $null = $cmd.Parameters.Add('@id',[System.Data.SqlDbType]::NVarChar,64); $cmd.Parameters['@id'].Value = $manifest.dataset_id
 $null = $cmd.Parameters.Add('@seed',[System.Data.SqlDbType]::Int); $cmd.Parameters['@seed'].Value = $manifest.seed
 $null = $cmd.Parameters.Add('@asof',[System.Data.SqlDbType]::DateTime2); $cmd.Parameters['@asof'].Value = [datetime]$manifest.as_of
 $null = $cmd.Parameters.Add('@count',[System.Data.SqlDbType]::Int); $cmd.Parameters['@count'].Value = $manifest.orders
 $null = $cmd.Parameters.Add('@hash',[System.Data.SqlDbType]::Char,64); $cmd.Parameters['@hash'].Value = $manifestHash
 $null = $cmd.ExecuteNonQuery()
 $transaction.Commit(); $transaction = $null
 Write-Output 'COMMITTED: SQL reconciliation and all row counts passed. Dataset status READY.'
} catch {
 if ($transaction) { try { $transaction.Rollback() } catch {} }
 throw
} finally { $connection.Dispose() }
