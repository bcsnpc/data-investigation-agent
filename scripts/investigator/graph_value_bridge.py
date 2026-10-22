"""Narrow bridge from real scoped SUM reads to an existing declared graph edge.

It never infers a dependency from equal aggregates or invents a graph edge.
"""
import copy,hashlib,json
from decimal import Decimal,InvalidOperation
from . import estate_graph_contract as c
from .estate_graph_repository import GraphRepository,structural
from .graph_value_verification import ValueVerificationResolver,PIN_KEYS,scope_hash

VERSION='compiled-value-attachments-v1'
AGGREGATE_LIMIT='Scoped aggregate SUM agreement only; individual rows or column values were not compared.'


def graph_hash(graph):
    if graph.get('truncated'):raise ValueError('VALUE_GRAPH_TRUNCATED')
    result={}
    for kind in ('nodes','edges'):
        result[kind]=[]
        for item in sorted(graph[kind],key=lambda v:v['id']):
            row={k:copy.deepcopy(v)for k,v in item.items()if k not in ('valid_from','valid_to')}
            row['properties'].pop('definition_source_owner',None)
            c.record(row,edge=kind=='edges');result[kind].append(structural(row))
    return c.digest(result)


def capability(plan):
    kind=plan.get('program',{}).get('kind')
    return {'supported':kind=='SUM','scope':'SCOPED_AGGREGATE_SUM_ONLY',
        'reason':None if kind=='SUM'else 'SUMX_RELATED_GRAPH_ATTACHMENT_NOT_IMPLEMENTED'if kind=='SUMX_RELATED'else 'VALUE_PROGRAM_NOT_BOUND',
        'limitation':AGGREGATE_LIMIT}


def _typed(value):
    if value is None:return {'state':'BLANK','typed_value':None}
    if type(value)not in (int,float,str,Decimal):raise ValueError('VALUE_ORIGINAL_NUMERIC_REQUIRED')
    try:n=Decimal(str(value))
    except InvalidOperation:raise ValueError('VALUE_ORIGINAL_NUMERIC_REQUIRED')from None
    if not n.is_finite():raise ValueError('VALUE_ORIGINAL_FINITE_REQUIRED')
    return {'state':'VALUE','typed_value':{'type':'DECIMAL','value':format(n,'f')}}


def _original(observation,model):
    receipt=observation['receipt'];statement=observation['statement'];native=observation['layer']=='SEMANTIC'
    if receipt.get('status')!='SUCCEEDED' or 'value'not in receipt:raise ValueError('VALUE_ORIGINAL_SUCCESSFUL_READ_REQUIRED')
    request=receipt.get('request',{})
    if request.get('query')!=statement:raise ValueError('VALUE_ORIGINAL_REQUEST_DIFFERS')
    raw=receipt.get('provider_response')
    if native:
        if not isinstance(raw,str)or request.get('workspace')!=model['workspace']or request.get('native_model_id')!=model['native_id']:
            raise ValueError('VALUE_NATIVE_ORIGINAL_BINDING_DIFFERS')
        body=json.loads(raw,parse_float=Decimal);rows=body['results'][0]['tables'][0]['rows']
        if len(rows)!=1:raise ValueError('VALUE_NATIVE_SCALAR_REQUIRED')
        row=rows[0];keys=[k for k in ('quantity','[quantity]')if k in row]
        identities=[row[k]for k in ('surface_identity','[surface_identity]')if k in row]
        if len(keys)!=1 or len(identities)!=1 or receipt['attestation']['reported']!={'identity':identities[0]}:
            raise ValueError('VALUE_NATIVE_ORIGINAL_REPORT_DIFFERS')
        value=row[keys[0]]
    else:
        if not isinstance(raw,dict)or raw.get('read_only_verified')is not True or raw.get('surface_report_binding')!='VALUE_QUERY':
            raise ValueError('VALUE_LOWER_ORIGINAL_ATTESTATION_REQUIRED')
        rows=raw.get('rows')
        if not isinstance(rows,list)or len(rows)!=1 or 'quantity'not in rows[0]:raise ValueError('VALUE_LOWER_SCALAR_REQUIRED')
        if raw.get('surface_report')!=receipt['attestation']['reported']:raise ValueError('VALUE_LOWER_ORIGINAL_REPORT_DIFFERS')
        if int(rows[0].get('duplicate_lookup_keys',-1))!=0:raise ValueError('VALUE_ORIGINAL_LOOKUP_GUARD_FAILED')
        value=rows[0]['quantity']
    if _typed(value)!=_typed(receipt['value']):raise ValueError('VALUE_ORIGINAL_RESULT_DIFFERS')
    c.timestamp(receipt['observed_at'])
    return _typed(value)


