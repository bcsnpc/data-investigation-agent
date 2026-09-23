"""Display physical membership from scoped provider identities, never infer bindings."""
from urllib.parse import urlsplit


def describe(asset, by_id=None):
    by_id=by_id or {}
    current=asset;seen=set();schema=None
    while current and current.get('id') not in seen:
        seen.add(current.get('id'))
        schema=schema or current.get('metadata',{}).get('schema_name')
        current=by_id.get(current.get('parent_id'))
    uri=urlsplit(asset.get('id',''));parts=uri.path.strip('/').split('/')
    if uri.scheme=='sql' and uri.netloc and parts[0]:
        return {'system':'SQL','connection':f'sql://{uri.netloc}/{parts[0]}',
                'schema':schema,'schema_status':'DISCOVERED' if schema else 'UNKNOWN'}
    if uri.scheme=='fabric' and uri.netloc and parts[0]:
        owner=f'fabric://{uri.netloc}/{parts[0]}'
        owner_asset=by_id.get(owner,{})
        return {'system':'FABRIC','connection':owner,'owner_kind':owner_asset.get('kind',asset.get('kind') if asset.get('id')==owner else 'UNKNOWN'),
                'schema':schema,'schema_status':'DISCOVERED' if schema else 'UNKNOWN',
                'sql_endpoint_binding':'NOT_ESTABLISHED'}
    return {'system':'UNKNOWN','connection':None,'schema':schema,'schema_status':'UNKNOWN'}


def object_feedback(store, config, objects, error):
    from .context_search import latest
    connection='sql://'+config['sql']['server']+'/'+config['sql']['database']
    context=latest(store) or {'assets':[]}
    by_id={a['id']:a for a in context['assets']}
    candidates={a['id']:a for a in objects.values()}
    candidates.update(by_id)
    name=error.feedback['object_name'].casefold()
    matches=[a for a in candidates.values() if a.get('availability','CURRENT')=='CURRENT'
             and a.get('kind') in ('SqlObject','LakehouseTable')
             and (a.get('metadata',{}).get('name') or a.get('name','')).casefold()==name]
    targets=[{'id':a['id'],'kind':a['kind'],'name':a.get('name') or a['metadata']['name'],
              'physical_binding':describe(a,by_id)} for a in matches[:8]]
    other=any(t['physical_binding']['connection']!=connection for t in targets)
    return {**error.feedback,'searched_connection':connection,'approved_schema':config['sql']['visibility_schema'],
            'catalog_targets':targets,'targets_truncated':len(matches)>len(targets),
            'catalog_search':{'operation':'search','value':error.feedback['object_name'][:200]},
            'binding_notice':('Same-name discovered candidates belong to different physical systems/connections. '
                'They cannot be joined in one query through this SQL connection. Inspect exact identities; '
                'use separately authorized reads and compare with explicit equivalence limits.' if other else
                'Inspect exact catalog targets and their schemas before proposing another query.'),
            'limitation':'Name matches are retrieval hints, not identity equivalence, query repair or permission.'}
