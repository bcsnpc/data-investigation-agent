import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from investigator.unified_runner import run,retry,transient,load,command
from investigator.process_tape import Tape,bytes_of

HEADER={'entry_point':'runner','context_identity':'fixture-context','config':{},'profile':{},'usage_policy':None,'engine_hash':'fixture-engine','state':{}}

class RunnerTests(unittest.TestCase):
    def test_default_investigation_registry_is_new_engine_legacy_is_explicit_baseline(self):
        from investigator.unified_runner import handlers
        registry=handlers()
        self.assertIs(registry['investigation'],registry['ledger-investigation'])
        self.assertIsNot(registry['legacy-baseline'],registry['investigation'])
    def test_delivered_warning_answer_exits_zero_and_records_intent_in_seal(self):
        from investigator.unified_runner import delivery_exit
        answer={'status':'DEMO_FINISHED','demo':{'ticket':{'state':'FINDINGS_SHARED','findings':{'classification':'TRANSFORMATION_LOGIC'}}},
                'verification_label':{'status':'NOT_VERIFIED'},'handoff_warnings':['ATTESTATION_LIMITED']}
        self.assertEqual(delivery_exit('investigation',answer),(0,'ANSWER_DELIVERED_WITH_LABELS'))
        with tempfile.TemporaryDirectory()as d:
            config=self.config(Path(d));config['checks']={'answer':{'kind':'investigation','options':{}}};sent={}
            result=run(config,'answer',registry={'investigation':lambda *_:answer},put=lambda k,v:sent.setdefault(k,v))
            self.assertEqual(result['exit_code'],0)
            exits=[(k,json.loads(v))for k,v in sent.items()if k.endswith('-worker-exit.json')]
            self.assertEqual(len(exits),1);self.assertEqual(exits[0][1]['last_step'],'investigation')
            manifest=json.loads(next(v for k,v in sent.items()if k.endswith('/run-record.json')))
            self.assertIn(exits[0][0],[r['key']for r in manifest['records']])
    def test_undelivered_ticket_exits_nonzero_but_not_found_answer_is_delivered(self):
        from investigator.unified_runner import delivery_exit
        for state in ('NEW','CLARIFYING','HELD'):
            self.assertEqual(delivery_exit('investigation',{'status':'DEMO_FINISHED','demo':{'ticket':{'state':state}}})[0],1)
        self.assertEqual(delivery_exit('ledger-investigation',{'verdict':'not found','outputs':{'business':'No supported cause.','technical':'Evidence gap.'}})[0],0)
    def test_failed_access_table_stops_before_handler_and_is_sealed(self):
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d));calls=[];sent=[]
            table={'status':'FAIL','rows':[{'id':'target','status':'FAIL','reason':'HTTP_403'}]}
            with patch('investigator.access_check.configured',return_value=table):
                result=run(config,'bronze',registry={'probe':lambda *args:calls.append('read')},put=lambda key,raw:sent.append((key,raw)))
            self.assertEqual(result['result']['reason'],'CHECK_ACCESS_FAILED')
            self.assertEqual(result['result']['access_check'],table)
            self.assertFalse(result['result']['investigation_executed'])
            self.assertEqual(calls,[])
            self.assertTrue(any(key.endswith('/run-record.json') for key,_ in sent))
            self.assertTrue(sent[-1][0].endswith('/timing-summary.json'))

    def test_access_check_handler_receives_the_already_recorded_preflight(self):
        from investigator.unified_runner import handlers
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d));config['checks']={'access':{'kind':'access-check','options':{}}}
            table={'status':'INCOMPLETE','rows':[{'status':'NOT_TESTABLE','reason':'UNBOUND'}]}
            sent=[]
            with patch('investigator.access_check.configured',return_value=table) as preflight:
                result=run(config,'access',registry=handlers(),put=lambda key,raw:sent.append((key,raw)))
            self.assertEqual(result['result'],table)
            preflight.assert_called_once()

    def config(self,root):
        return {'version':'dia-runner-estate-v1','manifest':'/inputs/estate.json','image':'registry/worker@sha256:'+'a'*64,'capture':{},'checks':{'bronze':{'kind':'probe','options':{}}},'output_root':str(root/'results'),'bootstrap':HEADER}
    def test_header_refuses_before_any_transport_or_handler(self):
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d));config['bootstrap']={'request':'old malformed header'}
            calls=[]
            with self.assertRaisesRegex(ValueError,'TAPE_BOOTSTRAP_FIELDS'):
                run(config,'bronze',registry={'probe':lambda *_:calls.append('read')},put=lambda *_:calls.append('put'))
            self.assertEqual(calls,[])
    def test_native_result_retained_even_when_final_seal_fails(self):
        with tempfile.TemporaryDirectory() as d:
            retained={}
            def handler(plan,ctx):
                ctx.record('native-result',{'value':7661})
                raise ValueError('FINAL_SEAL_FAILED')
            with self.assertRaisesRegex(ValueError,'FINAL_SEAL_FAILED'):
                run(self.config(Path(d)),'bronze',registry={'probe':handler},put=lambda k,v:retained.setdefault(k,v))
            values=[json.loads(v) for v in retained.values()]
            self.assertIn({'value':7661},values)
            status=[json.loads(v) for key,v in retained.items() if key.endswith('-status.json')][-1]
            self.assertEqual(status['status'],'FAILED')
            self.assertTrue(status['partial'])
            self.assertTrue(values[-1]['not_part_of_semantic_tape'])
    def test_existing_tape_each_event_mirrored_before_read_can_return(self):
        with tempfile.TemporaryDirectory() as d:
            retained={}
            def handler(plan,ctx):
                tape=Tape(ctx.root/'native.json',bootstrap=HEADER)
                tape.event('CONFIGURATION',bytes_of({'value':16}))
                self.assertEqual(sum('tape-event' in k for k in retained),2)
                tape.finish({'value':16})
                return {'value':16}
            result=run(self.config(Path(d)),'bronze',registry={'probe':handler},put=lambda k,v:retained.setdefault(k,v))
            self.assertEqual(result['status'],'COMPLETED')
            self.assertEqual(sum('tape-event' in k for k in retained),3)
    def test_transient_twice_retry_and_no_authorization_retry(self):
        calls=[];wait=[];events=[]
        def call():
            calls.append(1)
            if len(calls)<3:raise TimeoutError('connect')
            return 16
        self.assertEqual(retry(call,record=lambda *x:events.append(x),sleep=wait.append),16)
        self.assertEqual(wait,[30,45]);self.assertEqual(len(events),2)
        self.assertFalse(transient(ValueError('billing authorization failed')))
        self.assertFalse(transient(ValueError('guardrail denied')))
        from fabric_sql_surface import LowerReadError
        self.assertTrue(transient(LowerReadError('connect',18456,'SqlException')))
    def test_wrapped_url_timeout_retries_but_http_auth_and_certificate_errors_do_not(self):
        from urllib.error import URLError,HTTPError
        import ssl
        calls=[];wait=[];events=[]
        def call():
            calls.append(1)
            if len(calls)==1:raise URLError(TimeoutError('timed out'))
            return 'completed'
        self.assertEqual(retry(call,record=lambda *v:events.append(v),sleep=wait.append),'completed')
        self.assertEqual(wait,[30])
        self.assertTrue(events[0][1]['retry'])
        self.assertFalse(transient(HTTPError('https://example.invalid',401,'Unauthorized',None,None)))
        self.assertFalse(transient(URLError(ssl.SSLCertVerificationError('certificate verification failed'))))
        self.assertFalse(transient(URLError(ValueError('unknown failure'))))
    def test_retry_uses_new_attempt_directory_and_retains_first_failure(self):
        with tempfile.TemporaryDirectory() as d:
            roots=[];retained={}
            def handler(plan,ctx):
                roots.append(ctx.root)
                (ctx.root/'native.json').write_text('partial')
                if len(roots)==1:raise ConnectionError('connection reset')
                return {'value':16}
            result=run(self.config(Path(d)),'bronze',registry={'probe':handler},put=lambda k,v:retained.setdefault(k,v),sleep=lambda _:None)
            self.assertEqual(result['status'],'COMPLETED')
            self.assertNotEqual(roots[0],roots[1])
            self.assertTrue(all((p/'native.json').is_file() for p in roots))
            self.assertTrue(any('attempt-failure' in key for key in retained))
    def test_registry_has_no_user_code_or_shell(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'estate.json';config=self.config(Path(d));config['checks']['bad']={'kind':'os.system','options':{}}
            p.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError,'RUNNER_TYPED_CHECK_REQUIRED'):load(p)
            self.assertEqual(command('/inputs/runner.json','bronze'),['python','/app/scripts/dia.py','run','bronze','--estate','/inputs/runner.json','--runtime','worker'])
    def test_budget_mode_does_not_leak_to_later_or_replayed_operations(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'INVESTIGATOR_OPERATING_MODE':'LEGACY'},clear=False):
            def handler(plan,ctx):
                self.assertEqual(os.environ['INVESTIGATOR_OPERATING_MODE'],'BUILD_PHASE')
                return {}
            run(self.config(Path(d)),'bronze',registry={'probe':handler},put=lambda *_:None)
            self.assertEqual(os.environ['INVESTIGATOR_OPERATING_MODE'],'LEGACY')
    def test_sealed_scan_boundary_replay_is_limited_and_detects_content_change(self):
        from investigator.runner_replay import boundary
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d))
            result=run(config,'bronze',registry={'probe':lambda *_:{'nodes':3}},put=lambda *_:None,run_id='scan-test')
            root=Path(config['output_root'])/'scan-test'
            report=boundary(root,config['image'])
            self.assertEqual(report['coverage'],'BOUNDARY_ONLY')
            self.assertFalse(report['graph_recomputed'])
            first=next(root.glob('*-step-result.json'));first.write_text('{"nodes":4}')
            with self.assertRaisesRegex(ValueError,'MEMBER_CHANGED'):boundary(root,config['image'])
    def test_probe_recomputes_native_read_from_tape_without_transport(self):
        import copy,io
        from types import SimpleNamespace
        from investigator.runner_replay import probe
        from investigator.process_tape import active
        from investigator.physical_reads import scope
        from fabric_sql_surface import read
        from gateway_test_support import allow_sql
        from test_managed_sql_worker import AUTH
        reader={**AUTH,'server':'synthetic.database.windows.net','account':'reader'}
        config={'fabric':{'sql_reader':reader,'auth':{'tenant_id':AUTH['tenant_id']}}}
        request={'query':'SELECT value FROM dbo.synthetic','read_only_objects':['dbo.synthetic'],'result_columns':['value'],'max_rows':2}
        result={'rows':[{'value':7}]}
        child=SimpleNamespace(stdin=io.StringIO(),stdout=io.StringIO(json.dumps(result)+'\n'),wait=lambda timeout=None:0,poll=lambda:0,kill=lambda:None)
        from investigator.unified_runner import capture_header
        with tempfile.TemporaryDirectory() as header_root:
            deployed=self.config(Path(header_root))
            deployed['checks']['bronze']['options']={'config':config,'database':'db','request':request}
            bootstrap=capture_header(deployed)
        self.assertEqual(bootstrap['entry_point'],'runner_probe')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'probe.json';tape=Tape(path,bootstrap)
            with active(tape),scope(lambda k,f:f()),allow_sql(reader['server'],'db',['dbo.synthetic']),patch('subprocess.Popen',return_value=child):
                actual=read(config,'db',request);tape.finish(actual)
            original=path.read_bytes()
            original_popen=subprocess.Popen
            def offline_process(command,*args,**kwargs):
                if command[0]=='git':return original_popen(command,*args,**kwargs)
                raise AssertionError('live worker launched')
            with patch('investigator.live_gateway.current',side_effect=AssertionError('network used')),patch('subprocess.Popen',side_effect=offline_process):
                replayed=probe(path)
            self.assertTrue(replayed['matched'])
            self.assertEqual(replayed['result'],result)
            self.assertEqual(path.read_bytes(),original)
    def test_azure_launch_uses_pinned_image_existing_environment_and_no_inline_code(self):
        from types import SimpleNamespace
        from investigator.unified_runner import azure_launch
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d));config['run_id']='fixed-run'
            config['deployment']={'resource_id':'/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/existing-rg/providers/Microsoft.App/jobs/existing-job','cli':['python','-m','azure.cli']}
            calls=[]
            def execute(argv,**kwargs):
                calls.append(argv)
                if 'show' in argv:return SimpleNamespace(stdout=json.dumps({'properties':{'template':{'containers':[{'name':'worker','image':'old','env':[{'name':'EXISTING_REF','secretRef':'existing-vault-ref'}]}]}}}))
                template=json.loads(Path(argv[argv.index('--yaml')+1]).read_bytes())
                container=template['containers'][0]
                self.assertEqual(container['image'],config['image'])
                self.assertEqual(container['command'][0:3],['python','/app/scripts/dia.py','run'])
                self.assertEqual(container['args'],[])
                env={v['name']:v for v in container['env']}
                self.assertEqual(env['EXISTING_REF']['secretRef'],'existing-vault-ref')
                self.assertEqual(json.loads(env['DIA_RUNNER_ESTATE_JSON']['value']),config)
                return SimpleNamespace(stdout='{"name":"job-execution-1"}')
            budget=[]
            with patch.dict(sys.modules,{'investigator.build_phase':SimpleNamespace(admit_platform=lambda *a:budget.append(a))}):
                result=azure_launch(config,'bronze',execute=execute)
            self.assertEqual(result['execution_name'],'job-execution-1')
            self.assertEqual(len(calls),2);self.assertEqual(len(budget),1)
    def test_approved_worker_resources_override_execution_without_changing_schedule(self):
        import copy
        from types import SimpleNamespace
        from investigator.adapters.runner_deployment import launch
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d))
            config['deployment']={'resource_id':'/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/existing-rg/providers/Microsoft.App/jobs/job-dia-worker',
                'cli':['python','-m','azure.cli'],'execution_resources':{'cpu':1,'memory':'2Gi'}}
            job={'properties':{'configuration':{'scheduleTriggerConfig':{'cronExpression':'0 6 * * *'}},
                'template':{'containers':[{'name':'worker','image':'old','resources':{'cpu':0.5,'memory':'1Gi'}}]}}}
            before=copy.deepcopy(job);calls=[]
            def execute(argv,**kwargs):
                calls.append(argv)
                if 'show' in argv:return SimpleNamespace(stdout=json.dumps(job))
                self.assertIn('start',argv);self.assertNotIn('update',argv)
                template=json.loads(Path(argv[argv.index('--yaml')+1]).read_bytes())
                self.assertEqual(template['containers'][0]['resources'],{'cpu':1,'memory':'2Gi'})
                return SimpleNamespace(stdout='{"name":"larger-execution"}')
            with patch('investigator.build_phase.admit_platform'):
                self.assertEqual(launch(config,'bronze',execute=execute)['execution_name'],'larger-execution')
            self.assertEqual(job,before);self.assertEqual(len(calls),2)

    def test_resource_override_refuses_other_jobs_and_any_other_size(self):
        from investigator.adapters.runner_deployment import launch
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d))
            base='/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/existing-rg/providers/Microsoft.App/jobs/'
            for name,resources in [('job-dia-graph-scan',{'cpu':1,'memory':'2Gi'}),
                    ('job-dia-worker',{'cpu':2,'memory':'4Gi'}),('job-dia-worker',{'cpu':True,'memory':'2Gi'})]:
                config['deployment']={'resource_id':base+name,'cli':['python','-m','azure.cli'],'execution_resources':resources}
                with self.subTest(name=name,resources=resources),patch('investigator.build_phase.admit_platform'),self.assertRaisesRegex(ValueError,'RUNNER_WORKER_RESOURCE_OVERRIDE_REFUSED'):
                    launch(config,'bronze',execute=lambda *a,**k:self.fail('No Azure call before rejection'))

    def test_smoke_gold_uses_physical_meter_and_earned_demo_is_wired(self):
        from types import SimpleNamespace
        from investigator.unified_runner import handlers
        from investigator.physical_reads import _scope
        calls=[]
        class Meter:
            def __init__(self,*args):pass
            def __call__(self,fn):calls.append('physical');return fn()
            def close(self):calls.append('closed')
        def gold(payload):
            self.assertIsNotNone(_scope.get())
            _scope.get()['meter']('next-request',lambda:None)
            return {'value':7661}
        def smoke(config,context,**kwargs):
            self.assertEqual(kwargs['gold_read']({}),{'value':7661})
            self.assertEqual(kwargs['demo'](),{'status':'INVESTIGATED'})
            self.assertEqual(kwargs['blob_roundtrip']({'legacy_blob_config':'unused'},b'{"kind":"DAILY_SMOKE"}'),{'status':'PASS'})
            return {'status':'PASS'}
        def form(argv):
            root=Path(argv[argv.index('--job-root')+1]);root.mkdir()
            (root/'result.json').write_text('{"status":"INVESTIGATED"}')
        with tempfile.TemporaryDirectory() as d,patch('scan_estate_graph.Meter',Meter),patch('investigator.shared_state.configured_state',return_value=object()),patch('investigator.daily_smoke._gold_read',gold),patch('investigator.daily_smoke.run_smoke',smoke),patch('investigator.daily_smoke.capture_roundtrip',return_value={'status':'PASS'}) as blob,patch('cloud_form_worker.main',form):
            result=handlers()['smoke']({'options':{'config':{'demo_earned':True},'budget':{},'max_requests':10,'demo':{'bundle':'fixture','sha256':'a'*64}}},SimpleNamespace(root=Path(d)))
            self.assertEqual(result['status'],'PASS')
            self.assertEqual(calls,['physical','physical','closed'])
            blob.assert_called_once_with(unittest.mock.ANY,b'{"kind":"DAILY_SMOKE"}')

