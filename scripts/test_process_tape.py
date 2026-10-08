import json
import subprocess
import tempfile
import unittest
import copy
import sys
from pathlib import Path
from unittest.mock import patch
from investigator.process_tape import Tape,TapeError,active,event,uuid4,clock,bytes_of
from investigator.tape_worker import run
from investigator.process_tape import bounded_call


def bootstrap():
    return {'entry_point':'synthetic','context_identity':'retained-context',
            'config':{},'profile':{},'usage_policy':{},'engine_hash':'synthetic-engine','state':{}}


class TapeTests(unittest.TestCase):
    def test_worker_admission_never_rewrites_prior_envelope(self):
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'tape.json',bootstrap())
            before=tape.path.read_bytes()
            with patch.object(tape,'flush',wraps=tape.flush) as flush:
                tape.event('WORKER_START',bytes_of({'command':['offline-worker'],'mode':'STREAM'}))
                for n in range(100):tape.event('BUDGET_INPUT',bytes_of({'large_retained_history':'x'*10000,'n':n}))
                tape.event('WORKER_SEND',b'ALLOW\n')
                tape.event('WORKER_END',bytes_of({'returncode':0}))
                flush.assert_not_called()
            self.assertEqual(tape.path.read_bytes(),before)
            self.assertEqual(len(tape.journal_path.read_bytes().splitlines()),104)
            tape.finish({'status':'COMPLETED'})
            replay=Tape(tape.path)
            self.assertEqual(replay.events,tape.events)

    def test_new_code_reader_requires_committed_producer_legacy_v3_is_unchanged(self):
        from investigator import process_tape as journal
        with tempfile.TemporaryDirectory() as folder:
            b=bootstrap();b['entry_point']='code_reader'
            old=Path(folder)/'old.json'
            with patch.object(journal,'VERSION','bounded-worker-tape-v3'):
                recorded=Tape(old,b);recorded.finish({})
            original=old.read_bytes();replay=Tape(old);replay.finish({})
            self.assertEqual(old.read_bytes(),original);self.assertIsNone(replay.engine_revision)
            with patch('subprocess.check_output',return_value=' M scripts/investigator/reader.py'):
                with self.assertRaisesRegex(TapeError,'UNCOMMITTED_ENGINE'):Tape(Path(folder)/'dirty.json',b)
            with patch('subprocess.check_output',side_effect=['','a'*40]):
                current=Tape(Path(folder)/'new.json',b);current.finish({})
            replay=Tape(current.path);self.assertEqual(replay.engine_revision,'a'*40);replay.finish({})
    def test_v1_tape_replays_after_recorder_moves_to_v2(self):
        from investigator import process_tape as journal
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tape.json'
            with patch.object(journal, 'VERSION', 'bounded-worker-tape-v1'):
                recorded = Tape(path, bootstrap())
                recorded.event('BOUNDED_REQUEST', bytes_of({'request': 1}))
                recorded.event('BOUNDED_RESPONSE', bytes_of({'value': 2}))
                recorded.finish({})
            original = path.read_bytes()
            self.assertEqual(journal.VERSION, 'bounded-worker-tape-v4')
            replayed = Tape(path)
            self.assertEqual(replayed.version, 'bounded-worker-tape-v1')
            replayed.event('BOUNDED_REQUEST', bytes_of({'request': 1}))
            self.assertEqual(json.loads(replayed.take('BOUNDED_RESPONSE')), {'value': 2})
            replayed.finish({})
            self.assertEqual(path.read_bytes(), original)

    def test_v2_recording_replays_unchanged_under_v3(self):
        from investigator import process_tape as journal
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json'
            with patch.object(journal,'VERSION','bounded-worker-tape-v2'):
                recorded=Tape(path,bootstrap())
                recorded.event('BUDGET',b'{"decision":"ADMITTED","count":1}')
                recorded.finish({})
            original=path.read_bytes()
            replayed=Tape(path)
            replayed.event('BUDGET',b'{ "count":1, "decision":"ADMITTED" }')
            replayed.finish({})
            self.assertEqual(replayed.version,'bounded-worker-tape-v2')
            self.assertEqual(path.read_bytes(),original)

    def test_clock_events_persist_once_without_rewriting_prior_bodies(self):
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'tape.json',bootstrap())
            envelope=tape.path.read_bytes()
            with patch.object(tape,'flush',wraps=tape.flush) as flush:
                with active(tape):
                    for _ in range(2000):clock('synthetic',lambda:1000)
                flush.assert_not_called()
            self.assertEqual(tape.path.read_bytes(),envelope)
            self.assertEqual(len(tape.journal_path.read_bytes().splitlines()),2001)
            with self.assertRaisesRegex(TapeError,'JOURNAL_DIFFERS'):Tape(tape.path)
            tape.finish({})
            replayed=Tape(tape.path)
            with active(replayed):
                for _ in range(2000):clock('synthetic',lambda:self.fail('No current clock'))
                replayed.finish({})
            journal=tape.journal_path.read_bytes()
            tape.journal_path.write_bytes(journal.split(b'\n',1)[1])
            with self.assertRaisesRegex(TapeError,'JOURNAL_DIFFERS'):Tape(tape.path)

    def test_budget_input_decoder_rejects_hostile_owned_rows_and_unknown_tables(self):
        from investigator.tape_budget import validate_input,TABLES
        schemas={table:['environment','session_id'] for table in TABLES}
        body={'environment':'synthetic','owned_sessions':['own'],
            'tables':{table:{'columns':columns,'rows':[]} for table,columns in schemas.items()}}
        validate_input(body,'synthetic',{'own'},schemas)
        for change in ('owned','unknown','columns','environment'):
            bad=copy.deepcopy(body)
            if change=='owned':bad['tables']['adaptive_usage']['rows']=[['synthetic','own']]
            elif change=='unknown':bad['tables']['unknown']={}
            elif change=='columns':bad['tables']['adaptive_usage']['columns']=['other']
            else:bad['environment']='other'
            with self.subTest(change=change),self.assertRaises(TapeError):validate_input(bad,'synthetic',{'own'},schemas)

    def test_unrecorded_external_budget_change_is_not_a_complete_tape(self):
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'tape.json',bootstrap())
            for phase,rows in [('BEFORE',0),('AFTER',1),('BEFORE',2),('AFTER',2)]:
                tape.event('BUDGET',bytes_of({'phase':phase,'state':{'usage_rows':rows}}))
            with self.assertRaisesRegex(TapeError,'UNRECORDED_BUDGET_INPUT'):tape.finish({})

    def test_external_budget_inputs_replay_without_repeating_other_work_or_replacing_own_decisions(self):
        import sqlite3
        from contextlib import closing
        import test_flexible_investigation as fixture
        from investigator.usage_governance import UsageGovernor
        h=fixture.DynamicTests();h.setUp();self.addCleanup(h.doCleanups)
        policy={'environment':h.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':50,
            'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
        gov=UsageGovernor(h.runtime,policy,lambda:1000)
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);initial=folder/'initial.sqlite'
            with h.runtime.db() as db,closing(sqlite3.connect(initial)) as saved:db.backup(saved)
            def restore():
                with closing(sqlite3.connect(initial)) as saved,h.runtime.db() as db:saved.backup(db)
            def concurrent():
                with active(None):gov.metered_read('other-session','request',lambda:'other physical request')
                return 'own result'
            tape=Tape(folder/'tape.json',bootstrap())
            with active(tape):
                result=gov.metered_read('owned-session','request',concurrent)
                expected={'result':result,'charged':gov.snapshot()['read_allowance']['ordinary_charged']}
                tape.finish(expected)
            self.assertEqual(expected['charged'],2)
            restore();replayed=Tape(tape.path)
            with active(replayed):
                result=gov.metered_read('owned-session','request',lambda:'own result')
                actual={'result':result,'charged':gov.snapshot()['read_allowance']['ordinary_charged']}
                replayed.finish(actual)
            self.assertEqual(actual,expected)
            restore();replayed=Tape(tape.path)
            def corrupt_own():
                with h.runtime.db() as db:
                    db.execute("UPDATE adaptive_usage SET actual=? WHERE session_id='owned-session'",('{"wrong":true}',))
                return 'own result'
            with active(replayed),self.assertRaises(TapeError):
                gov.metered_read('owned-session','request',corrupt_own)

    def test_real_process_runtime_records_and_replays_its_two_outputs(self):
        self.exercise_process()

    def test_failed_composition_keeps_completed_outputs_and_recorded_retry_in_replay(self):
        self.exercise_process(failed_composition=True)

    def test_explicit_acceptance_context_pin_is_recorded_and_replayed(self):
        self.exercise_process(pinned_context=True)

    def test_fixture_state_and_selected_context_are_recorded_validated_and_replayed(self):
        self.exercise_process(pinned_context=True,fixture_state=True)

    def exercise_process(self,failed_composition=False,pinned_context=False,fixture_state=False):
        import test_flexible_investigation as fixture
        from investigator.runtime import Runtime
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.process_debugging import VERSION
        from investigator import synthesis_narrative as narrative
        from investigator.workspace import Workspace
        from investigator.question_intake import azure_resolve
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        if pinned_context:
            from investigator.onboarding import digest
            model=helper.store.get(helper.envelope['model_id'])
            helper.store.context_pins={model['id']:{'context_id':model['context_id'],'hash':digest(model['context'])}}
            if fixture_state:
                helper.store.acceptance_fixture_state={'name':'baseline','definition_hash':'a'*64,
                    'context':helper.store.context_pins[model['id']],'approval_reference':'synthetic explicit setup decision'}
        policy={'environment':helper.store.environment,'daily_limits':{'planner_calls':50,
            'cloud_calls':50,'input_characters':1000000,'output_tokens':100000},
            'max_inflight_planners':1,'no_progress_limit':3}
        native=lambda request:bounded_call('synthetic-native',request,lambda:helper.runtime.native_transport(request))
        runtime=Runtime(helper.store,helper.config,native,helper.runtime.source_transport)
        agent=AdaptiveRuntime(runtime,lambda _:self.fail('No open planner'),usage_policy=policy,
            planner_profile={'adapter':'injected','deployment':'synthetic'})
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        envelope['comparison_mode']='VERTICAL';envelope['ticket_shape']='MISMATCH_COMPLAINT'
        workspace=Workspace(agent,execution_enabled=True,question_resolver=azure_resolve)
        import httpx
        def provider(request):
            body=json.loads(request.content);view=json.loads(body['input'])
            if body['tool_choice']['name']=='extract_ticket_spans':
                from investigator.intake_extraction import SCHEMA
                value={key:[] for key in SCHEMA['properties']}
                value.update(kind='SOURCE_CORRECTNESS',reported_state='UNSPECIFIED',
                    primary=view['ticket'],measures=[{'quote':'Total','role':'PRIMARY'}])
            elif body['tool_choice']['name']=='resolve_business_question':
                metric=next(m for m in view['models'][0]['measures'] if m['name']=='Total')
                value={'value_mentions':[],'question_kind':{'kind':'SOURCE_CORRECTNESS','source':{'quote':view['text']}},
                    'report_quote':None,'visual_request':None,'target_request':None,'reported_candidates':[],
                    'action':'PROPOSE','model_id':view['models'][0]['id'],'measure_id':metric['id'],
                    'metric_quote':'Total','question':None,'triage':'MISMATCH_COMPLAINT:VERTICAL',
                    'filters':[],'dimension_ids':[]}
            else:
                value={'technical_output':{'text':'The quantity can.' if failed_composition else narrative.path_narrative.summary(view),
                    'evidence_ids':[view['evidence'][0]['id']]}}
            return httpx.Response(200,json={'id':'synthetic-response','object':'response',
                'model':'synthetic','created_at':1,'status':'completed','usage':None,
                'output':[{'type':'function_call','name':body['tool_choice']['name'],
                           'call_id':'synthetic-call','arguments':json.dumps(value)}]})
        with (patch.dict('os.environ',{'INVESTIGATOR_RECORD_RUNS':'1'}),
                patch('investigator.run_recording.ROOT',helper.fixture.root),
                patch.dict('os.environ',{'AZURE_OPENAI_ENDPOINT':'https://synthetic.openai.azure.com',
                    'AZURE_OPENAI_DEPLOYMENT':'synthetic','AZURE_OPENAI_API_KEY':'synthetic-key-for-test'}),
                patch('httpx.HTTPTransport',return_value=httpx.MockTransport(provider))):
            intake=workspace.intake.resolve({'text':'Does Total reflect source entries?',
                'request_key':'synthetic-process-ticket','parent_id':None})
            self.assertEqual(intake['status'],'PROPOSED',intake)
            scope=intake['proposal']
            preview=workspace.preview({**{k:scope[k] for k in ('model_id','measure_id','filters','dimension_ids')},
                'symptom':intake['text'],'predecessor':None,'intake_id':intake['id']})
            created=agent.create(preview['envelope'],'synthetic-process')
            agent.run(created['id']);result=agent.synthesize(created['id'])
        self.assertEqual(result['synthesis']['status'],'COMPLETED')
        if failed_composition:
            self.assertEqual(result['synthesis']['calls'],2)
            self.assertEqual(len(result['synthesis']['attempts']),2)
            self.assertEqual(result['synthesis']['validation'],'ORIGINAL_EVIDENCE_WITHOUT_MODEL_MECHANISM')
            for key in ('business_output','technical_output'):
                self.assertIn('Mechanism not stated',result['synthesis']['outputs'][key]['explanation']['text'])
                self.assertNotIn('The quantity can.',result['synthesis']['outputs'][key]['explanation']['text'])
        tape=agent._run_tapes[created['id']]
        if pinned_context:self.assertEqual(tape.bootstrap['state']['context_pins'],helper.store.context_pins)
        if fixture_state:self.assertEqual(tape.bootstrap['state']['fixture_state'],helper.store.acceptance_fixture_state)
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        from acceptance.unknown_domain.process_replay import replay
        with tempfile.TemporaryDirectory() as output:
            actual=replay(tape.path,Path(output)/'replay',native_transport=lambda request:
                bounded_call('synthetic-native',request,lambda:self.fail('No live transport in replay')))
        self.assertTrue(actual['matched'])
        self.assertEqual(actual['operations'],['intake','preview','create','run','synthesize'])
        self.assertEqual(actual['outputs'],result['synthesis'].get('outputs'))
        self.assertEqual(actual['session'],result)
        self.assertEqual(actual['outcome'],result['assessment']['classification'])
        with tempfile.TemporaryDirectory() as output,patch('acceptance.unknown_domain.process_replay.fingerprint',return_value='changed-engine'):
            with self.assertRaisesRegex(TapeError,'ENGINE_VERSION_MISMATCH'):
                replay(tape.path,Path(output)/'strict')
            actual=replay(tape.path,Path(output)/'current-code',allow_engine_drift=True,
                native_transport=lambda request:bounded_call('synthetic-native',request,lambda:self.fail('No live transport')))
        self.assertTrue(actual['matched'])
        self.assertEqual(actual['replay_engine_hash'],'changed-engine')
        self.assertEqual(actual['recorded_engine_hash'],result['engine_hash'])
        self.assertEqual(actual['outputs'],result['synthesis'].get('outputs'))

    def test_synthetic_worker_run_replays_decisions_and_both_outputs_without_network(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json'
            worker=lambda *a,**k:subprocess.CompletedProcess(a[0],0,'{"value":7}\n','')
            def procedure():
                event('OPERATION_START',{'name':'synthetic'})
                identity=str(uuid4());started=clock('run')
                event('CONFIGURATION',{'context':'retained-context','value':{}})
                event('BUDGET',{'admitted':True,'physical_requests':1})
                response=run(['python','read_worker.py'],input='{"query":"quantity"}',
                             timeout=10,text=True,fallback=worker)
                value=json.loads(response.stdout)['value']
                outputs={'business':f'The number is {value}.','technical':f'{identity}: quantity {value}; clock {started}.'}
                event('OPERATION_END',{'name':'synthetic'})
                return outputs
            tape=Tape(path,bootstrap())
            with active(tape):
                expected=procedure();tape.finish(expected)
            replay=Tape(path)
            with (active(replay),patch('socket.create_connection',side_effect=AssertionError('NETWORK')),
                    patch('socket.socket.connect',side_effect=AssertionError('NETWORK'))):
                actual=procedure();replay.finish(actual)
            self.assertEqual(bytes_of(actual),bytes_of(expected))

    def test_changed_request_bytes_refused_not_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            with active(tape):
                event('CONFIGURATION',{'scope':'one'});tape.finish({})
            replay=Tape(path)
            with active(replay),self.assertRaisesRegex(TapeError,'REQUEST_BYTES_DIFFER'):
                event('CONFIGURATION',{'scope':'two'})

    def test_started_worker_without_terminal_response_fails_completeness(self):
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'tape.json',bootstrap())
            tape.event('WORKER_START',bytes_of({'mode':'BOUNDED'}))
            with self.assertRaisesRegex(TapeError,'UNFINISHED_ATTEMPT'):tape.finish({})

    def test_secret_exclusion_does_not_capture_secret_or_validate_as_complete(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            with patch.dict('os.environ',{'PRIVATE_API_KEY':'synthetic-secret-long'}):
                tape.event('WORKER_READ',b'synthetic-secret-long')
            with self.assertRaisesRegex(TapeError,'EXCLUDED_BODY'):tape.finish({})
            self.assertNotIn(b'synthetic-secret-long',path.read_bytes())

    def test_bootstrap_with_unpinned_context_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            body=bootstrap();body['context_identity']=None
            tape=Tape(Path(folder)/'tape.json',body)
            with self.assertRaisesRegex(TapeError,'BOOTSTRAP_IDENTITY'):tape.finish({})

    def test_unknown_event_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'tape.json',bootstrap())
            with self.assertRaises(TapeError):tape.event('UNKNOWN',b'{}')

    def test_response_without_started_worker_is_not_a_complete_tape(self):
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'tape.json',bootstrap())
            tape.event('WORKER_READ',b'{}')
            with self.assertRaisesRegex(TapeError,'WITHOUT_REQUEST'):tape.finish({})

    def test_changed_final_output_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            tape.finish({'business':'Original.'})
            replay=Tape(path)
            with self.assertRaisesRegex(TapeError,'REQUEST_BYTES_DIFFER'):
                replay.finish({'business':'Replacement.'})

    def test_unknown_bootstrap_state_and_missing_completed_outputs_refused(self):
        body=bootstrap();body['entry_point']='workspace'
        body['state']={'environment':'synthetic','workspace_owner':None,
            'artifacts':{'catalog.sqlite':'0'*64,'inventory.sqlite':'1'*64},
            'dynamic_read_limit':12,'dynamic_input_limit':10000}
        for extra,reason in (({'unknown':True},'STATE_FIELDS'),({},'COMPLETED_OUTPUTS_MISSING')):
            with self.subTest(extra=extra),tempfile.TemporaryDirectory() as folder:
                changed=copy.deepcopy(body);changed['state'].update(extra)
                tape=Tape(Path(folder)/'tape.json',changed)
                with self.assertRaisesRegex(TapeError,reason):
                    tape.finish({'operation':'synthesize','error':None,'status':'COMPLETED','outputs':None,'result':{}})

    def test_fixture_binding_refuses_context_that_was_not_selected(self):
        body=bootstrap();body['entry_point']='workspace'
        pin={'context_id':'00000000-0000-4000-8000-000000000001','hash':'a'*64}
        body['state']={'environment':'synthetic','workspace_owner':None,
            'artifacts':{'catalog.sqlite':'0'*64,'inventory.sqlite':'1'*64},
            'dynamic_read_limit':12,'dynamic_input_limit':10000,'context_pins':{'model':pin},
            'fixture_state':{'name':'baseline','definition_hash':'b'*64,'context':{**pin,'hash':'c'*64},'approval_reference':'decision'}}
        with tempfile.TemporaryDirectory() as folder:
            tape=Tape(Path(folder)/'tape.json',body)
            with self.assertRaisesRegex(TapeError,'TAPE_FIXTURE_CONTEXT_DIFFERS'):
                tape.finish({'operation':'run','error':None,'status':'HELD','outputs':None,'result':{}})

    def test_real_metered_protocol_records_every_request_and_replays_without_worker(self):
        from investigator.physical_reads import run as physical_run,scope,guard_scope
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);child=folder/'worker.py';path=folder/'tape.json'
            child.write_text('''import json,sys
json.loads(sys.stdin.readline())
for kind in ['sql_database_permissions','sql_quantity']:
 print(json.dumps({'physical_read':'REQUEST','kind':kind,'cache_guard':kind!='sql_quantity','object':''}),flush=True)
 answer=sys.stdin.readline().strip()
 if answer=='REUSE':continue
 assert answer=='ALLOW'
 print(json.dumps({'physical_read':'DONE','kind':kind,'status':'AVAILABLE','guard_passed':True}),flush=True)
print(json.dumps({'status':'AVAILABLE','quantity':7}),flush=True)
''',encoding='utf8')
            def procedure():
                receipts=[];meters=[];results=[]
                with guard_scope(receipts.append):
                    for _ in range(2):
                        with scope(lambda kind,call:(meters.append(kind),call())[1]):
                            results.append(physical_run([sys.executable,str(child)],input='{"server":"host","database":"db"}',timeout=5).stdout)
                return {'guards':receipts,'meters':meters,'results':results}
            tape=Tape(path,bootstrap())
            with active(tape):expected=procedure();tape.finish(expected)
            # The initial physical slot is admitted by the caller, subsequent
            # slots by the meter. On reuse the quantity uses that initial slot.
            self.assertEqual(expected['meters'],['sql_quantity'])
            self.assertEqual([r['status'] for r in expected['guards']],['ESTABLISHED','REUSED'])
            child.unlink()
            replay=Tape(path)
            with active(replay),patch('subprocess.Popen',side_effect=AssertionError('No child during replay')):
                actual=procedure();replay.finish(actual)
            self.assertEqual(actual,expected)

    def test_recording_does_not_reduce_directory_coverage_or_change_payload(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.adaptive_candidates import catalog
        h=fixture.DynamicTests();h.setUp();self.addCleanup(h.doCleanups)
        agent=AdaptiveRuntime(h.runtime,lambda _:None)
        state=agent.get(agent.create(h.envelope,'tape-context')['id'])
        choices,_=catalog(h.store,h.config,h.envelope)
        before=agent.payload(state,choices)
        with tempfile.TemporaryDirectory() as folder,active(Tape(Path(folder)/'tape.json',bootstrap())):
            after=agent.payload(state,choices)
        self.assertEqual(bytes_of(before),bytes_of(after))
        directory=before['context_entry_points']
        counts={'entries':len(directory),'sql_entries':sum(a['kind']=='SqlObject' for a in directory),
                'payload_characters':len(bytes_of(before).decode())}
        self.assertGreater(counts['entries'],0);self.assertGreater(counts['sql_entries'],0)
        print('TAPE_CONTEXT_COVERAGE '+json.dumps({'before':counts,'after':counts}))

    def test_connection_retry_receipt_times_replay_without_sleeping(self):
        from sql_connect_retry import read_with_retry
        from unittest.mock import Mock
        failure={'error':'SQL_READ_FAILED','stage':'connect','sql_error_number':40613}
        replies=[failure,{'quantity':7}]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            with active(tape):
                expected=read_with_retry(Mock(side_effect=replies),Mock());tape.finish(expected)
            replay=Tape(path)
            with active(replay):
                actual=read_with_retry(Mock(side_effect=replies),lambda _:self.fail('No live sleep in replay'))
                replay.finish(actual)
            self.assertEqual(actual,expected)

    def test_engine_identity_producers_must_use_the_recordable_source(self):
        import ast
        root=Path(__file__).resolve().parent/'investigator'
        # Private tape-directory/call IDs and the guarded opaque-connection
        # producer do not create engine result identities. Their boundaries
        # are explicit; all other producers must use the common source.
        private={'process_tape.py','run_recording.py','planner_recording.py','physical_reads.py'}
        for path in root.rglob('*.py'):
            if path.name in private:continue
            tree=ast.parse(path.read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom) and node.module=='uuid':
                    self.assertNotIn('uuid4',[a.name for a in node.names],str(path))
                if isinstance(node,ast.Attribute) and node.attr=='uuid4':
                    self.fail('Unrecorded identity namespace call: '+str(path))

    def test_report_selection_identity_replays_from_inventory_without_a_probe(self):
        from test_report_scoped_cells import ScopedTests
        helper=ScopedTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.modify(helper.visual,lambda d:d.pop('filterConfig'))
        helper.modify(helper.slicer,lambda d:d['visual']['objects'].pop('general'))
        helper.request();helper.native()
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            with active(tape):expected=helper.prepare();tape.finish(expected)
            helper.scope.pop('selection_resolution',None)
            helper.scope.pop('selection_resolution_evidence_id',None)
            helper.scope['filters']=[]
            replay=Tape(path)
            with active(replay):actual=helper.prepare();replay.finish(actual)
            self.assertEqual(actual,expected)

    def test_final_cannot_introduce_unrecorded_identity(self):
        import sqlite3
        from contextlib import closing
        from investigator.process_tape import sha
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);body=bootstrap();body['entry_point']='workspace'
            hashes={}
            for name in ('catalog.sqlite','inventory.sqlite'):
                with closing(sqlite3.connect(folder/name)) as db:db.execute('CREATE TABLE inputs(value TEXT)');db.commit()
                hashes[name]=sha((folder/name).read_bytes())
            body['state']={'environment':'synthetic','workspace_owner':None,'artifacts':hashes,
                          'dynamic_read_limit':12,'dynamic_input_limit':10000}
            tape=Tape(folder/'tape.json',body)
            unrecorded=str(uuid4())
            with self.assertRaisesRegex(TapeError,'UNRECORDED_IDENTITY'):
                tape.finish({'operation':'run','error':None,'status':'HELD','outputs':None,
                             'result':{'selection_resolution_evidence_id':'selection-'+unrecorded}})


if __name__=='__main__':unittest.main()
