param([switch]$SaveCredentialOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$credentialDirectory = Join-Path $projectRoot '.local'
$credentialPath = Join-Path $credentialDirectory 'azure-sql.credential.xml'
if ($SaveCredentialOnly -or !(Test-Path -LiteralPath $credentialPath)) {
    $sqlUser = Read-Host 'SQL admin username (press Enter for pocsqladmin)'
    if ([string]::IsNullOrWhiteSpace($sqlUser)) { $sqlUser = 'pocsqladmin' }
    $sqlPassword = Read-Host 'SQL admin password (input is hidden)' -AsSecureString
    if ($sqlPassword.Length -eq 0) { throw 'Password cannot be empty.' }
    $credential = New-Object System.Management.Automation.PSCredential($sqlUser, $sqlPassword)
    New-Item -ItemType Directory -Path $credentialDirectory -Force | Out-Null
    $credential | Export-Clixml -LiteralPath $credentialPath
    if ($SaveCredentialOnly) { Write-Output 'Encrypted credential saved locally. No database changes made.'; return }
}
$credential = Import-Clixml -LiteralPath $credentialPath
Add-Type -AssemblyName System.Data
$builder = New-Object System.Data.SqlClient.SqlConnectionStringBuilder
$builder['Data Source'] = 'tcp:sql-orderops-9696025.database.windows.net,1433'
$builder['Initial Catalog'] = 'ordersops'
$builder['Encrypt'] = $true
$builder['TrustServerCertificate'] = $false
$builder['Connect Timeout'] = 60
$credential.Password.MakeReadOnly()
$sqlCredential = New-Object System.Data.SqlClient.SqlCredential($credential.UserName, $credential.Password)
$connection = New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
$connection.Credential = $sqlCredential
try {
    $connection.Open()
    $command = $connection.CreateCommand()
    $command.CommandTimeout = 120
    $command.CommandText = Get-Content -LiteralPath (Join-Path $projectRoot 'infra/sql/001_application_schema.sql') -Raw
    $null = $command.ExecuteNonQuery()
    $command.CommandText = "SELECT name FROM sys.tables WHERE schema_id = SCHEMA_ID('app') ORDER BY name"
    $reader = $command.ExecuteReader()
    while ($reader.Read()) { Write-Output ('Verified table: app.' + $reader.GetString(0)) }
    $reader.Close()
} finally {
    $connection.Dispose()
}
