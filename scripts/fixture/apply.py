"""Create the Fabric fixture from retained templates in an approved workspace.

Workspace/SQL identity provisioning remains an explicit owner prerequisite.
The prepared application table must contain the committed fixture literals;
this executor never grants application or workspace permissions implicitly.
All subsequent Fabric mutations use a durable create-only journal.
"""
import ast
import base64
import copy
import json
import re
from pathlib import Path
from uuid import UUID, uuid5, NAMESPACE_URL
from datetime import datetime, timezone
from .definitions import bind, definition, model_slots
from .seed import notebook_template
from investigator.onboarding import digest


def inputs(value):
    expected={'workspace_id','workspace_name','capacity_id','prefix','source_table',
              'source_object_id','source_connection','invoke_connection','approval_reference'}
    if set(value)!=expected:raise ValueError('Fixture apply inputs differ from the declared contract')
    for key in ('workspace_id','capacity_id','source_connection','invoke_connection'):
        UUID(value[key])
    for key in ('prefix','source_table'):
        if not isinstance(value[key],str) or not re.fullmatch('[A-Za-z][A-Za-z0-9_]{0,99}',value[key]):
            raise ValueError('Invalid create-only fixture name: '+key)
    if type(value['source_object_id']) is not int or value['source_object_id']<=0:
        raise ValueError('Prepared application object ID required')
    for key in ('workspace_name','approval_reference'):
        if not isinstance(value[key],str) or not value[key].strip():raise ValueError(key+' required')
    return copy.deepcopy(value)


def inline(path,document):
    return {'parts':[{'path':path,'payloadType':'InlineBase64',
                     'payload':base64.b64encode(json.dumps(document).encode()).decode()}]}


