"""Resolve an existing estate key from the project's Windows DPAPI secret store.

Never creates a key. An estate owner provisions a dedicated PSCredential file
whose password is a base64-encoded random key of at least 32 bytes. Python holds
the decoded key only in memory; no environment variable or scratch file is used.
"""
import base64
from pathlib import Path
import subprocess
from .privacy_projection import ProjectionError


def resolver(root):
    root=Path(root).resolve()
    local=(root/'.local').resolve()
    script=root/'infra/scripts/Read-PrivacyProjectionKey.ps1'
    def read(reference):
        path=(root/reference).resolve()
        if not path.is_relative_to(local) or path==local:
            raise ProjectionError('PRIVACY_KEY_MUST_USE_LOCAL_SECRET_STORE')
        completed=subprocess.run(['powershell','-NoProfile','-NonInteractive',
            '-File',str(script),'-CredentialPath',str(path)],
            capture_output=True,check=False)
        # stderr may include sensitive material from a broken local provider.
        # Neither output nor the command's exception is surfaced in evidence.
        if completed.returncode:
            raise ProjectionError('PRIVACY_SECRET_STORE_UNAVAILABLE')
        try:key=base64.b64decode(completed.stdout.strip(),validate=True)
        except (ValueError,TypeError):
            raise ProjectionError('PRIVACY_SECRET_STORE_INVALID_KEY') from None
        if len(key)<32:
            raise ProjectionError('PRIVACY_KEY_REQUIRES_256_BITS')
        return key
    return read
