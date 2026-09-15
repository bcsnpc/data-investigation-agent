# Internal transport for the catalog compiler, not a public arbitrary-SQL API.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Data
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$connection = $null
$command = $null
$reader = $null
try {
    $credential = Import-Clixml -LiteralPath $request.credential_file
    $credential.Password.MakeReadOnly()
    $builder = New-Object System.Data.SqlClient.SqlConnectionStringBuilder
    $builder['Data Source'] = "tcp:$($request.server),1433"
    $builder['Initial Catalog'] = $request.database
    $builder['Encrypt'] = $true
    $builder['TrustServerCertificate'] = $false
    $builder['ApplicationIntent'] = 'ReadOnly'
    $builder['Connect Timeout'] = 30
    $connection = New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
    $connection.Credential = New-Object System.Data.SqlClient.SqlCredential($credential.UserName, $credential.Password)
    $connection.Open()
    $command = $connection.CreateCommand()
    $command.CommandTimeout = 30
    $command.CommandText = $request.query
    foreach ($parameter in $request.parameters) {
        $null = $command.Parameters.Add($parameter.name, [System.Data.SqlDbType]::NVarChar, 200)
        $command.Parameters[$parameter.name].Value = $parameter.value
    }
    $reader = $command.ExecuteReader()
    if (-not $reader.Read() -or $reader.FieldCount -ne 3) { throw 'Unexpected aggregate result' }
    $result = [ordered]@{}
    for ($index = 0; $index -lt 3; $index++) {
        $value = $reader.GetValue($index)
        if ($value -is [DBNull]) { $result[$reader.GetName($index)] = $null }
        else { $result[$reader.GetName($index)] = $value.ToString([Globalization.CultureInfo]::InvariantCulture) }
    }
    if ($reader.Read() -or $reader.NextResult()) { throw 'Unexpected extra result' }
    $result | ConvertTo-Json -Compress
} catch {
    # Never emit connection strings, SQL errors, credentials or exception text.
    $failure = $_.Exception
    while ($failure.InnerException) { $failure = $failure.InnerException }
    $number = $null
    if ($failure -is [System.Data.SqlClient.SqlException]) { $number = $failure.Number }
    @{error='SourceReadFailed'; error_number=$number; error_kind=$failure.GetType().Name} | ConvertTo-Json -Compress
    exit 1
} finally {
    if ($reader) { $reader.Dispose() }
    if ($command) { $command.Dispose() }
    if ($connection) { $connection.Dispose() }
}