class Executor:
    def __init__(self,control,parameters,templates,*,sleep):
        self.control=control;self.p=inputs(parameters);self.templates=templates
        self.sleep=sleep;self.items={};self.metadata={};self.jobs={};self.source=None
        if control.workspace!=self.p['workspace_id']:raise ValueError('Approved workspace differs')

    def logical(self,key):
        return str(uuid5(NAMESPACE_URL,self.control.workspace+'/'+self.p['prefix']+'/'+key))

    def save(self):
        self.control.record.update(items=self.items,metadata=self.metadata,jobs=self.jobs)
        self.control.save()

    def create(self,key,collection,body):
        item=self.control.create(self.p['prefix']+'-'+key,collection,body)
        self.items[key]=item;self.save();return item

    def get(self,collection,key):
        return self.control.resolve(self.control.call('workspaces/'+self.control.workspace+'/'+collection+'/'+self.items[key]['id']))

    def run(self,key,collection,job_type):
        ctl=self.control
        endpoint='workspaces/'+ctl.workspace+'/'+collection+'/'+self.items[key]['id']
        if job_type=='RunNotebook':
            endpoint+='/jobs/execute/instances?beta=false'
            body={'executionData':{'compute':'Spark','computeConfiguration':{'defaultLakehouse':{
                'referenceType':'ById','itemId':self.items['bronze']['id'],'workspaceId':ctl.workspace}}}}
        else:endpoint+='/jobs/instances?jobType='+job_type;body={}
        response=ctl.call(endpoint,'POST',body,key=self.p['prefix']+'-'+key+'-run-once')
        location={k.lower():v for k,v in response.get('headers',{}).items()}.get('location','')
        prefix='https://api.fabric.microsoft.com/v1/workspaces/'+ctl.workspace+'/'
        if not location.startswith(prefix):raise ValueError('Job escaped the approved workspace')
        endpoint=location.split('/v1/',1)[1]
        for attempt in range(12):
            job=ctl.call(endpoint)['text'];self.jobs[key]=job;self.save()
            if job.get('status')=='Completed':return job
            if job.get('status') in ('Failed','Cancelled'):
                raise RuntimeError('Fixture job failed: '+json.dumps(job))
            if attempt<11:self.sleep(30)
        raise TimeoutError('Fixture job pending; inspect the retained instance, never issue a replacement run')

    def served(self,key,collection):
        return self.control.resolve(self.control.call('workspaces/'+self.control.workspace+'/'+collection+'/'+
            self.items[key]['id']+'/getDefinition','POST',{}))

    def provision(self):
        ctl=self.control;p=self.p
        workspace=ctl.call('workspaces/'+ctl.workspace)['text']
        if workspace.get('displayName')!=p['workspace_name'] or workspace.get('capacityId')!=p['capacity_id']:
            raise ValueError('Workspace name/capacity differs from owner approval')
        listing=ctl.call('workspaces/'+ctl.workspace+'/items')['text']
        if listing.get('continuationToken') or listing.get('continuationUri'):
            raise ValueError('Incomplete item listing cannot establish a new target')
        # A fresh executor never adopts existing objects by name. Completed
        # control receipts can be inspected explicitly, not silently overwritten.
        if listing.get('value'):raise ValueError('Fixture apply requires an empty approved workspace')
        for key in ('bronze','silver','gold','landing'):
            body={'displayName':p['prefix']+'_'+key,'description':'Create-only isolated synthetic fixture.'}
            if key=='landing':body['creationPayload']={'enableSchemas':True}
            self.create(key,'lakehouses',body)
        self.create('audit','warehouses',{'displayName':p['prefix']+'_ops_audit'})
        source=notebook_template(ctl.workspace,{k:self.items[k]['id'] for k in ('bronze','silver','gold')})['source']
        notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernel_info':{'name':'synapse_pyspark'}},
                  'cells':[{'cell_type':'code','execution_count':None,'outputs':[],
                            'metadata':{'language':'python','language_group':'synapse_pyspark'},
                            'source':source.splitlines(keepends=True)}]}
        self.create('notebook','notebooks',{'displayName':p['prefix']+'_seed_and_transform',
                    'definition':{**inline('notebook-content.ipynb',notebook),'format':'ipynb'}})
        retained=self.served('notebook','notebooks')
        parts=retained['definition']['parts']
        code=next((base64.b64decode(x['payload']).decode() for x in parts if x['path']=='notebook-content.py'),None)
        if code is None:
            raw=json.loads(base64.b64decode(next(x['payload'] for x in parts if x['path']=='notebook-content.ipynb')))
            code='\n'.join(''.join(x['source']) for x in raw['cells'] if x['cell_type']=='code')
        if ast.dump(ast.parse(code))!=ast.dump(ast.parse(source)):
            raise ValueError('Served notebook lost or changed committed statements; refuse execution')
        self.source=code
        self.run('notebook','notebooks','RunNotebook')
        for key in ('gold','landing'):
            self.metadata[key]=self.get('lakehouses',key)
            model_slots(self.metadata[key],self.logical(key),'ITEM_2' if key=='gold' else 'ITEM_3')
        self.metadata['audit']=ctl.call('workspaces/'+ctl.workspace+'/warehouses/'+self.items['audit']['id']+'/connectionString')['text']
        audit_server=self.metadata['audit']['connectionString']
        slots={'ITEM_5':p['source_connection'],'ITEM_6':ctl.workspace,'ITEM_7':self.items['landing']['id'],
               'ITEM_8':self.logical('copy-activity'),'ITEM_10':p['invoke_connection'],
               'ITEM_11':self.items['audit']['id'],'WAREHOUSE_ENDPOINT':audit_server,
               'WAREHOUSE_LINK_NAME':self.items['audit']['id'].replace('-','_')}
        substitutions={'stock_movements_round_two_20261003':p['source_table'],
                       'round_three_ops_audit_20261004':p['prefix']+'_ops_audit'}
        copy_doc=bind(self.templates['copy-job']['definition']['definition'],slots,substitutions)
        self.create('copy','copyJobs',{'displayName':p['prefix']+'_application_copy',
                    'definition':inline('copyjob-content.json',copy_doc)})
        slots['ITEM_9']=self.items['copy']['id']
        pipeline=bind(self.templates['audit-pipeline']['definition']['definition'],slots,substitutions)
        ddl=copy.deepcopy(pipeline);script=ddl['properties']['activities'][1]
        script['name']='CreateAuditTable';script['dependsOn']=[]
        script['typeProperties']['scripts']=[{'type':'Query','parameters':[],
            'text':Path(__file__).with_name('templates').joinpath('audit-table.sql').read_text()}]
        ddl['properties']['activities']=[script]
        self.create('audit-ddl','dataPipelines',{'displayName':p['prefix']+'_create_audit_once',
                    'definition':inline('pipeline-content.json',ddl)})
        self.run('audit-ddl','dataPipelines','Pipeline')
        self.create('pipeline','dataPipelines',{'displayName':p['prefix']+'_application_load',
                    'definition':inline('pipeline-content.json',pipeline)})
        self.run('pipeline','dataPipelines','Pipeline')
        for key,surface,slot in (('original-model','gold','ITEM_2'),('application-model','landing','ITEM_3')):
            slots_for_model=model_slots(self.metadata[surface],self.logical(key),slot)
            self.create(key,'semanticModels',{'displayName':p['prefix']+' '+key,
                'definition':definition(self.templates[key]['definition'],slots_for_model,substitutions)})
        for key in ('predicate-report','inventory-report','warehouse-report'):
            report=self.templates[key]['definition']
            report_slots={'ITEM_1':self.logical(key),'REPORT_LOGICAL_ID':self.logical(key),
                          'ITEM_4':self.items['original-model']['id'],
                          'WORKSPACE_NAME':p['workspace_name'],'MODEL_NAME':p['prefix']+' original-model'}
            self.create(key,'reports',{'displayName':report.get('displayName',p['prefix']+' predicates'),
                        'definition':definition(report,report_slots)})
        return {'items':copy.deepcopy(self.items),'jobs':copy.deepcopy(self.jobs),
                'metadata':copy.deepcopy(self.metadata),
                'status':'PROVISIONED_REQUIRES_EXPLICIT_READER_MODEL_GRANTS_AND_INSTALLATION_APPROVAL',
                'remaining':['Read + Build on the two returned models, with before/after listings',
                             'reader audit row versus own copy activity output',
                             'fresh manifest, semantics observations, lineage verification and discovery approval'],
                'approval_reference':p['approval_reference']}

    def grant_models(self,principal):
        """Only the two returned models, under the caller's explicit approval."""
        receipts=[]
        for key in ('original-model','application-model'):
            endpoint='groups/'+self.control.workspace+'/datasets/'+self.items[key]['id']+'/users'
            before=self.control.call(endpoint,audience='powerbi')['text']
            request={'identifier':principal,'datasetUserAccessRight':'ReadExplore','principalType':'User'}
            self.control.call(endpoint,'POST',request,audience='powerbi',key=self.p['prefix']+'-'+key+'-reader')
            after=self.control.call(endpoint,audience='powerbi')['text']
            matches=[x for x in after.get('value',[]) if x.get('identifier',x.get('emailAddress','')).lower()==principal.lower()]
            if len(matches)!=1 or matches[0].get('datasetUserAccessRight')!='ReadExplore':
                raise ValueError('Model-specific Read + Build not established by after listing')
            receipts.append({'item':self.items[key]['id'],'human_decision':self.p['approval_reference'],
                             'before':before,'request':request,'after':after})
        self.control.record['identity_scope_changes']=receipts;self.control.save()
        return receipts

    def manifest(self,base,directory):
        """Rebind only declared fixture resources to actual returned item IDs."""
        from investigator.estate_manifest import validate
        directory=Path(directory).resolve();old_workspace=base['adapters'][0]['options']['fabric']['workspace_id']
        mapping={old_workspace:self.control.workspace}
        logical={'original-model':'original-model','original-serving':'gold','original-refined':'silver',
                 'original-landing':'bronze','model':'application-model','landing':'landing'}
        for layer in base['layers']:
            if layer['id'] in logical:
                mapping[layer['asset_id'].removeprefix('fabric://').split('/')[1]]=self.items[logical[layer['id']]]['id']
            elif layer['role']=='APPLICATION':
                mapping[layer['asset_id'].rsplit('/',1)[1]]=str(self.p['source_object_id'])
        for row in base['resources']:
            mapping[row['asset_id'].removeprefix('fabric://').split('/')[1]]=self.items['audit' if row['id']=='load-audit' else 'pipeline']['id']
        for row in base['pipelines']:
            mapping[row['delivery_asset_id'].removeprefix('fabric://').split('/')[1]]=self.items['copy']['id']
            mapping[row['producer_asset_id'].removeprefix('fabric://').split('/')[1]]=self.items['pipeline']['id']
        for boundary in base['lineage']['code_locations']:
            for location in boundary['locations']:
                mapping[location['path'].split('/',1)[0]]=self.items['notebook']['id']
        def visit(value):
            if isinstance(value,dict):
                return {k:visit(v) for k,v in value.items() if k!='string_semantics'}
            if isinstance(value,list):return [visit(x) for x in value]
            if isinstance(value,str):
                for before,after in mapping.items():value=value.replace(before,after)
                return value.replace('stock_movements_round_two_20261003',self.p['source_table'])
            return value
        result=visit(base);fabric=result['adapters'][0]['options']['fabric']
        fabric['sql_reader']['server']=self.metadata['gold']['properties']['sqlEndpointProperties']['connectionString']
        fabric['native_reader']['workspace_ids']=[self.control.workspace]
        result['storage']['inventory']=str(directory/'inventory.sqlite')
        result['lineage']['inference']['enabled']=False
        for boundary in result['lineage']['code_locations']:boundary['may_infer_from_code']=False
        for source in result['lineage']['code_sources']:
            if source['kind']=='LOCAL_PATH':source['path']=str(directory/'code')
        result['fixture_states']=[s for s in result.get('fixture_states',[]) if s['id']!='round-ten-visuals']
        for state in result['fixture_states']:
            state['id']=self.p['prefix'].lower().replace('_','-')+'-'+state['id'];state['evidence']=[]
        result['lineage'].pop('verification_sample',None)
        validate(result)
        return result


