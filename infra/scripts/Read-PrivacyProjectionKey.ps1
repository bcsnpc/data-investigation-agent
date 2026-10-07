param([Parameter(Mandatory=$true)][string]$CredentialPath)
$ErrorActionPreference = 'Stop'
# Called through a captured process pipe only. Do not log, transcript, echo
# the credential object, or copy the password into a file/environment variable.
try {
    $privacyCredential = Import-Clixml -LiteralPath $CredentialPath
    if ($privacyCredential -isnot [System.Management.Automation.PSCredential]) {
        throw 'Invalid privacy credential'
    }
    $privacyEncodedKey = $privacyCredential.GetNetworkCredential().Password
    $privacyDecodedKey = [Convert]::FromBase64String($privacyEncodedKey)
    if ($privacyDecodedKey.Length -lt 32) { throw 'Invalid privacy key length' }
    [Console]::Out.Write([Convert]::ToBase64String($privacyDecodedKey))
} catch {
    # Never emit the original error, credential path contents, or password.
    [Console]::Error.Write('Privacy secret store unavailable')
    exit 1
}
