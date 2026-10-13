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


if __name__=='__main__':unittest.main()
