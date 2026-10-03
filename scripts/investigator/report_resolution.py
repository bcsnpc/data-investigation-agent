"""Resolve a request over a stated report; native inspection stays in the adapter."""
import copy
from uuid import uuid4
from . import report_scope, definition_target, reported_figure
from .declared_reproduction import UnsupportedRestriction


class ResolutionRefused(ValueError):
    """An explicit unresolved selection, not a producer contract failure."""


def _prepare(adapter, layer, measure_id, scope, observations):
    from .process_debugging import attest, _observation
    result = copy.deepcopy(scope)
    reports = adapter.report_catalog()
    report_scope.report_binding(scope['report_binding'], reports=reports)
    declarations, grouping = adapter.report_selection_inventory(measure_id, scope['report_binding'])
    for declaration in declarations:
        report_scope.validate_inventory(declaration['inventory'], declaration['restrictions'],
            binding=scope['report_binding'], reports=reports)
    request = scope.get('selection_request')
    if request is None: return result, observations
    report_scope.validate_request(request, reports=reports)
    quote = request['value_source']['quote']; matches = {}
    for declaration in declarations:
        for entry in declaration['inventory']['entries']:
            if entry['disposition'] != 'ACTIVE': continue
            for r in entry['restrictions']:
                for value in r['values']:
                    if definition_target.literal_text(value) == quote:
                        matches[(entry['id'], r['field_id'])] = (declaration, value)
    columns = adapter.selection_columns()
    source = request['column_source']
    if source is not None:
        named = [c for c in columns if c['name'] == source['quote']]
        if len(named) != 1: raise ResolutionRefused('Target ambiguity: explicitly stated column does not match exactly one catalog column.')
        candidates = [named[0]['id']]
    elif len(matches) == 1:
        (entry_id, column_id), (declaration, value) = next(iter(matches.items()))
        target = {'resolution_kind':'EVIDENCE','report_binding':scope['report_binding'],
            'column_id':column_id,'inventory_entry_id':entry_id,'source':request['value_source']}
        report_scope.validate_target(target,reports=reports,inventory=declaration['inventory'],active=declaration['restrictions'])
        attach(result,observations,target,declarations,grouping,columns)
        result['filters'].append({'column_id':column_id,'operator':'in','values':[value]})
        return result, observations
    elif matches:
        raise ResolutionRefused('Target ambiguity: multiple ACTIVE declarations carry the stated value: '+', '.join(sorted(k[1] for k in matches)))
    else:
        candidates = grouping
        if any(e['disposition']=='UNSUPPORTED' for d in declarations for e in d['inventory']['entries']):
            raise ResolutionRefused('Target ambiguity: unsupported report declaration prevents establishing the absence of a declared selection.')
    if not candidates: raise ResolutionRefused('Target ambiguity: no scoped grouping column can test the stated value.')
    remaining = getattr(adapter, 'remaining_diagnostic_reads', None)
    if remaining is not None and remaining() < len(candidates):
        raise ResolutionRefused('Target ambiguity: diagnostic cap cannot cover every grouping column; no partial value lookup was chosen.')
    for column in candidates:
        probe = attest(adapter.observe_selection_value(layer, column, quote, scope['report_binding']))
        if probe.evidence:
            observation = _observation(probe.evidence,'selection_value_existence')
            observation['execution_surface'] = probe.execution_surface
            observations.append(observation)
        if probe.status != 'OBSERVED' or not probe.evidence:
            raise ResolutionRefused('Target ambiguity: value-existence observation unavailable for '+column+'.')
    by_id = {o['id']:o for o in observations}; found = [o for o in observations if o['value_exists']]
    if source is not None:
        target={'resolution_kind':'STATED','report_binding':scope['report_binding'],'column_id':candidates[0],
            'source':source,'value_source':request['value_source'],'lookup':{
                'status':'MATCH' if found else 'MISMATCH','receipt_ids':[observations[0]['id']]}}
        report_scope.validate_target(target,reports=reports,columns=columns,observations=by_id)
        attach(result,observations,target,declarations,grouping,columns)
        if not found: raise ResolutionRefused('Target ambiguity: explicitly stated column does not contain the stated value; MISMATCH receipt '+observations[0]['id']+'.')
    else:
        if len(found)!=1: raise ResolutionRefused('Target ambiguity: '+('no grouping column contains the value.' if not found else 'multiple grouping columns contain the value: '+', '.join(o['column_id'] for o in found)))
        # All candidate contexts share the report manifest. Absence was checked across all.
        declaration = declarations[0]
        target={'resolution_kind':'OBSERVED','report_binding':scope['report_binding'],'column_id':found[0]['column_id'],
                'receipt_id':found[0]['id'],'source':request['value_source']}
        report_scope.validate_target(target,reports=reports,inventory=declaration['inventory'],active=declaration['restrictions'],
            grouping_columns=candidates,observations=by_id)
    if source is None: attach(result,observations,target,declarations,grouping,columns)
    result['filters'].append({'column_id':target['column_id'],'operator':'in','values':[found[0]['searched_value']]})
    return result, observations