def _column(graph,plan,layer):
    nodes=graph['nodes'];semantic=plan['program']['column']
    if layer=='SEMANTIC':
        matches=[n for n in nodes if n['kind']=='COLUMN'and n['properties'].get('asset_id')==semantic]
    else:
        lower=[p for p in plan['layers']if p.get('layer_id')==layer]
        if len(lower)!=1 or 'compilation_error'in lower[0]:raise ValueError('VALUE_LAYER_NOT_COMPILED')
        column=lower[0]['mapping']['columns'].get(semantic)
        if not column:raise ValueError('VALUE_QUANTITY_COLUMN_NOT_MAPPED')
        parents={n['id']for n in nodes if n['kind']=='TABLE'and n['properties'].get('asset_id')==column['object_id']}
        if len(parents)!=1:raise ValueError('VALUE_PHYSICAL_OBJECT_NOT_UNIQUE_IN_GRAPH')
        children={e['target']for e in graph['edges']if e['kind']=='CONTAINS'and e['source']in parents}
        matches=[n for n in nodes if n['id']in children and n['kind']=='COLUMN'and n['label']==column['column']]
    if len(matches)!=1 or matches[0]['confidence']=='UNKNOWN':raise ValueError('VALUE_QUANTITY_COLUMN_NOT_UNIQUE_IN_GRAPH')
    return matches[0]['id']


