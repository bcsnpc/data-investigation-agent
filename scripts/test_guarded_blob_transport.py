import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from azure.core.pipeline.transport import HttpTransport, HttpResponse, HttpRequest
from azure.storage.blob import BlobClient
from investigator.adapters.guarded_transport import GuardedTransport


class Response(HttpResponse):
    def __init__(self, request, status):
        super().__init__(request, None)
        self.status_code = status
        self.headers = {'etag': 'sealed-etag', 'x-ms-request-id': 'fake-id', 'content-length': '0'}
        self.reason = 'synthetic'
    def body(self): return b''
    def text(self, encoding=None): return ''


class Wire(HttpTransport):
    def __init__(self, statuses=(201,)): self.statuses=list(statuses); self.sent=[]
    def open(self): pass
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def send(self, request, **kwargs):
        self.sent.append((request.method, request.url))
        result=self.statuses.pop(0)
        if isinstance(result, Exception): raise result
        return Response(request, result)


class Gate:
    def __init__(self, allowed=True): self.calls=[]; self.allowed=allowed
    def http(self, identity, method, url, body=None, headers=None):
        self.calls.append((identity,method,url))
        if not self.allowed: raise RuntimeError('DENIED')


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.receipts=Path(self.temp.name)/'controls.jsonl'
    def records(self): return [json.loads(line) for line in self.receipts.read_text().splitlines()]
    def client(self, wire, gate=None, retry=0):
        self.gate=gate or Gate()
        transport=GuardedTransport(self.gate,'platform',receipts=self.receipts,inner=wire)
        transport.sleep=lambda duration:None
        return BlobClient.from_blob_url('https://synthetic.blob.core.windows.net/archive/fixture',
                      transport=transport,retry_total=retry)

    def test_real_blob_sdk_dispatch_is_gated_and_journaled(self):
        wire=Wire();self.client(wire).upload_blob(b'private-evidence',overwrite=False)
        self.assertEqual(len(wire.sent),1);self.assertEqual(len(self.gate.calls),1)
        records=self.records();self.assertEqual([r['phase'] for r in records],['DISPATCHED','RESPONSE'])
        self.assertEqual(records[1]['status'],201)
        self.assertNotIn('private-evidence',self.receipts.read_text())
        self.assertEqual(records[0]['id'],records[1]['id'])

    def test_retried_physical_request_is_gated_and_counted_separately(self):
        wire=Wire((503,201));self.client(wire,retry=1).upload_blob(b'x',overwrite=False)
        self.assertEqual(len(wire.sent),2);self.assertEqual(len(self.gate.calls),2)
        self.assertEqual(sum(r['physical_requests'] for r in self.records() if r['phase']=='DISPATCHED'),2)

    def test_denial_and_receipt_failure_prevent_send(self):
        wire=Wire();client=self.client(wire,Gate(False))
        with self.assertRaisesRegex(RuntimeError,'DENIED'):client.upload_blob(b'x')
        self.assertEqual(wire.sent,[]);self.assertFalse(self.receipts.exists())
        client=self.client(wire)
        with patch.object(GuardedTransport,'_record',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):client.upload_blob(b'x')
        self.assertEqual(wire.sent,[])

    def test_failed_request_remains_counted_without_error_message_or_secret(self):
        wire=Wire((ConnectionResetError('secret-body-and-token'),));client=self.client(wire)
        with self.assertRaises(ConnectionResetError):client.upload_blob(b'private-data')
        records=self.records();self.assertEqual(records[-1]['error_type'],'ConnectionResetError')
        self.assertEqual(records[0]['phase'],'DISPATCHED');self.assertNotIn('secret-body',self.receipts.read_text())

    def test_platform_correlation_id_does_not_enter_engine_tape_or_result(self):
        from investigator import process_tape
        from types import SimpleNamespace
        # The only capture interaction allowed is none: control identity belongs
        # to the private HTTP journal, not deterministic investigation evidence.
        tape=SimpleNamespace(replaying=False,event=lambda *args: self.fail('control entered tape'))
        wire=Wire();client=self.client(wire)
        with process_tape.active(tape), patch.object(process_tape,'uuid4',side_effect=AssertionError('engine identity consumed')):
            result=client.upload_blob(b'private-evidence',overwrite=False)
        identifier=self.records()[0]['id']
        self.assertNotIn(identifier,str(result))
        self.assertEqual(len(wire.sent),1)

    def test_redirect_target_needs_its_own_permission(self):
        # RedirectPolicy/StorageHosts may issue another send; the final transport
        # sees that exact URL, not just the URL initially passed into the SDK.
        wire=Wire();gate=Gate();transport=GuardedTransport(gate,'platform',receipts=self.receipts,inner=wire)
        transport.send(HttpRequest('GET','https://synthetic.blob.core.windows.net/archive/a'))
        gate.allowed=False
        with self.assertRaisesRegex(RuntimeError,'DENIED'):
            transport.send(HttpRequest('GET','https://elsewhere.invalid/archive/a'))
        self.assertEqual(len(wire.sent),1)


if __name__=='__main__': unittest.main()
