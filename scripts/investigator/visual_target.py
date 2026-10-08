"""Consumer-owned referent: a stated visual is never replaced by a value match."""
import copy
import re
from . import reported_figure


class TargetUnresolved(ValueError):
    def __init__(self, candidates, reason='No visual matches the declared ticket context.', code='TARGET_UNRESOLVED'):
        self.candidates = copy.deepcopy(candidates)
        self.code = code
        super().__init__(code + ': ' + reason)


def resolve(request, *, ticket, candidates, report_id, measure_id):
    eligible = [c for c in candidates if c['report_id'] == report_id
                and measure_id in c['measure_ids']]
    matched = eligible
    source = mode_source = mode = None
    basis = {'matched': ['report', 'measure'],
             'absent': ['visual_name', 'cell_mode', 'reported_value_in_inventory', 'selection_in_inventory']}
    if request is not None:
        if not isinstance(request, dict) or set(request) != {'source', 'mode', 'mode_source'}:
            raise TargetUnresolved(eligible, 'Invalid visual constraint contract.')
        source, mode_source, mode = (request[k] for k in ('source', 'mode_source', 'mode'))
        if mode not in ('UNGROUPED', 'KEYED', 'TOTAL'):
            raise TargetUnresolved(eligible, 'Cell mode is unresolved.')
        if source is not None:
            quote = reported_figure.span(source, ticket)
            matched = [c for c in matched if quote in c['names']]
            basis['matched'].append('visual_name');basis['absent'].remove('visual_name')
        if mode_source is not None:
            quote = reported_figure.span(mode_source, ticket)
            if mode == 'KEYED':
                raise TargetUnresolved(eligible, 'A keyed target requires a named visual and independently validated cell keys.')
            if mode == 'TOTAL' and not re.search(r'\btotals?\b', quote, re.I):
                raise TargetUnresolved(eligible, 'A total must be explicitly requested.')
            if mode == 'UNGROUPED' and not re.search(r'\bglobal\b', quote, re.I):
                raise TargetUnresolved(eligible, 'Ungrouped scope needs an explicit global request.')
            # An aggregate "total" alone does not name a matrix TOTAL cell:
            # the same aggregate may be displayed by an ungrouped card.
            if mode != 'TOTAL' or source is not None:
                matched = [c for c in matched if bool(c['grouping_columns']) == (mode != 'UNGROUPED')]
                basis['matched'].append('cell_mode');basis['absent'].remove('cell_mode')
        elif source is None and mode is not None:
            raise TargetUnresolved(eligible, 'Cell mode cannot select a visual without ticket evidence.')
    if len(matched) > 1:
        raise TargetUnresolved(matched, 'More than one visual matches the declared ticket context.', 'TARGET_AMBIGUOUS')
    if not matched:
        raise TargetUnresolved([], 'No visual matches the declared ticket context.')
    candidate = matched[0]
    if candidate.get('unsupported'):
        raise TargetUnresolved([candidate], candidate['unsupported'])
    if mode is None:
        mode = 'KEYED' if candidate['grouping_columns'] else 'UNGROUPED'
    if mode not in ('UNGROUPED', 'KEYED', 'TOTAL'):
        raise TargetUnresolved([candidate], 'Cell mode is unresolved.')
    if bool(candidate['grouping_columns']) != (mode != 'UNGROUPED'):
        raise TargetUnresolved([candidate], 'Cell mode contradicts the declared grouping.')
    if mode == 'TOTAL':
        if not isinstance(mode_source,dict) or not re.search(
                r'\btotals?\b',reported_figure.span(mode_source,ticket),re.I):
            raise TargetUnresolved([candidate], 'A total must be explicitly requested.')
    return {'target_id': candidate['target_id'], 'report_id': report_id,
            'measure_id': measure_id, 'mode': mode,
            'source': copy.deepcopy(source), 'mode_source': copy.deepcopy(mode_source),
            'resolution': 'RESOLVED', 'match_basis': basis}


def validate(value, *, ticket, candidates, report_id, measure_id):
    if not isinstance(value, dict) or set(value) != {
            'target_id', 'report_id', 'measure_id', 'mode', 'source', 'mode_source', 'resolution', 'match_basis'}:
        raise TargetUnresolved([c for c in candidates if c['report_id'] == report_id])
    request = {k:value[k] for k in ('source','mode','mode_source')}
    if value['source'] is None and value['mode_source'] is None:request=None
    expected = resolve(request,
                       ticket=ticket, candidates=candidates,
                       report_id=report_id, measure_id=measure_id)
    if value != expected:
        raise TargetUnresolved([c for c in candidates if c['report_id'] == report_id],
                               'Resolved target differs from the stated referent.')
    return value


def complete(value, candidates, filters):
    """A keyed referent needs one explicitly supplied key per declared group."""
    if value['mode'] != 'KEYED':
        return
    from .declared_reproduction import compose
    candidate = next(c for c in candidates if c['target_id'] == value['target_id'])
    selected = compose([{'field_id':f['column_id'], 'operator':'IN', 'values':f['values']}
                        for f in filters if f['operator'] == 'in'])
    singleton = {f['field_id'] for f in selected if len(f['values']) == 1}
    if not set(candidate['grouping_columns']) <= singleton:
        raise TargetUnresolved([candidate], 'Every grouping column requires a stated cell key.')
