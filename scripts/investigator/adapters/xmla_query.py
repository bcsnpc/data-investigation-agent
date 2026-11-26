"""Configured native DAX reader. No owner fallback, impersonation or XMLA writes."""
import json
from pathlib import Path
import subprocess
from uuid import UUID

ROOT = Path(__file__).resolve().parents[3]


def validate(value):
    from metadata_config import keys, text
    from fabric_sql_auth import profile_path
    keys(value, ['mode', 'library', 'workspace_id', 'workspace_name', 'models'])
    if value['mode'] != 'xmla':raise ValueError('Unsupported DAX transport')
    profile_path(value['library'])
    UUID(value['workspace_id']);text(value['workspace_name'])
    if not isinstance(value['models'],dict) or not 1 <= len(value['models']) <= 50:
        raise ValueError('Bounded XMLA model bindings required')
    for identity,name in value['models'].items():UUID(identity);text(name)
    return value


def read(config, request, token, *, timeout_seconds, run=None):
    validate(config)
    if request['workspace'] != config['workspace_id'] or request['native_model_id'] not in config['models']:
        raise ValueError('XMLA target outside configured bindings')
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 90:
        raise ValueError('XMLA query timeout bound')
    from investigator.live_gateway import authorize_native_control
    authorize_native_control('XMLA_EVALUATE',dict(workspace=request['workspace'],model=request['native_model_id']),request['query'])
    from fabric_sql_auth import profile_path
    library=profile_path(config['library'])
    if not library.is_file():
        raise ValueError('Configured XMLA library unavailable')
    payload=dict(library=str(library),workspace=config['workspace_name'],model=config['models'][request['native_model_id']],
                 query=request['query'],access_token=token,timeout_seconds=timeout_seconds)
    try:
        completed=(run or subprocess.run)(['powershell','-NoProfile','-NonInteractive','-File',str(ROOT/'infra/scripts/Read-XmlaQuery.ps1')],
            input=json.dumps(payload),capture_output=True,text=True,encoding='utf-8',timeout=timeout_seconds+30)
    except subprocess.TimeoutExpired:
        raise TimeoutError('XMLA native completion uncertain') from None
    # Raw native errors can contain credential/connection details: never expose them.
    if completed.returncode:raise RuntimeError('XMLA native query failed')
    if len(completed.stdout.encode('utf-8')) > 2*1024*1024:raise ValueError('XMLA response exceeds budget')
    from decimal import Decimal
    response=json.loads(completed.stdout,parse_float=Decimal)
    if set(response)!={'results'} or len(response['results'])!=1:raise ValueError('XMLA response shape')
    tables=response['results'][0]
    if set(tables)!={'tables'} or len(tables['tables'])!=1:raise ValueError('XMLA table shape')
    table=tables['tables'][0]
    if set(table)!={'rows'} or not isinstance(table['rows'],list) or len(table['rows'])>10000:
        raise ValueError('XMLA row bound')
    if any(not isinstance(row,dict) for row in table['rows']):raise ValueError('XMLA row shape')
    return completed.stdout
