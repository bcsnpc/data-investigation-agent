$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$credential = Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/portal-operator.credential.xml')
Set-Clipboard -Value $credential.GetNetworkCredential().Password
Write-Output 'Portal access password copied to your clipboard. Paste it into the portal sign-in form.'
