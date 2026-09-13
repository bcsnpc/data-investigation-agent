param([string]$BaseUrl='http://localhost:3000')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
function Assert-Status {
 param([string]$Path,[int]$Expected,$Session=$null)
 try { $response=Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl$Path" -WebSession $Session; $status=[int]$response.StatusCode }
 catch { if(!$_.Exception.Response){throw};$status=[int]$_.Exception.Response.StatusCode }
 if($status -ne $Expected){throw "Unexpected HTTP status on $Path : $status"}
}
Assert-Status '/api/orders' 401
$credential=Import-Clixml -LiteralPath (Join-Path $projectRoot '.local/portal-operator.credential.xml')
$body=@{password=$credential.GetNetworkCredential().Password}|ConvertTo-Json
$null=Invoke-RestMethod -Uri "$BaseUrl/api/login" -Method Post -ContentType 'application/json' -Body $body -SessionVariable session
$summary=Invoke-RestMethod -Uri "$BaseUrl/api/summary" -WebSession $session
if($summary.orders -ne 100000){throw 'Unexpected order count.'}
$first=Invoke-RestMethod -Uri "$BaseUrl/api/orders?page=1" -WebSession $session
$second=Invoke-RestMethod -Uri "$BaseUrl/api/orders?page=2" -WebSession $session
if($first.orders.Count -ne 25 -or $second.orders.Count -ne 25 -or $first.orders[0].order_id -eq $second.orders[0].order_id){throw 'Pagination mismatch.'}
$filtered=Invoke-RestMethod -Uri "$BaseUrl/api/orders?status=PARTIALLY_RETURNED" -WebSession $session
if(@($filtered.orders|Where-Object status -ne 'PARTIALLY_RETURNED').Count -or !$filtered.orders.Count){throw 'Status filter mismatch.'}
$search=Invoke-RestMethod -Uri "$BaseUrl/api/orders?search=ORD-000002" -WebSession $session
if($search.total -ne 1){throw 'Order search mismatch.'}
$detail=Invoke-RestMethod -Uri "$BaseUrl/api/orders/ORD-000002" -WebSession $session
if($detail.order.total_amount -ne 1682.64 -or $detail.refunds[0].refund_amount -ne 153 -or $detail.lines.Count -ne 2 -or $detail.audit.Count -lt 5){throw 'Order detail does not match verified SQL baseline.'}
$dates=Invoke-RestMethod -Uri "$BaseUrl/api/orders?from=2026-08-01&to=2026-08-31" -WebSession $session
if($dates.total -ne 21365){throw 'Date filter does not match baseline.'}
Assert-Status '/api/orders?page=-1' 400 $session
Assert-Status '/api/orders/ORD-999999' 404 $session
$null=Invoke-RestMethod -Uri "$BaseUrl/api/logout" -Method Post -WebSession $session
Assert-Status '/api/orders' 401 $session
Write-Output 'PASS: live portal authentication, pagination, search, status/date filters, linked order details, invalid input, missing order and logout.'
