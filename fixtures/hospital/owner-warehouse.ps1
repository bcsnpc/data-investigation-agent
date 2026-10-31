param(
    [Parameter(Mandatory=$true)][string]$Requirements,
    [Parameter(Mandatory=$true)][string]$Receipt,
    [Parameter(Mandatory=$true)][string]$BootstrapSql,
    [Parameter(Mandatory=$true)][string]$AzurePython,
    [Parameter(Mandatory=$true)][string]$AzureProfile,
    [switch]$InspectOnly
)
$ErrorActionPreference = 'Stop'
$config = Get-Content -LiteralPath $Requirements -Raw | ConvertFrom-Json
if ($config.warehouse_id -ne 'ef705467-9870-481c-b977-aad877b83c30') { throw 'Only HealthNet warehouse is approved' }
$result = [ordered]@{database_id=$config.warehouse_id;server=$config.warehouse_server;identity='existing Fabric owner via isolated Azure profile';operation='HealthNet bootstrap only; no grants';client='System.Data.SqlClient'}
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
    if ($InspectOnly) {
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
if ($InspectOnly) { Write-Output 'HealthNet warehouse inspection succeeded; receipt saved.' }
else { Write-Output 'HealthNet warehouse bootstrap succeeded; receipt saved.' }
