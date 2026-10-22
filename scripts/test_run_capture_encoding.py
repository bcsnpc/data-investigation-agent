import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investigator.process_tape import bytes_of
from investigator.run_capture import DurableCapture, record_value, ENCODING

HEADER={'entry_point':'runner','context_identity':'fixture-context','config':{},'profile':{},'usage_policy':None,'engine_hash':'fixture-engine','state':{}}


class LargeCatalogCaptureTests(unittest.TestCase):
    def test_catalog_read_larger_than_gateway_blob_bound_is_preserved_exactly(self):
        from investigator.adapters.runner_blobs import MAX_BYTES
        # A realistic repeated definition payload crosses the actual gateway
        # limit. The transport still refuses any object above that same limit.
        original={'event':{'kind':'READ_RESULT','body':'definition:'+'x'*MAX_BYTES},'tape':'native.json'}
        retained={}
        def bounded_put(key,raw):
            self.assertLessEqual(len(raw),MAX_BYTES)
            retained[key]=raw
        with tempfile.TemporaryDirectory()as folder:
            capture=DurableCapture(Path(folder)/'run',bounded_put,run_id='large-context',bootstrap={**HEADER,'state':{'runner_image':'same-image'}})
            ref=capture.record('tape-event',original)
            self.assertEqual(ref['encoding'],ENCODING)
            self.assertEqual(bytes_of(record_value(retained[ref['key']],ref['encoding'])),bytes_of(original))
            capture.record('status',{'status':'COMPLETED','partial':False})
            capture.seal()
            self.assertIn('large-context/run-record.json',retained)
            from investigator.runner_replay import boundary
            self.assertTrue(boundary(capture.root,'same-image')['matched'])

    def test_changed_original_hash_or_length_and_unknown_encoding_refuse(self):
        with tempfile.TemporaryDirectory()as folder,patch('investigator.run_capture.MAX_BLOB_BYTES',2048):
            retained={}
            capture=DurableCapture(Path(folder)/'run',lambda k,v:retained.setdefault(k,v),run_id='changed',bootstrap=HEADER)
            ref=capture.record('tape-event',{'body':'x'*5000})
            encoded=json.loads(retained[ref['key']])
            for field,value in (('sha256','0'*64),('bytes',4999)):
                altered={**encoded,field:value}
                with self.assertRaisesRegex(ValueError,'CAPTURE_RECORD_DECODED_BYTES_CHANGED'):
                    record_value(bytes_of(altered),ENCODING)
            with self.assertRaisesRegex(ValueError,'ENCODING_UNSUPPORTED'):
                record_value(retained[ref['key']],'unknown')

    def test_secret_validation_precedes_compression_and_transport(self):
        from investigator.planner_recording import RecordingError
        with tempfile.TemporaryDirectory()as folder,patch('investigator.run_capture.MAX_BLOB_BYTES',2048):
            retained={}
            capture=DurableCapture(Path(folder)/'run',lambda k,v:retained.setdefault(k,v),run_id='private',bootstrap=HEADER)
            before=dict(retained)
            with patch.dict(os.environ,{'DIA_TEST_PASSWORD':'synthetic-private-credential-123456'}):
                with self.assertRaises(RecordingError):
                    capture.record('tape-event',{'body':'x'*5000,'data':'synthetic-private-credential-123456'})
            self.assertEqual(retained,before)

    def test_ordinary_and_legacy_records_keep_exact_bytes_without_envelope(self):
        original={'version':ENCODING,'payload':'ordinary user data, not an encoded record'}
        self.assertEqual(record_value(bytes_of(original)),original)
        with tempfile.TemporaryDirectory()as folder:
            retained={}
            capture=DurableCapture(Path(folder)/'run',lambda k,v:retained.setdefault(k,v),run_id='legacy',bootstrap=HEADER)
            ref=capture.record('result',original)
            self.assertNotIn('encoding',ref)
            self.assertEqual(retained[ref['key']],bytes_of(original))
