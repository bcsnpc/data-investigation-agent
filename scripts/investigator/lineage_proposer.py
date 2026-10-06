"""Approval-time platform proposals, never reader evidence or executable bindings."""
import copy
from typing import Protocol
from jsonschema import Draft202012Validator

KINDS=('READS_FROM','WRITES_TO','ORCHESTRATES','SHORTCUT','CONTAINS','ASSOCIATION','HIDDEN','COLUMN_LINEAGE')
CATEGORIES=('VALUE_OBJECT','CODE','PIPELINE','OTHER')
TEXT={'type':'string','minLength':1,'maxLength':500}

def obj(fields):
    return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}

COLUMN=obj({'source_column':TEXT,'target_column':TEXT})
EDGE=obj({'source':TEXT,'target':TEXT,'kind':{'enum':list(KINDS)},
          'columns':{'anyOf':[COLUMN,{'type':'null'}]}})
SCHEMA=obj({'provenance':{'const':'PROPOSED_BY_PLATFORM'},
    'items':{'type':'array','maxItems':2048,'items':obj({'id':TEXT,'platform_type':TEXT,
        'category':{'enum':list(CATEGORIES)},'workspace':TEXT,'name':TEXT})},
    'edges':{'type':'array','maxItems':8192,'items':EDGE},
    'workspaces':{'type':'array','maxItems':128,'items':obj({'id':TEXT,'name':TEXT})}})

class LineageProposer(Protocol):
    def propose(self,manifest:dict)->dict: ...
    def layer_items(self,manifest:dict)->dict: ...
    def declared_writers(self,manifest:dict)->set: ...

def validate(graph):
    Draft202012Validator(SCHEMA).validate(graph)
    items={i['id']:i for i in graph['items']};spaces={w['id'] for w in graph['workspaces']}
    if len(items)!=len(graph['items']) or len(spaces)!=len(graph['workspaces']):
        raise ValueError('Proposed graph repeats an identity')
    if any(i['workspace'] not in spaces for i in items.values()):
        raise ValueError('Proposed item has no proposed workspace')
    edges=set()
    for e in graph['edges']:
        if e['source'] not in items or e['target'] not in items:raise ValueError('Proposed edge has an unresolved endpoint')
        if (e['kind']=='COLUMN_LINEAGE')!=(e['columns'] is not None):raise ValueError('Column lineage shape differs from relation kind')
        identity=(e['source'],e['target'],e['kind'],str(e['columns']))
        if identity in edges:raise ValueError('Proposed graph repeats an edge')
        edges.add(identity)
    return copy.deepcopy(graph)

def findings(manifest,graph,layer_items,declared_writers=()):
    """The mapping is adapter-produced; native type/URI strings never branch here.

    These findings cannot change scope, approve code access or establish a binding.
    """
    graph=validate(graph);layers={l['id'] for l in manifest['layers']}
    if set(layer_items)!=layers:raise ValueError('Layer item mapping must cover the entire declared inventory')
    inventory={i['id']:i for i in graph['items']};declared={v for v in layer_items.values() if v}
    adjacency={i:set() for i in inventory}
    for e in graph['edges']:
        if e['kind'] in ('READS_FROM','SHORTCUT','ORCHESTRATES'):adjacency[e['source']].add(e['target'])
        elif e['kind']=='WRITES_TO':adjacency[e['target']].add(e['source'])
    def reaches(start,end):
        seen=set();todo=[start]
        while todo:
            n=todo.pop()
            if n==end and n!=start:return True
            if n in seen:continue
            seen.add(n)
            for child in adjacency.get(n,()):
                if child==end:return True
                todo.append(child)
        return False
    missing=[]
    for b in manifest['lineage']['bindings']:
        lower,upper=layer_items[b['from_layer']],layer_items[b['to_layer']]
        if lower is None or upper is None or not reaches(upper,lower):
            missing.append({'from_layer':b['from_layer'],'to_layer':b['to_layer'],
                'from_item':lower,'to_item':upper,'reason':'No proposed dependency path; absence is not proof of no lineage.'})
    writers=[];proposals=[];unmanifested=[]
    named={(layer_items[b['from_layer']],layer_items[b['to_layer']]) for b in manifest['lineage']['bindings']}
    # Native item declarations are decoded by the installed adapter, never here.
    code_items=set(declared_writers)
    for e in graph['edges']:
        if e['source'] in declared and e['target'] in declared and (e['target'],e['source']) not in named:
            unmanifested.append(copy.deepcopy(e))
        if e['kind'] in ('WRITES_TO','ORCHESTRATES') and e['target'] in declared:
            item=inventory[e['source']]
            if item['category'] in ('CODE','PIPELINE'):
                proposals.append({'item':item['id'],'workspace':item['workspace'],'target':e['target'],
                    'kind':e['kind'],'provenance':'PROPOSED_BY_PLATFORM','decision':'PENDING_APPROVER'})
                if item['id'] not in code_items:writers.append(copy.deepcopy(item))
    return {'provenance':'PROPOSED_BY_PLATFORM','nonblocking':True,'missing_declared_paths':missing,
            'unmanifested_edges':unmanifested,'code_source_proposals':proposals,'undeclared_writers':writers}

def at_approval(manifest,proposer,record):
    if not manifest.get('lineage_proposer',False):return None
    graph=validate(proposer.propose(manifest))
    result={'graph':graph,'findings':findings(manifest,graph,proposer.layer_items(manifest),proposer.declared_writers(manifest))}
    record(copy.deepcopy(result))
    return result
