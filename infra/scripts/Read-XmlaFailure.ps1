$ErrorActionPreference='Stop'
# Re-issue one already-admitted query through the XMLA interface to the same
# semantic model, only to obtain the model's specific error. Workspace and model
# are always named. The error text goes to the calling process only; it is
# reduced to codes there and never stored.
$connection=$null
$stage='setup'
try {
  $request=[Console]::In.ReadToEnd() | ConvertFrom-Json
  $names=@($request.PSObject.Properties.Name | Sort-Object)
  if (($names -join ',') -ne 'access_token,library,model_name,query,workspace_name') { throw 'Unexpected request fields' }
  foreach ($field in 'workspace_name','model_name','query','library') {
    if ([string]::IsNullOrWhiteSpace($request.$field)) { throw "$field required" }
  }
  $stage='library'
  Add-Type -Path $request.library
  $stage='connect'
  $source='powerbi://api.powerbi.com/v1.0/myorg/'+$request.workspace_name
  $connection=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection
  $connection.ConnectionString="Data Source=$source;Initial Catalog=$($request.model_name);User ID=;Password=$($request.access_token)"
  $connection.Open()
  $stage='query'
  $command=$connection.CreateCommand()
  $command.CommandTimeout=60
  $command.CommandText=$request.query
  $reader=$command.ExecuteReader()
  $reader.Close()
  @{status='NO_ERROR';stage='complete'} | ConvertTo-Json -Compress
} catch {
  $messages=@(); $e=$_.Exception
  while ($e) { $messages+=$e.Message; $e=$e.InnerException }
  $text=($messages -join ' | ')
  if ($text.Length -gt 8000) { $text=$text.Substring(0,8000) }
  @{status=if($stage -in 'connect','query'){'ERROR_CAPTURED'}else{'UNAVAILABLE'};stage=$stage;
    error_type=$_.Exception.GetType().Name;message=$text} | ConvertTo-Json -Compress
  exit 1
} finally { if ($connection) { $connection.Dispose() } }
