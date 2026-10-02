"""Native visual roles become neutral measure-and-key cell addresses."""
import copy
from ..onboarding import digest

# This knowledge is adapter-owned; no native role names cross this boundary.
ROLES = {
    'card': ({}, {'Values'}),
    'multiRowCard': ({}, {'Values'}),
    'tableEx': ({'Values': 'mixed'}, {'Values'}),
    'pivotTable': ({'Rows': 'group', 'Columns': 'group'}, {'Values'}),
    'clusteredBarChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'clusteredColumnChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'stackedBarChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'stackedColumnChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'lineChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
}


def projected_measure(model, document, measure_id):
    from .report_predicates import member
    state = document.get('visual', {}).get('query', {}).get('queryState', {})
    return any(isinstance(p, dict) and isinstance(p.get('field'), dict)
               and 'Measure' in p['field'] and member(model, p['field'], 'Measure')['id'] == measure_id
               for role in state.values() for p in role.get('projections', []))


def roles(model, document):
    from .report_predicates import member, Refusal
    visual = document.get('visual', {}); kind = visual.get('visualType')
    if kind not in ROLES: raise Refusal('UNSUPPORTED_VISUAL_TYPE: ' + str(kind))
    groups, value_roles = ROLES[kind]
    state = visual.get('query', {}).get('queryState', {})
    columns, measures = {}, {}
    for role, binding in state.items():
        if role not in groups and role not in value_roles:
            raise Refusal('UNSUPPORTED_PROJECTION_ROLE: ' + str(role))
        for projection in binding.get('projections', []):
            field = projection.get('field', {})
            if 'Column' in field and role in groups:
                asset = member(model, field, 'Column'); columns[asset['id']] = asset
            elif 'Measure' in field and role in value_roles:
                asset = member(model, field, 'Measure'); measures[asset['id']] = asset
            else:
                name = projection.get('displayName') or projection.get('queryRef') or str(next(iter(field), 'UNKNOWN'))
                raise Refusal('UNSUPPORTED_PROJECTED_FIELD: ' + name)
    return list(columns.values()), list(measures.values())


def addresses(model, document, target_id, measure_id, scope):
    from .report_predicates import Refusal
    from ..declared_reproduction import compose
    columns, measures = roles(model, document)
    if measure_id not in {m['id'] for m in measures}: return []
    stated = {}
    for restriction in scope.get('filters', []):
        if restriction.get('operator', 'in') != 'in': continue
        stated.setdefault(restriction['column_id'], []).append({
            'field_id': restriction['column_id'], 'operator': 'IN', 'values': restriction['values']})
    keys = []; missing = []
    for column in columns:
        values = compose(stated[column['id']])[0]['values'] if column['id'] in stated else []
        if len(values) != 1: missing.append(column['name'])
        else: keys.append({'field_id': column['id'], 'operator': 'IN', 'values': values})
    if missing: raise Refusal('MISSING_CELL_KEYS: ' + ', '.join(missing))
    def cell(keys, mode):
        result = {'target_id': target_id, 'measure_id': measure_id,
                  'grouping_columns': sorted(c['id'] for c in columns),
                  'key_restrictions': sorted(copy.deepcopy(keys), key=lambda r: r['field_id']), 'mode': mode}
        result['id'] = digest(result)
        return result
    result = [cell(keys, 'KEYED' if columns else 'UNGROUPED')]
    if columns: result.append(cell([], 'TOTAL'))
    return result
