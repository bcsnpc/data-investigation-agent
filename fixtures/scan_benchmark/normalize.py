"""Scoring-side projection of genuine discovery facts; no truth/manifest input.

Missing engine assertions remain unknown. This adapter never derives expected
layer labels, authority or trap outcomes from estate specs or object names.
"""


def sql_facts(batch, graph):
    index={a['id']:a for a in batch['assets']}
    names={a['id']:a['name']for a in index.values()if a['kind']=='SqlObject'}
    names.update({a['id']:names[a['parent_id']]+'.'+a['name']for a in index.values()
                  if a['kind']=='SqlColumn'and a['parent_id']in names})
    objects=[]
    for a in index.values():
        if a['kind']!='SqlObject':continue
        m=a['metadata']
        objects.append(dict(address=a['name'],columns=m.get('columns',[]),
            layer=m.get('layer','UNKNOWN'),source_of_truth=m.get('source_of_truth','UNKNOWN')))
    edges=[]
    for e in graph.get('edges',[]):
        if e['source']not in names or e['target']not in names:continue
        relation=e.get('relation')
        if relation not in('DERIVED_FROM','READS','WRITES'):continue
        if relation=='DERIVED_FROM'and index[e['source']]['kind']=='SqlObject':relation='READS'
        proof=e.get('evidence',[])
        if not any(isinstance(p,dict)and 'INFERRED_FROM_CODE'in p.get('detail','')for p in proof):continue
        value=dict(source=names[e['source']],target=names[e['target']],relation=relation,knowledge='parsed')
        if value not in edges:edges.append(value)
    return dict(origin='DIA_NATIVE_DISCOVERY',objects=objects,edges=edges,
        permission_gaps=[],traps={},uncertain_objects=[])
