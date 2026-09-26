"""Obtain a semantic model's specific error through XMLA, as the configured reader.

Execute Queries can report a model failure only generically; the XMLA interface
to the same model exposes the underlying error. This reduces that error to
codes (identity-platform codes, named error codes, hexadecimal engine codes).
Message text is never returned or stored. Run under the Fabric environment,
which holds the reader's MSAL cache. Request on stdin: tenant, account, library,
workspace_name, model_name, query.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'infra/scripts/Read-XmlaFailure.ps1'
CODE_PATTERNS = (r'\bAADSTS\d{5,6}\b', r'\b[A-Z][A-Za-z0-9]{3,80}ErrorCode\b', r'\b0x[0-9A-Fa-f]{8}\b')


def extract_codes(text, limit=10):
    """Codes only, in order of first appearance, never the surrounding text."""
    if not isinstance(text, str):
        return []
    found = []
    for match in sorted((m for p in CODE_PATTERNS for m in re.finditer(p, text)), key=lambda m: m.start()):
        code = match.group(0)
        code = code[:2]+code[2:].upper() if code.lower().startswith('0x') else code
        if code not in found:
            found.append(code)
    return found[:limit]


def read(request, token, run=subprocess.run):
    library = (ROOT/request['library']).resolve()
    if (ROOT/'.local').resolve() not in library.parents or not library.is_file():
        return {'status': 'UNAVAILABLE', 'stage': 'library', 'codes': []}
    payload = json.dumps({'library': str(library), 'workspace_name': request['workspace_name'],
                          'model_name': request['model_name'], 'query': request['query'],
                          'access_token': token(request)})
    completed = run(['powershell', '-NoProfile', '-NonInteractive', '-File', str(SCRIPT)], input=payload,
                    capture_output=True, text=True, encoding='utf-8', timeout=150)
    try:
        answer = json.loads(completed.stdout)
    except (TypeError, ValueError):
        return {'status': 'UNAVAILABLE', 'stage': 'response', 'codes': []}
    return {'status': answer.get('status'), 'stage': answer.get('stage'), 'error_type': answer.get('error_type'),
            'codes': extract_codes(answer.get('message'))}


def reader_token(request):
    from connect_fixture_reader import application, token
    return token(application(request['tenant']), request['account'], request['tenant'],
                 'https://analysis.windows.net/powerbi/api/.default')


if __name__ == '__main__':
    import sys
    try:
        print(json.dumps(read(json.load(sys.stdin), reader_token)))
    except Exception as exc:
        print(json.dumps({'status': 'UNAVAILABLE', 'stage': 'token', 'error_type': type(exc).__name__, 'codes': []}))
        raise SystemExit(1)
