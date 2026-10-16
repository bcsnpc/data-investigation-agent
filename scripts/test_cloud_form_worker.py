import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch

import cloud_form_worker as worker


class CloudFormWorkerTests(unittest.TestCase):
    def bundle(self,root,job):
        manifest={'model':{'credential':{'mode':'key_vault'}},
                  'storage':{'catalog':str(job/'catalog.sqlite'),'inventory':str(job/'inventory.sqlite')}}
        objects={'manifest':manifest,'approval':{},'index':{'status':'READY'},'scope':{},'form':{'description':'original'}}
        def save(name,raw):
            (root/name).write_bytes(raw);return {'path':name,'sha256':hashlib.sha256(raw).hexdigest()}
        bundle={'version':'cloud-form-attempt-v1',
            **{key:save(key+'.json',json.dumps(value).encode()) for key,value in objects.items()},
            'snapshots':{key:save(key+'.sqlite',b'private snapshot') for key in ('catalog','inventory')},
            'model_pin':{'model_id':'model','context_id':'context','context_hash':'hash'}}
        path=root/'job.json';path.write_text(json.dumps(bundle));return path,worker.file_hash(path)

    def test_bundle_ready_label_never_replaces_consumer_proof_or_rewrites_config(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);job=root/'work';path,hash=self.bundle(root,job)
            before=(root/'manifest.json').read_bytes()
            with patch('investigator.estate_manifest.validate'),patch('estate_readiness.current_pins',return_value=({},{})),\
                 patch('investigator.estate_readiness.assess_named_scope',return_value={'status':'BLOCKED','detail':'missing reader receipt'}) as assess:
                with self.assertRaisesRegex(ValueError,'CLOUD_ROUTE_NOT_READY'):worker.prepare(path,hash,job)
            assess.assert_called_once()
            self.assertEqual((root/'manifest.json').read_bytes(),before)
            self.assertEqual((job/'catalog.sqlite').read_bytes(),b'private snapshot')
            with self.assertRaises(FileExistsError):
                with patch('investigator.estate_manifest.validate'):worker.prepare(path,hash,job)

    def test_storage_path_cannot_escape_private_job(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);job=root/'work';path,_=self.bundle(root,job)
            manifest=json.loads((root/'manifest.json').read_bytes())
            manifest['storage']['catalog']=str(root/'protected.sqlite')
            (root/'manifest.json').write_text(json.dumps(manifest))
            bundle=json.loads(path.read_bytes());bundle['manifest']['sha256']=worker.file_hash(root/'manifest.json')
            path.write_text(json.dumps(bundle))
            with patch('investigator.estate_manifest.validate'):
                with self.assertRaisesRegex(ValueError,'OUTSIDE_JOB'):worker.prepare(path,worker.file_hash(path),job)
            self.assertFalse(job.exists());self.assertFalse((root/'protected.sqlite').exists())

    def test_pinned_artifact_rejects_changed_bytes_and_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'form.json';path.write_bytes(b'{}')
            ref={'path':'form.json','sha256':hashlib.sha256(b'{}').hexdigest()}
            self.assertEqual(worker.pinned(root,ref),path)
            path.write_bytes(b'{ }')
            with self.assertRaisesRegex(ValueError,'HASH_OR_PATH'):worker.pinned(root,ref)
            with self.assertRaisesRegex(ValueError,'NOT_RELATIVE'):worker.pinned(root,{**ref,'path':'../other'})

    def test_scope_is_validated_before_preview_or_any_dispatch(self):
        original=Mock(return_value={'original':'preview'})
        workspace=SimpleNamespace(preview=original)
        worker.guard_preview(workspace,{'scope':{'constraints':{'kind':'WHOLE_ENTITY_QUANTITY',
            'filters':[],'dimension_ids':[],'measure_ids':['measure']}}},'model')
        request={'model_id':'model','measure_id':'measure','filters':[],'dimension_ids':[]}
        self.assertEqual(workspace.preview(request),{'original':'preview'})
        for field,value in [('model_id','other'),('measure_id','other'),('filters',[{}]),('dimension_ids',['column'])]:
            with self.assertRaisesRegex(ValueError,'OUTSIDE_VERIFIED_SCOPE'):workspace.preview({**request,field:value})
        self.assertEqual(original.call_count,1)

    def test_held_or_question_form_is_returned_unchanged_without_run(self):
        for state in ('HELD','CLARIFYING'):
            saved={'ticket':{'state':state},'revision':1}
            workspace=SimpleNamespace(forms=SimpleNamespace(submit=Mock(return_value=saved)),run_session_once=Mock())
            form={'description':'Exact original text'}
            self.assertIs(worker.run_form(workspace,form),saved)
            workspace.forms.submit.assert_called_once_with(form)
            workspace.run_session_once.assert_not_called()

    def test_cloud_authority_and_durable_recording_are_required(self):
        argv=['--bundle','never-open.json','--sha256','0'*64,'--job-root','never-create']
        with patch.dict('os.environ',{},clear=True):
            with self.assertRaisesRegex(ValueError,'POSTGRES_AUTHORITY'):worker.main(argv)
        with patch.dict('os.environ',{'INVESTIGATOR_STATE_BACKEND':'postgresql'},clear=True):
            with self.assertRaisesRegex(ValueError,'DURABLE_RECORDING'):worker.main(argv)

    def test_one_queue_claim_and_finish_no_automatic_retry(self):
        from contextlib import contextmanager
        saved={'ticket':{'state':'INVESTIGATING','id':'ticket','session_id':'session'},'revision':3}
        finished={'ticket':{'state':'FINDINGS_SHARED'},'revision':4}
        query=Mock();query.execute.return_value.fetchone.return_value=('FINISHED',)
        @contextmanager
        def connect():yield query
        workspace=SimpleNamespace(forms=SimpleNamespace(submit=Mock(return_value=saved)),
            store=SimpleNamespace(connect=connect),run_session_once=Mock(return_value=True),
            smart_intake=SimpleNamespace(finish=Mock(return_value=finished)))
        self.assertIs(worker.run_form(workspace,{'description':'q'}),finished)
        workspace.run_session_once.assert_called_once_with('session')
        workspace.smart_intake.finish.assert_called_once_with({'ticket_id':'ticket','revision':3})
        workspace.run_session_once.return_value=False;workspace.smart_intake.finish.reset_mock()
        with self.assertRaisesRegex(ValueError,'NOT_OWNED_OR_ALREADY_RUN'):worker.run_form(workspace,{'description':'q'})
        workspace.smart_intake.finish.assert_not_called()



class NativeCaptureExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.captures=self.root/'source';self.captures.mkdir()
        self.job=self.root/'one-attempt';self.job.mkdir()

    def capture(self,identity,*,sealed=True,pointer=True):
        from investigator.process_tape import Tape,bytes_of
        from test_slim_recording import CONFIG
        path=self.captures/identity;path.mkdir()
        (path/'catalog.sqlite').write_bytes(b'never copy this database')
        tape=Tape(path/'tape.json',{'entry_point':'synthetic','context_identity':'test','config':{},
            'profile':{},'usage_policy':{},'engine_hash':'test','state':{}})
        if sealed:tape.finish({'status':'COMPLETED'})
        if pointer:
            receipt={'version':'slim-recording-v1','configuration':CONFIG,
                'bundle':{'sha256':'b'*64,'bytes':10},'bundle_seal':'c'*64,
                'source_seal':json.loads(tape.path.read_bytes())['seal'],
                'restoration_verified':True,'engine_replay':'NOT_RUN','retired_private_files':[]}
            (path/'slim-recording.json').write_text(json.dumps(receipt,indent=3)+'\n')
        return path

    def test_new_native_pointer_bytes_and_index_export_without_databases_or_old_captures(self):
        old=self.capture('11111111-1111-4111-8111-111111111111');before=worker.capture_ids(self.captures)
        new=self.capture('22222222-2222-4222-8222-222222222222')
        originals={p.name:p.read_bytes() for p in new.iterdir()}
        result=worker.export_capture_pointers(self.captures,before,self.job)
        self.assertEqual((result['count'],result['native_pointers'],result['incomplete']),(1,1,0))
        self.assertEqual(result['captures'][0]['status'],'NATIVE_POINTER_EXPORTED')
        target=self.job/'captures'/new.name/'slim-recording.json'
        self.assertEqual(target.read_bytes(),originals['slim-recording.json'])
        self.assertEqual({p.name:p.read_bytes() for p in new.iterdir()},originals)
        self.assertEqual(sorted(p.name for p in (self.job/'captures').rglob('*') if p.is_file()),['index.json','slim-recording.json'])
        self.assertFalse((self.job/'captures'/old.name).exists())

    def test_retired_databases_are_not_needed_or_reconstituted_for_pointer_export(self):
        path=self.capture('11111111-1111-4111-8111-111111111111')
        (path/'catalog.sqlite').unlink()
        with patch('investigator.process_tape.Tape',side_effect=AssertionError('No full snapshot validation during export')):
            result=worker.export_capture_pointers(self.captures,set(),self.job)
        self.assertEqual(result['native_pointers'],1)
        self.assertEqual(result['captures'][0]['tape_validation'],'SEALED_ENVELOPE_AND_EVENT_JOURNAL_ONLY')
        self.assertFalse((path/'catalog.sqlite').exists())

    def test_stage_archive_includes_native_index_and_pointer_bytes(self):
        import zipfile
        from cloud_stage_worker import package
        path=self.capture('11111111-1111-4111-8111-111111111111')
        worker.export_capture_pointers(self.captures,set(),self.job)
        inputs=self.root/'inputs';inputs.mkdir();output=self.root/'stage.zip'
        package(inputs,self.root,output)
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.read('one-attempt/captures/'+path.name+'/slim-recording.json'),(path/'slim-recording.json').read_bytes())
            self.assertEqual(json.loads(archive.read('one-attempt/captures/index.json'))['count'],1)
            self.assertFalse(any(name.endswith('.sqlite') for name in archive.namelist()))

    def test_missing_unsealed_and_sealed_unpublished_each_get_explicit_disposition(self):
        (self.captures/'11111111-1111-4111-8111-111111111111').mkdir()
        self.capture('22222222-2222-4222-8222-222222222222',sealed=False,pointer=False)
        self.capture('33333333-3333-4333-8333-333333333333',pointer=False)
        result=worker.export_capture_pointers(self.captures,set(),self.job)
        self.assertEqual(result['count'],3);self.assertEqual(result['incomplete'],3)
        self.assertEqual([r['status'] for r in result['captures']],
            ['MISSING_TAPE','UNSEALED_OR_INVALID_TAPE','SEALED_WITHOUT_PUBLICATION_POINTER'])

    def test_bad_publication_pointer_retained_verbatim_with_failure(self):
        path=self.capture('11111111-1111-4111-8111-111111111111')
        (path/'slim-recording.json').write_bytes(b'{ invalid publication }')
        result=worker.export_capture_pointers(self.captures,set(),self.job)
        self.assertEqual(result['captures'][0]['status'],'CAPTURE_EXPORT_INVALID')
        self.assertEqual((self.job/'captures'/path.name/'slim-recording.json').read_bytes(),b'{ invalid publication }')

    def test_success_and_failure_both_export_after_attempt(self):
        with worker.retaining_capture_pointers(self.job,self.captures):
            self.capture('11111111-1111-4111-8111-111111111111')
        self.assertEqual(json.loads((self.job/'captures/index.json').read_bytes())['native_pointers'],1)
        second=self.root/'failed-attempt';second.mkdir()
        with self.assertRaisesRegex(RuntimeError,'original worker failure'):
            with worker.retaining_capture_pointers(second,self.captures):
                self.capture('22222222-2222-4222-8222-222222222222',pointer=False)
                raise RuntimeError('original worker failure')
        self.assertEqual(json.loads((second/'captures/index.json').read_bytes())['incomplete'],1)

    def test_export_failure_never_masks_original_attempt_failure(self):
        with patch.object(worker,'export_capture_pointers',side_effect=OSError('disk full')):
            with self.assertRaisesRegex(RuntimeError,'original failure'):
                with worker.retaining_capture_pointers(self.job,self.captures):raise RuntimeError('original failure')
        error=json.loads((self.job/'capture-export-error.json').read_bytes())
        self.assertEqual(error,{'status':'CAPTURE_EXPORT_FAILED','error_type':'OSError','primary_error_type':'RuntimeError'})

    def test_export_failure_after_success_is_not_silently_accepted(self):
        with patch.object(worker,'export_capture_pointers',side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError,'disk full'):
                with worker.retaining_capture_pointers(self.job,self.captures):pass

    def test_zero_new_captures_is_explicit_not_a_replay_pass(self):
        result=worker.export_capture_pointers(self.captures,set(),self.job)
        self.assertEqual(result['status'],'NO_NEW_CAPTURES');self.assertEqual(result['count'],0)

if __name__=='__main__':unittest.main()
