"""Model-only compact view; original observations remain the validation source."""
import copy


def view(transcript, evidence, ticket):
    targets = dict(ticket.get('target_registry', {}))
    scopes = dict(ticket.get('scope_registry', {}))
    layers = set()
    rows = []
    for event in transcript:
        row = {k: copy.deepcopy(event[k]) for k in
               ('event', 'ordinal', 'tool', 'summary', 'reason', 'receipt_id', 'evidence_id')
               if k in event}
        result = event.get('result', {})
        if event.get('event') == 'TOOL_RESULT':
            row.update(status=result.get('status'), evidence_ids=result.get('evidence_ids', []))
            if result.get('reason'): row['reason'] = result['reason']
            if event.get('tool') == 'resolve_ticket' and result.get('status') == 'ADMITTED':
                targets.update(result.get('target_registry', {}))
                scopes.update(result.get('scope_registry', {}))
            if event.get('tool') == 'lineage':
                layers.update(x['id'] for x in result.get('data', {}).get('path', {}).get('layers', []) if 'id' in x)
        rows.append(row)
    # Already-admitted AgentProcess supplies scopes through its target registry.
    scopes.update({x['scope_id']: {} for x in targets.values() if 'scope_id' in x})
    ids = {'target_id': sorted(targets), 'scope_id': sorted(scopes),
           'layer_id': sorted(layers), 'id': sorted(evidence)}
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
            if source in ids and (source != 'id' or name == 'get_evidence'):
                node['description'] = node.get('description', '') + '\nExact currently valid identifiers: ' + repr(ids[source])
    return decision_schema(schemas, outcomes)
