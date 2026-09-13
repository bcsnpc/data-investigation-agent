param([string]$BaseUrl='https://orderops-portal-9696025.azurewebsites.net')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$credential=Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/portal-operator.credential.xml')
$login=@{password=$credential.GetNetworkCredential().Password}|ConvertTo-Json
$null=Invoke-RestMethod -Uri "$BaseUrl/api/login" -Method Post -ContentType 'application/json' -Body $login -SessionVariable session
try {
 $orders=Invoke-RestMethod -Uri "$BaseUrl/api/orders?status=PAID" -WebSession $session
 if(!$orders.orders.Count){throw 'A paid order is required for the stale-version check.'}
 $id=$orders.orders[0].order_id
 $before=Invoke-RestMethod -Uri "$BaseUrl/api/orders/$id" -WebSession $session
 $command=@{action='ship';requestId=[guid]::NewGuid().ToString();expectedUpdatedAt='2000-01-01T00:00:00.000Z';reason='Hosted stale-version verification';carrier='TEST';trackingNumber=[guid]::NewGuid().ToString()}|ConvertTo-Json
 function Assert-ActionStatus {
  param([int]$Expected,[string]$Body,$Headers,$WebSession)
  try {
   $r=Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/api/orders/$id/actions" -Method Post -ContentType 'application/json' -Body $Body -Headers $Headers -WebSession $WebSession
   $status=[int]$r.StatusCode
  } catch {
   if(!$_.Exception.Response){throw}
   $status=[int]$_.Exception.Response.StatusCode
  }
  if($status -ne $Expected){throw "Action endpoint returned $status; expected $Expected."}
 }
 Assert-ActionStatus 401 $command @{'X-Order-Action'='1';'Sec-Fetch-Site'='same-origin'} $null
 Assert-ActionStatus 403 $command @{} $session
 Assert-ActionStatus 403 $command @{'X-Order-Action'='1';'Sec-Fetch-Site'='cross-site'} $session
 Assert-ActionStatus 400 '{}' @{'X-Order-Action'='1';'Sec-Fetch-Site'='same-origin'} $session
 Assert-ActionStatus 409 $command @{'X-Order-Action'='1';'Sec-Fetch-Site'='same-origin'} $session
 $after=Invoke-RestMethod -Uri "$BaseUrl/api/orders/$id" -WebSession $session
 if($after.order.status -ne $before.order.status -or $after.order.updated_at -ne $before.order.updated_at -or $after.audit.Count -ne $before.audit.Count -or $after.shipments.Count -ne $before.shipments.Count){throw 'Order changed during rejection checks.'}
 Write-Output "PASS: hosted action authentication, cross-site rejection, input validation and SQL stale-version conflict. $id unchanged."
} finally { $null=Invoke-RestMethod -Uri "$BaseUrl/api/logout" -Method Post -WebSession $session }
