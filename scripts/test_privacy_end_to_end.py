"""Real store/intake/preview/procedure/synthesis path, synthetic transports only."""
import copy,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID
from investigator.privacy_capture import Capture
from investigator.privacy_projection import Projection,canonical
from investigator.privacy_installation import Installation
from investigator.privacy_tape import PrivacyTape
from investigator.onboarding import digest
from investigator.process_tape import bounded_call
from investigator.reported_figure import span


class EndToEndTests(unittest.TestCase):
    def test_span_identity_uses_projected_ticket_positions_and_keeps_numeric_precision(self):
        policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
            'estate_id':'synthetic','key_reference':'secret/synthetic','columns':['person']}
        p=Projection(policy,lambda _:b'synthetic-in-memory-key-32-bytes!!')
        text='PRIVATE_PERSON reports 7 units.';source={'quote':'7 units','start':23,'end':30}
        source['start']=text.index('7 units');source['end']=source['start']+len(source['quote'])
        with Capture(p,[]).active():span(source,text)
        p.bind('person','PRIVATE_PERSON');p.prepare_spans()
        result=p.project({'text':text,'source':source})
        self.assertEqual(span(result['source'],result['text']),'7 units')
        self.assertNotEqual(result['source']['start'],source['start'])

    def test_projected_accounting_pin_replays_actual_output_release(self):
        from investigator.usage_governance import charged
        from investigator.process_tape import active
        policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
            'estate_id':'synthetic','key_reference':'secret/synthetic','columns':['person']}
        key=lambda _:b'synthetic-in-memory-key-32-bytes!!'
        row={'reserved':json.dumps({'output_tokens':100}),'actual':json.dumps({'output_tokens':30}),
             'status':'SETTLED'}
        with tempfile.TemporaryDirectory() as folder:
            tape=PrivacyTape(Path(folder)/'tape.json',Projection(policy,key))
            tape.event('BOOTSTRAP',canonical({'state':{'accounting_version':3}}))
            with active(tape):expected=charged(row)
            tape.finish({'status':'COMPLETED'})
            replay=PrivacyTape(tape.path,Projection(policy,key),replay=True)
            with active(replay):self.assertEqual(charged(row),expected)

    def test_projected_tape_peek_validates_without_consumption(self):
        from investigator.privacy_projection import ProjectionError
        policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
            'estate_id':'synthetic','key_reference':'secret/synthetic','columns':['person']}
        key=lambda _:b'synthetic-in-memory-key-32-bytes!!'
        with tempfile.TemporaryDirectory() as folder:
            tape=PrivacyTape(Path(folder)/'tape.json',Projection(policy,key))
            self.assertIsNone(tape.peek('CONTROL'))
            tape.event('CONTROL',canonical({'status':'FAILED'}));tape.finish({})
            replay=PrivacyTape(tape.path,Projection(policy,key),replay=True)
            self.assertEqual(replay.peek('CONTROL'),canonical({'status':'FAILED'}))
            self.assertIsNone(replay.peek('OTHER'));self.assertEqual(replay.index,0)
            replay.events[0]['sha256']='0'*64
            with self.assertRaises(ProjectionError):replay.peek('CONTROL')

    def test_projected_no_governor_does_not_pin_unprepared_delta(self):
        from investigator.privacy_installation import _admission_state
        no_governor=SimpleNamespace(concurrency_limit=1,agent=SimpleNamespace(governor=None))
        self.assertNotIn('budget_checkpoint',_admission_state(no_governor,SimpleNamespace(),False))
        governed=SimpleNamespace(concurrency_limit=1,agent=SimpleNamespace(governor=object()))
        self.assertEqual(_admission_state(governed,SimpleNamespace(),False)['budget_checkpoint'],'DELTA_V2')

    def test_projected_admission_pins_keep_legacy_contract_and_refuse_changed_pins(self):
        from investigator.privacy_installation import _admission_state
        from investigator.privacy_projection import ProjectionError
        workspace=SimpleNamespace(concurrency_limit=3)
        self.assertIsNone(_admission_state(workspace,SimpleNamespace(bootstrap={}),True))
        legacy={'workspace_concurrency_limit':1}
        self.assertEqual(_admission_state(workspace,SimpleNamespace(bootstrap={'state':legacy}),True),legacy)
        for name,value in [('local_accounting','OTHER'),('budget_checkpoint','OTHER'),('snapshot_clock','OTHER'),
                           ('physical_transport_retries',True),('physical_transport_retries',3),
                           ('provider_transport_retries',3),('accounting_version',True),('accounting_version',999)]:
            with self.subTest(name=name,value=value),self.assertRaises(ProjectionError):
                _admission_state(workspace,SimpleNamespace(bootstrap={'state':{name:value}}),True)

    def test_projected_tape_exposes_bootstrap_admission_state_without_raw_disk(self):
        policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
            'estate_id':'synthetic','key_reference':'secret/synthetic','columns':['person']}
        key=lambda _:b'synthetic-in-memory-key-32-bytes!!'
        p=Projection(policy,key);p.bind('person','PRIVATE_PERSON')
        bootstrap={'state':{'workspace_concurrency_limit':3},'person':'PRIVATE_PERSON'}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=PrivacyTape(path,p)
            tape.event('BOOTSTRAP',canonical(bootstrap))
            self.assertEqual(tape.bootstrap['state']['workspace_concurrency_limit'],3)
            self.assertFalse(path.exists())
            tape.finish({'status':'COMPLETED'})
            self.assertNotIn(b'PRIVATE_PERSON',path.read_bytes())
            replay=PrivacyTape(path,Projection(policy,key),replay=True)
            self.assertEqual(replay.bootstrap['state']['workspace_concurrency_limit'],3)
            replay.event('BOOTSTRAP',canonical(replay.bootstrap))
            replay.finish({'status':'COMPLETED'})

    def test_sensitive_column_full_procedure_has_no_raw_disk_sidecar_output_or_broken_seal(self):
        from investigator.runtime import Runtime
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.workspace import Workspace
        from investigator.enterprise_discovery import Discovery
        from investigator.native_identity import KEY,make
        from investigator import planner_recording
        import test_enterprise_discovery as fixture
        from test_process_debugging import Adapter
        ws='11111111-1111-4111-8111-111111111111';mid='22222222-2222-4222-8222-222222222222'
        rid='33333333-3333-4333-8333-333333333333'
        column='fabric://'+ws+'/'+mid+'/table/Entities/columns/region'
        policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
            'estate_id':'synthetic','key_reference':'secret/synthetic','columns':[column]}
        raw='Sensitive Person Test'
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=Projection(policy,lambda _:b'synthetic-in-memory-key-32-bytes!!')
            capture=Capture(p,[root/'catalog.sqlite',root/'inventory.sqlite']);self.addCleanup(capture.close)
            with capture.active(),patch('test_enterprise_discovery.tempfile.TemporaryDirectory',
                 return_value=SimpleNamespace(name=folder,cleanup=lambda:None)),patch('test_enterprise_discovery.uuid4',
                 side_effect=[UUID(ws),UUID(mid),UUID(rid)]+[UUID(rid)]*20):
                helper=fixture.DiscoveryTests();helper.setUp()
                helper.config['fabric']['native_reader']={'mode':'isolated_reader','tenant_id':ws,
                    'principal_id':rid,'account':'reader@example.com','workspace_ids':[ws]}
                helper.config['_estate']={'recording':policy,'resources':[],
                    'lineage':{'inference':{'code_resources':[]}},
                    'capability_ceiling':sorted(Adapter([],{}).capabilities()),'layers':[
                    {'id':'semantic','asset_id':'top','reachable':True,'role':'SEMANTIC','business_name':'reported calculation'},
                    {'id':'serving','asset_id':'lower','reachable':True,'role':'SERVING','business_name':'source records'}]}
                helper.discovery=Discovery(helper.store,helper.config);helper.scan()
                model=helper.store.list(True)[0]
                column=next(a['id'] for a in __import__('investigator.model_context',fromlist=['assets']).assets(model['context']) if a['name']=='region')
                self.assertEqual(p.policy['columns'],[column])
                measure=next(m['id'] for m in model['context']['measures'] if m['name']=='Total')
                helper.store.privacy_capture=capture
                native=lambda request:{'results':[{'tables':[{'rows':[{'[m0]':7}]}]}]}
                runtime=Runtime(helper.store,helper.config,native,None)
                usage={'environment':'test','daily_limits':{'planner_calls':50,'cloud_calls':50,
                    'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
                agent=AdaptiveRuntime(runtime,lambda _:self.fail('No investigation planner'),usage_policy=usage)
                def resolver(payload):
                    def call():
                        answer={'reported_figure':{'state':'UNSPECIFIED'},'action':'PROPOSE','model_id':model['id'],
                            'measure_id':measure,'metric_quote':'Total','question':None,
                            'ticket_shape':'MISMATCH_COMPLAINT','comparison_mode':'VERTICAL',
                            'filters':[{'column_id':column,'operator':'in','values':[raw]}],
                            'dimension_ids':[],'scope_quotes':[{'column_id':column,'quote':raw}]}
                        with planner_recording.recording({'payload':payload,'stage':'intake'}) as record:
                            record.safe_write('request.body',canonical(payload))
                            record.safe_write('response.body',canonical(answer))
                        return answer
                    return bounded_call('synthetic:intake',payload,call),{'usage':{'output_tokens':50}}
                workspace=Workspace(agent,execution_enabled=True,question_resolver=resolver)
                install=Installation(workspace,capture,root/'tapes')
            class Reader(Adapter):
                def __init__(self,*args,**kwargs):
                    super().__init__(['top','lower'],{'top':7,'lower':7})
                    self.meter=kwargs['meter_read'];self.config=helper.config
                def resolve_path(self,measure):
                    path=super().resolve_path(measure)
                    path['evidence']['metadata']={'context_version':__import__('investigator.context_search',fromlist=['latest']).latest(helper.store)['version']}
                    return path
                def evaluate(self,layer,measure,scope):
                    # Synthetic distinct objects, evaluated by the unchanged
                    # procedure. Both quantities and their surface reports are
                    # recorded through the real bounded boundary.
                    from investigator.process_debugging import Probe
                    def read():
                        original=super(Reader,self).evaluate(layer,measure,scope)
                        from investigator import native_diagnostics as nd
                        extract=nd.extract
                        def response(value,request):
                            return {**extract(value,request),'surface_report':original.surface_report,
                                    'surface_report_binding':'VALUE_QUERY'}
                        plan={'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],
                              'measure_ids':[measure],'filters':scope['filters'],'dimension_id':None,
                              'include_dependencies':False}
                        with patch.object(nd,'extract',side_effect=response):
                            receipt=nd.run(helper.store,plan,lambda request:bounded_call('synthetic:quantity',request,native_call))
                        evidence={'id':receipt['id'],'tool':'native','request_hash':receipt['request_hash'],
                            'values':receipt['result']['rows'],'measure_id':measure,'dimension_id':None,
                            'test_purpose':'ESTABLISH_BASELINE'}
                        from dataclasses import replace
                        return vars(replace(original,evidence=evidence))
                    def native_call():return native(None)
                    record=self.meter('synthetic_quantity',read)
                    return Probe(**record)
            from investigator.evidence_synthesis import azure_synthesize
            def synthesis(payload,options):
                def generate(view,**kwargs):
                    answer={'technical_output':{'text':'The recorded quantity passes through the declared read.',
                        'evidence_ids':[e['id'] for e in view['evidence']]}}
                    return bounded_call('synthetic:synthesis',view,lambda:(answer,{'usage':{'output_tokens':30}}))
                with patch('ticket_planner.azure_generate',side_effect=generate):
                    return azure_synthesize(payload,options)
            request={'text':'Total looks wrong for '+raw+'.','request_key':'private-case','parent_id':None}
            with patch('investigator.adapters.microsoft_process.MicrosoftProcessAdapter',Reader), \
                 patch.object(planner_recording,'ROOT',root), \
                 patch('investigator.evidence_synthesis.azure_synthesize',side_effect=synthesis):
                result=install.investigate(request)
            self.assertEqual(result['tape_class'],'PRIVACY_PROJECTED')
            self.assertNotIn(raw,json.dumps(result))
            self.assertEqual(result['result']['status'],'COMPLETED',result['result'])
            self.assertEqual(agent.get(result['result']['id'])['synthesis']['status'],'COMPLETED',agent.get(result['result']['id'])['synthesis'])
            for file in root.rglob('*'):
                if file.is_file():self.assertNotIn(raw.encode(),file.read_bytes(),str(file))
            tape=PrivacyTape(result['recording'],Projection(policy,lambda _:b'synthetic-in-memory-key-32-bytes!!'),replay=True)
            import base64
            from investigator.budget_tape_contract import ACCOUNTING_VERSION
            from investigator.local_accounting import PIN as LOCAL_ACCOUNTING_PIN
            self.assertEqual(tape.bootstrap['state']['local_accounting'],LOCAL_ACCOUNTING_PIN)
            self.assertEqual(tape.accounting_version,ACCOUNTING_VERSION)
            self.assertEqual(tape.bootstrap['state']['budget_checkpoint'],'DELTA_V2')
            self.assertEqual(tape.bootstrap['state']['snapshot_clock'],'ONE_CLOCK_V1')
            self.assertEqual(tape.bootstrap['state']['physical_transport_retries'],2)
            self.assertEqual(tape.bootstrap['state']['provider_transport_retries'],2)
            for event in tape.events:self.assertNotIn(raw.encode(),base64.b64decode(event['body']))
            before={str(file):file.read_bytes() for file in root.rglob('*') if file.is_file()}
            with patch('investigator.adapters.microsoft_process.MicrosoftProcessAdapter',Reader), \
                 patch.object(planner_recording,'ROOT',root), \
                 patch('investigator.evidence_synthesis.azure_synthesize',side_effect=synthesis):
                replay=install.replay(result['recording'])
            self.assertEqual(replay['result'],result['result'])
            self.assertEqual(before,{str(file):file.read_bytes() for file in root.rglob('*') if file.is_file()})
            from investigator.privacy_storage import EvidenceStore,connect
            capture.close();loaded=EvidenceStore(root/'catalog.sqlite',Projection(policy,lambda _:b'synthetic-in-memory-key-32-bytes!!'))
            self.addCleanup(loaded.close)
            with connect(root/'catalog.sqlite') as db:
                for table in ('workspace_intakes','workspace_previews','model_contexts'):
                    for body,identity in db.execute('SELECT body,hash FROM '+table):
                        self.assertEqual(digest(json.loads(body)),identity,table)
                for body,identity in db.execute('SELECT body,hash FROM adaptive_syntheses'):
                    self.assertEqual(digest(json.loads(body)),identity)
                for body,identity in db.execute('SELECT state,state_hash FROM adaptive_sessions'):
                    self.assertEqual(digest(json.loads(body)),identity)
                from investigator.receipt_integrity import verify
                for (identity,) in db.execute('SELECT id FROM native_diagnostics'):
                    self.assertEqual(verify(db,'native',identity)['state'],'SEALED')
