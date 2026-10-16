import hashlib,io,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import Mock
from cloud_stage_worker import run,extract

def zipped():
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w')as z:z.writestr('hello.json','{}')
 return out.getvalue()
class CloudStageTests(unittest.TestCase):
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
