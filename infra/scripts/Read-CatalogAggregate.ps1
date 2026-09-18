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
    if ($request.require_read_only) {
        # ApplicationIntent alone does not enforce read-only access. Verify the
        # configured principal's effective permissions before proposed SQL runs.
        $guard = $connection.CreateCommand()
        try {
            $guard.CommandTimeout = 15
            $guard.CommandText = "SELECT COUNT(*) FROM sys.fn_my_permissions(NULL,'DATABASE') WHERE permission_name NOT IN ('CONNECT','SELECT','VIEW DEFINITION','VIEW DATABASE STATE','VIEW DATABASE PERFORMANCE STATE','VIEW DATABASE SECURITY STATE')"
            if ([int]$guard.ExecuteScalar() -ne 0) { throw 'Proposed SQL requires a read-only principal' }
            $objects = @($request.read_only_objects)
            if ($objects.Count -lt 1 -or $objects.Count -gt 24) { throw 'Invalid object permission scope' }
            $guard.CommandText = "SELECT COUNT(*) FROM sys.fn_my_permissions(@object,'OBJECT') WHERE permission_name NOT IN ('SELECT','VIEW DEFINITION')"
            $null = $guard.Parameters.Add('@object', [System.Data.SqlDbType]::NVarChar, 300)
            foreach ($objectName in $objects) {
                $guard.Parameters['@object'].Value = $objectName
                if ([int]$guard.ExecuteScalar() -ne 0) { throw 'Proposed SQL object is not read-only' }
            }
            $guard.Parameters.Clear()
            $guard.CommandText = 'SELECT CURRENT_USER'
            $sourcePrincipal = [string]$guard.ExecuteScalar()
        } finally { $guard.Dispose() }
    }
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
        $minimumColumns = 2
        $maximumColumns = 9
        if ($request.require_read_only) { $minimumColumns = 1; $maximumColumns = 16 }
        if ($columns.Count -lt $minimumColumns -or $columns.Count -gt $maximumColumns -or $reader.FieldCount -ne $columns.Count) { throw 'Invalid record shape' }
        for ($index = 0; $index -lt $columns.Count; $index++) {
            if ($reader.GetName($index) -cne $columns[$index]) { throw 'Record column differs' }
        }
        $types = @{}
        if ($request.require_read_only) {
            for ($index = 0; $index -lt $columns.Count; $index++) { $types[$columns[$index]] = $reader.GetFieldType($index).Name }
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
        $result = @{rows=@($rows.ToArray())}
        if ($request.require_read_only) {
            $result.read_only_verified = $true
            $result.column_types = $types
            $result.execution_identity = @{principal=$sourcePrincipal;server=$request.server;database=$request.database;provenance='TRANSPORT_PERMISSION_CHECK'}
        }
        $result | ConvertTo-Json -Depth 8 -Compress
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