def attach(scope,observations,target,declarations,grouping,columns):
    from .process_debugging import _observation
    if any(f['column_id']==target['column_id'] for f in scope['filters']):
        raise ValueError('Selection request conflicts with an already proposed filter; no guessed filter is adopted.')
    observation=_observation({'id':'report-selection-'+str(uuid4()),'tool':'process',
        'check_kind':'REPORT_SELECTION_RESOLUTION','target':copy.deepcopy(target),
        'reports':copy.deepcopy(declarations[0]['evidence']['report_catalog']),
        'inventories':[{'inventory':d['inventory'],'restrictions':d['restrictions']} for d in declarations],
        'grouping_columns':grouping,'columns':columns,'completeness':'COMPLETE_RESPONSE'},'selection_resolution')
    if 'descriptor' in scope.get('selection_request',{}):
        from .selection_descriptor import note
        observation['selection_request']=copy.deepcopy(scope['selection_request'])
        column=next((c for c in columns if c['id']==target['column_id']),None)
        observation['descriptor_hint']=note(scope['selection_request']['descriptor'],column['name'] if column else None)
    observations.append(observation)
    scope['selection_resolution']=copy.deepcopy(target)
    scope['selection_resolution_evidence_id']=observation['id']


def validate(observation, originals):
    target=observation['target']; inventories=observation['inventories']
    if 'selection_request' in observation:
        from .selection_descriptor import note
        request=observation['selection_request']
        report_scope.validate_request(request,reports=observation['reports'])
        column=next((c for c in observation['columns'] if c['id']==target['column_id']),None)
        if observation.get('descriptor_hint')!=note(request['descriptor'],column['name'] if column else None):
            raise ValueError('Nonbinding descriptor evidence differs from the resolved column')
    if not inventories: raise ValueError('Resolution requires a scoped report inventory')
    for item in inventories:
        report_scope.validate_inventory(item['inventory'],item['restrictions'],binding=target['report_binding'],reports=observation['reports'])
    matches={}
    quote=(target.get('value_source') or target['source'])['quote']
    for item in inventories:
        for entry in item['inventory']['entries']:
            for r in entry['restrictions'] if entry['disposition']=='ACTIVE' else []:
                if any(definition_target.literal_text(v)==quote for v in r['values']): matches[(entry['id'],r['field_id'])]=item
    if target['resolution_kind']=='EVIDENCE':
        if len(matches)!=1: raise ValueError('Resolution requires exactly one ACTIVE declaration across the stated report')
        item=next(iter(matches.values()))
    else:
        if target['resolution_kind']=='OBSERVED' and matches: raise ValueError('Observed resolution cannot replace a declared report selection')
        item=inventories[0]
    return report_scope.validate_target(target,reports=observation['reports'],inventory=item['inventory'],active=item['restrictions'],
        observations=originals,grouping_columns=observation['grouping_columns'],columns=observation['columns'])


def prepare(adapter,layer,measure_id,scope):
    observations=[]
    try: return _prepare(adapter,layer,measure_id,scope,observations)
    except (ResolutionRefused,UnsupportedRestriction) as exc:
        exc.observations=copy.deepcopy(observations)
        raise
