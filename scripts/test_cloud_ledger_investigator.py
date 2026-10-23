import contextlib
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import cloud_investigator as worker


class Assembly(unittest.TestCase):
    def test_retained_view_is_explicit_and_preserves_mandatory_labels(self):
        current=object();process=object();context={'version':'approved'};pin={'context_id':'approved'}
        self.assertEqual(worker.retained_view(current,process,{},context=context,visual='visual',measure_id='measure'),(current,[]))
        view=SimpleNamespace(warning_labels=['Retained approved context; not current or value-verified.','Current graph unavailable.'])
        with patch('investigator.adapters.retained_graph_continuation.RetainedApprovedContinuation',return_value=view)as build:
            actual,labels=worker.retained_view(current,process,{'retained_continuation':pin},context=context,visual='visual',measure_id='measure')
        self.assertIs(actual,view);self.assertEqual(labels,view.warning_labels);self.assertIsNot(labels,view.warning_labels)
        build.assert_called_once_with(current,process,context=context,pin=pin,visual='visual',measure_id='measure')
    def test_unavailable_owner_becomes_explicit_no_read_port_not_a_lost_run(self):
        retained=[]
        path={'unavailable_owners':{'report':{'reason':'MetadataUnavailable'}},'stops':[{'node':'visual','reason':'Owner definition refresh unavailable'}]}
        with patch('investigator.adapters.ledger_investigator_ports.ProcessValues',side_effect=ValueError('EXACT_MEASURE_GRAPH_BINDING_REQUIRED')):
            reader,checks=worker.compiled_values(None,path,visual='visual',measure_id='measure',retain=retained.append)
        self.assertIsNone(checks)
        with self.assertRaisesRegex(ValueError,'CURRENT_GRAPH_DEFINITION_OWNER_UNAVAILABLE'):reader('visual',None,{})
        self.assertEqual(retained[0]['native_value_queries'],0)

    def test_wrong_measure_without_owner_unavailability_still_refuses(self):
        with patch('investigator.adapters.ledger_investigator_ports.ProcessValues',side_effect=ValueError('EXACT_MEASURE_GRAPH_BINDING_REQUIRED')):
            with self.assertRaisesRegex(ValueError,'EXACT_MEASURE_GRAPH_BINDING_REQUIRED'):
                worker.compiled_values(None,{},visual='visual',measure_id='wrong',retain=lambda value:None)

    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def ref(self,name,value):
        path=self.root/name;path.write_text(json.dumps(value));return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    def specification(self,**updates):
        value={'ticket':self.ref('ticket.json',{'text':'Did the last Copy Job run fail?',
            'request':{'kind':'FACT','subject':'job','question':'RUN_STATUS'}}),
            'graph':{'estate':'fixture','identity':'reader','allowed_objects':['job']},
            'budget':{'environment':'development'},'max_requests':12,'model_enabled':False,
            'generation_options':{},'step_cap':3,'wall_seconds':60,'warnings':[],'recording_mode':'TEST'}
        value.update(updates);return {'spec':self.ref('spec.json',value)}
    def test_spec_requires_exact_hashed_scope_no_query_or_dynamic_handler(self):
        options=self.specification()
        self.assertEqual(worker.specification(options)['graph']['allowed_objects'],['job'])
        options['execute']='arbitrary'
        with self.assertRaisesRegex(ValueError,'RUNNER_OPTIONS'):worker.specification(options)
        ref=self.ref('tampered.json',{});Path(ref['path']).write_text('changed')
        with self.assertRaisesRegex(ValueError,'HASH_DIFFERS'):worker.reference(ref)
    def test_fact_assembly_needs_no_native_or_model_and_settles_meter(self):
        options=self.specification();events=[]
        context=SimpleNamespace(root=self.root,record=lambda name,value:events.append((name,value)) or {'key':str(len(events))})
        meter=SimpleNamespace(used=0,before={'physical':0},usage=SimpleNamespace(snapshot=lambda:{'physical':0}),close=lambda:events.append(('closed',{})))
        state=SimpleNamespace(backend='postgresql')
        model={'credential':{'mode':'key_vault'},'endpoint':'https://mock.openai.azure.com','deployment':'test'}
        manifest={'environment':'development','model':model}
        fakefiles=SimpleNamespace(capture=lambda path:{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
        with contextlib.ExitStack() as stack:
            for target,value in [
                ('investigator.shared_state.configured_state',state),('investigator.estate_manifest.load',manifest),
                ('investigator.adapters.estate_installation.configuration',{'_estate':{'operating_mode':'BUILD_PHASE'}}),
                ('investigator.estate_graph_repository.GraphRepository',object()),('investigator.estate_graph_api.GraphAPI',object()),
                ('investigator.live_gateway.current',object()),('cloud_graph_interpreter.runtime_governor',SimpleNamespace(policy={})),
                ('scan_estate_graph.Meter',meter),('investigator.runtime.fingerprint','a'*64),
                ('investigator.source_revision.committed_revision','b'*40),('investigator.slim_recording.validate',{}),
                ('investigator.slim_recording.stores',(None,fakefiles))]:
                stack.enter_context(patch(target,return_value=value))
            native=stack.enter_context(patch('investigator.adapters.ledger_investigator_ports.installed_process'))
            decision=stack.enter_context(patch('investigator.adapters.ledger_investigator_ports.AzureDecision'))
            def run(plan,ctx,**ports):
                self.assertIsNone(ports['value_reader']);self.assertIsNone(ports['decide'])
                return {'verdict':'failed job'}
            stack.enter_context(patch('cloud_investigator.run',run))
            setting=self.root/'slim.json';setting.write_text('{}')
            stack.enter_context(patch.dict(os.environ,{'DIA_SLIM_RECORDING_CONFIG':str(setting)}))
            result=worker.execute({'options':options,'manifest':'unused'},context)
            self.assertEqual(result['physical_requests'],0);self.assertEqual(result['model_calls'],0)
            native.assert_not_called();decision.assert_not_called()
        self.assertEqual(events[-1][0],'closed')
        self.assertTrue(any(name=='investigator-tape' for name,_ in events))
    def test_compare_without_native_inputs_refuses_before_shared_io(self):
        options=self.specification(ticket=self.ref('compare.json',{'visual':'visual','request':{'kind':'COMPARE'}}))
        with patch('investigator.shared_state.configured_state') as state:
            with self.assertRaisesRegex(ValueError,'NATIVE_INPUT_REQUIRED'):
                worker.execute({'options':options},SimpleNamespace(root=self.root))
            state.assert_not_called()
    def test_real_ticket_mode_defaults_to_normal_and_rejects_unknown_label(self):
        options=self.specification();path=Path(options['spec']['path']);value=json.loads(path.read_bytes());value.pop('recording_mode')
        options={'spec':self.ref('normal-spec.json',value)}
        self.assertNotIn('recording_mode',worker.specification(options))
        value['recording_mode']='not-exact-but-call-it-replay'
        with self.assertRaisesRegex(ValueError,'RECORDING_MODE'):worker.specification({'spec':self.ref('invalid-mode.json',value)})
    def test_normal_status_assembly_has_no_native_tape_provider_or_catalog(self):
        options=self.specification(recording_mode='NORMAL',model_enabled=True);events=[]
        context=SimpleNamespace(root=self.root,record=lambda name,value:events.append((name,value))or {'key':str(len(events))})
        meter=SimpleNamespace(used=0,before={},usage=SimpleNamespace(snapshot=lambda:{}),close=lambda:None)
        manifest={'environment':'development','model':{'credential':{},'endpoint':'unused','deployment':'unused'}}
        with contextlib.ExitStack()as stack:
            for target,value in [('investigator.shared_state.configured_state',SimpleNamespace(backend='postgresql')),
                ('investigator.estate_manifest.load',manifest),('investigator.adapters.estate_installation.configuration',{}),
                ('investigator.estate_graph_repository.GraphRepository',object()),('investigator.estate_graph_api.GraphAPI',object()),
                ('investigator.live_gateway.current',object()),('cloud_graph_interpreter.runtime_governor',SimpleNamespace(policy={})),
                ('scan_estate_graph.Meter',meter),('investigator.runtime.fingerprint','a'*64),('investigator.source_revision.committed_revision','b'*40)]:
                stack.enter_context(patch(target,return_value=value))
            for target in ('investigator.process_tape.Tape','investigator.adapters.ledger_investigator_ports.AzureDecision','investigator.ticket_catalog.materialize','investigator.slim_recording.stores'):
                stack.enter_context(patch(target,side_effect=AssertionError('Not used by a normal ledger-only question')))
            stack.enter_context(patch('cloud_investigator.run',return_value={'verdict':'failed job','outputs':{'business':'failed job','technical':'retained ledger fact'}}))
            answer=worker.execute({'options':options,'manifest':'unused','run_id':'normal-status'},context)
        self.assertEqual(answer['recording'],{'mode':'NORMAL','byte_exact_replay':False})
        self.assertEqual(answer['model_calls'],0);self.assertFalse(any(k=='investigator-tape'for k,_ in events))
        self.assertTrue(any(k=='normal-audit-batch'for k,_ in events))
        self.assertEqual([v['stage']for k,v in events if k=='progress'],['ACKNOWLEDGED','ANSWER'])
    def test_normal_mode_cannot_bypass_existing_projected_installation_refusal(self):
        from investigator.privacy_projection import ProjectionError
        options=self.specification(recording_mode='NORMAL');events=[]
        context=SimpleNamespace(root=self.root,record=lambda k,v:events.append((k,v))or {'key':str(len(events))})
        with patch('investigator.estate_manifest.load',return_value={'recording':{'tape_class':'PRIVACY_PROJECTED'}}),patch('investigator.shared_state.configured_state',side_effect=AssertionError('No source/state call before privacy admission')):
            with self.assertRaisesRegex(ProjectionError,'PROJECTED_CAPTURE_NOT_INSTALLED'):
                worker.execute({'options':options,'manifest':'unused','run_id':'projected'},context)
        self.assertFalse(any(k in ('investigator-native','investigator-bundle')for k,_ in events))
    def test_graph_wrapper_records_then_replays_with_network_source_absent(self):
        from investigator.process_tape import Tape,active
        path=self.root/'graph-tape.json'
        bootstrap={'entry_point':'ledger_investigator','context_identity':'fixture','config':{},'profile':{},
                   'usage_policy':None,'engine_hash':'a'*64,'state':{}}
        source=SimpleNamespace(node_facts=lambda node,now:{'facts':[{'subject':node,'state':'OBSERVED'}]})
        with active(Tape(path,bootstrap=bootstrap)) as _:
            result=worker.JournalGraph(source).node_facts('job',now='2026-10-22T00:00:00Z')
            from investigator.process_tape import ACTIVE
            ACTIVE.get().finish(result)
        tape=Tape(path)
        with active(tape):
            replay=worker.JournalGraph(None).node_facts('job',now='2026-10-22T00:00:00Z');tape.finish(replay)
        self.assertEqual(result,replay)
    def test_expired_admission_finishes_not_found_without_read_or_model(self):
        from test_ledger_investigator import ToolLoopTests
        from investigator.usage_governance import UsageHold
        tools,engine,reader,events=ToolLoopTests().build()
        def expired(*args):raise UsageHold('INVESTIGATOR_RUN_DEADLINE')
        engine.admit=expired
        result=engine.run({'visual':'visual','text':'Why is this lower?'})
        self.assertEqual(result['verdict'],'not found')
        self.assertEqual(result['stop_reason'],'TICKET_BUDGET_REACHED')
        reader.assert_not_called()
    def test_top_up_only_requested_admitted_subjects_and_scan_category(self):
        from investigator.build_phase import purpose
        config={'estate':'fixture','subjects':{'job':{},'other':{}},'key_tables':['other']}
        def collect(config,**kwargs):
            self.assertEqual(set(config['subjects']),{'job'});self.assertEqual(config['key_tables'],[])
            self.assertEqual(purpose(),'SCAN');self.assertTrue(kwargs['force'])
            return {'collection':{'status':'COLLECTED'},'physical_requests':2}
        with patch('cloud_facts_collector.validate',side_effect=lambda value:value),patch('cloud_facts_collector.collect',collect):
            collector=worker.PathCollector(config,object(),['job'],lambda value:None)
            self.assertEqual(collector.run('fixture',['job'],now='2026-10-22T00:00:00Z',force=True)['purpose'],'SCAN')
            with self.assertRaisesRegex(ValueError,'OUTSIDE_PATH'):
                collector.run('fixture',['other'],now='2026-10-22T00:00:00Z')


if __name__=='__main__':unittest.main()
