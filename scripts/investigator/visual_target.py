"""Consumer-owned referent: a stated visual is never replaced by a value match."""
import copy
import re
from . import reported_figure


class TargetUnresolved(ValueError):
    def __init__(self, candidates, reason='A target visual must be named unambiguously.'):
        self.candidates = copy.deepcopy(candidates)
        super().__init__('TARGET_UNRESOLVED: ' + reason)


def resolve(request, *, ticket, candidates, report_id, measure_id):
    eligible = [c for c in candidates if c['report_id'] == report_id
                and measure_id in c['measure_ids']]
    if not isinstance(request, dict) or set(request) != {'source', 'mode', 'mode_source'}:
        raise TargetUnresolved(eligible)
    quote = reported_figure.span(request['source'], ticket)
    matched = [c for c in eligible if quote in c['names']]
    if len(matched) != 1:
        raise TargetUnresolved(matched or eligible)
    candidate = matched[0]
    if candidate.get('unsupported'):
        raise TargetUnresolved([candidate], candidate['unsupported'])
    mode = request['mode']
    if mode not in ('UNGROUPED', 'KEYED', 'TOTAL'):
        raise TargetUnresolved([candidate], 'Cell mode is unresolved.')
    if bool(candidate['grouping_columns']) != (mode != 'UNGROUPED'):
        raise TargetUnresolved([candidate], 'Cell mode contradicts the declared grouping.')
    if mode == 'TOTAL':
        if not isinstance(request['mode_source'],dict) or not re.search(
                r'\btotals?\b',reported_figure.span(request['mode_source'],ticket),re.I):
            raise TargetUnresolved([candidate], 'A total must be explicitly requested.')
    elif request['mode_source'] is not None:
        raise TargetUnresolved([candidate], 'Only an explicit total carries a total span.')
    return {'target_id': candidate['target_id'], 'report_id': report_id,
            'measure_id': measure_id, 'mode': mode,
            'source': copy.deepcopy(request['source']),
            'mode_source': copy.deepcopy(request['mode_source'])}


def validate(value, *, ticket, candidates, report_id, measure_id):
    if not isinstance(value, dict) or set(value) != {
            'target_id', 'report_id', 'measure_id', 'mode', 'source', 'mode_source'}:
        raise TargetUnresolved([c for c in candidates if c['report_id'] == report_id])
    expected = resolve({k:value[k] for k in ('source','mode','mode_source')},
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
