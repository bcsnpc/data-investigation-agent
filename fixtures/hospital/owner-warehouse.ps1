param(
    [Parameter(Mandatory=$true)][string]$Requirements,
    [Parameter(Mandatory=$true)][string]$Receipt,
    [Parameter(Mandatory=$true)][string]$BootstrapSql,
    [Parameter(Mandatory=$true)][string]$AzurePython,
    [Parameter(Mandatory=$true)][string]$AzureProfile,
    [switch]$InspectOnly,
    [string]$MartsSql,
    [switch]$InspectRaw,
    [string]$ReadSql
)
$ErrorActionPreference = 'Stop'
$config = Get-Content -LiteralPath $Requirements -Raw | ConvertFrom-Json
if ($config.warehouse_id -ne 'ef705467-9870-481c-b977-aad877b83c30') { throw 'Only HealthNet warehouse is approved' }
$result = [ordered]@{database_id=$config.warehouse_id;server=$config.warehouse_server;identity='existing Fabric owner via isolated Azure profile';operation='HealthNet bootstrap only; no grants';client='System.Data.SqlClient'}
if ($ReadSql) { $result.operation = 'HealthNet owner reconciliation SELECT only' }
if ($MartsSql) { $result.operation = 'HealthNet marts/procedures only; existing bootstrap retained; no grants' }
if ($InspectRaw) { $result.operation = 'HealthNet raw SQL endpoint metadata SELECT only' }
if ($InspectOnly) { $result.operation = 'HealthNet audit/control SELECT only; no grants or writes' }
$connection = $null
try {
    $previousProfile = $env:AZURE_CONFIG_DIR
    try {
        $env:AZURE_CONFIG_DIR = $AzureProfile
        $auth = (& $AzurePython -m azure.cli account get-access-token --resource 'https://database.windows.net/' --tenant 'dff91047-ebc2-4657-8dbe-5af328d57780' -o json | ConvertFrom-Json)
        if ($LASTEXITCODE -ne 0) { throw 'Existing owner token request failed' }
    } finally { $env:AZURE_CONFIG_DIR = $previousProfile }
    $builder = New-Object System.Data.SqlClient.SqlConnectionStringBuilder
    $builder['Data Source'] = 'tcp:' + $config.warehouse_server + ',1433'
    $builder['Initial Catalog'] = $config.warehouse_id
    $builder['Encrypt'] = $true
    $builder['TrustServerCertificate'] = $false
    $builder['Connect Timeout'] = 60
    $builder['Application Name'] = 'HealthNet-owner-build'
    $connection = New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
    $connection.AccessToken = $auth.accessToken
    $auth = $null
    $connection.Open()
    $command = $connection.CreateCommand()
    $command.CommandTimeout = 180
    $command.CommandText = 'SELECT SUSER_SNAME()'
    $result.served_identity = $command.ExecuteScalar()
    $command.CommandText = 'SELECT COUNT(*) FROM sys.tables'
    $result.tables_before = $command.ExecuteScalar()
    if ($ReadSql) {
        $text = Get-Content -LiteralPath $ReadSql -Raw
        if ($text -match '(?i)\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|GRANT|REVOKE|TRUNCATE|MERGE)\b') { throw 'Reconciliation file must contain SELECT statements only' }
        $command.CommandText = $text
        $command.CommandTimeout = 900
        $reader = $command.ExecuteReader()
        $sets = @()
        try {
            do {
                $rows = @()
                while ($reader.Read()) {
                    $row = [ordered]@{}
                    for ($index=0; $index -lt $reader.FieldCount; $index++) {
                        $value = $reader.GetValue($index)
                        if ($value -is [DBNull]) { $value = $null }
                        elseif ($value -is [DateTime]) { $value = $value.ToString('o') }
                        $row[$reader.GetName($index)] = $value
                    }
                    $rows += $row
                }
                $sets += ,@($rows)
            } while ($reader.NextResult())
        } finally { $reader.Close() }
        $result.result_sets = $sets
    } elseif ($InspectRaw) {
        $command.CommandText = 'SELECT t.name table_name,c.name column_name,ty.name type_name FROM hn_raw.sys.tables t JOIN hn_raw.sys.columns c ON c.object_id=t.object_id JOIN hn_raw.sys.types ty ON ty.user_type_id=c.user_type_id ORDER BY t.name,c.column_id'
        $reader = $command.ExecuteReader()
        $rows = @()
        try { while ($reader.Read()) { $rows += [ordered]@{table=$reader.GetString(0);column=$reader.GetString(1);type=$reader.GetString(2)} } } finally { $reader.Close() }
        $result.raw_columns = $rows
    } elseif ($MartsSql) {
        $command.CommandText = "SELECT COUNT(*) FROM sys.tables WHERE name='core_facility'"
        if ($command.ExecuteScalar() -ne 0) { throw 'Marts already exist or partial deployment: inspect before resuming' }
        $result.completed_batches = @()
        $batches = [regex]::Split((Get-Content -LiteralPath $MartsSql -Raw), '(?im)^\s*GO\s*$')
        foreach ($batch in $batches) {
            if ([string]::IsNullOrWhiteSpace($batch)) { continue }
            $command.CommandTimeout = 900
            $command.CommandText = $batch
            [void]$command.ExecuteNonQuery()
            $result.completed_batches += $batch.Substring(0,[Math]::Min(120,$batch.Length))
            $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Receipt -Encoding UTF8
        }
    } elseif ($InspectOnly) {
        $command.CommandText = 'SELECT run_id,pipeline_name,table_name,status,rows_read,rows_written FROM dbo.load_audit ORDER BY pipeline_name,table_name,run_id'
        $reader = $command.ExecuteReader()
        $audit = @()
        try {
            while ($reader.Read()) {
                $row = [ordered]@{}
                for ($index=0; $index -lt $reader.FieldCount; $index++) {
                    $row[$reader.GetName($index)] = $reader.GetValue($index)
                }
                $audit += $row
            }
        } finally { $reader.Close() }
        $result.audit_rows = $audit
    } else {
        if ($result.tables_before -ne 0) { throw 'Existing tables: inspect before resuming; no overwrite' }
        $command.CommandText = Get-Content -LiteralPath $BootstrapSql -Raw
        [void]$command.ExecuteNonQuery()
    }
    $command.CommandText = 'SELECT COUNT(*) FROM dbo.core_date'
    $result.calendar_rows = $command.ExecuteScalar()
    $command.CommandText = 'SELECT COUNT(*) FROM dbo.security_mapping'
    $result.security_rows = $command.ExecuteScalar()
    $result.status = 'SUCCEEDED'
} catch {
    $result.status = 'FAILED'
    $result.error_type = $_.Exception.GetType().FullName
    $result.error = $_.Exception.Message
} finally {
    if ($null -ne $connection) { $connection.Dispose() }
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Receipt -Encoding UTF8
}
if ($result.status -ne 'SUCCEEDED') { Write-Output $result.error; exit 1 }
if ($ReadSql) { Write-Output 'HealthNet owner reconciliation SELECTs completed; receipt saved.' }
elseif ($MartsSql) { Write-Output 'HealthNet marts/procedures deployed; receipt saved.' }
elseif ($InspectRaw) { Write-Output 'HealthNet raw SQL metadata inspected; receipt saved.' }
elseif ($InspectOnly) { Write-Output 'HealthNet warehouse inspection succeeded; receipt saved.' }
else { Write-Output 'HealthNet warehouse bootstrap succeeded; receipt saved.' }
