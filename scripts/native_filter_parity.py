"""One-order semantic diagnostic; no arbitrary DAX or equivalence certification."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from urllib.request import Request, build_opener
from uuid import UUID

from investigation_query_worker import filters
from metadata_auth import FabricCliTokens, NoRedirect


def query(currency, order_id):
    filters(currency, order_id)
    if order_id is None:
        raise ValueError('An explicit order is required')
    cells = []
    for scope, table in [('native', 'FactOrder'), ('adapter', 'FactOrderLine')]:
        for metric, measure, fmt in [('orders', '[Order Count]', '0'), ('cash', '[Net Cash]', '0.0000')]:
            cells.append(f'"{scope}_{metric}",FORMAT(COALESCE(CALCULATE({measure},'
                         f'TREATAS({{"{currency}"}},{table}[currency]),'
                         f'TREATAS({{"{order_id}"}},FactOrder[order_id])),0),"{fmt}","en-US")')
    return 'EVALUATE ROW(' + ','.join(cells) + ')'


def assess(response):
    results = response.get('results', [])
    if 'error' in response or len(results) != 1 or 'error' in results[0]:
        raise ValueError('Incomplete semantic result')
    tables = results[0].get('tables', [])
    if len(tables) != 1 or 'error' in tables[0] or len(tables[0].get('rows', [])) != 1:
        raise ValueError('Incomplete semantic table')
    row = tables[0]['rows'][0]
    values = {}
    for scope in ('native', 'adapter'):
        for metric in ('orders', 'cash'):
            key = scope + '_' + metric
            raw = row.get('[' + key + ']')
            if not isinstance(raw, str):
                raise ValueError('Missing formatted metric')
            try:
                value = Decimal(raw)
            except InvalidOperation as exc:
                raise ValueError('Invalid metric') from exc
            if not value.is_finite() or (metric == 'orders' and (value < 0 or value != value.to_integral_value())):
                raise ValueError('Invalid metric')
            values[key] = value
    status = 'OBSERVED_MATCH' if all(values['native_' + m] == values['adapter_' + m] for m in ('orders', 'cash')) else 'OBSERVED_MISMATCH'
    if all(value == 0 for value in values.values()):
        status = 'NO_MATCHING_ORDERS'
    return {'status': status, 'values': {k: str(v) for k, v in values.items()},
            'classification': 'UNRESOLVED', 'snapshot_comparable': False,
            'runtime_filter_verified': False,
            'limitation': 'One-order measure diagnostic only; does not reproduce report state, RLS, or prove common source versions.'}


def run(tenant, workspace, model, currency, order_id):
    tenant, workspace, model = (str(UUID(x)) for x in (tenant, workspace, model))
    dax = query(currency, order_id)
    token = FabricCliTokens(tenant).get_token('https://analysis.windows.net/powerbi/api/.default')
    request = Request(f'https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/executeQueries',
                      data=json.dumps({'queries': [{'query': dax}], 'serializerSettings': {'includeNulls': True}}).encode(),
                      headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    with build_opener(NoRedirect()).open(request, timeout=90) as response:
        raw = json.load(response)
    evidence = {'workspace': workspace, 'model': model, 'currency': currency, 'order_id': order_id,
                'query': dax, 'response': raw, 'captured_at': datetime.now(timezone.utc).isoformat(),
                'result': assess(raw)}
    evidence['evidence_hash'] = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('tenant', 'workspace', 'model', 'currency', 'order-id', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    # Reserve the destination before spending a cloud request; never overwrite evidence.
    with Path(args.output).open('x', encoding='utf-8') as output:
        try:
            result = run(args.tenant, args.workspace, args.model, args.currency, args.order_id)
        except Exception as exc:
            result = {'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}
            json.dump(result, output, indent=2)
            raise SystemExit('Semantic diagnostic unavailable; see saved error type')
        json.dump(result, output, indent=2)
        print(result['result']['status'])
