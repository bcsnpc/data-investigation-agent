import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock,patch

from cloud_runner_context import prepare_for_verification,retain_dependencies
from investigator.artifact_store import Files,LocalObjects
from investigator.shared_state import SharedState,TRANSACTION_ACTIVE


class CurrentImagePreparationTests(unittest.TestCase):
    def test_current_image_preparation_uses_normal_cas_publication_without_long_lease(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);state=SharedState.offline(root/'state.sqlite');state.migrate()
            context=SimpleNamespace(root=root/'attempt',record=Mock(),step=lambda name,fn:fn());context.root.mkdir()
            def prepare(inputs,work):
                out=work/'verification';out.mkdir()
                for name in ('approval.json','context.json','model.json','publication-candidate.json'):
                    (out/name).write_text(json.dumps({'name':name,'engine_hash':'current-image'}))
                return {'status':'PREPARED'}
            def publish(s,candidate):
                self.assertIs(s,state);self.assertFalse(TRANSACTION_ACTIVE.get())
                self.assertEqual(candidate['engine_hash'],'current-image')
                return {'readiness':'NOT_EARNED_BY_PUBLICATION'}
            with patch('investigator.shared_state.configured_state',return_value=state), \
                 patch('cloud_stage_worker.prepare_phase',side_effect=prepare), \
                 patch('cloud_context_prepare.publish',side_effect=publish), \
                 patch('investigator.shared_writer_lease.acquire') as acquire:
                prepared=prepare_for_verification({'options':{'inputs':str(root/'inputs')}},context)
            acquire.assert_not_called()
            self.assertEqual(json.loads((prepared/'publication.json').read_bytes())['readiness'],'NOT_EARNED_BY_PUBLICATION')
            self.assertEqual(context.record.call_count,4)

    def test_verification_registry_prepares_and_retains_before_execute_and_never_demands_replay(self):
        from investigator.unified_runner import handlers
        with tempfile.TemporaryDirectory() as folder:
            context=SimpleNamespace(root=Path(folder),record=Mock(),step=lambda name,fn:fn())
            order=[]
            def retain(*args,**kwargs):order.append(('retain',kwargs['phase']))
            def execute(*args,**kwargs):
                self.assertEqual(order,[('prepare',None),('retain','BEFORE_READS')])
                kwargs['retain'](Path(folder)/'capture',phase='BEFORE_READS')
                kwargs['retain'](Path(folder)/'capture',phase='AFTER_EXECUTION')
                return {'status':'FAILED','error':{'message':'preserved live result'}}
            with patch('cloud_runner_context.prepare_for_verification',side_effect=lambda *_:(order.append(('prepare',None)) or Path(folder)/'prepared')), \
                 patch('cloud_runner_context.retain_dependencies',side_effect=retain), \
                 patch('cloud_verification_run.execute',side_effect=execute):
                result=handlers()['verification']({'manifest':'estate.json','run_id':'fresh','options':{'inputs':'inputs','spec':'spec.json','spec_sha256':'hash'}},context)
            self.assertEqual(result['status'],'FAILED')
            self.assertEqual(order[-1],('retain','AFTER_EXECUTION'))


class DependencyRetentionTests(unittest.TestCase):
    def test_partial_dependencies_survive_without_a_final_tape_and_restore_exactly(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);capture=root/'capture';capture.mkdir()
            (capture/'tape.events.jsonl').write_text('{"partial":true}\n')
            (capture/'context.json').write_text('{"fixture":"synthetic"}')
            files=Files(LocalObjects(root/'cas'));context=SimpleNamespace(record=Mock())
            value=retain_dependencies(capture,context,kind='verification',phase='BEFORE_READS',files=files)
            self.assertEqual(value['status'],'RETAINED');self.assertEqual(len(value['files']),2)
            for row in value['files']:
                target=root/'restored'/row['name'];files.restore(row['sha256'],target)
                self.assertEqual(target.read_bytes(),(capture/row['name']).read_bytes())
            self.assertEqual(context.record.call_args.args[0],'dependency-manifest')
    def test_unknown_files_are_refused_and_completed_members_remain_recorded_on_upload_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);capture=root/'capture';capture.mkdir()
            (capture/'credential-cache.json').write_text('{}')
            context=SimpleNamespace(record=Mock());files=Mock()
            with self.assertRaisesRegex(ValueError,'UNDECLARED_MEMBER'):
                retain_dependencies(capture,context,kind='verification',phase='partial',files=files)
            files.capture.assert_not_called()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'context.json').write_text('{}');(root/'model.json').write_text('{}')
            files=Mock();files.capture.side_effect=[{'sha256':'a'*64,'bytes':2},RuntimeError('upload stopped')]
            context=SimpleNamespace(record=Mock())
            with self.assertRaisesRegex(RuntimeError,'upload stopped'):
                retain_dependencies(root,context,kind='verification',phase='partial',files=files)
            self.assertEqual(context.record.call_args.args[0],'dependency-file')
            self.assertEqual(context.record.call_args.args[1]['name'],'context.json')


