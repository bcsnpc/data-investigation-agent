"""Explicit, pinned historical view; never repairs or relabels the current graph.

Only trusted assembly may install this view. Native resolution is reused verbatim;
no discovery, model proposal, label similarity or current-owner fallback occurs.
"""
import copy
from urllib.parse import unquote
from .. import estate_graph_contract as c


def validate_pin(pin, *, context, visual, measure_id):
    if not isinstance(pin, dict) or set(pin) != {'context_id','context_hash','as_of','visual','measure_id'}:
        raise ValueError('RETAINED_CONTINUATION_PIN_REQUIRED')
    if pin['context_id'] != context.get('version') or pin['context_hash'] != c.digest(context):
        raise ValueError('RETAINED_CONTINUATION_CONTEXT_DIFFERS')
    if c.timestamp(pin['as_of']) != c.timestamp(context.get('created')):
        raise ValueError('RETAINED_CONTINUATION_AS_OF_DIFFERS')
    if pin['visual'] != visual or pin['measure_id'] != measure_id:
        raise ValueError('RETAINED_CONTINUATION_TARGET_DIFFERS')
    approval=context.get('retained_metadata_approval')
    if not isinstance(approval,dict) or not approval.get('owner') or not approval.get('decision'):
        raise ValueError('RETAINED_CONTEXT_APPROVAL_REQUIRED')
    return copy.deepcopy(pin)


def _owner(asset_id, assets):
    current=asset_id; seen=set()
    while current in assets and current not in seen:
        seen.add(current); parent=assets[current].get('parent_id')
        if not parent or parent not in assets or assets[parent].get('kind')=='Workspace':return current
        current=parent
    raise ValueError('RETAINED_ASSET_OWNER_NOT_DECLARED')


def _resolved(process, measure_id, context):
    path=copy.deepcopy(process.resolve_path(measure_id)); layers=path.get('layers',[])
    if not 2<=len(layers)<=32 or layers[0].get('measure',{}).get('id')!=measure_id:
        raise ValueError('RETAINED_DECLARED_PATH_REQUIRED')
    if path.get('evidence',{}).get('metadata',{}).get('context_version')!=context['version']:
        raise ValueError('RETAINED_NATIVE_CONTEXT_DIFFERS')
    assets={a['id']:a for a in context['assets']}
    for layer in layers:
        if layer.get('id') not in assets or layer.get('measure',{}).get('id')!=measure_id:
            raise ValueError('RETAINED_LAYER_NOT_IN_CONTEXT')
    source=layers[1]
    if (source.get('binding',{}).get('status')!='RESOLVED' or
        source.get('binding',{}).get('provenance')!='DECLARED_BY_DEFINITION' or
        source.get('direct_source_proof',{}).get('provenance')!='DECLARED_BY_DEFINITION'):
        raise ValueError('RETAINED_DECLARED_SOURCE_REQUIRED')
    contracts={(x['upper_layer'],x['lower_layer']):x for x in path.get('quantity_contracts',[])}
    for upper,lower in zip(layers[1:],layers[2:]):
        if (upper['id'],lower['id']) not in contracts:raise ValueError('RETAINED_QUANTITY_CONTRACT_REQUIRED')
    return path,assets


def required_objects(process, *, context, estate, measure_id):
    """Offline authority preparation; caller must explicitly admit these exact IDs."""
    path,assets=_resolved(process,measure_id,context)
    return [c.identity(estate,_owner(a,assets),kind,['asset',a]) for kind,a in
            [('MEASURE',measure_id),*[( 'TABLE',v['id']) for v in path['layers']]]]


