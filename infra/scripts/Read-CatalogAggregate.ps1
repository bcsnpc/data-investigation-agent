# Internal transport for the catalog compiler, not a public arbitrary-SQL API.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Data
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$connection = $null
$command = $null
$reader = $null
$stage = 'connect'
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
    $stage = 'query'
    $command = $connection.CreateCommand()
    $command.CommandTimeout = 30
    $command.CommandText = $request.query
    foreach ($parameter in $request.parameters) {
        $null = $command.Parameters.Add($parameter.name, [System.Data.SqlDbType]::NVarChar, 200)
        $command.Parameters[$parameter.name].Value = $parameter.value
    }
    $reader = $command.ExecuteReader()
    if ($request.response_mode -eq 'records') {
        if ($request.max_rows -lt 2 -or $request.max_rows -gt 251) { throw 'Invalid record budget' }
        $columns = @($request.result_columns)
        if ($columns.Count -lt 2 -or $columns.Count -gt 9 -or $reader.FieldCount -ne $columns.Count) { throw 'Invalid record shape' }
        for ($index = 0; $index -lt $columns.Count; $index++) {
            if ($reader.GetName($index) -cne $columns[$index]) { throw 'Record column differs' }
        }
        $rows = New-Object System.Collections.Generic.List[object]
        while ($reader.Read()) {
            if ($rows.Count -ge $request.max_rows) { throw 'Record response exceeds budget' }
            $row = [ordered]@{}
            for ($index = 0; $index -lt $columns.Count; $index++) {
                $value = $reader.GetValue($index)
                if ($value -is [DBNull]) { $row[$columns[$index]] = $null }
                else {
                    $value = $value.ToString([Globalization.CultureInfo]::InvariantCulture)
                    if ($value.Length -gt 1000) { throw 'Record value exceeds budget' }
                    $row[$columns[$index]] = $value
                }
            }
            $rows.Add($row)
        }
        if ($reader.NextResult()) { throw 'Unexpected extra record result' }
        @{rows=@($rows.ToArray())} | ConvertTo-Json -Depth 8 -Compress
        return
    }
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
    @{error='SourceReadFailed'; error_number=$number; error_kind=$failure.GetType().Name; stage=$stage} | ConvertTo-Json -Compress
    exit 1
} finally {
    if ($reader) { $reader.Dispose() }
    if ($command) { $command.Dispose() }
    if ($connection) { $connection.Dispose() }
}