class DemoSnapshotTests(unittest.TestCase):
    def test_demo_uses_just_prepared_snapshot_and_preserves_source(self):
        import sqlite3
        from contextlib import closing
        from cloud_runner_context import install_private_snapshots
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);prepared=root/'prepared';prepared.mkdir()
            for name in ('catalog','inventory'):
                with closing(sqlite3.connect(prepared/(name+'.sqlite'))) as db:
                    db.execute('CREATE TABLE proof(revision INTEGER)');db.execute('INSERT INTO proof VALUES(85)');db.commit()
            manifest=root/'estate.json';manifest.write_text(json.dumps({'storage':{name:str(root/'private'/(name+'.sqlite')) for name in ('catalog','inventory')}}))
            paths=install_private_snapshots(manifest,prepared)
            with closing(sqlite3.connect(paths['catalog'])) as db:self.assertEqual(db.execute('SELECT revision FROM proof').fetchone(),(85,))
            with self.assertRaisesRegex(FileExistsError,'ALREADY_EXISTS'):install_private_snapshots(manifest,prepared)
    def test_failed_or_refused_verification_never_appears_demo_eligible(self):
        from cloud_runner_context import demo_after_verification
        context=SimpleNamespace(record=Mock(),step=Mock())
        for v in [{'status':'FAILED'},{'status':'COMPLETED','verification_status':'REFUSED'}]:
            result=demo_after_verification(v,{},context,'prepared')
            self.assertIsNone(result['demo']);self.assertEqual(result['status'],'VERIFICATION_STOPPED')
        context.step.assert_not_called()

    def test_real_workspace_shape_without_close_still_returns_delivered_demo(self):
        from contextlib import nullcontext
        from cloud_runner_context import demo_after_verification
        steps=[]
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        context=SimpleNamespace(root=Path(folder.name),record=Mock(),step=lambda name,fn:(steps.append(name),fn())[1])
        from investigator.onboarding import digest
        current={'id':'model','context_id':'context','context':{}}
        proof={'model_pin':{'model_id':'model'},'model_sha256':digest(current),'constraints':{'kind':'WHOLE_ENTITY_QUANTITY','measure_ids':['measure'],'filters':[],'dimension_ids':[]}}
        workspace=SimpleNamespace(forms=object(),store=SimpleNamespace(shared_catalog=object(),get=lambda _:current),agent=SimpleNamespace(governor=SimpleNamespace(shared=object())),preview=Mock())
        manifest={'model':{'credential':{'mode':'key_vault'},'endpoint':'https://model.example','deployment':'existing'}}
        plan={'run_id':'synthetic-demo','manifest':'estate.json','options':{'demo_ticket':'form.json','spec':'spec.json'}}
        verification={'status':'COMPLETED','verification_status':'VERIFIED'}
        with patch('cloud_verification_proof.reference',return_value={'prepared':'prepared'}), \
             patch('cloud_verification_proof.validate',return_value=proof), \
             patch('cloud_verification_proof.validate_form_scope',return_value={}), \
             patch('cloud_runner_context.install_private_snapshots',return_value={}), \
             patch('cloud_runner_context.read',return_value={'description':'same retained family A'}), \
             patch('investigator.estate_installation.build',return_value=(manifest,workspace)), \
             patch('run_adaptive_investigation.local_azure_key',return_value=nullcontext()), \
             patch('cloud_form_worker.run_form',return_value={'state':'COMPLETE','finding':'TRANSFORMATION_LOGIC'}):
            result=demo_after_verification(verification,plan,context,'prepared')
        self.assertEqual(result['status'],'DEMO_FINISHED')
        self.assertEqual(result['demo']['state'],'COMPLETE')
        self.assertIn('configured-demo',steps)


