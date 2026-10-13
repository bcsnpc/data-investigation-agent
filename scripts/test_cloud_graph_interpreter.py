import hashlib,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.artifact_store import Files,LocalObjects
from investigator.shared_state import SharedState,StateConflict
from investigator.planner_recording import ACTIVE
from cloud_graph_interpreter import execute,tasks_from_bytes,runtime_governor
POLICY={'environment':'synthetic','daily_limits':{'planner_calls':20,'cloud_calls':2,'input_characters':200000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':2}


class CloudGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.state=SharedState.offline(self.root/'state.sqlite');self.state.migrate()
        self.files=Files(LocalObjects(self.root/'objects'))
        self.state.put('usage_policy',POLICY['environment'],{'policy':POLICY,'round_policy':None})
        self.statepatch=patch('investigator.shared_state.configured_state',return_value=self.state);self.statepatch.start();self.addCleanup(self.statepatch.stop)
        self.envpatch=patch.dict('os.environ',{'INVESTIGATOR_WORKER_ID':'test-worker'});self.envpatch.start();self.addCleanup(self.envpatch.stop)
        self.gov=runtime_governor(self.state,POLICY['environment'],self.root)
        self.calls=[]
    def task(self):
        text='out = incoming'
        return {'estate':'e','owner':'o','code':text,'definition_hash':hashlib.sha256(text.encode()).hexdigest(),
            'source_id':'code','observed_at':'2026-10-13T00:00:00Z',
            'nodes':[{'id':'out','kind':'COLUMN','label':'Output'},{'id':'in','kind':'COLUMN','label':'Input'}]}
    def producer(self,request,schema,options):
        self.calls.append(request);record=ACTIVE.get()
        raw=json.dumps(request).encode();record.request(SimpleNamespace(read=lambda:raw))
        answer={'edges':[{'source':'out','target':'in','kind':'COMPUTED_FROM','start':0,'end':14,
            'quote':'out = incoming','explanation':'Declared assignment only'}]}
        response=json.dumps(answer).encode();record.response(SimpleNamespace(status_code=200,read=lambda:response))
        self.assertEqual(options['max_output_tokens'],8000)
        return answer,{'usage':{'input_tokens':30,'output_tokens':40,'total_tokens':70}}
    def run_batch(self,tasks=None,producer=None,batch='b'):
        tasks=tasks or [self.task()];raw=json.dumps(tasks).encode();h=hashlib.sha256(raw).hexdigest()
        return execute(tasks,batch_id=batch,input_sha256=h,state=self.state,governor=self.gov,files=self.files,
            work=self.root/batch,producer=producer or self.producer)
    def result(self,summary):
        target=self.root/(summary['batch_id']+'-restored.json');self.files.restore(summary['result']['sha256'],target)
        return json.loads(target.read_bytes())
    def test_full_shared_reservation_body_recording_cas_and_inferred_only(self):
        summary=self.run_batch();result=self.result(summary)
        self.assertEqual(summary['status'],'COMPLETED');self.assertEqual(summary['estate_reads'],0)
        edge=result['results'][0]['result']['edges'][0]
        self.assertEqual(edge['confidence'],'INFERRED');self.assertFalse(edge['properties']['execution_established'])
        capture=result['captures'][0];self.assertTrue(capture['complete'])
        self.assertIn('request.body',capture['files']);self.assertIn('response.body',capture['files'])
        with self.state.transaction() as db:
            row=db.execute('SELECT reserved,actual,status FROM state_usage').fetchone()
        reserved=json.loads(row[0]);self.assertEqual(reserved['output_tokens'],8000)
        self.assertGreater(reserved['input_characters'],len(self.task()['code']))
        self.assertEqual(json.loads(row[1])['output_tokens'],40);self.assertEqual(row[2],'SETTLED')
    def test_four_distinct_tasks_allowed_no_retry_same_batch(self):
        self.run_batch([self.task() for _ in range(4)])
        self.assertEqual(len(self.calls),4)
        with self.assertRaises(StateConflict):self.run_batch()
        self.assertEqual(len(self.calls),4)
    def test_auth_error_stops_remaining_calls_and_retains_uncertain_receipt(self):
        class AuthenticationError(Exception):pass
        def reject(request,schema,options):
            self.calls.append(request);ACTIVE.get().request(SimpleNamespace(read=lambda:b'{"safe":"request"}'))
            ACTIVE.get().response(SimpleNamespace(status_code=401,read=lambda:b'{"error":"Unauthorized"}'))
            raise AuthenticationError('Do not log raw provider errors')
        result=self.result(self.run_batch([self.task(),self.task()],reject))
        self.assertEqual(len(self.calls),1);self.assertEqual(result['not_run'],[1]);self.assertEqual(result['status'],'STOPPED')
        with self.state.transaction() as db:row=db.execute('SELECT status FROM state_usage').fetchone()
        self.assertEqual(row[0],'UNCERTAIN')
        self.assertEqual(result['results'][0]['error']['error_type'],'AuthenticationError')
    def test_invalid_batch_hash_or_scope_rejected_before_model(self):
        raw=json.dumps([self.task()]).encode()
        with self.assertRaisesRegex(ValueError,'INPUT_HASH_DIFFERS'):tasks_from_bytes(raw,'a'*64)
        with self.assertRaisesRegex(ValueError,'TASK_BOUND'):self.run_batch([self.task()]*5)
        bad=self.task();bad['code']='altered'
        with self.assertRaisesRegex(ValueError,'HASH_DIFFERS'):self.run_batch([bad])
        self.assertEqual(self.calls,[])
    def test_first_rejection_is_not_retried_or_repaired(self):
        def invalid(request,schema,options):
            result,meta=self.producer(request,schema,options);result['edges'][0]['quote']='wrong'
            return result,meta
        result=self.result(self.run_batch([self.task(),self.task()],invalid))
        self.assertEqual(len(self.calls),1);self.assertEqual(result['status'],'STOPPED');self.assertEqual(result['not_run'],[1])
    def test_settlement_failure_keeps_original_error_and_stops(self):
        def invalid(request,schema,options):
            self.producer(request,schema,options)
            raise ValueError('original rejection')
        with patch.object(self.gov,'settle',side_effect=RuntimeError('settlement unavailable')):
            result=self.result(self.run_batch([self.task(),self.task()],invalid))
        self.assertEqual(result['results'][0]['error']['error_type'],'ValueError')
        self.assertEqual(result['settlement_errors'][0]['error']['error_type'],'RuntimeError')
        self.assertEqual(result['not_run'],[1]);self.assertEqual(len(self.calls),1)
    def test_explicit_capture_work_directory_ignores_unwritable_default_root(self):
        from investigator import planner_recording
        default=planner_recording.ROOT/'.local'/'planner-recordings'
        original=Path.mkdir;attempts=[]
        def guarded(path,*args,**kwargs):
            if path==default or default in path.parents:
                attempts.append(path);raise PermissionError(13,'Permission denied',str(path))
            return original(path,*args,**kwargs)
        with patch.object(Path,'mkdir',guarded):
            summary=self.run_batch()
        self.assertEqual(summary['status'],'COMPLETED');self.assertEqual(attempts,[])
        self.assertEqual(len(list((self.root/'b'/'planner-recordings').glob('*/request.body'))),1)
        self.assertTrue(self.result(summary)['captures'][0]['complete'])
    def test_capture_permission_failure_has_safe_stage_and_errno(self):
        original=Path.mkdir
        def guarded(path,*args,**kwargs):
            if path.parent.name=='planner-recordings':raise PermissionError(13,'Permission denied',str(path))
            return original(path,*args,**kwargs)
        with patch.object(Path,'mkdir',guarded):result=self.result(self.run_batch())
        error=result['results'][0]['error']
        self.assertEqual(error['stage'],'CAPTURE_INITIALIZATION');self.assertEqual(error['errno'],13)
        self.assertIn('denied',error['message'].lower());self.assertEqual(self.calls,[])


if __name__=='__main__':unittest.main()
