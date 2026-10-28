"""Ticket-free, offline structural graph health; never claims successful reads."""
from collections import defaultdict,deque,Counter

DATA_EDGES={'COMPUTED_FROM','JOINED_VIA','COPIED_TO','DERIVED_IN_STEP'}
AUXILIARY={'FILTER','SECURITY_ROLE','REFRESH_SCHEDULE','RELATIONSHIP','INTERACTION'}
PRODUCERS={'PIPELINE','COPY_ACTIVITY','NOTEBOOK','PROCEDURE','QUERY_STEP'}


def analyze(snapshot):
    nodes={n['id']:n for n in snapshot['nodes']};edges=snapshot['edges'];out=defaultdict(list);parent={}
    for e in edges:
        if e['kind']=='CONTAINS':parent[e['target']]=e['source']
        elif e['kind'] in DATA_EDGES:out[e['source']].append(e)
    queryable=set(snapshot.get('queryable_assets',[]));rows=[]
    for visual in sorted((n for n in nodes.values() if n['kind']=='VISUAL'),key=lambda n:n['id']):
        seen=set();queue=deque([visual['id']]);breaks=[]
        while queue:
            ident=queue.popleft()
            if ident in seen:continue
            seen.add(ident);node=nodes.get(ident)
            if node is None:
                breaks.append({'node':ident,'reason':'MISSING_PARENT_OR_DEPENDENCY','component':'scanner data'});continue
            if node['kind'] in AUXILIARY:continue
            if node.get('confidence')=='UNKNOWN':
                breaks.append({'node':ident,'reason':(node.get('unknown') or {}).get('reason','UNKNOWN_BINDING'),'component':'scanner data'})
            linked=out[ident]
            if not linked and not node.get('properties',{}).get('system_of_record'):
                breaks.append({'node':ident,'reason':'NO_UPSTREAM_BINDING','component':'scanner data'})
            for edge in linked:
                if edge.get('confidence')=='UNKNOWN':breaks.append({'node':ident,'reason':'AMBIGUOUS_OR_UNKNOWN_DEPENDENCY','component':'scanner data'})
                queue.append(edge['target'])
        reached=[nodes[i]for i in seen if i in nodes]
        if not any(n.get('properties',{}).get('system_of_record') for n in reached):
            breaks.append({'node':visual['id'],'reason':'NO_DECLARED_SOURCE_SYSTEM_REACHED','component':'route builder'})
        if not any(n['kind'] in PRODUCERS for n in reached):
            breaks.append({'node':visual['id'],'reason':'NO_PRODUCER_REACHED','component':'route builder'})
        if queryable and not any(n.get('properties',{}).get('asset_id') in queryable for n in reached):
            breaks.append({'node':visual['id'],'reason':'NO_INSTALLED_QUERY_ROUTE','component':'route builder'})
        report=parent.get(parent.get(visual['id']))
        rows.append({'visual':visual['id'],'name':visual['label'],'report':report,'report_name':nodes.get(report,{}).get('label','UNKNOWN_CONTAINMENT'),
            'fully_traceable':not breaks,'nodes':sorted(seen),'breaks':breaks})
    groups=defaultdict(list)
    for r in rows:groups[r['report']].append(r)
    def totals(items):
        count=sum(r['fully_traceable']for r in items)
        return {'visuals':len(items),'fully_traceable':count,'percentage':round(100*count/len(items),2)if items else None}
    return {'version':'graph-health/1','basis':'Retained declared graph structure; not proof of live readability, snapshot alignment or data correctness.',
        'overall':totals(rows),'reports':[{'report':key,'name':items[0]['report_name'],**totals(items)}for key,items in groups.items()],
        'break_counts':dict(Counter(b['component']+': '+b['reason']for r in rows for b in r['breaks'])),'visuals':rows}


def markdown(result):
    lines=['# Graph health','',result['basis'],'','| Report | Full paths / visuals | Percent |','|---|---:|---:|']
    for r in result['reports']:lines.append(f"| {r['name']} | {r['fully_traceable']}/{r['visuals']} | {r['percentage']}% |")
    lines+=['',f"Overall: {result['overall']}",'','## Every break','']
    for v in result['visuals']:
        for b in v['breaks']:lines.append(f"- {v['report_name']} / {v['name']} (`{v['visual']}`): {b['component']}: {b['reason']} at `{b['node']}`.")
    return '\n'.join(lines)+'\n'