class DemoSubmissionBindingTests(unittest.TestCase):
    def test_execution_keys_are_fresh_between_runs_stable_within_run_and_input_is_unchanged(self):
        import copy,json
        from cloud_runner_context import bind_demo_submission
        form={'request_key':'original-preserved','description':'The Global card shows 8,765; compare with source.',
              'report_id':'report','page_id':'page','visual_id':'global-card','comparing':{'kind':'APPLICATION'},
              'value_seen':{'value':'8765','precision':{'kind':'EXACT'}},'filters':[{'name':'Region','values':['North']}]}
        before=copy.deepcopy(form)
        first,binding=bind_demo_submission(form,'run-one')
        repeated,repeated_binding=bind_demo_submission(form,'run-one')
        second,_=bind_demo_submission(form,'run-two')
        self.assertEqual(first,repeated);self.assertEqual(binding,repeated_binding)
        self.assertNotEqual(first['request_key'],second['request_key'])
        self.assertLessEqual(len(first['request_key']),100)
        self.assertEqual(binding['original_request_key'],'original-preserved')
        self.assertEqual(binding['effective_request_key'],first['request_key'])
        self.assertEqual(binding['run_id'],'run-one')
        for effective in (first,second):
            content={k:v for k,v in effective.items() if k!='request_key'}
            original={k:v for k,v in before.items() if k!='request_key'}
            self.assertEqual(json.dumps(content,sort_keys=True).encode(),json.dumps(original,sort_keys=True).encode())
        self.assertEqual(form,before)
        first['filters'][0]['values'].append('South')
        self.assertEqual(form,before)

    def test_legacy_call_without_execution_id_keeps_existing_submission_key(self):
        from cloud_runner_context import bind_demo_submission
        original={'request_key':'legacy','description':'unchanged'}
        submitted,binding=bind_demo_submission(original,None)
        self.assertEqual(submitted,original);self.assertIsNot(submitted,original);self.assertIsNone(binding)


class DurableCapturePointerTests(unittest.TestCase):
    def test_native_pointer_and_index_are_durable_on_success_and_primary_error(self):
        from cloud_runner_context import retaining_native_captures
        from test_cloud_form_worker import NativeCaptureExportTests
        for failed in (False,True):
            helper=NativeCaptureExportTests();helper.setUp();self.addCleanup(helper.doCleanups)
            context=SimpleNamespace(root=helper.job,record=Mock())
            # Use the production exporter and a real sealed synthetic pointer.
            with patch('metadata_config.ROOT',helper.root):
                from contextlib import contextmanager
                from cloud_form_worker import retaining_capture_pointers
                @contextmanager
                def bound(job,unused):
                    with retaining_capture_pointers(job,helper.captures):yield
                with patch('cloud_form_worker.retaining_capture_pointers',side_effect=bound):
                    try:
                        with retaining_native_captures(context):
                            directory=helper.capture('11111111-1111-4111-8111-111111111111')
                            if failed:raise RuntimeError('primary worker failure')
                    except RuntimeError as exc:
                        self.assertTrue(failed);self.assertEqual('primary worker failure',str(exc))
            rows={call.args[0]:call.args[1] for call in context.record.call_args_list}
            self.assertEqual(1,rows['native-capture-index']['body']['native_pointers'])
            pointer=helper.job/rows['native-capture-pointer']['path']
            self.assertEqual(pointer.read_bytes(),(directory/'slim-recording.json').read_bytes())
            self.assertEqual(rows['native-capture-pointer']['body'],json.loads(pointer.read_bytes()))
            import hashlib
            self.assertEqual(rows['native-capture-pointer']['sha256'],hashlib.sha256(pointer.read_bytes()).hexdigest())
            self.assertFalse(any(p.suffix=='.sqlite' for p in (helper.job/'captures').rglob('*')))

    def test_pointer_record_failure_cannot_replace_primary_error(self):
        from cloud_runner_context import retaining_native_captures
        with tempfile.TemporaryDirectory() as folder:
            context=SimpleNamespace(root=Path(folder),record=Mock(side_effect=ValueError('record upload failed')))
            with patch('metadata_config.ROOT',Path(folder)):
                with self.assertRaisesRegex(RuntimeError,'original worker error'):
                    with retaining_native_captures(context):raise RuntimeError('original worker error')
            self.assertTrue((Path(folder)/'captures/index.json').exists())
