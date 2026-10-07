"""Closed estate installation contract; adapter options remain adapter-owned."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from .layer_roles import ROLES
from .process_debugging import REQUIRED_CAPABILITIES, OPTIONAL_CAPABILITIES
from .workspace import DYNAMIC_READ_BOUNDS, DYNAMIC_INPUT_BOUNDS
from .estate_limits import STATEMENT_BOUND
from .code_sources import CODE_SOURCE_SCHEMA, validate_sources as validate_code_inventory
from .binding_sample import SAMPLE_SCHEMA
from .string_semantics import SCHEMA as STRING_SEMANTICS


def obj(properties, optional=()):
    return {'type':'object','additionalProperties':False,'properties':properties,
            'required':[k for k in properties if k not in optional]}


STRING={'type':'string','minLength':1,'maxLength':500}
BOOL={'type':'boolean'}
def enum(values):return {'type':'string','enum':list(values)}
def array(items):return {'type':'array','items':items,'maxItems':512}
def integer(low,high):return {'type':'integer','minimum':low,'maximum':high}
REFERENCE=obj({'adapter':STRING,'address':STRING,'reader':STRING})
SCOPE=obj({'resource':STRING,'rights':array(enum(('READ','BUILD','CATALOG','QUERY')))})
RESOURCE=obj({'id':STRING,'asset_id':STRING,'reach':REFERENCE})
NORMALIZATION={'oneOf':[
    obj({'status':{'const':'UNDECLARED'},'reason':STRING}),
    obj({'status':{'const':'DECLARED'},'collation':STRING,'trim':BOOL,
         'case_fold':BOOL,'evidence':STRING})]}
RETENTION_PERIOD={'oneOf':[{'const':'indefinite'},integer(1,36500)]}
RETENTION=obj({'tape_days':RETENTION_PERIOD,'ledger_days':RETENTION_PERIOD})
RECORDING={'oneOf':[
    obj({'tape_class':{'const':'EXACT'}}),
    obj({'tape_class':{'const':'PRIVACY_PROJECTED'},
         'version':{'const':'estate-privacy-projection-v1'},'estate_id':STRING,
         'key_reference':STRING,'columns':array(STRING)})]}
PROVIDER_REGION={'oneOf':[
    obj({'status':{'const':'DECLARED'},'name':STRING,'evidence':STRING}),
    obj({'status':{'const':'UNDECLARED'},'reason':STRING})]}
SCHEMA=obj({
    'version':{'const':'estate-manifest-v1'},'environment':STRING,
    'lineage_proposer':BOOL,'assistant_proposer':BOOL,
    'storage':obj({'catalog':STRING,'inventory':STRING}),
    'retention':RETENTION,
    'recording':RECORDING,
    'adapters':array(obj({'id':STRING,'implementation':STRING,
        'options':{'type':'object'}})),
    'layers':array(obj({'id':STRING,'asset_id':STRING,'role':enum(ROLES),
        'business_name':{'type':'string','minLength':1,'maxLength':80},
        'reachable':BOOL,'reach':REFERENCE,'serverless':BOOL,
        'worker_timeout_seconds':integer(30,600),'comparison_normalization':NORMALIZATION,
        'string_semantics':STRING_SEMANTICS},
        optional=('serverless','worker_timeout_seconds','comparison_normalization','string_semantics'))),
    'resources':array(RESOURCE),
    'identities':array(obj({'id':STRING,'principal':STRING,'credential_reference':STRING,
        'scopes':array(SCOPE)})),
    'system_of_record':{'anyOf':[STRING,{'type':'null'}]},
    'pipelines':array(obj({'id':STRING,'from_layer':STRING,'to_layer':STRING,
        'producer_asset_id':STRING,'delivery_asset_id':STRING,
        'audit':{'oneOf':[obj({'status':{'const':'PRESENT'},'resource':STRING}),
            obj({'status':{'const':'UNAVAILABLE'},'reason':STRING})]},
        'history_resource':{'anyOf':[STRING,{'type':'null'}]}})),
    'lineage':obj({'bindings':array(obj({'from_layer':STRING,'to_layer':STRING,
        'provenance':enum(('DECLARED_BY_DEFINITION','DECLARED_BY_CONFIGURATION'))})),
        'inference':obj({'enabled':BOOL,'code_resources':array(STRING)}),
        'code_sources':array(CODE_SOURCE_SCHEMA),
        'code_locations':array(obj({'from_layer':STRING,'to_layer':STRING,
            'may_infer_from_code':BOOL,'locations':array(obj({'source':STRING,'path':STRING}))})),
        'verification_sample':SAMPLE_SCHEMA,
        'source_delivery':{'anyOf':[obj({k:STRING for k in
            ('source_asset_id','key_column_id','version_column_id','modified_column_id','time_semantics')}),{'type':'null'}]}}, optional=('code_sources','code_locations','verification_sample')),
    'capability_ceiling':array(enum(sorted(REQUIRED_CAPABILITIES|OPTIONAL_CAPABILITIES))),
    'model':obj({'provider':STRING,'deployment':STRING,'endpoint':STRING,
        'region':PROVIDER_REGION,
        'generation_options':obj({'reasoning_effort':enum(('none','low','medium','high')),
            'max_output_tokens':integer(500,16000),'timeout_seconds':integer(10,120),
            'max_payload_characters':integer(8000,128000)}),
        # Provider-owned closed validation belongs to its installed registry,
        # not to the platform-neutral installation contract.
        'credential':{'type':'object'},
        'max_planner_recoveries':integer(0,1)}, optional=('region',)),
    'budgets':obj({'diagnostic_reads_per_run':integer(*DYNAMIC_READ_BOUNDS),
        'binding_verification':obj({'probes_per_binding':{'const':2},'metadata_probes':integer(0,32),
                                   'session_cap':integer(1,2048)}),
        'input_characters_per_run':integer(*DYNAMIC_INPUT_BOUNDS),
        'max_boundaries':integer(0,32),'rolling_window_seconds':{'const':86400},
        'rolling_physical_requests':integer(1,10000000),
        'planner_daily':obj({'calls':integer(1,10000000),'input_characters':integer(1,10000000),
            'output_tokens':integer(1,10000000),'max_inflight':integer(1,4),'no_progress_limit':integer(1,4)}),
        'round':obj({'id':STRING,'starts_at_epoch':{'type':'number','minimum':0},
            'physical_requests':integer(1,10000000),'restoration_reserved':integer(0,10000000)})}, optional=('binding_verification',)),
    'accepted_limits':array(obj({'code':STRING,'resource':STRING,
        'statement':{'type':'string','minLength':1,'maxLength':STATEMENT_BOUND}})),
    # Evaluator-only declarations; not projected into tools or prompts.
    'fixture_states':array(obj({'id':STRING,'description':STRING,
        'arithmetic':{'type':'string','minLength':1,'maxLength':2000},
        'evidence':array(STRING)}))}, optional=('fixture_states','lineage_proposer','assistant_proposer','retention','recording'))


def validate(value):
    errors=sorted(Draft202012Validator(SCHEMA).iter_errors(value),key=lambda e:str(list(e.path)))
    if errors:
        e=errors[0];raise ValueError('manifest.'+'.'.join(map(str,e.path))+': '+e.message)
    from .generation_policy import validate as generation
    generation(value['model']['generation_options'])
    from .privacy_projection import declaration as recording_declaration
    recording_declaration(value.get('recording',{'tape_class':'EXACT'}))
    def indexed(name):
        result={}
        for i,row in enumerate(value[name]):
            if row['id'] in result:raise ValueError(f'manifest.{name}.{i}.id: duplicate')
            result[row['id']]=row
        return result
    layers=indexed('layers');resources=indexed('resources');adapters=indexed('adapters');identities=indexed('identities')
    from .string_semantics import validate as validate_string_semantics
    for layer in layers.values():
        if 'string_semantics' in layer:validate_string_semantics(layer['string_semantics'])
    indexed('pipelines')
    if 'fixture_states' in value:indexed('fixture_states')
    from .layer_roles import declarations as roles
    roles([{k:l[k] for k in ('asset_id','role','business_name')} for l in value['layers']])
    if value['lineage']['source_delivery'] is not None:
        from .source_delivery import declaration
        declaration(value['lineage']['source_delivery'])
        if value['lineage']['source_delivery']['source_asset_id'] not in {l['asset_id'] for l in value['layers']}:
            raise ValueError('manifest.lineage.source_delivery.source_asset_id: undeclared layer')
    if not layers:raise ValueError('manifest.layers: at least one declared layer required')
    if set(layers)&set(resources):raise ValueError('manifest.resources.id: collides with a layer')
    code_sources={s['id']:s for s in value['lineage'].get('code_sources',[])}
    if set(code_sources)&(set(layers)|set(resources)):raise ValueError('manifest.lineage.code_sources.id: resource collision')
    all_resources={**layers,**resources,**code_sources}
    def ref(key,pool,path):
        if key not in pool:raise ValueError('manifest.'+path+': unknown reference '+key)
    if value['system_of_record'] is not None:ref(value['system_of_record'],layers,'system_of_record')
    for name,rows in (('layers',layers),('resources',resources)):
        for key,row in rows.items():
            reach=row['reach'];ref(reach['adapter'],adapters,f'{name}.{key}.reach.adapter')
            ref(reach['reader'],identities,f'{name}.{key}.reach.reader')
            scopes=[s for s in identities[reach['reader']]['scopes'] if s['resource']==key]
            if len(scopes)!=1 or 'READ' not in scopes[0]['rights']:
                raise ValueError(f'manifest.{name}.{key}.reach.reader: no declared READ scope')
    for key,identity in identities.items():
        seen=set()
        for scope in identity['scopes']:
            ref(scope['resource'],all_resources,f'identities.{key}.scopes.resource')
            if scope['resource'] in seen or len(scope['rights'])!=len(set(scope['rights'])):
                raise ValueError(f'manifest.identities.{key}.scopes: duplicate')
            seen.add(scope['resource'])
    for i,pipeline in enumerate(value['pipelines']):
        for side in ('from_layer','to_layer'):ref(pipeline[side],layers,f'pipelines.{i}.{side}')
        if pipeline['audit']['status']=='PRESENT':ref(pipeline['audit']['resource'],resources,f'pipelines.{i}.audit.resource')
        if pipeline['history_resource'] is not None:ref(pipeline['history_resource'],resources,f'pipelines.{i}.history_resource')
    for i,binding in enumerate(value['lineage']['bindings']):
        for side in ('from_layer','to_layer'):ref(binding[side],layers,f'lineage.bindings.{i}.{side}')
    inference=value['lineage']['inference']
    if inference['enabled'] and not inference['code_resources'] and not any(x['may_infer_from_code'] and x['locations'] for x in value['lineage'].get('code_locations',[])):
        raise ValueError('manifest.lineage.inference.code_resources: enabled without source')
    for key in inference['code_resources']:ref(key,resources,'lineage.inference.code_resources')
    for i,limit in enumerate(value['accepted_limits']):ref(limit['resource'],all_resources,f'accepted_limits.{i}.resource')
    validate_code_inventory(value)
    from .business_vocabulary import validate_identifier_form
    for i,limit in enumerate(value['accepted_limits']):
        from .estate_limits import render
        try:render(limit['statement'])
        except ValueError as exc:raise ValueError(f'manifest.accepted_limits.{i}.statement: '+str(exc)) from exc
        try:validate_identifier_form(limit['statement'])
        except ValueError as exc:raise ValueError(f'manifest.accepted_limits.{i}.statement: '+str(exc)) from exc
    ceiling=value['capability_ceiling']
    if ceiling!=sorted(set(ceiling)):raise ValueError('manifest.capability_ceiling: sorted unique list required')
    if not REQUIRED_CAPABILITIES<=set(ceiling):raise ValueError('manifest.capability_ceiling: missing required operations')
    if value['budgets']['round']['restoration_reserved']>value['budgets']['round']['physical_requests']:
        raise ValueError('manifest.budgets.round.restoration_reserved: exceeds pot')
    from .adapters.estate_installation import validate_registered_options
    validate_registered_options(value)
    return copy.deepcopy(value)


def load(path):
    # The only configuration read. Credential references name secrets, not
    # other configuration files; no environment/default file participates.
    return validate(json.loads(Path(path).read_text(encoding='utf-8-sig')))


def policy(manifest):
    b=manifest['budgets'];p=b['planner_daily']
    return {'environment':manifest['environment'],'daily_limits':{
        'cloud_calls':b['rolling_physical_requests'],'planner_calls':p['calls'],
        'input_characters':p['input_characters'],'output_tokens':p['output_tokens']},
        'max_inflight_planners':p['max_inflight'],'no_progress_limit':p['no_progress_limit']}
