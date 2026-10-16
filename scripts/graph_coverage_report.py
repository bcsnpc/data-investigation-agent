"""Offline operator coverage summary. Reachability never earns verification."""
from collections import Counter,defaultdict
import json

DEPENDENCIES={'COMPUTED_FROM','DERIVED_IN_STEP','COPIED_TO','JOINED_VIA','FILTERED_BY'}
COLUMNS={'COLUMN','CALCULATED_COLUMN'}
PHYSICAL={'SqlColumn','WarehouseColumn','LakehouseColumn'}


def coverage(graph,baseline):
    if graph.get('truncated'):raise ValueError('COVERAGE_GRAPH_TRUNCATED')
    if len(graph['nodes'])+len(graph['edges'])>10000:raise ValueError('COVERAGE_GRAPH_BOUND')
    nodes={n['id']:n for n in graph['nodes']};unavailable=graph.get('unavailable_owners',{})
    edges=defaultdict(list)
    for edge in graph['edges']:
        if edge['kind'] in DEPENDENCIES:edges[edge['source']].append(edge)
    def blocked(item):
        return bool({item['owner'],item.get('properties',{}).get('definition_source_owner')} & unavailable.keys())
    def start(node_id):
        if node_id not in nodes:return {'id':node_id,'status':'REMOVED','source_columns':[],
            'terminal_physical_columns':[],'complete_verified':False,'stops':['START_REMOVED']}
        visited=set();active=set();stops=set();sources=set();physical=set();proof_scopes=set();all_verified=True
        def visit(identity):
            nonlocal all_verified
            if identity in active:stops.add('DEPENDENCY_CYCLE');all_verified=False;return
            if identity in visited:return
            visited.add(identity);active.add(identity)
            node=nodes[identity]
            if blocked(node):stops.add('OWNER_UNAVAILABLE');all_verified=False;active.remove(identity);return
            if node['confidence']=='UNKNOWN':stops.add('UNKNOWN_NODE');all_verified=False;active.remove(identity);return
            is_source=node['kind'] in COLUMNS and node['properties'].get('system_of_record') is True
            if is_source:sources.add(identity)
            linked=edges[identity]
            if not linked:
                if node['properties'].get('native_kind') in PHYSICAL:physical.add(identity)
                if not is_source:stops.add('NO_DECLARED_SOURCE_CONTINUATION');all_verified=False
            for edge in linked:
                target=edge['target']
                if blocked(edge):stops.add('OWNER_UNAVAILABLE');all_verified=False;continue
                if edge['confidence']=='UNKNOWN':stops.add('UNKNOWN_EDGE');all_verified=False;continue
                if edge['properties'].get('execution_established') is False:
                    stops.add('DEPLOYMENT_NOT_ESTABLISHED');all_verified=False;continue
                if target not in nodes:stops.add('TARGET_NOT_PRESENT');all_verified=False;continue
                proof=edge['verification']
                if edge['confidence']!='VERIFIED' or proof['state']!='CURRENT' or not proof['evidence_ids'] or not proof['scope_hash']:
                    all_verified=False
                else:proof_scopes.add(proof['scope_hash'])
                visit(target)
            active.remove(identity)
        visit(node_id)
        return {'id':node_id,'status':'UNAVAILABLE' if 'OWNER_UNAVAILABLE' in stops else 'PRESENT',
            'source_columns':sorted(sources),'terminal_physical_columns':sorted(physical),
            'complete_verified':bool(sources) and all_verified and not stops and len(proof_scopes)==1,
            'stops':sorted(stops),'visited':len(visited)}
    current={n['id'] for n in nodes.values() if n['kind'] in ('VISUAL','SLICER')}
    baseline_ids={n['id'] for n in baseline['nodes'] if n['kind'] in ('VISUAL','SLICER')}
    rows=[start(identity) for identity in sorted(current|baseline_ids)]
    def totals(ids):
        selected=[row for row in rows if row['id'] in ids]
        return {'starts':len(selected),'present':sum(r['status']!='REMOVED' for r in selected),
            'unavailable':sum(r['status']=='UNAVAILABLE' for r in selected),
            'reaches_declared_source_column':sum(bool(r['source_columns']) for r in selected),
            'reaches_terminal_physical_column':sum(bool(r['terminal_physical_columns']) for r in selected),
            'complete_verified_paths':sum(r['complete_verified'] for r in selected)}
    return {'nodes':len(nodes),'edges':len(graph['edges']),
        'nodes_by_kind':dict(Counter(n['kind'] for n in nodes.values())),
        'nodes_by_confidence':dict(Counter(n['confidence'] for n in nodes.values())),
        'edges_by_kind':dict(Counter(e['kind'] for e in graph['edges'])),
        'edges_by_confidence':dict(Counter(e['confidence'] for e in graph['edges'])),
        'declared_source_columns':sum(n['kind'] in COLUMNS and n['properties'].get('system_of_record') is True for n in nodes.values()),
        'unavailable_owners':unavailable,'current_starts':totals(current),'baseline_cohort':totals(baseline_ids),
        'new_start_ids':sorted(current-baseline_ids),'removed_start_ids':sorted(baseline_ids-current),'starts':rows}


