import hashlib,io,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import Mock,patch
from cloud_stage_worker import run,extract

def zipped():
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w')as z:z.writestr('hello.json','{}')
 return out.getvalue()
class CloudStageTests(unittest.TestCase):
 def test_missing_actual_lease_stops_before_publication_or_estate_read(self):
  from cloud_stage_worker import verify_phase
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory()as folder:
   root=Path(folder);inputs=root/'inputs';work=root/'work';(inputs/'verification').mkdir(parents=True);work.mkdir()
   candidate=inputs/'verification/publication-candidate.json';candidate.write_text('{}')
   with patch('investigator.shared_state.configured_state',return_value=SimpleNamespace(backend='postgresql')), \
     patch('cloud_context_prepare.publish')as publish,patch('cloud_verification_run.execute')as execute:
    with self.assertRaisesRegex(ValueError,'EXCLUSIVE_WRITER_JOB_DECLARATION_DIFFERS'):
     verify_phase(inputs,work,{'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'deadline':100})
    publish.assert_not_called();execute.assert_not_called()
 def test_budget_mismatch_refuses_before_publication_or_verification(self):
  from cloud_stage_worker import verify_phase
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory()as folder:
   root=Path(folder);inputs=root/'inputs';work=root/'work';(inputs/'verification').mkdir(parents=True);work.mkdir()
   candidate=inputs/'verification/publication-candidate.json';candidate.write_text('{}')
   (inputs/'verification/context.json').write_text('{}');(inputs/'verification/endpoints.json').write_text('{}')
   (inputs/'verification-spec.json').write_text(json.dumps({'budgets':{'round':{'id':'OLD'},'binding_verification':{'session_cap':40}}}))
   manifest={'budgets':{'round':{'id':'NEW'},'binding_verification':{'session_cap':40}}}
   with patch('investigator.shared_state.configured_state',return_value=SimpleNamespace(backend='postgresql')), \
     patch('investigator.estate_manifest.load',return_value=manifest), \
     patch('investigator.adapters.estate_installation.configuration',return_value={}), \
     patch('investigator.shared_writer_lease.require'), \
     patch('cloud_context_prepare.publish')as publish,patch('cloud_verification_run.execute')as execute:
    with self.assertRaisesRegex(ValueError,'VERIFICATION_BUDGET_DIFFERS'):
     verify_phase(inputs,work,{'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'deadline':100})
    publish.assert_not_called();execute.assert_not_called()

 def test_preparation_preserves_current_owner_decision(self):
  from cloud_stage_worker import prepare_phase
  with tempfile.TemporaryDirectory()as folder:
   root=Path(folder);inputs=root/'inputs';work=root/'work'
   inputs.mkdir();(work/'verification').mkdir(parents=True)
   plan={'model_id':'model','source_context':'context','source_context_hash':'hash','decision':'Owner approved fresh round; counters preserved'}
   (inputs/'operator-plan.json').write_text(json.dumps(plan));(inputs/'endpoints.json').write_text('{}')
   (work/'verification/publication-candidate.json').write_text('{}')
   with patch('cloud_context_prepare.prepare',return_value={'approval':{}})as prepare:
    prepare_phase(inputs,work)
   self.assertEqual(prepare.call_args.kwargs['decision'],plan['decision'])
   plan['decision']='';(inputs/'operator-plan.json').write_text(json.dumps(plan))
   with patch('cloud_context_prepare.prepare')as prepare,self.assertRaisesRegex(ValueError,'OWNER_DECISION_REQUIRED'):
    prepare_phase(inputs,work)
   prepare.assert_not_called()
 def test_prepare_failure_retains_artifacts_and_never_publishes_or_verifies(self):
  with tempfile.TemporaryDirectory()as folder:
   root=Path(folder);raw=zipped();upload=Mock();verify=Mock()
   def prepare(inputs,work):
    (work/'verification').mkdir();(work/'verification/progress.json').write_text('{"completed":1}')
    raise ValueError('STOPPED_AFTER_PARTIAL_PREPARATION')
   config={'phase':'prepare','input_url':'input','input_sha256':hashlib.sha256(raw).hexdigest(),'compressed_limit':10000,'expanded_limit':10000,'output_url':'output'}
   result=run(config,download=lambda *_:raw,upload=upload,inputs=root/'inputs',work=root/'work',prepare_fn=prepare,verify_fn=verify)
   verify.assert_not_called();self.assertEqual(result['status'],'FAILED')
   with zipfile.ZipFile(io.BytesIO(upload.call_args.args[1]))as z:
    self.assertEqual(json.loads(z.read('verification/progress.json')),{'completed':1})
    self.assertEqual(json.loads(z.read('stage-result.json'))['message'],'STOPPED_AFTER_PARTIAL_PREPARATION')
 def test_changed_hash_never_prepares_and_archives_failure(self):
  with tempfile.TemporaryDirectory()as folder:
   root=Path(folder);prepare=Mock();upload=Mock()
   result=run({'phase':'prepare','input_url':'input','input_sha256':'0'*64,'compressed_limit':10000,'expanded_limit':10000,'output_url':'output'},download=lambda *_:zipped(),upload=upload,inputs=root/'inputs',work=root/'work',prepare_fn=prepare)
   prepare.assert_not_called();self.assertEqual(result['status'],'FAILED');upload.assert_called_once()
 def test_zip_escape_refused(self):
  raw=io.BytesIO()
  with zipfile.ZipFile(raw,'w')as z:z.writestr('../escape','bad')
  with tempfile.TemporaryDirectory()as folder,self.assertRaisesRegex(ValueError,'ZIP_PATH'):
   extract(raw.getvalue(),Path(folder)/'inputs',expected=hashlib.sha256(raw.getvalue()).hexdigest(),expanded_limit=100)
if __name__=='__main__':unittest.main()
