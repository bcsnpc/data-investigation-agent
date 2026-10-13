import unittest
from audit_recording_content import shapes, tape, catalog_schema, row_array_class
class RecordingContentAuditTests(unittest.TestCase):
 def test_nested_transport_json_is_inspected_and_not_called_bulk_by_count(self):
  import json
  result=shapes({'stdout':json.dumps({'result':{'rows':[{'value':1}]*300}}),'assets':[{}]*2000})
  self.assertEqual(result['max_rows'],300);self.assertEqual(len(result['candidates']),1)
  self.assertEqual(result['candidates'][0]['classification'],'REVIEW_REQUIRED_NOT_AUTOMATICALLY_BULK')
 def test_bounded_rows_and_metadata_arrays_distinguished(self):
  result=shapes({'rows':[{}]*249,'definitions':[{}]*1000})
  self.assertEqual(result['row_arrays'],1);self.assertEqual(result['candidates'],[])
 def test_accounting_class_requires_known_event_and_path(self):
  self.assertEqual(row_array_class('BUDGET_INPUT','/tables/adaptive_usage/rows'),'CONTROL_ACCOUNTING_ROWS')
  self.assertEqual(row_array_class('BOUNDED_RESPONSE','/tables/adaptive_usage/rows'),'UNCLASSIFIED_ROW_ARRAY')
  self.assertEqual(row_array_class('BUDGET_INPUT','/tables/client_rows/rows'),'UNCLASSIFIED_ROW_ARRAY')
 def test_audit_does_not_change_tape_and_names_opaque_event_gap(self):
  import tempfile,json,base64,hashlib
  from pathlib import Path
  with tempfile.TemporaryDirectory()as folder:
   path=Path(folder)/'tape.json'
   raw=json.dumps({'version':'synthetic-v1','events':[{'kind':'WORKER_READ','body':base64.b64encode(b'not JSON').decode()}]}).encode()
   path.write_bytes(raw);before=path.stat().st_mtime_ns
   result=tape(path)
   self.assertEqual(result['status'],'PARTIAL_DECODING')
   self.assertEqual(result['decode_failures'],[{'event':0,'kind':'WORKER_READ'}])
   self.assertEqual(result['sha256'],hashlib.sha256(raw).hexdigest())
   self.assertEqual(path.read_bytes(),raw);self.assertEqual(path.stat().st_mtime_ns,before)
 def test_catalog_schema_never_treats_schema_as_payload_verification(self):
  import tempfile,sqlite3
  from pathlib import Path
  with tempfile.TemporaryDirectory()as folder:
   path=Path(folder)/'catalog.sqlite'
   db=sqlite3.connect(path)
   db.execute('CREATE TABLE unexpected_business_copy(secret_value TEXT)');db.close()
   result=catalog_schema(path)
   self.assertEqual(result['tables'],['unexpected_business_copy'])
   self.assertEqual(result['status'],'SCHEMA_ONLY_NO_PAYLOAD_AUDIT')
if __name__=='__main__':unittest.main()
