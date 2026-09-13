param(
 [string]$ResourceGroup='rg-investigator-dev',
 [string]$Location='centralus',
 [string]$PlanName='plan-orderops-dev',
 [string]$AppName='orderops-portal-9696025'
)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$python=Join-Path $projectRoot '.local/azure-cli-env/Scripts/python.exe'
function Invoke-Azure {
 param([string[]]$Arguments)
 $result=& $python -m azure.cli @Arguments --only-show-errors -o json
 if($LASTEXITCODE -ne 0){throw 'Azure command failed; deployment stopped.'}
 if($result){return ($result | ConvertFrom-Json)}
}
$account=Invoke-Azure -Arguments @('account','show')
$null=Invoke-Azure -Arguments @('group','show','--name',$ResourceGroup)
$plans=Invoke-Azure -Arguments @('appservice','plan','list','--resource-group',$ResourceGroup)
$plan=@($plans | Where-Object name -eq $PlanName)
if(!$plan.Count){
 $null=Invoke-Azure -Arguments @('appservice','plan','create','--resource-group',$ResourceGroup,'--name',$PlanName,'--location',$Location,'--is-linux','--sku','F1')
}elseif($plan[0].sku.name -ne 'F1'){throw 'Existing plan is not F1 Free. Refusing to change or use a paid plan automatically.'}
$apps=Invoke-Azure -Arguments @('webapp','list','--resource-group',$ResourceGroup)
if(!@($apps | Where-Object name -eq $AppName).Count){
 $null=Invoke-Azure -Arguments @('webapp','create','--resource-group',$ResourceGroup,'--plan',$PlanName,'--name',$AppName,'--runtime','NODE:24-lts')
}
$null=Invoke-Azure -Arguments @('webapp','update','--resource-group',$ResourceGroup,'--name',$AppName,'--https-only','true')
$null=Invoke-Azure -Arguments @('webapp','config','set','--resource-group',$ResourceGroup,'--name',$AppName,'--startup-file','npm start','--ftps-state','Disabled','--min-tls-version','1.2')
& (Join-Path $PSScriptRoot 'Start-OrderPortal.ps1') -PrepareOnly
$sql=Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/runtime-credentials/orderops_app.credential.xml')
$portal=Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/portal-operator.credential.xml')
$session=Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/portal-session.credential.xml')
$token=Invoke-Azure -Arguments @('account','get-access-token','--resource','https://management.azure.com/')
$resource="https://management.azure.com/subscriptions/$($account.id)/resourceGroups/$ResourceGroup/providers/Microsoft.Web/sites/$AppName/config/appsettings"
$headers=@{Authorization="Bearer $($token.accessToken)"}
# Preserve existing settings, and keep secret values out of CLI arguments/output.
$existing=Invoke-RestMethod -Method Post -Uri "$resource/list?api-version=2024-11-01" -Headers $headers
$settings=@{}
foreach($property in $existing.properties.PSObject.Properties){$settings[$property.Name]=$property.Value}
$settings['SQL_SERVER']='sql-orderops-9696025.database.windows.net'
$settings['SQL_DATABASE']='ordersops'
$settings['SQL_USER']=$sql.UserName
$settings['SQL_PASSWORD']=$sql.GetNetworkCredential().Password
$settings['PORTAL_PASSWORD']=$portal.GetNetworkCredential().Password
$settings['SESSION_SECRET']=$session.GetNetworkCredential().Password
$settings['NODE_ENV']='production'
$settings['SCM_DO_BUILD_DURING_DEPLOYMENT']='true'
$null=Invoke-RestMethod -Method Put -Uri "${resource}?api-version=2024-11-01" -Headers $headers -ContentType 'application/json' -Body (@{properties=$settings}|ConvertTo-Json -Depth 5)
$settings.Clear();$token=$null;$headers=$null
Write-Output 'App settings configured. Secret values were not printed.'
& python (Join-Path $projectRoot 'scripts/package_portal.py')
if($LASTEXITCODE -ne 0){throw 'Packaging failed.'}
$null=Invoke-Azure -Arguments @('webapp','deploy','--resource-group',$ResourceGroup,'--name',$AppName,'--src-path',(Join-Path $projectRoot '.local/order-portal.zip'),'--type','zip','--timeout','600000')
$app=Invoke-Azure -Arguments @('webapp','show','--resource-group',$ResourceGroup,'--name',$AppName)
@{url="https://$($app.defaultHostName)";appName=$AppName;resourceGroup=$ResourceGroup;sku='F1';subscriptionId=$account.id}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $projectRoot '.local/portal-deployment.json')
Write-Output "Deployed: https://$($app.defaultHostName)"
