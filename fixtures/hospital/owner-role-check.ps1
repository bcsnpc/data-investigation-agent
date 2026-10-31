# Owner-only XMLA diagnostic. FAILED is not a security-test pass; native UI fallback is recorded separately.
param([Parameter(Mandatory=$true)][string]$ModelId,[Parameter(Mandatory=$true)][ValidateSet('Executive','HospitalManager','DepartmentHead','Doctor')][string]$Role,[Parameter(Mandatory=$true)][string]$Receipt,[switch]$CheckOLS,[switch]$UnrestrictedControl,[string]$ClientLibrary=(Join-Path $PSScriptRoot '../../.local/hospital-estate/xmla-client/Microsoft.AnalysisServices.AdomdClient.dll'))
$ErrorActionPreference='Stop'
$models=@{'df6e3f67-deb6-4cb8-b15a-353176931679'='Revenue';'0ef2b1a3-c6b7-4623-b962-39fe12c84d06'='Productivity';'85e662ed-c4e6-41fb-9e43-be0c5a6aeeae'='Operations'}
if (-not $models.ContainsKey($ModelId)) { throw 'HealthNet model only' }
$result=[ordered]@{model_id=$ModelId;model=$models[$ModelId];role=$Role;identity='existing Fabric owner admin@skynwhy.com';surface='XMLA native role testing';ols_probe=[bool]$CheckOLS};$connection=$null;$token=$null
try {
 $previous=$env:AZURE_CONFIG_DIR
 try {
  $env:AZURE_CONFIG_DIR='D:\data_investigation_agent\.local\azure-fabric-sql'
  $auth=(& D:\data_investigation_agent\.local\azure-cli-env\Scripts\python.exe -m azure.cli account get-access-token --resource 'https://analysis.windows.net/powerbi/api' --tenant 'dff91047-ebc2-4657-8dbe-5af328d57780' -o json | ConvertFrom-Json)
  if ($LASTEXITCODE -ne 0) { throw 'Owner token request failed' };$token=$auth.accessToken;$expiration=[DateTimeOffset]::FromUnixTimeSeconds([long]$auth.expires_on);$auth=$null
 } finally { $env:AZURE_CONFIG_DIR=$previous }
 $assembly=[System.Reflection.Assembly]::LoadFrom([IO.Path]::GetFullPath($ClientLibrary))
 $connection=[Activator]::CreateInstance($assembly.GetType('Microsoft.AnalysisServices.AdomdClient.AdomdConnection',$true))
 $builder=New-Object System.Data.Common.DbConnectionStringBuilder
 $builder['Data Source']='powerbi://api.powerbi.com/v1.0/myorg/HealthNet Analytics';$builder['Initial Catalog']='HealthNet '+$models[$ModelId];if (-not $UnrestrictedControl) { $builder['Roles']=$Role };
 $result.effective_upn='native owner; no user impersonation';
 if ($UnrestrictedControl) { $result.role='OWNER_CONTROL_NO_ROLE_OVERRIDE' };
 $builder['Connect Timeout']=60
 $connection.ConnectionString=$builder.ConnectionString
 $accessTokenType=$assembly.GetType('Microsoft.AnalysisServices.AdomdClient.AccessToken',$true)
 $connection.AccessToken=[Activator]::CreateInstance($accessTokenType,[object[]]@($token,$expiration,$null))
 $connection.Open();$command=$connection.CreateCommand();$command.CommandTimeout=120
 $query=if($CheckOLS){'EVALUATE ROW("hidden_cost",SUM(mart_provider_productivity_daily[synthetic_cost_cents]))'}elseif($models[$ModelId] -eq 'Revenue'){'EVALUATE ROW("served_upn",USERPRINCIPALNAME(),"rows",COALESCE(COUNTROWS(mart_charge),0),"headline",[Gross Charges])'}else{'EVALUATE ROW("served_upn",USERPRINCIPALNAME(),"rows",COALESCE(COUNTROWS(mart_encounter),0),"headline",[Visits])'}
 $result.query=$query;$reader=$command.ExecuteReader();$rows=@()
 try {while($reader.Read()){$row=[ordered]@{};for($i=0;$i -lt $reader.FieldCount;$i++){$v=$reader.GetValue($i);if($v -is [DBNull]){$v=$null};$row[$reader.GetName($i)]=$v};$rows+=,$row}}finally{$reader.Close()}
 $result.rows=$rows;$result.status='SERVED'
} catch {
 $message=$_.Exception.Message;if($token){$message=$message.Replace($token,'[REDACTED]')};$result.status='FAILED';$result.error=$message;$result.error_type=$_.Exception.GetType().FullName
} finally {if($connection){$connection.Dispose()};$token=$null;$result|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $Receipt -Encoding UTF8}
Write-Output ($result.status+' '+$result.model+' '+$Role)
if ($result.status -eq 'FAILED') { exit 1 }