class CaptureGatewayTests(unittest.TestCase):
    config=RunnerTests.config
    def gateway(self):
        from investigator.live_gateway import Gateway
        return Gateway({'version':1,'live_enabled':True,'identities':{'capture':{'role':'platform','runner_captures':[{'account_url':'https://synthetic.blob.core.windows.net','prefix':'round20','run_id':'run-one','max_bytes':1024}]}}})
    def test_only_exact_run_prefix_and_immutable_bounded_json_put_is_allowed(self):
        from investigator.live_gateway import GatewayDenied
        gateway=self.gateway();url='https://synthetic.blob.core.windows.net/captures/round20/run-one/00000001-header.json'
        headers={'If-None-Match':'*','x-ms-blob-type':'BlockBlob'}
        with patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'},clear=False):
            gateway.http('capture','PUT',url,b'{}',headers)
            gateway.http('capture','GET',url)
            gateway.http('capture','HEAD',url)
            for method,target,body,h in [('PUT',url,b'{}',{}),('PUT',url,b'x'*1025,headers),('DELETE',url,None,{}),
                    ('PUT',url.replace('run-one','run-two'),b'{}',headers),('PUT',url.replace('/run-one/','/run-one-adjacent/'),b'{}',headers),
                    ('PUT',url.replace('00000001-header.json','../run-two/00000001-header.json'),b'{}',headers),
                    ('PUT',url.replace('00000001-header.json','%2e%2e/run-two/00000001-header.json'),b'{}',headers),
                    ('PUT',url+'?comp=metadata',b'{}',headers)]:
                with self.subTest(method=method,target=target),self.assertRaises(GatewayDenied):gateway.http('capture',method,target,body,h)
    def test_real_process_kill_preserves_partial_remote_blob_objects(self):
        # The fake Blob service is an independent filesystem durable store. The
        # child uses the real runner and is killed while the second read blocks.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);blob=root/'fake-blob';blob.mkdir()
            script=root/'child.py'
            config=self.config(root)
            script.write_text('''import json,time,sys
from pathlib import Path
from investigator.unified_runner import run
root=Path(sys.argv[1]);config=json.loads(sys.argv[2])
def put(key,raw):
 p=root/'fake-blob'/key;p.parent.mkdir(exist_ok=True,parents=True)
 with p.open('xb') as f:f.write(raw);f.flush();__import__('os').fsync(f.fileno())
def handler(plan,ctx):
 ctx.step('first-read',lambda:{'value':7661})
 (root/'ready').write_text('ready')
 time.sleep(60)
run(config,'bronze',registry={'probe':handler},put=put,run_id='killed-run')
''')
            env={**os.environ,'PYTHONPATH':str(Path(__file__).parent)}
            child=subprocess.Popen([sys.executable,str(script),str(root),json.dumps(config)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                import time
                deadline=time.time()+15
                while not (root/'ready').exists() and child.poll() is None and time.time()<deadline:time.sleep(.05)
                self.assertTrue((root/'ready').exists(),child.communicate(timeout=1) if child.poll() is not None else 'child failed to reach read')
                child.kill();child.wait(timeout=5)
                entries=[json.loads(p.read_bytes()) for p in sorted((blob/'killed-run').glob('*.json'))]
                self.assertTrue(any(v.get('result')=={'value':7661} for v in entries))
                self.assertTrue(any(v.get('status')=='STARTED' and v.get('partial') for v in entries))
                self.assertFalse(any(v.get('status')=='COMPLETED' for v in entries))
            finally:
                if child.poll() is None:child.kill();child.wait()
                child.communicate()

if __name__=='__main__':unittest.main()
