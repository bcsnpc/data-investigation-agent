"""Consumer-owned form authority, separate from model-inferred ticket spans.

This port binds selected identities to the retained catalog. It neither reads
quantities nor supplies provider-generated scope. Description interpretation is
an explicit remaining step, never silently discarded.
"""
import copy
import re
from jsonschema import Draft202012Validator
from . import ticket_protocol as protocol, reported_figure
from .onboarding import digest

VERSION = 'estate-form-input-v1'
NULL_ID = {'anyOf': [protocol.ID, {'type': 'null'}]}
SCHEMA = protocol.obj({
    'version': {'const': VERSION}, 'request_key': protocol.ID,
    'report_id': NULL_ID, 'page_id': NULL_ID, 'target_id': NULL_ID,
    'cell_mode': {'enum': ['UNGROUPED', 'TOTAL', 'KEYED', None]},
    'value_seen': {'anyOf': [protocol.TEXT, {'type': 'null'}]},
    'comparison': {'enum': [*protocol.ROUTES, None]},
    'description': {**protocol.TEXT, 'minLength': 0},
    'cell_keys': {'type': 'array', 'maxItems': 6, 'items': protocol.obj({
        'column_id': protocol.ID, 'value': {'anyOf': [protocol.TEXT,
            {'type':'integer'}, {'type':'boolean'}, {'type':'null'}]}})}}, optional=('cell_keys',))


def resolve(request, models, configuration):
    """Bind explicit picks; an unresolved field produces at most one batch.

    Live list IDs must first be mapped by the platform adapter into these
    retained neutral IDs. A live name or equal quantity never grants authority.
    """
    Draft202012Validator(SCHEMA).validate(request)
    from .ticket_clarification import settings
    configured = settings(configuration)
    routes = {v['route'] for v in configured['comparison_choices']}
    route = request['comparison']
    if route is not None and route not in routes:
        raise ValueError('Comparison outside estate intake choices')
    base = {'version': VERSION, 'authority': 'USER_SUPPLIED_FORM',
            'request_hash': digest(request), 'catalog_hash': digest(models),
            'execution_authorized': False,
            'description_requires_interpretation': bool(request['description']),
            'questions': [], 'scope': None}
    if route == 'OTHER_REPORT':
        return {**base, 'status': 'HELD', 'reason': 'OTHER_REPORT_COMING_SOON'}
    reports = [(m, r) for m in models for r in m.get('reports', [])
               if r['id'] == request['report_id']]
    if request['report_id'] is None:
        return {**base, 'status': 'NEEDS_INPUT', 'questions': [{'field': 'REPORT_PAGE'}]}
    if len(reports) != 1:
        raise ValueError('Selected report is absent or ambiguously bound')
    model, report = reports[0]
    visuals = [v for v in model.get('visuals', []) if v['report_id'] == report['id']]
    if request['page_id'] is None:
        return {**base, 'status': 'NEEDS_INPUT', 'questions': [{'field': 'REPORT_PAGE'}]}
    eligible = [v for v in visuals if v.get('page_id') == request['page_id']]
    if not eligible:
        raise ValueError('Selected page has no retained executable visual')
    selected = request['target_id']
    if selected is not None:
        eligible = [v for v in eligible if v['target_id'] == selected]
        if len(eligible) != 1:
            raise ValueError('Selected visual is outside the selected report/page')
    if len(eligible) != 1:
        return {**base, 'status': 'NEEDS_INPUT', 'questions': [{
            'field': 'NUMBER', 'candidate_target_ids': [v['target_id'] for v in eligible]}]}
    visual = eligible[0]
    if visual.get('unsupported') or len(visual['measure_ids']) != 1:
        return {**base, 'status': 'HELD', 'reason': 'TARGET_NOT_EXECUTABLE'}
    mode = request['cell_mode']
    if mode is None:
        if visual['grouping_columns']:
            return {**base, 'status': 'NEEDS_INPUT', 'questions': [{'field': 'NUMBER'}]}
        mode = 'UNGROUPED'
    if bool(visual['grouping_columns']) != (mode != 'UNGROUPED'):
        raise ValueError('Selected cell mode contradicts the selected visual')
    keys = request.get('cell_keys', [])
    if len({k['column_id'] for k in keys}) != len(keys):
        raise ValueError('Duplicate cell key')
    if keys and (mode != 'KEYED' or set(k['column_id'] for k in keys) != set(visual['grouping_columns'])):
        raise ValueError('Cell keys must match exactly the selected visual grouping')
    from .filter_scope import compile_filter
    columns = {c['column_id']: c for c in model.get('columns', [])}
    for k in keys:
        if k['column_id'] not in columns:
            raise ValueError('Cell key is absent from the retained column catalog')
        compile_filter({'column_id': k['column_id'], 'operator': 'in', 'values': [k['value']]},
                       {'dataType': columns[k['column_id']]['data_type']}, 'validated_reference')
    if mode == 'KEYED' and not keys:
        return {**base, 'status': 'NEEDS_INPUT', 'questions': [
            {'field': 'NUMBER', 'reason': 'CELL_KEYS_UNRESOLVED'}]}
    if route is None:
        return {**base, 'status': 'NEEDS_INPUT', 'questions': [{'field': 'COMPARISON'}]}
    wording = request['value_seen']
    figure = {'state': 'UNSPECIFIED'}
    if wording is not None:
        source = {'start': 0, 'end': len(wording), 'quote': wording}
        from .intake_statement_registry import empty_matches
        if empty_matches(wording):
            if re.search(r'\d', wording):
                raise ValueError('An empty state and a numeric figure cannot share the value field')
            figure = {'state': 'EMPTY', 'source': source}
        else:
            value, precision = reported_figure.stated(wording)
            figure = {'state': 'NUMBER', 'value': value, 'precision': precision, 'source': source}
        reported_figure.validate(figure, wording)
    return {**base, 'status': 'BOUND', 'scope': {
        'model_id': model['id'], 'report_id': report['id'], 'page_id': request['page_id'],
        'target_id': visual['target_id'], 'measure_id': visual['measure_ids'][0],
        'cell_mode': mode, 'comparison': route, 'reported_figure': copy.deepcopy(figure),
        'figure_document': wording, 'figure_pointer': '/value_seen',
        'filters': [{'column_id': k['column_id'], 'operator': 'in',
                     'values': [copy.deepcopy(k['value'])]} for k in keys]}}
