[CmdletBinding()]
param([string]$OutputPath)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not $OutputPath) { $OutputPath=Join-Path $projectRoot '.local/sql-metadata.json' }
Add-Type -AssemblyName System.Data
$credential=Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/runtime-credentials/orderops_investigator.credential.xml')
$credential.Password.MakeReadOnly()
$connection=New-Object System.Data.SqlClient.SqlConnection('Data Source=tcp:sql-orderops-9696025.database.windows.net,1433;Initial Catalog=ordersops;Encrypt=True;TrustServerCertificate=False;Connect Timeout=60')
$connection.Credential=New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
$queries=[ordered]@{
 objects="SELECT o.object_id, s.name AS schema_name,o.name,o.type_desc,o.create_date,o.modify_date FROM sys.objects o JOIN sys.schemas s ON s.schema_id=o.schema_id WHERE o.is_ms_shipped=0 AND o.type IN ('U','V','P','FN','IF','TF')"
 columns="SELECT c.object_id,c.column_id,c.name,t.name AS data_type,c.max_length,c.precision,c.scale,c.is_nullable,c.is_identity,cc.definition AS computed_definition,dc.definition AS default_definition FROM sys.columns c JOIN sys.objects o ON o.object_id=c.object_id JOIN sys.types t ON t.user_type_id=c.user_type_id LEFT JOIN sys.computed_columns cc ON cc.object_id=c.object_id AND cc.column_id=c.column_id LEFT JOIN sys.default_constraints dc ON dc.object_id=c.default_object_id WHERE o.is_ms_shipped=0"
 keys="SELECT i.object_id,i.name,i.is_primary_key,i.is_unique,ic.key_ordinal,c.name AS column_name FROM sys.indexes i JOIN sys.index_columns ic ON ic.object_id=i.object_id AND ic.index_id=i.index_id JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id JOIN sys.objects o ON o.object_id=i.object_id WHERE o.is_ms_shipped=0 AND i.is_unique=1 AND ic.key_ordinal>0"
 foreign_keys="SELECT fk.name,fkc.parent_object_id,fkc.parent_column_id,fkc.referenced_object_id,fkc.referenced_column_id,fkc.constraint_column_id,fk.is_disabled,fk.is_not_trusted FROM sys.foreign_keys fk JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id=fk.object_id"
 definitions="SELECT object_id,definition FROM sys.sql_modules WHERE OBJECTPROPERTY(object_id,'IsMSShipped')=0"
 checks="SELECT parent_object_id,name,definition,is_disabled,is_not_trusted FROM sys.check_constraints WHERE is_ms_shipped=0"
 permissions="SELECT HAS_PERMS_BY_NAME('app','SCHEMA','VIEW DEFINITION') AS can_view_definition"
}
try {
 $connection.Open()
 $result=[ordered]@{server=$connection.DataSource;database=$connection.Database;collected_at_utc=[DateTime]::UtcNow.ToString('o')}
 foreach($entry in $queries.GetEnumerator()) {
  $command=$connection.CreateCommand(); $command.CommandTimeout=60; $command.CommandText=$entry.Value
  $reader=$command.ExecuteReader(); $rows=New-Object System.Collections.Generic.List[object]
  try {
   while($reader.Read()) {
    $row=[ordered]@{}
    for($i=0;$i -lt $reader.FieldCount;$i++) {
     $value=$reader.GetValue($i)
     if($value -is [DBNull]) { $value=$null }
     elseif($value -is [DateTime]) { $value=$value.ToString('o') }
     $row[$reader.GetName($i)]=$value
    }
    $rows.Add($row)
   }
  } finally { $reader.Dispose(); $command.Dispose() }
  $result[$entry.Key]=@($rows.ToArray())
 }
 $result | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 -LiteralPath $OutputPath
 Write-Output 'SQL metadata captured using the investigator identity.'
} finally { $connection.Dispose() }
