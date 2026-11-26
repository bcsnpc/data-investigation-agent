$ErrorActionPreference = 'Stop'
$r = [Console]::In.ReadToEnd() | ConvertFrom-Json
$connection = $null
try {
    $asm = [Reflection.Assembly]::LoadFrom($r.library)
    $connection = [Activator]::CreateInstance($asm.GetType('Microsoft.AnalysisServices.AdomdClient.AdomdConnection', $true))
    $builder = New-Object System.Data.Common.DbConnectionStringBuilder
    $builder['Data Source'] = 'powerbi://api.powerbi.com/v1.0/myorg/' + [Uri]::EscapeDataString($r.workspace)
    $builder['Initial Catalog'] = $r.model
    $builder['Connect Timeout'] = $r.timeout_seconds
    $connection.ConnectionString = $builder.ConnectionString
    $claims = $r.access_token.Split('.')[1].Replace('-', '+').Replace('_', '/')
    $claims = $claims.PadRight($claims.Length + ((4 - $claims.Length % 4) % 4), '=')
    $expiry = ([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($claims)) | ConvertFrom-Json).exp
    $type = $asm.GetType('Microsoft.AnalysisServices.AdomdClient.AccessToken', $true)
    $connection.AccessToken = [Activator]::CreateInstance($type, [object[]]@($r.access_token, [DateTimeOffset]::FromUnixTimeSeconds([long]$expiry), $null))
    $connection.Open()
    $command = $connection.CreateCommand()
    $command.CommandTimeout = $r.timeout_seconds
    $command.CommandText = $r.query
    $reader = $command.ExecuteReader()
    $rows = @()
    try {
        while ($reader.Read()) {
            if ($rows.Count -ge 10000) { throw 'XMLA row bound' }
            $row = [ordered]@{}
            for ($i = 0; $i -lt $reader.FieldCount; $i++) {
                $value = $reader.GetValue($i)
                if ($value -is [DBNull]) { $value = $null }
                $name = $reader.GetName($i)
                if ($row.Contains($name)) { throw 'Duplicate XMLA column' }
                $row[$name] = $value
            }
            $rows += ,$row
        }
        if ($reader.NextResult()) { throw 'Multiple XMLA results refused' }
    } finally { $reader.Close() }
    $json = ConvertTo-Json -Compress -Depth 12 -InputObject @{results=@(@{tables=@(@{rows=$rows})})}
    if ([Text.Encoding]::UTF8.GetByteCount($json) -gt 2097152) { throw 'XMLA response bound' }
    [Console]::WriteLine($json)
} catch {
    [Console]::WriteLine('{"error":"XMLA_NATIVE_QUERY_FAILED"}')
    exit 1
} finally {
    if ($connection) { $connection.Dispose() }
    $r = $null
}