def verify_source(parameters,config,read):
    """Exact reader-side seeded rows, not an aggregate oracle or owner recount."""
    from .seed import load
    p=inputs(parameters);table=next(t for t in load()['tables'] if t['name'].startswith('stock_movements_'))
    columns=[c[0] for c in table['columns']]
    request={'query':"SELECT OBJECT_ID(N'app."+p['source_table']+"') AS [fixture_source_object_id],"+','.join('['+c+']' for c in columns)+' FROM [app].['+p['source_table']+'] ORDER BY [movement_id]',
             'parameters':[],'response_mode':'records','max_rows':400,'result_columns':['fixture_source_object_id']+columns,
             'require_read_only':True,'read_only_objects':['[app].['+p['source_table']+']']}
    served=read(config,request)
    if not served.get('read_only_verified'):raise ValueError('Prepared source reader was not guarded')
    if any(str(row.get('fixture_source_object_id'))!=str(p['source_object_id']) for row in served['rows']):
        raise ValueError('Prepared source object identity differs from the declared binding')
    actual=[[str(row[c]) for c in columns] for row in served['rows']]
    expected=sorted([[str(v) for v in row] for row in table['rows']],key=lambda row:int(row[columns.index('movement_id')]))
    if actual!=expected:raise ValueError('Prepared source differs from the committed fixture rows')
    return {'status':'EXACT_COMMITTED_ROWS_MATCH','request':request,'response':served,'row_count':len(actual)}


