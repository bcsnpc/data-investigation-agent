"""Neutral cell contract: measure, grouping, and separately stated key values."""
from .onboarding import digest


def validate(cell, measure_id, scope=None):
    from .declared_reproduction import compose
    required = {'id', 'target_id', 'measure_id', 'grouping_columns', 'key_restrictions', 'mode'}
    if not isinstance(cell, dict) or set(cell) != required: raise ValueError('Cell contract differs')
    if cell['measure_id'] != measure_id or not isinstance(cell['target_id'], str) or not cell['target_id']:
        raise ValueError('Cell requires a resolved measure and target')
    columns = cell['grouping_columns']; keys = cell['key_restrictions']
    if not isinstance(columns, list) or columns != sorted(set(columns)):
        raise ValueError('Cell grouping columns must be canonical')
    composed = compose(keys)
    if composed != keys or any(len(r['values']) != 1 for r in keys):
        raise ValueError('Cell keys must state exactly one value per grouping column')
    if cell['mode'] == 'KEYED':
        if not columns or columns != [r['field_id'] for r in keys]: raise ValueError('Cell grouping keys are incomplete')
    elif cell['mode'] == 'TOTAL':
        if not columns or keys: raise ValueError('Total cell has grouping metadata but no keys')
    elif cell['mode'] == 'UNGROUPED':
        if columns or keys: raise ValueError('Ungrouped cell cannot carry grouping keys')
    else: raise ValueError('Unknown cell mode')
    if scope is not None and cell['mode'] == 'KEYED':
        supplied = {}
        for r in scope.get('filters', []):
            if r.get('operator', 'in') == 'in':
                supplied.setdefault(r['column_id'], []).append({'field_id': r['column_id'], 'operator': 'IN', 'values': r['values']})
        for key in keys:
            if key['field_id'] not in supplied or compose(supplied[key['field_id']]) != [key]:
                raise ValueError('Cell key was not stated in the resolved ticket scope')
    if cell['id'] != digest({k: v for k, v in cell.items() if k != 'id'}):
        raise ValueError('Cell identity differs from its resolved address')
    return cell
