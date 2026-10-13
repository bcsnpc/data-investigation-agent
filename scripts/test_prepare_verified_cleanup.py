import json
from pathlib import Path
import tempfile
import unittest
from investigator.artifact_store import canonical, digest, ArtifactError
from prepare_verified_cleanup import build, verify_remote


class CleanupTests(unittest.TestCase):
    def test_conservation_and_changed_or_outside_receipt_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/'batch').mkdir()
            row={'path':'.local/old/tape.json','bytes':3,'sha256':'a'*64,'download_verified_sha256':'a'*64,
                 'tier':'Archive','blob':'originals/a/b.gz','etag':'exact','stored_bytes':20}
            def setup(value):
                raw=canonical({'objects':[value]}); (root/'batch/receipt.json').write_bytes(raw)
                return {'batches':[{'batch':'batch','receipt_sha256':digest(raw),'files':1}],'original_paths':1}
            checkpoint=setup(row);plan=build(checkpoint,root,root,protected_parents=[])
            self.assertEqual(len(plan['files']),1);self.assertEqual(len(plan['blobs']),1)
            held=build(checkpoint,root,root,protected_parents=['.local/old'])
            self.assertTrue(held['files'][0]['runtime_protected'])
            self.assertFalse(plan['files'][0]['runtime_protected'])
            with self.assertRaisesRegex(ArtifactError,'READBACK_PROOF'):
                build(setup({**row,'download_verified_sha256':'b'*64}),root,root,protected_parents=[])
            with self.assertRaisesRegex(ArtifactError,'PATH_OUTSIDE'):
                build(setup({**row,'path':'../elsewhere'}),root,root,protected_parents=[])
            setup(row);(root/'batch/receipt.json').write_bytes(b'{}')
            with self.assertRaisesRegex(ArtifactError,'RECEIPT_SHA'):build(checkpoint,root,root,protected_parents=[])

    def test_only_unchanged_remote_readback_admits_cleanup(self):
        plan={'blobs':[{'blob':'blob','etag':'exact','stored_bytes':20}]}
        class Client:
            def __init__(self,headers): self.headers=headers;self.calls=[];self.closed=0
            def request(self,key,operation,**kw):
                self.calls.append(operation)
                return type('Response',(),{'headers':self.headers})()
            def close(self,response):self.closed+=1
        correct={'etag':'exact','x-ms-access-tier':'Archive','content-length':'20'}
        client=Client(correct);self.assertEqual(verify_remote(plan,client)['blobs'],1)
        self.assertEqual(client.calls,['HEAD']);self.assertEqual(client.closed,1)
        for field,value in [('etag','changed'),('content-length','21'),('x-ms-access-tier','Hot')]:
            client=Client({**correct,field:value})
            with self.assertRaisesRegex(ArtifactError,'REMOTE_CHANGED'):verify_remote(plan,client)
            self.assertEqual(client.closed,1)

    def test_owner_template_has_idempotence_containment_hash_and_no_recursive_delete(self):
        text=Path(__file__).with_name('owner_verified_cleanup.ps1.template').read_text()
        for required in ['Test-Path -LiteralPath','ReparsePoint','ComputeHash','StartsWith($prefix',
                         'FileShare]::Read','Remove-Item -LiteralPath','VerifyOnly','AvailableFreeSpace']:
            self.assertIn(required,text)
        self.assertNotIn('-Recurse',text)


if __name__=='__main__':unittest.main()
