param([Parameter(Mandatory=$true)][string]$RequestPath)
$ErrorActionPreference='Stop'
$request=Get-Content -LiteralPath $RequestPath -Raw | ConvertFrom-Json
Add-Type -AssemblyName System.Data
Add-Type -AssemblyName System.Web.Extensions
Add-Type -ReferencedAssemblies System.Data,System.Web.Extensions,System.Xml -TypeDefinition @'
using System;
using System.Data;
using System.Data.SqlClient;
using System.IO;
using System.Text;
using System.Globalization;
using System.Collections.Generic;
using System.Web.Script.Serialization;

public class SnapshotTable {
 public string name;
 public string file;
 public long rows;
 public List<Dictionary<string,string>> columns;
}
public static class SnapshotExport {
 public static SnapshotTable Export(SqlConnection connection, SqlTransaction tx, string table, string folder) {
  var result = new SnapshotTable { name=table, file=table+".jsonl", rows=0, columns=new List<Dictionary<string,string>>() };
  var json = new JavaScriptSerializer();
  using(var command = connection.CreateCommand()) {
   command.Transaction=tx;
   command.CommandTimeout=300;
   // Table comes only from the fixed allowlist in the calling script.
   command.CommandText="SELECT * FROM [app].["+table+"]";
   using(var reader=command.ExecuteReader(CommandBehavior.SequentialAccess)) {
    var schema=reader.GetSchemaTable();
    for(int i=0;i<reader.FieldCount;i++) {
     result.columns.Add(new Dictionary<string,string>{{"name",reader.GetName(i)},{"sql_type",reader.GetDataTypeName(i)},{"clr_type",reader.GetFieldType(i).FullName},
      {"size",schema.Rows[i]["ColumnSize"].ToString()},{"precision",schema.Rows[i]["NumericPrecision"].ToString()},
      {"scale",schema.Rows[i]["NumericScale"].ToString()},{"nullable",schema.Rows[i]["AllowDBNull"].ToString()}});
    }
    using(var stream=new FileStream(Path.Combine(folder,result.file),FileMode.CreateNew,FileAccess.Write,FileShare.None))
    using(var writer=new StreamWriter(stream,new UTF8Encoding(false))) {
     writer.NewLine="\n";
     while(reader.Read()) {
      var row=new object[reader.FieldCount];
      for(int i=0;i<reader.FieldCount;i++) {
       object value=reader.GetValue(i);
       if(value==DBNull.Value) row[i]=null;
       else if(value is DateTime) row[i]=((DateTime)value).ToString("o",CultureInfo.InvariantCulture);
       else if(value is DateTimeOffset) row[i]=((DateTimeOffset)value).ToString("o",CultureInfo.InvariantCulture);
       else if(value is byte[]) row[i]=Convert.ToBase64String((byte[])value);
       else if(value is IFormattable) row[i]=((IFormattable)value).ToString(null,CultureInfo.InvariantCulture);
       else row[i]=value.ToString();
      }
      writer.WriteLine(json.Serialize(row));
      result.rows++;
     }
    }
   }
  }
  return result;
 }
}
'@
$connection=$null
$transaction=$null
try {
 $credential=Import-Clixml -LiteralPath $request.credential_file
 $credential.Password.MakeReadOnly()
 $builder=New-Object System.Data.SqlClient.SqlConnectionStringBuilder
 $builder['Data Source']="tcp:$($request.server),1433"
 $builder['Initial Catalog']=$request.database
 $builder['Encrypt']=$true
 $builder['TrustServerCertificate']=$false
 $builder['Connect Timeout']=60
 $connection=New-Object System.Data.SqlClient.SqlConnection($builder.ConnectionString)
 $connection.Credential=New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
 $connection.Open()
 $check=$connection.CreateCommand()
 $check.CommandText='SELECT snapshot_isolation_state FROM sys.databases WHERE name=DB_NAME()'
 if([int]$check.ExecuteScalar() -ne 1) { throw 'SNAPSHOT isolation must already be enabled' }
 $check.Dispose()
 $started=[DateTime]::UtcNow.ToString('o')
 $transaction=$connection.BeginTransaction([System.Data.IsolationLevel]::Snapshot)
 $tables=@()
 foreach($name in @('customers','products','orders','order_lines','payments','shipments','shipment_lines','refunds','refund_lines','audit_log')) {
  $table=[SnapshotExport]::Export($connection,$transaction,$name,$request.output)
  $tables+=$table
  Write-Output "Captured $name`: $($table.rows) rows"
 }
 $transaction.Commit()
 $finished=[DateTime]::UtcNow.ToString('o')
 # The receipt is written only after the read transaction succeeds.
 $receipt=@{snapshot_id=$request.snapshot_id;isolation='SNAPSHOT';transaction_completed=$true;started_at=$started;finished_at=$finished;tables=$tables}
 $receipt | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $request.output 'receipt.json')
} catch {
 Write-Output "Snapshot export failed: $($_.Exception.GetType().Name). No READY manifest published."
 exit 1
} finally {
 if($transaction) { $transaction.Dispose() }
 if($connection) { $connection.Dispose() }
}