class RetainedApprovedContinuation:
    def __init__(self,current,process,*,context,pin,visual,measure_id):
        self.pin=validate_pin(pin,context=context,visual=visual,measure_id=measure_id)
        self.current=current; self.visual=visual; self.at=current.at
        self.path,self.assets=_resolved(process,measure_id,context)
        raw,_=current._read([visual]); original=raw[visual]
        visual_asset=original.get('properties',{}).get('asset_id')
        asset=self.assets.get(visual_asset)
        if not asset or asset.get('kind')!='ReportVisual':raise ValueError('RETAINED_VISUAL_NOT_IN_CONTEXT')
        measure=self.assets.get(measure_id)
        if not measure or measure.get('kind')!='Measure':raise ValueError('RETAINED_MEASURE_NOT_IN_CONTEXT')
        model=_owner(measure_id,self.assets); report=_owner(visual_asset,self.assets)
        if context.get('report_bindings',{}).get(report)!=model:raise ValueError('RETAINED_REPORT_MODEL_DIFFERS')
        # A native field reference is interpreted only inside the exactly bound model.
        table=self.assets.get(measure.get('parent_id'),{})
        references=[]
        def visit(value):
            if isinstance(value,dict):
                m=value.get('Measure')
                if isinstance(m,dict):references.append((m.get('Expression',{}).get('SourceRef',{}).get('Entity'),m.get('Property')))
                for child in value.values():visit(child)
            elif isinstance(value,list):
                for child in value:visit(child)
        visit(asset.get('metadata',{}))
        if set(references)!={(table.get('name'),measure.get('name'))}:
            raise ValueError('RETAINED_VISUAL_MEASURE_DIFFERS')
        self.basis={'kind':'RETAINED_APPROVED_CONTEXT',**self.pin,
                    'approval':copy.deepcopy(context['retained_metadata_approval']),'verified':False,
                    'limitation':'Not a current graph repair; retained definitions may differ from the served estate.'}
        current_path=current.path_to_source(visual)
        self.basis['current_graph_stops']=copy.deepcopy(current_path['stops'])
        self.basis['current_unavailable_owners']=copy.deepcopy(current_path.get('unavailable_owners',{}))
        self.warning_labels=[
            'Retained approved context: '+pin['context_id']+'; hash '+pin['context_hash']+'; as of '+pin['as_of']+'. Definitions were not recollected; this path is not current or value-verified.',
            'Current graph limitations: '+c.canonical({'stops':self.basis['current_graph_stops'],'unavailable_owners':self.basis['current_unavailable_owners']})]
        self.nodes=[]; self.edges=[]
        def proof(source,pointer):
            a=self.assets[source]
            return {'source':'STATIC_DEFINITION','source_id':source,'definition_hash':a['content_hash'],
                    'observed_at':pin['as_of'],'span':{'kind':'JSON_POINTER','path':pointer}}
        def node(kind,asset_id,id=None):
            a=self.assets[asset_id];owner=_owner(asset_id,self.assets)
            n=c.node(id or c.identity(current.estate,owner,kind,['asset',asset_id]),owner,kind,a.get('name') or asset_id,
                     proof(asset_id,''),properties={'asset_id':asset_id,'native_kind':a['kind'],
                         'context_basis':copy.deepcopy(self.basis)})
            n.update(valid_from=c.timestamp(pin['as_of']),valid_to=None);self.nodes.append(n);return n
        visual_node=node('VISUAL',visual_asset,visual); measure_node=node('MEASURE',measure_id)
        layer_nodes=[node('TABLE',x['id']) for x in self.path['layers']]
        contracts={(x['upper_layer'],x['lower_layer']):x for x in self.path.get('quantity_contracts',[])}
        def link(upper,lower,source,details):
            e=c.edge(c.identity(current.estate,upper['owner'],'COMPUTED_FROM',upper['id']+'->'+lower['id']),
                upper['owner'],'COMPUTED_FROM',upper['id'],lower['id'],proof(source,''),
                properties={'context_basis':copy.deepcopy(self.basis),'retained_declaration':copy.deepcopy(details)})
            e.update(valid_from=c.timestamp(pin['as_of']),valid_to=None);self.edges.append(e)
        link(visual_node,measure_node,visual_asset,{'exact_model_binding':model,'field_reference':references[0]})
        link(measure_node,layer_nodes[0],measure_id,{'expression':measure.get('metadata',{}).get('expression')})
        for index,(upper,lower) in enumerate(zip(layer_nodes,layer_nodes[1:])):
            if index==0:
                details=self.path['layers'][1]['direct_source_proof'];source=details['definition_asset_id']
                details={'direct_source_proof':details,'binding':self.path['layers'][1]['binding']}
            else:
                details=contracts[(upper['properties']['asset_id'],lower['properties']['asset_id'])];source=details['definition_asset_id']
            link(upper,lower,source,details)
        ids=[n['id'] for n in self.nodes]
        current.gateway.graph_objects(current.estate,ids,identity=current.identity)
        if not set(ids)<=current.allowed:raise PermissionError('RETAINED_CONTINUATION_OUTSIDE_ADMITTED_SLICE')
        self._by_id={n['id']:n for n in self.nodes}
        self.result={'estate':current.estate,'as_of':pin['as_of'],'nodes':self.nodes,'edges':self.edges,
            'stops':[{'node':layer_nodes[-1]['id'],'reason':str(self.path.get('stopped_by') or 'Retained declared path ends here.')}],
            'unavailable_owners':{},'truncated':False,'context_basis':self.basis}
        current._bounded(self.result)

    def path_to_source(self,visual):
        if visual!=self.visual:raise ValueError('RETAINED_CONTINUATION_TARGET_DIFFERS')
        return copy.deepcopy(self.result)

    def definition_of(self,node):
        if node not in self._by_id:return self.current.definition_of(node)
        value=self._by_id[node];asset=self.assets[value['properties']['asset_id']]
        return {'node':node,'provenance':value['provenance'],'definition':copy.deepcopy(asset.get('metadata')),
                'collection_unavailable':None,'valid_from':value['valid_from'],'valid_to':None,
                'context_basis':copy.deepcopy(self.basis)}

    def as_of(self,time):
        # A different historical view must never silently reuse this approval pin.
        return self.current.as_of(time)

    def __getattr__(self,name):return getattr(self.current,name)
