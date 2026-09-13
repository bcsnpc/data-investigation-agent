"""Bounded value reads; no caller-provided SQL, DAX, URLs or access tokens."""
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import Request, build_opener
from uuid import UUID

from metadata_auth import FabricCliTokens, NoRedirect

ROOT = Path(__file__).resolve().parents[1]


def filters(currency, order_id):
    if not isinstance(currency, str) or not re.fullmatch(r'[A-Z]{3}', currency):
        raise ValueError('Three-letter currency required')
    if order_id is not None and (not isinstance(order_id, str) or not re.fullmatch(r'ORD-[0-9]{6}', order_id)):
        raise ValueError('Unsupported order ID')


def dax(currency, order_id):
    filters(currency, order_id)
    clauses = [f'TREATAS({{"{currency}"}},FactOrderLine[currency])']
    if order_id:
        clauses.append(f'TREATAS({{"{order_id}"}},FactOrder[order_id])')
    return ('EVALUATE CALCULATETABLE(ROW("order_count",FORMAT(COALESCE([Order Count],0),"0","en-US"),'
            '"net_cash",FORMAT(COALESCE([Net Cash],0),"0.0000","en-US")),' + ','.join(clauses) + ')')


def extract_dax(response):
    if response.get('error') or len(response.get('results', [])) != 1:
        raise ValueError('DAX result unavailable')
    result = response['results'][0]
    tables = result.get('tables', [])
    if result.get('error') or len(tables) != 1 or tables[0].get('error') or len(tables[0].get('rows', [])) != 1:
        raise ValueError('DAX result incomplete')
    row = tables[0]['rows'][0]
    return {key: row[f'[{key}]'] for key in ('order_count', 'net_cash')}


def execute(request):
    filters(request['currency'], request.get('order_id'))
    layer = request['layer']
    if layer not in ('sql', 'bronze', 'silver', 'gold', 'semantic'):
        raise ValueError('Unsupported layer')
    if layer == 'semantic':
        workspace, model = str(UUID(request['workspace'])), str(UUID(request['model']))
        query = dax(request['currency'], request.get('order_id'))
        body = {'queries': [{'query': query}], 'serializerSettings': {'includeNulls': True}}
        token = FabricCliTokens(request['tenant']).get_token('https://analysis.windows.net/powerbi/api/.default')
        http = Request(f'https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/executeQueries',
                       data=json.dumps(body).encode(), headers={'Authorization': 'Bearer '+token, 'Content-Type': 'application/json'})
        with build_opener(NoRedirect()).open(http, timeout=90) as result:
            values = extract_dax(json.load(result))
        from datetime import datetime, timezone
        return {'values': values, 'query': query, 'captured_at': datetime.now(timezone.utc).isoformat()}
    suffix = '.database.windows.net' if layer == 'sql' else '.datawarehouse.fabric.microsoft.com'
    if not re.fullmatch(r'[a-zA-Z0-9.-]+', request['server']) or not request['server'].endswith(suffix):
        raise ValueError('Unsupported SQL host')
    payload = {key: request.get(key) for key in ('layer', 'currency', 'order_id', 'server', 'database', 'credential_file')}
    if layer != 'sql':
        payload['access_token'] = FabricCliTokens(request['tenant']).get_token('https://database.windows.net/.default')
    result = subprocess.run(['powershell', '-NoProfile', '-File', str(ROOT/'infra/scripts/Read-InvestigationMetric.ps1')],
                            input=json.dumps(payload), text=True, capture_output=True, timeout=150)
    if result.returncode:
        # Only fixed error code/type/stage/number is emitted by the SQL helper.
        failure = json.loads(result.stdout)
        return {key: failure.get(key) for key in ('error', 'error_type', 'stage', 'sql_error_number')}
    return json.loads(result.stdout)


if __name__ == '__main__':
    try:
        print(json.dumps(execute(json.load(sys.stdin))))
    except Exception as exc:
        print(json.dumps({'error': 'QUERY_UNAVAILABLE', 'error_type': type(exc).__name__}))
        raise SystemExit(1)