def dependency_observations(assets):
    """Collection status and retained row counts, separate from graph reachability."""
    rows=[]
    for asset in assets:
        if asset['kind']!='EngineDependencyMetadata':continue
        metadata=asset['metadata'];result=metadata['result'];receipt=result.get('receipt') or {}
        rows.append({'asset':asset['id'],'owner':asset.get('parent_id'),'kind':result.get('request',{}).get('kind'),
            'status':result.get('status'),'row_count':len(result.get('rows') or []),
            'model_definition_hash':metadata.get('model_definition_hash'),
            'receipt_status':receipt.get('status'),'receipt_id':receipt.get('receipt_id'),
            'error':receipt.get('error'),'unknown':result.get('unknown')})
    return rows


def markdown(report):
    lines=['# Round Nineteen B graph coverage readback','',report['at'],'',
      'Platform PostgreSQL and hash-verified definition readback only; no estate or model calls.',
      'A successful owner refresh is not evidence that an INFO query succeeded. Query results below come from retained dependency assets.','',
      '| Estate | Nodes / edges | Original starts present / cohort | Reaches declared source column | Complete VERIFIED | Unavailable starts |',
      '|---|---:|---:|---:|---:|---:|']
    for estate,value in report['estates'].items():
        s=value['baseline_cohort'];lines.append(f"| {estate} | {value['nodes']} / {value['edges']} | {s['present']} / {s['starts']} | {s['reaches_declared_source_column']} | {s['complete_verified_paths']} | {s['unavailable']} |")
    lines+=['','Declared source means an explicit `system_of_record` column. Terminal physical columns are separately reported in JSON; they are not assumed to be the application source. Complete VERIFIED requires all traversed dependency branches to terminate at declared source columns, current edge receipts at one scope, and no UNKNOWN, unavailable, unestablished-deployment or cyclic branch. This report cannot promote an edge.','']
    for estate,value in report['estates'].items():
        lines += ['## '+estate,'', 'Node kinds: `'+json.dumps(value['nodes_by_kind'],sort_keys=True)+'`.',
          'Edge kinds: `'+json.dumps(value['edges_by_kind'],sort_keys=True)+'`.',
          'Edge confidence: `'+json.dumps(value['edges_by_confidence'],sort_keys=True)+'`.','',
          '| Model owner | Metadata kind | Status | Retained rows | Receipt status |','|---|---|---|---:|---|']
        for row in value['dependency_observations']:
            lines.append('| '+ ' | '.join(str(row.get(k,'')) for k in ('owner','kind','status','row_count','receipt_status'))+' |')
        if not value['dependency_observations']:lines+=['| No retained dependency observation | | NOT_COLLECTED | 0 | |']
        lines+=['',f"Unavailable owners: {len(value['unavailable_owners'])}. Raw records and exact errors remain in the private readback.",'']
    return '\n'.join(lines)+'\n'
