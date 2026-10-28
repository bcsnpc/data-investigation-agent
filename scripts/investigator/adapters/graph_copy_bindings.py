"""Copy dependencies bound by connection UUID and native destination UUID."""
from copy import deepcopy


def activities(doc,kind):
    if kind!='CopyJob':return doc.get('properties',{}).get('activities',doc.get('activities',[]))
    base=doc.get('properties',{});result=[]
    for item in doc.get('activities',[]):
        props=item.get('properties',{});source={**deepcopy(base.get('source',{})),**deepcopy(props.get('source',{}))}
        sink={**deepcopy(base.get('destination',{})),**deepcopy(props.get('destination',{}))}
        result.append({'name':item.get('id','Copy'),'type':'Copy','typeProperties':{'source':source,'sink':sink,'translator':deepcopy(props.get('translator',{}))}})
    return result


def resolve(assets,properties):
    values=list(assets.values());source=properties.get('source',{});sink=properties.get('sink',{})
    ds=source.get('datasetSettings',{});connection=ds.get('externalReferences',source.get('connectionSettings',{}).get('externalReferences',{})).get('connection')
    matches=[a for a in values if a['kind']=='SourceConnection'and a.get('metadata',{}).get('id')==connection]
    if len(matches)!=1:return None
    details=matches[0]['metadata'].get('connectionDetails',{});path=details.get('path')
    if details.get('type')!='SQL'or not isinstance(path,str)or path.count(';')!=1:return None
    server,database=path.split(';');root='sql://'+server+'/'+database
    table=ds.get('typeProperties',ds);schema,name=table.get('schema'),table.get('table')
    sources=[a for a in values if a['kind']=='SqlObject'and a.get('parent_id')==root and a['metadata'].get('schema_name')==schema and a['metadata'].get('name')==name]
    ds=sink.get('datasetSettings',{});link=ds.get('linkedService',{}).get('properties',sink.get('connectionSettings',{}));location=link.get('typeProperties',{})
    workspace,artifact=location.get('workspaceId'),location.get('artifactId');table=ds.get('typeProperties',ds)
    root='fabric://'+str(workspace)+'/'+str(artifact)
    destinations=[]
    for a in values:
        if a['kind']not in ('LakehouseTable','WarehouseTable')or a.get('parent_id')!=root:continue
        meta=a.get('metadata',{});sch=meta.get('schema_name','dbo');nm=meta.get('name',a['name'])
        if '.'in nm:sch,nm=nm.split('.',1)
        if (sch,nm)==(table.get('schema','dbo'),table.get('table')):destinations.append(a)
    if len(sources)!=1 or len(destinations)!=1:return None
    return {'source_asset':sources[0]['id'],'destination_asset':destinations[0]['id'],
      'connection_asset':matches[0]['id'],'native_destination':{'workspaceId':workspace,'artifactId':artifact},
      'source_query':source.get('sqlReaderQuery'),'basis':'EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS'}


def attach(graph,node,properties,proof):
    binding=resolve(graph.assets,properties)
    if binding is None:return False
    source,target=binding['source_asset'],binding['destination_asset']
    if source not in graph.by_asset or target not in graph.by_asset:return False
    graph.nodes[node]['properties']['native_copy_binding']=binding
    for edge in list(graph.edges.values()):
        if edge['kind']=='CONTAINS'and edge['target']==node and graph.nodes[edge['source']]['kind']=='PIPELINE':
            graph.link('COMPUTED_FROM',edge['source'],node,proof,properties={'basis':'NATIVE_COPY_ACTIVITY_OWNERSHIP'})
    graph.link('COMPUTED_FROM',node,graph.by_asset[source],proof,properties=binding)
    graph.link('DERIVED_IN_STEP',graph.by_asset[target],node,proof,properties=binding)
    # Observed source-system object is a graph terminal, not an assertion that
    # this object is the estate's system of record or that values match.
    graph.nodes[graph.by_asset[source]]['properties']['source_system_object']=True
    return True
