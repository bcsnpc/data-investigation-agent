param([switch]$PrepareOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$portalCredential = Join-Path $projectRoot '.local/portal-operator.credential.xml'
$sessionCredential = Join-Path $projectRoot '.local/portal-session.credential.xml'
foreach ($path in @($portalCredential,$sessionCredential)) {
 if (!(Test-Path -LiteralPath $path)) {
  $bytes = New-Object byte[] 32
  $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
  $secure = ConvertTo-SecureString ([Convert]::ToBase64String($bytes)) -AsPlainText -Force
  (New-Object System.Management.Automation.PSCredential('portal-operator',$secure)) | Export-Clixml -LiteralPath $path
 }
}
if ($PrepareOnly) { Write-Output 'Portal credentials prepared and encrypted locally.'; return }
$sql = Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/runtime-credentials/orderops_app.credential.xml')
$env:SQL_SERVER = 'sql-orderops-9696025.database.windows.net'
$env:SQL_DATABASE = 'ordersops'
$env:SQL_USER = $sql.UserName
$env:SQL_PASSWORD = $sql.GetNetworkCredential().Password
$env:PORTAL_PASSWORD = (Import-Clixml -LiteralPath $portalCredential).GetNetworkCredential().Password
$env:SESSION_SECRET = (Import-Clixml -LiteralPath $sessionCredential).GetNetworkCredential().Password
$env:NODE_ENV = 'development'
$env:PORT = '3000'
Push-Location (Join-Path $projectRoot 'apps/order-portal')
try { node server/index.js } finally {
 Pop-Location
 Remove-Item Env:SQL_PASSWORD,Env:PORTAL_PASSWORD,Env:SESSION_SECRET -ErrorAction SilentlyContinue
}