def build_bundle(*,model,plan,result,binding,graph):
    fields={'version','estate','graph_hash','model_hash','boundaries'}
    if not isinstance(binding,dict)or set(binding)!=fields or binding['version']!=VERSION:raise ValueError('VALUE_GRAPH_BINDING_REQUIRED')
    if not capability(plan)['supported']:raise ValueError(capability(plan)['reason'])
    from cloud_value_execution import _compile
    recompiled=_compile(model,[p['mapping']for p in plan['layers']],{'measure_id':plan['measure_id'],'target_id':plan['visual_address']['target_id'],'tolerance':plan['tolerance']})
    if c.digest(recompiled)!=c.digest(plan):raise ValueError('VALUE_RECOMPILED_PLAN_DIFFERS')
    if graph_hash(graph)!=binding['graph_hash']or c.digest(model)!=binding['model_hash']:raise ValueError('VALUE_CURRENT_GRAPH_OR_MODEL_PIN_DIFFERS')
    if result.get('status')!='VALUES_AGREE_UNDER_MAPPING':raise ValueError('VALUE_OBSERVATION_NOT_SUCCESSFUL')
    boundaries=binding['boundaries']
    if not isinstance(boundaries,list)or not 1<=len(boundaries)<=20 or len({b.get('edge_id')for b in boundaries})!=len(boundaries):raise ValueError('VALUE_GRAPH_BOUNDARY_BOUND')
    order=['SEMANTIC']+[p['layer_id']for p in plan['layers']]
    if len(set(order))!=len(order):raise ValueError('VALUE_LAYER_IDENTITIES_NOT_UNIQUE')
    observations=result['reads'];by_layer={v['layer']:v for v in observations}
    if len(by_layer)!=len(observations)or set(by_layer)!=set(order):raise ValueError('VALUE_ORIGINAL_LAYER_COVERAGE')
    edges={e['id']:e for e in graph['edges']};nodes={n['id']:n for n in graph['nodes']}
    bundle={'version':VERSION,'estate':binding['estate'],'checks':{},'mappings':{},'reads':{},'originals':copy.deepcopy(observations)}
    for spec in boundaries:
        if set(spec)!={'edge_id','source_layer','target_layer'}:raise ValueError('VALUE_GRAPH_BOUNDARY_SHAPE')
        upper,lower=spec['source_layer'],spec['target_layer']
        if upper not in order or order.index(upper)+1>=len(order)or order[order.index(upper)+1]!=lower:raise ValueError('VALUE_GRAPH_LAYERS_NOT_ADJACENT')
        edge=edges.get(spec['edge_id'])
        if not edge or edge['kind']not in ('COMPUTED_FROM','DERIVED_IN_STEP','COPIED_TO')or edge['confidence']=='UNKNOWN':raise ValueError('VALUE_EXISTING_GRAPH_EDGE_REQUIRED')
        if edge['properties'].get('execution_established')is False:raise ValueError('VALUE_GRAPH_EXECUTION_NOT_ESTABLISHED')
        if edge['source']!=_column(graph,plan,upper)or edge['target']!=_column(graph,plan,lower):raise ValueError('VALUE_GRAPH_EDGE_QUANTITY_ENDPOINTS_DIFFER')
        if any(nodes[i]['owner']in graph.get('unavailable_owners',{})for i in (edge['source'],edge['target'])):raise ValueError('VALUE_GRAPH_OWNER_UNAVAILABLE')
        common={k:copy.deepcopy(plan[k])for k in ('visual_address','visual_cell','inventory','active_restrictions','report_binding','report_catalog','tolerance')}
        lower_plans={v['layer_id']:v for v in plan['layers']}
        coordinates=lambda side:{'model_id':model['native_id'],'workspace':model['workspace']}if side=='SEMANTIC'else lower_plans[side]['endpoint']
        translation={'quantity_grain':'SCOPED_AGGREGATE_SUM_ONLY','program':copy.deepcopy(plan['program']),
            'model_hash':c.digest(model),'source_layer':upper,'target_layer':lower,
            'layer_mappings':{side:copy.deepcopy(lower_plans[side]['mapping'])for side in (upper,lower)if side!='SEMANTIC'},
            'original_receipt_hashes':{side:c.digest(by_layer[side]['receipt'])for side in (upper,lower)},
            'restriction_mappings':[{'restriction_hash':c.digest(r),'source':{'layer':upper,'applied_restriction':copy.deepcopy(r)},
                'target':{'layer':lower,'applied_restriction':copy.deepcopy(r)},'definition_hash':edge['provenance']['definition_hash']}
                for r in plan['active_restrictions']+plan['visual_cell']['key_restrictions']]}
        mid=c.digest({'edge':edge['id'],'translation':translation,'scope':plan['scope_hash']})
        mapping={'version':'graph-value-mapping-v1','id':mid,'producer':'LINEAGE_VALUE_COMPILER','estate':binding['estate'],
            'edge_id':edge['id'],'source':edge['source'],'target':edge['target'],'definition_hash':edge['provenance']['definition_hash'],
            'graph_hash':binding['graph_hash'],'scope_hash':plan['scope_hash'],'mapping':translation,'mapping_hash':c.digest(translation),
            **common,'endpoint_hashes':{'source':c.digest(coordinates(upper)),'target':c.digest(coordinates(lower))},
            'source_statement_hash':hashlib.sha256(by_layer[upper]['statement'].encode()).hexdigest(),
            'target_statement_hash':hashlib.sha256(by_layer[lower]['statement'].encode()).hexdigest()}
        if mapping['scope_hash']!=scope_hash(mapping):raise ValueError('VALUE_COMPILED_SCOPE_HASH_DIFFERS')
        ids={}
        for side,layer in (('source',upper),('target',lower)):
            observed=by_layer[layer];value=_original(observed,model)
            expected=plan['native_statement']if layer=='SEMANTIC'else lower_plans[layer]['statement']
            if observed['statement']!=expected:raise ValueError('VALUE_ACTUAL_COMPILED_STATEMENT_DIFFERS')
            identity=c.digest([mid,side,observed]);ids[side]=identity
            bundle['reads'][identity]={'id':identity,'producer':'QUERY_READ','status':'SUCCEEDED','estate':binding['estate'],
                'object_id':edge[side],**{k:mapping[k]for k in ('scope_hash','definition_hash','mapping_hash')},
                'endpoint_hash':mapping['endpoint_hashes'][side],'statement_hash':mapping[side+'_statement_hash'],
                'statement':expected,'value':value,'attestation':copy.deepcopy(observed['receipt']['attestation']),
                'snapshot':copy.deepcopy(observed['receipt'].get('snapshot')),'observed_at':observed['receipt']['observed_at']}
        check_id=c.digest([mid,ids]);bundle['mappings'][mid]=mapping
        bundle['checks'][check_id]={'version':'graph-value-check-v1','id':check_id,'producer':'LINEAGE_VALUE_CHECK',
            **{k:mapping[k]for k in ('estate','edge_id','source','target','scope_hash','definition_hash','graph_hash')},'mapping_id':mid,
            'source_read':ids['source'],'target_read':ids['target'],'explanation_read':None,
            'observed_at':max(bundle['reads'][i]['observed_at']for i in ids.values())}
    bundle['seal']=c.digest(bundle)
    return bundle


