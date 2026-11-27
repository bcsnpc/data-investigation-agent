"""Offline completeness audit of a hash-pinned native discovery bundle.

This does not authenticate, infer mappings by name or confer read permission.
"""
import re


def check(bundle,configuration):
    assets=bundle.get('assets',[])
    if isinstance(assets,dict):assets=list(assets.values())
    index={a['id']:a for a in assets};gaps=[]
    if len(index)!=len(assets):gaps.append('duplicate asset identity')
    if not index:gaps.append('native discovery assets missing')
    bindings=bundle.get('source_bindings',[])
    nodes=bundle.get('graph',{}).get('nodes',[])
    edges=bundle.get('graph',{}).get('edges',[])
    columns={}
    for a in assets:
        if a['kind']=='SemanticColumn':columns.setdefault(a['parent_id'],set()).add(a['name'])
    models=[a for a in assets if a['kind']=='SemanticModel']
    tables=[a for a in assets if a['kind']=='SemanticTable']
    for a in assets:
        if a['kind'] in ('SqlObject','WarehouseTable','LakehouseTable'):
            cs=a.get('metadata',{}).get('columns',[])
            if not cs or any(not c.get('name')or not c.get('data_type')for c in cs):
                gaps.append('columns missing: '+a['id'])
    for table in tables:
        table_id=table['id'];model=table['parent_id']
        native_columns=table.get('metadata',{}).get('columns',[])
        for column in native_columns:
            if column.get('name') not in columns.get(table_id,set()):gaps.append('semantic column missing: '+table_id+'/'+str(column.get('name')))
        matched=[b for b in bindings if b.get('table_asset')==table_id and b.get('model_id')==model]
        if not matched:gaps.append('source binding missing: '+table_id)
        for binding in matched:
            source=index.get(binding.get('source_asset'),{})
            address='sql://'+str(binding.get('server'))+'/'+str(binding.get('sql_database'))
            if source.get('parent_id')!=address or not re.fullmatch('[a-f0-9]{64}',binding.get('definition_sha256','')):
                gaps.append('source binding evidence/address differs: '+table_id)
            if not any(c['server']==binding.get('server')and c['database']==binding.get('sql_database') for c in configuration.get('connections',{}).values()):
                gaps.append('source connection not installed: '+table_id)
    for a in assets:
        if a['kind'] not in ('Measure','SemanticRelationship'):continue
        table=index.get(a.get('parent_id'),{})
        model=table.get('parent_id') if a['kind']=='Measure' else a.get('parent_id')
        model_tables={t['name']:t['id'] for t in tables if t['parent_id']==model}
        meta=a.get('metadata',{})
        if a['kind']=='SemanticRelationship':
            for side in ('from','to'):
                if meta.get(side+'Column')not in columns.get(model_tables.get(meta.get(side+'Table')),set()):
                    gaps.append('relationship column missing: '+a['id']+'/'+side)
        else:
            expression=meta.get('expression','')
            if isinstance(expression,list):expression='\n'.join(expression)
            for match in re.finditer(r"(?:'((?:[^']|'')+)'|\b([A-Za-z_][\w]*))\[([^\]]+)\]",expression):
                name=(match[1]or match[2]).replace("''", "'");column=match[3]
                if column not in columns.get(model_tables.get(name),set()):
                    gaps.append('measure column missing: '+a['id']+'/'+name+'['+column+']')
            graph_ids={n['id'] for n in nodes if n.get('properties',{}).get('asset_id')==a['id']}
            if not any(e['source']in graph_ids and e['kind']=='COMPUTED_FROM' for e in edges):
                declarations=[d for d in assets if d['kind']=='EngineDependencyMetadata'and d.get('parent_id')==model]
                if not declarations:gaps.append('native dependencies missing: '+a['id'])
    proofs=bundle.get('model_readability',{})
    for model in models:
        proof=proofs.get(model['id'],{})
        if not (proof.get('status')=='SUCCEEDED' and proof.get('read_only_verified')is True and
                proof.get('identity_reference') and proof.get('observed_at') and
                re.fullmatch('[a-f0-9]{64}',proof.get('capture_sha256',''))):
            gaps.append('model readability not proved: '+model['id'])
        rls=proof.get('rls_route',{})
        if rls.get('status')!='VERIFIED' or rls.get('model_id')!=model['id'] or not rls.get('identity_reference'):
            gaps.append('RLS route not proved: '+model['id'])
    return {'status':'DISCOVERY_COMPLETE'if not gaps else'DISCOVERY_INCOMPLETE',
        'complete':not gaps,'assets':len(assets),'models':len(models),'model_tables':len(tables),
        'gaps':sorted(set(gaps)),'network_calls':0}
