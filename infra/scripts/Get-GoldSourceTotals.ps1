$ErrorActionPreference='Stop'
$projectRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Add-Type -AssemblyName System.Data
$credential=Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/runtime-credentials/orderops_app.credential.xml')
$credential.Password.MakeReadOnly()
$connection=New-Object System.Data.SqlClient.SqlConnection('Data Source=tcp:sql-orderops-9696025.database.windows.net,1433;Initial Catalog=ordersops;Encrypt=True;TrustServerCertificate=False;Connect Timeout=60')
$connection.Credential=New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
try {
 $connection.Open()
 $command=$connection.CreateCommand()
 $command.CommandTimeout=120
 $command.CommandText=Get-Content -LiteralPath (Join-Path $projectRoot 'infra/sql/005_gold_source_totals.sql') -Raw
 $reader=$command.ExecuteReader()
 $rows=@()
 while($reader.Read()) {
  $row=@{}
  for($i=0;$i -lt $reader.FieldCount;$i++) {
   $value=$reader.GetValue($i)
   if($value -is [System.IFormattable]) { $value=$value.ToString($null,[System.Globalization.CultureInfo]::InvariantCulture) }
   $row[$reader.GetName($i)]=$value
  }
  $rows+=$row
 }
 ConvertTo-Json -InputObject $rows -Depth 4 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $projectRoot '.local/gold-source-totals.json')
 Write-Output 'Captured read-only Azure SQL totals in .local/gold-source-totals.json.'
} finally { $connection.Dispose() }
