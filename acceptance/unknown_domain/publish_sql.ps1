param([Parameter(Mandatory=$true)][string]$Folder)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Data
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$inputData=Get-Content -LiteralPath (Join-Path $Folder 'publisher-input.json') -Raw | ConvertFrom-Json
$credential=Import-Clixml -LiteralPath (Join-Path $root '.local/azure-sql.credential.xml')
$credential.Password.MakeReadOnly()
$connection=New-Object System.Data.SqlClient.SqlConnection('Server=tcp:sql-orderops-9696025.database.windows.net,1433;Database=ordersops;Encrypt=True;TrustServerCertificate=False;Connect Timeout=30')
$connection.Credential=New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
$transaction=$null
try {
    $connection.Open()
    $transaction=$connection.BeginTransaction()
    foreach($table in $inputData.tables) {
        if ($table.name -notmatch '^[a-z_]+_[a-f0-9]{6}$') { throw 'Invalid isolated table name' }
        $definitions=@()
        foreach($column in $table.columns) {
            if ($column[0] -notmatch '^[a-z_]+$') { throw 'Invalid column name' }
            $type='nvarchar(100)';if($column[1] -eq 'int'){$type='int'}
            $definitions+="[$($column[0])] $type NOT NULL"
        }
        if($table.primary_key) {
            $keyColumns=@()
            foreach($keyColumn in $table.primary_key) {
                if($keyColumn -notin @($table.columns | ForEach-Object {$_[0]})){throw 'Unknown primary key column'}
                $keyColumns+="[$keyColumn]"
            }
            $definitions+='PRIMARY KEY ('+($keyColumns -join ',')+')'
        }
        foreach($foreignKey in $table.foreign_keys) {
            $target=@($inputData.tables | Where-Object {$_.name -eq $foreignKey.table})
            if($target.Count -ne 1 -or $foreignKey.column -notin @($table.columns | ForEach-Object {$_[0]}) -or $foreignKey.target_column -notin @($target[0].columns | ForEach-Object {$_[0]})){throw 'Unknown foreign key target'}
            $definitions+="FOREIGN KEY ([$($foreignKey.column)]) REFERENCES app.[$($foreignKey.table)] ([$($foreignKey.target_column)])"
        }
        $command=$connection.CreateCommand();$command.Transaction=$transaction;$command.CommandTimeout=30
        $command.CommandText="CREATE TABLE app.[$($table.name)] ("+($definitions -join ',')+")"
        $null=$command.ExecuteNonQuery()
        $values=@()
        for($i=0;$i -lt $table.columns.Count;$i++) {
            $values+="@p$i"
            $type=[System.Data.SqlDbType]::NVarChar;if($table.columns[$i][1] -eq 'int'){$type=[System.Data.SqlDbType]::Int}
            $null=$command.Parameters.Add("@p$i",$type,100)
        }
        $command.CommandText="INSERT INTO app.[$($table.name)] VALUES ("+($values -join ',')+")"
        foreach($row in $table.rows) {
            for($i=0;$i -lt $table.columns.Count;$i++){$command.Parameters[$i].Value=$row[$i]}
            $null=$command.ExecuteNonQuery()
        }
        $command.Dispose()
    }
    $transaction.Commit();$transaction=$null
    $tables=@()
    foreach($table in $inputData.tables) {
        $command=$connection.CreateCommand();$command.CommandTimeout=30
        $command.CommandText="SELECT * FROM app.[$($table.name)]"
        $reader=$command.ExecuteReader();$rows=New-Object System.Collections.Generic.List[object]
        while($reader.Read()) {
            $row=New-Object object[] $reader.FieldCount
            $null=$reader.GetValues($row);$rows.Add($row)
        }
        $reader.Dispose();$command.Dispose()
        $tables+=@{name=$table.name;columns=$table.columns;rows=@($rows.ToArray())}
    }
    @{suffix=$inputData.suffix;tables=$tables}|ConvertTo-Json -Depth 20|Set-Content -LiteralPath (Join-Path $Folder 'sql-readback.json') -Encoding UTF8
    @{status='COMPLETED';tables=$tables.Count}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $Folder 'publisher-sql-status.json')
} catch {
    if($transaction){$transaction.Rollback()}
    @{status='FAILED';error_type=$_.Exception.GetType().Name}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $Folder 'publisher-sql-status.json')
    exit 1
} finally {$connection.Dispose()}
