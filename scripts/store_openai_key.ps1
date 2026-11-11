# Owner-operated: never pass the key on the command line or print it.
$ErrorActionPreference = 'Stop'
$key = Read-Host 'OpenAI project API key' -AsSecureString
$tempPath = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid().ToString() + '.key')
$ptr = [IntPtr]::Zero
try {
    New-Item -ItemType File -Path $tempPath | Out-Null
    $acl = Get-Acl -LiteralPath $tempPath
    $acl.SetAccessRuleProtection($true, $false)
    $owner = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $acl.SetAccessRule([Security.AccessControl.FileSystemAccessRule]::new($owner, 'FullControl', 'Allow'))
    Set-Acl -LiteralPath $tempPath -AclObject $acl
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($key)
    [IO.File]::WriteAllText($tempPath, [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr), [Text.UTF8Encoding]::new($false))
    if (Get-Command az -ErrorAction SilentlyContinue) {
        az keyvault secret set --vault-name kv-dia-d5dd7d65 --name openai-api-key --file $tempPath --output none
    } else {
        & 'D:\data_investigation_agent\.local\azure-cli-env\Scripts\python.exe' -m azure.cli keyvault secret set --vault-name kv-dia-d5dd7d65 --name openai-api-key --file $tempPath --output none
    }
    if ($LASTEXITCODE -ne 0) { throw 'Key Vault upload failed; no secret was printed.' }
    Write-Output 'OpenAI key stored in the existing Key Vault.'
} finally {
    if ($ptr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    if (Test-Path -LiteralPath $tempPath) { Remove-Item -LiteralPath $tempPath -Force }
    $key.Dispose()
}
