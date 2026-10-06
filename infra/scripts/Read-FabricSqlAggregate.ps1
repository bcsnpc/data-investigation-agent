param([switch]$Metered)
# Internal transport for compiled, admitted reads against a Fabric SQL analytics
# endpoint. Not a public arbitrary-SQL API: the query arrives already compiled
# against a declared catalog. The database is always named. In the same
# connection the endpoint reports who connected and to which database, and the
# principal's effective permissions are checked to be read-only first.
function Begin-PhysicalRead([string]$Kind) {
    if ($Metered) {
        [Console]::Out.WriteLine((@{physical_read='REQUEST';kind=$Kind} | ConvertTo-Json -Compress))
        [Console]::Out.Flush()
        if ([Console]::In.ReadLine() -cne 'ALLOW') { throw 'Read admission refused' }
    }
}
function Begin-Guard([string]$Kind, [string]$ObjectName = '') {
    if (-not $Metered) { return $true }
    [Console]::Out.WriteLine((@{physical_read='REQUEST';kind=$Kind;cache_guard=$true;object=$ObjectName} | ConvertTo-Json -Compress))
    [Console]::Out.Flush()
    $answer = [Console]::In.ReadLine()
    if ($answer -ceq 'REUSE') { return $false }
    if ($answer -cne 'ALLOW') { throw 'Guard admission refused' }
    return $true
}
function End-PhysicalRead([string]$Kind, [bool]$GuardPassed = $false) {
    if ($Metered) {
        [Console]::Out.WriteLine((@{physical_read='DONE';kind=$Kind;status='AVAILABLE';guard_passed=$GuardPassed} | ConvertTo-Json -Compress))
        [Console]::Out.Flush()
    }
}
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Data
$connection = $null
$command = $null
$reader = $null
$stage = 'setup'
try {
    $rawRequest = if ($Metered) { [Console]::In.ReadLine() } else { [Console]::In.ReadToEnd() }
    $request = $rawRequest | ConvertFrom-Json
    $names = @($request.PSObject.Properties.Name | Sort-Object)
    if (($names -join ',') -ne 'access_token,database,max_rows,parameters,query,read_only_objects,result_columns,server') { throw 'Unexpected request fields' }
    if ([string]::IsNullOrWhiteSpace($request.database)) { throw 'Database name required' }
    if ($request.server -notmatch '^[A-Za-z0-9.-]+$') { throw 'Invalid server' }
    $builder = New-Object System.Data.SqlClient.SqlConnectionStringBuilder
    $builder['Data Source'] = "tcp:$($request.server),1433"
    $builder['Initial Catalog'] = $request.database
    $builder['Encrypt'] = $true
    $builder['TrustServerCertificate'] = $false
    $builder['ApplicationIntent'] = 'ReadOnly'
    $builder['Connect Timeout'] = 30
    $connection = New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
    $connection.AccessToken = $request.access_token
    $stage = 'connect'
    $connection.Open()
    $stage = 'query'
    $guard = $connection.CreateCommand()
    try {
        $guard.CommandTimeout = 15
        $guard.CommandText = 'SELECT SUSER_SNAME() AS login_name, DB_NAME() AS database_name'
        Begin-PhysicalRead 'sql_identity'
        $self = $guard.ExecuteReader()
        if (-not $self.Read()) { throw 'Self-report returned no row' }
        $surfaceReport = @{identity=[string]$self['login_name']; object=[string]$self['database_name']}
        $self.Close()
        End-PhysicalRead 'sql_identity'
        $guard.CommandText = "SELECT COUNT(*) FROM sys.fn_my_permissions(NULL,'DATABASE') WHERE permission_name NOT IN ('CONNECT','SELECT','VIEW DEFINITION','VIEW DATABASE STATE','VIEW DATABASE PERFORMANCE STATE','VIEW DATABASE SECURITY STATE')"
        if (Begin-Guard 'sql_database_permissions') {
            $permissionCount = [int]$guard.ExecuteScalar()
            if ($permissionCount -ne 0) { throw 'Proposed SQL requires a read-only principal' }
            End-PhysicalRead 'sql_database_permissions' $true
        }
        $objects = @($request.read_only_objects)
        if ($objects.Count -lt 1 -or $objects.Count -gt 24) { throw 'Invalid object permission scope' }
        $guard.CommandText = "SELECT COUNT(*) FROM sys.fn_my_permissions(@object,'OBJECT') WHERE permission_name NOT IN ('SELECT','VIEW DEFINITION')"
        $null = $guard.Parameters.Add('@object', [System.Data.SqlDbType]::NVarChar, 300)
        foreach ($objectName in $objects) {
            $guard.Parameters['@object'].Value = $objectName
            if (Begin-Guard 'sql_object_permissions' $objectName) {
                $permissionCount = [int]$guard.ExecuteScalar()
                if ($permissionCount -ne 0) { throw 'Proposed SQL object is not read-only' }
                End-PhysicalRead 'sql_object_permissions' $true
            }
        }
    } finally { $guard.Dispose() }
    $recordBounds = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'WorkerResponseBounds.json') -Raw | ConvertFrom-Json).FABRIC_SQL
    if ($request.max_rows -lt $recordBounds.minimum_rows -or $request.max_rows -gt $recordBounds.maximum_rows) { throw 'Invalid record budget' }
    $command = $connection.CreateCommand()
    $command.CommandTimeout = 60
    # Value and distinguishing evidence are one result, not the earlier guard
    # query's answer. Guards remain unchanged and metered separately.
    $command.CommandText = "SELECT q.*, SUSER_SNAME() AS __surface_identity, DB_NAME() AS __surface_object, LEFT(@@VERSION, CHARINDEX(' (', @@VERSION) - 1) AS __surface_engine FROM (" + $request.query + ") AS q"
    foreach ($parameter in $request.parameters) {
        $null = $command.Parameters.Add($parameter.name, [System.Data.SqlDbType]::NVarChar, 200)
        $command.Parameters[$parameter.name].Value = $parameter.value
    }
    Begin-PhysicalRead 'sql_quantity'
    $reader = $command.ExecuteReader()
    End-PhysicalRead 'sql_quantity'
    $columns = @($request.result_columns)
    if ($columns.Count -lt 1 -or $columns.Count -gt 16 -or $reader.FieldCount -ne ($columns.Count + 3)) { throw 'Invalid record shape' }
    $types = @{}
    for ($index = 0; $index -lt $columns.Count; $index++) {
        if ($reader.GetName($index) -cne $columns[$index]) { throw 'Record column differs' }
        $types[$columns[$index]] = $reader.GetFieldType($index).Name
    }
    $surfaceReport = $null
    $rows = New-Object System.Collections.Generic.List[object]
    while ($reader.Read()) {
        if ($rows.Count -ge $request.max_rows) { throw 'Record response exceeds budget' }
        if ($reader.GetName($columns.Count) -cne '__surface_identity' -or $reader.GetName($columns.Count + 1) -cne '__surface_object' -or $reader.GetName($columns.Count + 2) -cne '__surface_engine') { throw 'Quantity self-report columns differ' }
        $current = @{identity=[string]$reader.GetValue($columns.Count); object=[string]$reader.GetValue($columns.Count + 1); engine=[string]$reader.GetValue($columns.Count + 2)}
        if ($surfaceReport -and ($surfaceReport.identity -cne $current.identity -or $surfaceReport.object -cne $current.object -or $surfaceReport.engine -cne $current.engine)) { throw 'Inconsistent quantity self-report' }
        $surfaceReport = $current
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
    @{rows=@($rows.ToArray()); column_types=$types; read_only_verified=$true; surface_report=$surfaceReport; surface_report_binding='VALUE_QUERY';
      execution_identity=@{principal=$surfaceReport.identity; server=$request.server; database=$request.database;
                           provenance='SURFACE_SELF_REPORT'}} | ConvertTo-Json -Depth 8 -Compress
} catch {
    # Never emit connection strings, SQL errors, tokens or exception text.
    $failure = $_.Exception
    while ($failure.InnerException) { $failure = $failure.InnerException }
    $number = $null
    if ($failure -is [System.Data.SqlClient.SqlException]) { $number = $failure.Number }
    @{error='FabricSqlReadFailed'; error_number=$number; error_kind=$failure.GetType().Name; stage=$stage} | ConvertTo-Json -Compress
    exit 1
} finally {
    if ($reader) { $reader.Dispose() }
    if ($command) { $command.Dispose() }
    if ($connection) { $connection.Dispose() }
}
