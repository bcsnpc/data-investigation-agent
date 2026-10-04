"""Synthetic upstream inputs; no estate payload is used by decoder regression tests."""
import io
import json
import unittest
from urllib.error import HTTPError
from unittest.mock import patch
from investigator.physical_reads import decode_completion
from metadata_auth import MetadataHttp
from read_xmla_failure import extract_codes
from run_native_diagnostic import worker_failure


class Reply(io.BytesIO):
    status=200
    headers={}
    def __enter__(self):return self
    def __exit__(self,*args):self.close()


class DecoderTests(unittest.TestCase):
    def test_sql_guard_acknowledgement_requires_actual_positive_guard_result(self):
        success='{"physical_read":"DONE","kind":"sql_object_permissions","status":"AVAILABLE","guard_passed":true}'
        self.assertTrue(decode_completion(success,'sql_object_permissions',guard=True)['guard_passed'])
        for wrong in (success.replace('true','false'),success.replace(',"guard_passed":true','')):
            with self.assertRaisesRegex(RuntimeError,'Guard success'):
                decode_completion(wrong,'sql_object_permissions',guard=True)
        with self.assertRaisesRegex(RuntimeError,'completion'):
            decode_completion(success,'sql_database_permissions',guard=True)
        self.assertIsNone(decode_completion('{"error":"SQL_READ_FAILED"}','sql_quantity'))

    def test_metadata_http_decoder_preserves_json_null_empty_and_refuses_invalid_json(self):
        from types import SimpleNamespace
        tokens=SimpleNamespace(get_token=lambda scope:'synthetic-auth')
        for raw,expected in [(b'{"value":[],"next":null}',{'value':[],'next':None}),(b'',{})]:
            opener=SimpleNamespace(open=lambda *a,**k:Reply(raw))
            self.assertEqual(MetadataHttp(tokens,opener)('workspaces')['text'],expected)
        opener=SimpleNamespace(open=lambda *a,**k:Reply(b'not json'))
        with self.assertRaises(ValueError):MetadataHttp(tokens,opener)('workspaces')

    def test_native_rejection_reduces_raw_service_failure_to_safe_code(self):
        error=HTTPError('https://synthetic.invalid',403,'private explanation',{},
            io.BytesIO(b'{"error":{"code":"Forbidden","message":"unretained details"}}'))
        result=worker_failure(error)
        self.assertEqual(result['http_status'],403)
        self.assertEqual(result['service_error_code'],'Forbidden')
        self.assertFalse(result['completion_uncertain'])
        self.assertNotIn('unretained',json.dumps(result))

    def test_xmla_projection_keeps_codes_not_message_and_deduplicates(self):
        raw='private text AADSTS50173 then 0xc1450012 again AADSTS50173'
        self.assertEqual(extract_codes(raw),['AADSTS50173','0xC1450012'])
        self.assertEqual(extract_codes('private text without recognised codes'),[])


if __name__=='__main__':unittest.main()
