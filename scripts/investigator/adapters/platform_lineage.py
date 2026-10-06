"""Item-rooted platform relation decoding. All returned graphs are proposals."""
from urllib.parse import urlsplit
from uuid import UUID
from ..lineage_proposer import validate

RELATIONS={'Datasource':'READS_FROM','PushData':'WRITES_TO','Orchestration':'ORCHESTRATES',
    'Shortcut':'SHORTCUT','CascadeDelete':'CONTAINS','WeakAssociation':'ASSOCIATION','HiddenInWorkspace':'HIDDEN'}

def item_address(asset):
    p=urlsplit(asset)
    if p.scheme!='fabric':return None
    parts=p.path.strip('/').split('/')
    if not parts:return None
    return str(UUID(p.netloc)),str(UUID(parts[0]))

def category(kind):
    return 'CODE' if kind in ('Notebook','SparkJobDefinition','Dataflow','DataBuildToolJob') else 'PIPELINE' if kind in ('DataPipeline','CopyJob') else 'VALUE_OBJECT' if kind in ('Lakehouse','Warehouse','SemanticModel','SQLEndpoint') else 'OTHER'

class FabricLineageProposer:
    def __init__(self,request,meter,anchors):
        # One caller-declared root per unique workspace; never enumerate/follow up.
        if len({a['workspace'] for a in anchors})!=len(anchors):raise ValueError('At most one relation request per workspace')
        for a in anchors:
            if set(a)!={'workspace','item','type','name'}:raise ValueError('Declared graph root fields differ')
            UUID(a['workspace']);UUID(a['item'])
        self.request=request;self.meter=meter;self.anchors=anchors;self.responses=[]

    def layer_items(self,manifest):
        return {l['id']:a[1] if (a:=item_address(l['asset_id'])) else None for l in manifest['layers']}

    def declared_writers(self,manifest):
        items=set()
        for source in manifest['lineage'].get('code_sources',[]):
            items.update(source.get('item_ids',[]))
        for pipeline in manifest.get('pipelines',[]):
            for key in ('producer_asset_id','delivery_asset_id'):
                if a:=item_address(pipeline[key]):items.add(a[1])
        return items

    def propose(self,manifest):
        declared={item_address(l['asset_id']) for l in manifest['layers']}
        graph={'provenance':'PROPOSED_BY_PLATFORM','items':[],'edges':[],'workspaces':[]}
        for anchor in self.anchors:
            if (anchor['workspace'],anchor['item']) not in declared:raise ValueError('Relation root is outside the declared layers')
            endpoint=f"workspaces/{anchor['workspace']}/items/{anchor['item']}/relations/upstream?beta=true"
            response=self.meter(lambda:self.request('GET',endpoint))
            self.responses.append({'endpoint':endpoint,'response':response})
            if response['status']!=200:raise RuntimeError('Item relations HTTP '+str(response['status'])+': '+str(response['body']))
            body=response['body']
            if set(body)!={'items','relations','workspaces'}:raise ValueError('Item relations API shape differs; no follow-up')
            items=list(body['items']);spaces=list(body['workspaces'])
            # The documented example omits the requested root in items. It is
            # supplied solely from the caller declaration, not fabricated API evidence.
            if not any(i['id']==anchor['item'] for i in items):
                items.append({'id':anchor['item'],'type':anchor['type'],'displayName':anchor['name'],'workspaceId':anchor['workspace']})
            if not any(w['id']==anchor['workspace'] for w in spaces):
                spaces.append({'id':anchor['workspace'],'displayName':'Declared root workspace'})
            for i in items:
                graph['items'].append({'id':i['id'],'platform_type':i['type'],'category':category(i['type']),
                    'workspace':i['workspaceId'],'name':i['displayName']})
            for e in body['relations']:
                if e['relationType'] not in RELATIONS:raise ValueError('Unsupported platform relation kind: '+e['relationType'])
                graph['edges'].append({'source':e['itemId'],'target':e['dependentOnItemId'],
                    'kind':RELATIONS[e['relationType']],'columns':None})
            graph['workspaces'].extend({'id':w['id'],'name':w['displayName']} for w in spaces)
        # Merge repeated cross-workspace nodes only when every reported field agrees.
        for key,identity in [('items','id'),('workspaces','id'),('edges',None)]:
            unique={}
            for row in graph[key]:
                k=row[identity] if identity else str(sorted(row.items()))
                if k in unique and unique[k]!=row:raise ValueError('Conflicting platform graph identity')
                unique[k]=row
            graph[key]=list(unique.values())
        return validate(graph)

class UnityCatalogLineageStub:
    def __init__(self,manifest):
        from ..estate_manifest import validate as validate_manifest
        validate_manifest(manifest)
        if {a['implementation'] for a in manifest['adapters']}!={'databricks'}:
            raise ValueError('Unity Catalog stub requires a declared Databricks adapter')
    def propose(self,manifest):
        raise NotImplementedError('Unity Catalog lineage transport is not installed; no network request')