class CompiledValueResolver(ValueVerificationResolver):
    def __call__(self,evidence_id):
        proof=super().__call__(evidence_id);proof['qualification']+=' '+AGGREGATE_LIMIT
        return proof


def _current(state,db,repository,environment,model,binding):
    graph={kind:list(repository._current(db,binding['estate'],kind).values())for kind in ('nodes','edges')}
    graph['unavailable_owners']={}
    owners={n['owner']for n in graph['nodes']}
    if len(owners)>1000:raise ValueError('VALUE_GRAPH_OWNER_BOUND')
    from .shared_state import encoded
    for owner in owners:
        try:events=state._get(db,'graph_owner_collection',encoded([binding['estate'],owner]))['body']['events']
        except KeyError:continue
        if events and events[-1]['status']in ('REFRESHING','UNAVAILABLE'):graph['unavailable_owners'][owner]=events[-1]
    current=copy.deepcopy(state._get(db,'catalog_model',encoded([environment,model['id']]))['body'])
    context=state._get(db,'catalog_context',encoded([environment,model['id'],current['context_id']]))['body']
    if c.digest(context['body'])!=context['hash']:raise ValueError('VALUE_CURRENT_MODEL_CONTEXT_HASH_DIFFERS')
    current['context']=context['body']
    if c.digest(current)!=binding['model_hash']or current.get('enabled')is not True:raise ValueError('VALUE_CURRENT_PUBLISHED_MODEL_DIFFERS')
    if graph_hash(graph)!=binding['graph_hash']:raise ValueError('VALUE_CURRENT_GRAPH_CHANGED')
    return graph


def attach(*,state,environment,model,plan,result,binding,retain,observed_at):
    repository=GraphRepository(state)
    with state.transaction()as db:
        graph=_current(state,db,repository,environment,model,binding)
        bundle=build_bundle(model=model,plan=plan,result=result,binding=binding,graph=graph)
        resolver=CompiledValueResolver(lambda i:copy.deepcopy(bundle['checks'][i]),lambda i:copy.deepcopy(bundle['mappings'][i]),
            lambda i:copy.deepcopy(bundle['reads'][i]),current_pins=lambda m:{k:copy.deepcopy(m[k])for k in PIN_KEYS})
        proofs=[resolver(i)for i in bundle['checks']]
    # Publication must complete before a confidence row can point to the proof.
    # No writer transaction or lease spans the Blob request.
    retain('mapped-value-proof-bundle',bundle)
    with state.transaction()as db:
        _current(state,db,repository,environment,model,binding)
        repository.value_verification_resolver=resolver
        changed=repository.value_verify_edges(binding['estate'],list(bundle['checks']),observed_at=observed_at,_db=db)
    return {'status':'VALUE_VERIFIED','confidence_awarded':True,'edge_ids':[p['edge_ids'][0]for p in proofs],
        'bundle_sha256':c.digest(bundle),'publication':changed,'proofs':proofs,'complete_path_claimed':False,
        'qualification':AGGREGATE_LIMIT,'limit':'Only selected existing edge aggregates were checked; no complete application path is implied.'}
