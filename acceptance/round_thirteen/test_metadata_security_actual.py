import base64,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path[:0]=[str(Path.cwd()/'scripts'),str(Path(__file__).parent)]
from metadata_capture import safe,snapshot
from investigator.planner_recording import RecordingError

def wrapped():
 encoded=''.join('\\u%04x'%ord(c) for c in 'synthetic-sensitive-password')
 return json.dumps('{"password":"'+encoded+'"}')

class Tests(unittest.TestCase):
 def test_inline_checker_nested_json_and_decoded_definition(self):
  for value in ({'text':wrapped()},{'payload':base64.b64encode(json.dumps({'text':wrapped()}).encode()).decode()}):
   with self.assertRaisesRegex(RecordingError,'RECORDING_SECRET_DETECTED'):safe(value)
 def test_inline_bound_is_refusal_not_silent_skip(self):
  value='ordinary text'
  for _ in range(10):value=json.dumps(value)
  with self.assertRaisesRegex(RecordingError,'METADATA_CAPTURE_JSON_DECODING_BOUND'):safe({'text':value})
 def test_secret_bearing_view_ddl_refused_before_backup(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);source=root/'source.sqlite';target=root/'snapshot.sqlite'
   db=sqlite3.connect(source);db.execute("CREATE VIEW fixture AS SELECT 'password=synthetic-sensitive-password' AS note");db.commit();db.close()
   with self.assertRaisesRegex(RecordingError,'RECORDING_SECRET_DETECTED'):snapshot(source,target)
   self.assertFalse(target.exists())
 def test_text_and_blob_snapshot_reject_before_backup(self):
  for blob in (False,True):
   with self.subTest(blob=blob),tempfile.TemporaryDirectory() as directory:
    root=Path(directory);source=root/'source.sqlite';target=root/'snapshot.sqlite'
    db=sqlite3.connect(source);db.execute('CREATE TABLE fixture(value)')
    value=json.dumps({'text':wrapped()});db.execute('INSERT INTO fixture VALUES(?)',(value.encode() if blob else value,));db.commit();db.close()
    with self.assertRaisesRegex(RecordingError,'RECORDING_SECRET_DETECTED'):snapshot(source,target)
    self.assertFalse(target.exists())

if __name__=='__main__':unittest.main()
