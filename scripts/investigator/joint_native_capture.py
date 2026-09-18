"""One-response native aggregate/record consistency, never a remote snapshot claim."""
from .model_context import assets as model_assets
from .onboarding import fields
from . import aggregate_semantics, native_diagnostics


def attach(model, plan, request):
    measure = plan['aggregate_measure_id']
    shape = aggregate_semantics.describe(model, measure)
    if shape['state'] != 'SUPPORTED': raise ValueError('Joint capture requires a direct count or exact sum')
    assets = {a['id']: a for a in model_assets(model['context'])}
    table = shape['input_id'] if shape['operation'] == 'count_rows' else assets[shape['input_id']]['parent_id']
    if table != plan['object_id']: raise ValueError('Aggregate and records must use the same table')
    if shape['operation'] == 'sum' and shape['input_id'] not in plan['column_ids']:
        raise ValueError('Aggregate input must be projected')
    if any(assets[f['column_id']]['parent_id'] != table for f in plan['filters']):
        raise ValueError('Joint capture currently requires filters on the projected table')
    scalar = {k: plan[k] for k in ('model_id', 'revision', 'context_id', 'filters')}
    scalar.update(measure_ids=[measure], dimension_id=None, include_dependencies=False)
    compiled = native_diagnostics.build(model, scalar)
    record_table = request['query'].removeprefix('EVALUATE ')
    scalar_table = compiled['query'].removeprefix('EVALUATE ').replace('ROW("m0",', 'ROW("__aggregate",', 1)
    request['query'] = 'EVALUATE GENERATEALL(' + scalar_table + ',' + record_table + ')'
    request['joint_aggregate'] = {'measure_id': measure, 'shape': shape, 'transport': 'ONE_QUERY_ONE_RESPONSE',
                                  'layout': 'REPEATED_TOTAL_WITH_EMPTY_ROW'}


def split(rows, request):
    if not isinstance(rows, list) or not 1 <= len(rows) <= request['limit'] + 1:
        raise ValueError('Joint response exceeds budget or is empty')
    names = ['[c' + str(i) + ']' for i in range(len(request['types']))] + ['[multiplicity]']
    records = []; scalar = None
    for row in rows:
        fields(row, names + ['[__aggregate]'])
        current = native_diagnostics.typed(row['[__aggregate]'])
        if current['type'] not in ('decimal', 'blank'):
            raise ValueError('Numeric or blank aggregate required')
        if scalar is not None and scalar != current:
            raise ValueError('Repeated aggregate differs within response')
        scalar = current
        if row['[multiplicity]'] is None:
            if len(rows) != 1 or any(row[n] is not None for n in names):
                raise ValueError('Malformed empty-record placeholder')
        else: records.append({n: row[n] for n in names})
    return records, scalar


def reconcile(request, result, scalar):
    from .record_aggregate import reconstruct, equal
    shape = request['joint_aggregate']['shape']
    body = {'measure_id': request['joint_aggregate']['measure_id'], 'observed': scalar,
            'status': 'NOT_ASSESSED', 'reconstructed': None, 'gaps': [],
            'capture_binding': 'ONE_QUERY_ONE_RESPONSE', 'root_cause_verified': False,
            'shared_generation_verified': False, 'effective_report_context_verified': False}
    if result['completeness'] != 'COMPLETE_RESPONSE': body['gaps'].append('RECORD_CAPTURE_INCOMPLETE')
    else:
        try:
            rebuilt = reconstruct({'status': 'COMPLETED', 'request': request, 'result': result},
                                  shape['operation'], shape['input_id'] if shape['operation'] == 'sum' else None)
            body.update(reconstructed=rebuilt, status='CAPTURE_RECONCILES' if equal(scalar, rebuilt['value']) else 'CAPTURE_INCONSISTENCY')
        except ValueError: body['gaps'].append('RECONSTRUCTION_UNAVAILABLE')
    body['limitation'] = 'One response binds the aggregate and projected groups. It does not certify remote snapshot isolation, source equivalence, report context or a cause.'
    return body