def run(manifest,parameters,directory,*,grant_models=False):
    """Explicit publisher controls; approvals are retained, never manufactured."""
    import time
    from metadata_auth import FabricCliTokens
    from investigator.estate_manifest import policy
    from investigator.adapters.estate_installation import configuration
    from investigator.onboarding import ModelStore
    from investigator.runtime import Runtime
    from investigator.usage_governance import UsageGovernor
    from run_source_diagnostic import transport
    from .control import FixtureControl,publisher_transport
    from .rebuild import templates
    parameters=inputs(parameters);directory=Path(directory).resolve()
    config=configuration(manifest);store=ModelStore(manifest['storage']['catalog'],config['storage']['database'],manifest['environment'])
    governor=UsageGovernor(Runtime(store,config,None,None),policy(manifest),time.time)
    session='fixture-apply-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    with FixtureControl(parameters['workspace_id'],governor,directory,session,
                        publisher_transport(FabricCliTokens(config['fabric']['auth']['tenant_id']))) as control:
        try:
            control.record['source_verification']=governor.metered_read(session,'prepared-source',
                lambda:verify_source(parameters,config,transport));control.save()
            executor=Executor(control,parameters,templates(),sleep=time.sleep)
            result=executor.provision()
            if grant_models:
                result['model_grants']=executor.grant_models(config['fabric']['native_reader']['account'])
            fresh=executor.manifest(manifest,directory)
            # Never overwrite an existing manifest or local definition export.
            code=directory/'code'/executor.items['notebook']['id']/'notebook-content.py'
            code.parent.mkdir(parents=True,exist_ok=True)
            with code.open('x',encoding='utf8') as f:f.write(executor.source)
            target=directory/'estate.yaml'
            with target.open('x',encoding='utf8') as f:json.dump(fresh,f,indent=2)
            result.update(manifest=str(target),manifest_hash=digest(fresh),
                          code_export={'path':str(code),'sha256':__import__('hashlib').sha256(code.read_bytes()).hexdigest(),
                                       'provenance':'SERVED_PUBLISHER_DEFINITION_EXPLICIT_LOCAL_EXPORT'})
            control.finish('PROVISIONED_INSTALLATION_APPROVAL_PENDING',details=result)
            return control.record
        except BaseException as error:
            control.finish('PARTIAL_OR_REFUSED',error=error)
            raise
        finally:
            with store.connect() as db:
                charges=db.execute("SELECT actual FROM adaptive_usage WHERE session_id=? AND kind='cloud'",(session,)).fetchall()
            physical=sum(json.loads(row[0] or '{}').get('cloud_calls',0) for row in charges)
            with Path('docs/runs/ledger.jsonl').open('a',encoding='utf8') as f:
                f.write(json.dumps({'experiment':'FIXTURE_REBUILD_APPLY','trial_kind':'ESTATE_CONTROL',
                    'status':control.record['status'],'artifact':str(control.path),
                    'physical_requests_charged':physical,'publisher_transport_invocations':control.dispatched,'diagnostic_reads':0,
                    'source_verification':control.record.get('source_verification',{}).get('status'),
                    'human_decision':parameters['approval_reference'],'error':control.record.get('error'),
                    'notes_doc':'docs/round-ten-rebuild-rehearsal.md'})+'\n')


