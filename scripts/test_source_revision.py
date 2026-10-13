import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from investigator.source_revision import committed_revision
class ImageRevisionTests(unittest.TestCase):
 def test_image_revision_requires_exact_tracked_code_and_coverage(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'scripts/investigator').mkdir(parents=True);source=root/'scripts/investigator/a.py';source.write_text('a=1')
   row={'path':'scripts/investigator/a.py','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
   manifest={'version':2,'engine_revision':'a'*40,'files':[row]};p=root/'image-source-manifest.json';p.write_text(json.dumps(manifest))
   with patch('investigator.runtime.fingerprint_files',return_value=(root,[source])):
    self.assertEqual(committed_revision(root),'a'*40)
    source.write_text('a=2')
    with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):committed_revision(root)
    source.write_text('a=1');manifest['files']=[];p.write_text(json.dumps(manifest))
    with self.assertRaisesRegex(ValueError,'FILE_MISSING'):committed_revision(root)
    manifest['files']=[row];manifest['engine_revision']='forged';p.write_text(json.dumps(manifest))
    with self.assertRaisesRegex(ValueError,'PROVENANCE'):committed_revision(root)
if __name__=='__main__':unittest.main()
