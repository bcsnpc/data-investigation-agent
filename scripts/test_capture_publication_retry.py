import unittest
from urllib.error import HTTPError,URLError
from investigator.adapters.runner_blobs import immutable_upload
from investigator.artifact_store import ArtifactError


class PublicationRetryTests(unittest.TestCase):
    def test_lost_put_response_requires_exact_readback_without_rerunning_step(self):
        stored={};calls=[];waits=[]
        def put(key,raw):
            calls.append(key)
            if key in stored:raise HTTPError('https://fixture',412,'exists',{},None)
            stored[key]=raw
            raise URLError(TimeoutError('lost response'))
        immutable_upload(put,stored.__getitem__,'record',b'original',sleep=waits.append)
        self.assertEqual(calls,['record','record'])
        self.assertEqual(waits,[1])

    def test_conflicting_existing_bytes_refuse(self):
        def put(*args):raise HTTPError('https://fixture',412,'exists',{},None)
        with self.assertRaisesRegex(ArtifactError,'IMMUTABLE_BYTES_DIFFER'):
            immutable_upload(put,lambda key:b'changed','record',b'original',sleep=lambda _:None)

    def test_transient_retry_is_bounded_and_permission_denial_is_not_retried(self):
        calls=[]
        def timeout(*args):calls.append(1);raise URLError('timeout')
        with self.assertRaises(URLError):immutable_upload(timeout,None,'r',b'x',sleep=lambda _:None)
        self.assertEqual(len(calls),3)
        calls.clear()
        def forbidden(*args):calls.append(1);raise HTTPError('https://fixture',403,'forbidden',{},None)
        with self.assertRaises(HTTPError):immutable_upload(forbidden,None,'r',b'x',sleep=lambda _:None)
        self.assertEqual(len(calls),1)


if __name__=='__main__':unittest.main()