def inspect_existing(control,parameters,manifest):
    """Read-only completion audit of manually provisioned artifacts, never apply.

    This deliberately does not certify a from-zero factory execution. It makes
    that distinction explicit instead of relabelling the earlier manual work.
    """
    parameters=inputs(parameters)
    workspace=control.call('workspaces/'+control.workspace)['text']
    if workspace.get('displayName')!=parameters['workspace_name'] or workspace.get('capacityId')!=parameters['capacity_id']:
        raise ValueError('Workspace name/capacity differs')
    listing=control.call('workspaces/'+control.workspace+'/items')['text']
    if listing.get('continuationToken') or listing.get('continuationUri'):raise ValueError('Incomplete listing')
    actual={x['id']:x for x in listing.get('value',[])}
    roots={row['asset_id'].removeprefix('fabric://').split('/')[1] for row in manifest['layers']+manifest['resources']
           if row['asset_id'].startswith('fabric://')}
    if not roots<=set(actual):raise ValueError('Manifest points at missing provisioned artifacts')
    return {'status':'EXISTING_ARTIFACTS_LISTED_NOT_A_FROM_ZERO_APPLY','manifest_hash':digest(manifest),
            'workspace_id':control.workspace,'artifacts':sorted(roots),'items':listing,
            'manual_steps_preserved':True}
