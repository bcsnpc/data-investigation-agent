# Shared connection helper; importing this file performs no SQL operations.
Add-Type -AssemblyName System.Data
function Open-OrderOpsConnection {
 param([Parameter(Mandatory=$true)][string]$CredentialPath)
 $credential = Import-Clixml -LiteralPath $CredentialPath
 $credential.Password.MakeReadOnly()
 $conn = New-Object System.Data.SqlClient.SqlConnection('Data Source=tcp:sql-orderops-9696025.database.windows.net,1433;Initial Catalog=ordersops;Encrypt=True;TrustServerCertificate=False;Connect Timeout=60')
 $conn.Credential = New-Object System.Data.SqlClient.SqlCredential($credential.UserName,$credential.Password)
 try { $conn.Open(); return $conn } catch { $conn.Dispose(); throw 'SQL connection failed. Check the saved credential and server firewall.' }
}
