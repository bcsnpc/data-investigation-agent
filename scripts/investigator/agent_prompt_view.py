"""Model-only compact view; original observations remain the validation source."""
import copy
import json
from .agent_intake_settlement import INTAKE_ADMITTED


def view(transcript, evidence, ticket, fixed_facts=None):
    targets = dict(ticket.get('target_registry', {}))
    scopes = dict(ticket.get('scope_registry', {}))
    layers = set(); steps = set()
    fixed_facts = fixed_facts or {}
    rows = []
    for event in transcript:
        row = {k: copy.deepcopy(event[k]) for k in
               ('event', 'ordinal', 'tool', 'summary', 'reason', 'receipt_id', 'evidence_id',
                'note', 'evidence_ids', 'original_receipt_id', 'validation', 'error_type')
               if k in event}
        result = event.get('result', {})
        if event.get('event') == 'TOOL_RESULT':
            row.update(status=result.get('status'), evidence_ids=result.get('evidence_ids', []))
            if result.get('reason'): row['reason'] = result['reason']
            data = result.get('data', {})
            row['summary'] = {k: copy.deepcopy(data[k]) for k in ('layer','value_state','status','reason') if k in data}
            # A bounded scalar quantity is a useful summary, never a substitute
            # for its complete receipt. Large/non-scalar results require a fetch.
            if 'value' in data and len(json.dumps(data['value'], default=str)) <= 1000:
                row['summary']['value'] = copy.deepcopy(data['value'])
            if 'path' in data:
                row['summary']['path_layers'] = [x['id'] for x in data['path'].get('layers', []) if 'id' in x]
                row['summary']['stopped_by'] = data['path'].get('stopped_by')
            if event.get('tool') == 'resolve_ticket' and result.get('status') == INTAKE_ADMITTED:
                targets.update(result.get('target_registry', {}))
                scopes.update(result.get('scope_registry', {}))
            if event.get('tool') == 'lineage':
                resolved = result.get('data', {}).get('path', {}).get('layers', [])
                layers.update(x['id'] for x in resolved if 'id' in x)
                steps.update(range(1, len(resolved)))
        rows.append(row)
    # Already-admitted AgentProcess supplies scopes through its target registry.
    scopes.update({x['scope_id']: {} for x in targets.values() if 'scope_id' in x})
    ids = {'target_id': sorted(targets), 'scope_id': sorted(scopes),
           'layer_id': sorted(layers), 'id': sorted(evidence), 'step': sorted(steps),
           'report_id': [fixed_facts['report_id']] if fixed_facts.get('report_id') else [],
           'page_id': [fixed_facts['page_id']] if fixed_facts.get('page_id') else [],
           'measure_id': sorted({v['measure_id'] for v in targets.values() if 'measure_id' in v})}
    index = {ref: {k: saved[k] for k in ('tool', 'receipt_id')} |
             {'status': saved['result'].get('status')} for ref, saved in evidence.items()}
    catalog = []
    for item in ticket.get('tool_catalog', []):
        entry = {'name': item['name'], 'description': item.get('description', '')}
        if entry['name'] in ('reproduce','lineage','probe_layer','read_transformation','check_freshness','compare_reports','query_source'):
            entry['description'] += '\nExact admitted targets: ' + repr(ids['target_id']) + '; scopes: ' + repr(ids['scope_id']) + '; resolved layers: ' + repr(ids['layer_id'])
        catalog.append(entry)
    catalog.append({'name':'get_evidence', 'description':'Fetch full unchanged retained evidence. Exact valid IDs: '+repr(ids['id'])})
    return {'transcript': rows, 'evidence': index, 'valid_identifiers': ids, 'tool_catalog': catalog}


def described_schema(schemas, outcomes, ids):
    from .agent_loop import decision_schema
    schemas = copy.deepcopy(schemas)
    for name, schema in schemas.items():
        for key, node in schema.get('properties', {}).items():
            source = 'target_id' if key in ('a', 'b') else key
            if ids.get(source) and (source != 'id' or name == 'get_evidence'):
                node['description'] = node.get('description', '') + '\nExact currently valid identifiers: ' + repr(ids[source])
    result=decision_schema(schemas, outcomes)
    from .process_outcomes import REQUIRED_ROLES
    for choice in result['anyOf']:
        node=choice.get('properties',{}).get('outcome')
        if node is not None:
            node['description']='Required producer evidence roles (necessary, not sufficient): '+repr({
                outcome:list(REQUIRED_ROLES[outcome]) for outcome in sorted(outcomes) if outcome in REQUIRED_ROLES})+'. Tool unavailability is not evidence for these roles; all existing support and coverage gates still apply.'
    return result
