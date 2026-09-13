param([switch]$Browser)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$credential = Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/runtime-credentials/orderops_app.credential.xml')
$env:SQL_SERVER = 'sql-orderops-9696025.database.windows.net'
$env:SQL_DATABASE = 'ordersops'
$env:SQL_USER = $credential.UserName
$env:SQL_PASSWORD = $credential.GetNetworkCredential().Password
try {
 $script = if ($Browser) { 'apps/order-portal/server/actions.browser.js' } else { 'apps/order-portal/server/actions.integration.js' }
 node (Join-Path $projectRoot $script)
 if ($LASTEXITCODE -ne 0) { throw 'Order action integration verification failed.' }
} finally { Remove-Item Env:SQL_PASSWORD -ErrorAction SilentlyContinue }
