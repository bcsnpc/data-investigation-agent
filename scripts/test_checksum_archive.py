import base64
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from investigator.archive_migration import plan
from investigator.artifact_store import ArtifactError,canonical,digest
from investigator.streaming_archive_bundle import prepare
from investigator.checksum_archive import publish
from investigator.resumable_archive import Journal
from investigator.adapters.platform_archive import bind,permits
from test_resumable_archive import URL,KEY,gateway


class Remote:
    account_url=URL
    def __init__(self):
        self.parts={};self.body=None;self.ids=[];self.tier=None;self.md5=None;self.calls=[]
        self.fail_stage=None;self.fail_after_commit=False;self.corrupt_md5=False;self.reverse=False
    def checksum_properties(self,key):
        self.calls.append('HEAD')
        if self.body is None:return None
        return {'etag':'immutable','tier':self.tier,'stored_bytes':len(self.body),
                'stored_md5':'wrong' if self.corrupt_md5 else self.md5}
    def checksum_blocks(self,key):
        self.calls.append('BLOCKS')
        ids=list(reversed(self.ids)) if self.reverse else self.ids
        return {'committed':[(x,len(self.parts[x])) for x in ids],
                'uncommitted':{k:len(v) for k,v in self.parts.items()} if self.body is None else {}}
    def stage_checked(self,key,identity,data):
        self.calls.append(('STAGE',identity))
        if sum(isinstance(x,tuple) for x in self.calls)==self.fail_stage:raise OSError('interrupted')
        self.parts[identity]=data
    def commit_cool(self,key,ids,md5):
        self.calls.append('COMMIT');self.body=b''.join(self.parts[x] for x in ids)
        self.ids=list(ids);self.md5=md5;self.tier='Cool'
        assert base64.b64encode(hashlib.md5(self.body).digest()).decode()==md5
        if self.fail_after_commit:raise OSError('commit response lost')
    def archive(self,key,etag):self.calls.append('ARCHIVE');self.tier='Archive'
    def download_chunks(self,key):raise AssertionError('No download is permitted')


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        path=self.root/'.local/round-five/file.json';path.parent.mkdir(parents=True);path.write_bytes(b'example'*1000)
        self.manifest=plan(self.root,[path.relative_to(self.root).as_posix()],protected=[],finished_statement='synthetic')
        self.sha=digest(canonical(self.manifest));self.plan,_=prepare(self.manifest,self.sha);self.psha=digest(canonical(self.plan))
        self.review={'status':'APPROVED','manifest_sha256':self.sha,'reviewer':'test','basis':'synthetic'}
        self.journal=Journal(self.root/'journal',self.psha,URL)
    def run_publish(self,remote,journal=None,cap=100000):
        return publish(self.plan,self.psha,self.manifest,self.sha,self.review,remote,journal or self.journal,max_stored_bytes=cap)
    def test_checked_upload_resume_and_no_download_claim(self):
        remote=Remote();remote.fail_stage=2
        with patch('investigator.resumable_archive.BLOCK_BYTES',80):
            with self.assertRaises(OSError):self.run_publish(remote)
            first=next(x for x in remote.calls if isinstance(x,tuple));remote.fail_stage=None
            receipt=self.run_publish(remote,Journal(self.journal.path,self.psha,URL))
            self.assertEqual(remote.calls.count(first),1)
            self.assertFalse(receipt['integrity']['download_performed'])
            self.assertFalse(receipt['integrity']['server_computed_sha256'])
            self.assertNotIn('download_verified_sha256',receipt['objects'][0])
            self.assertEqual(remote.tier,'Archive')
            self.run_publish(remote,Journal(self.journal.path,self.psha,URL))
            with self.assertRaisesRegex(ArtifactError,'WITHOUT_MATCHING_VERIFICATION'):
                self.run_publish(remote,Journal(self.root/'missing',self.psha,URL))
    def test_lost_commit_recovers_only_checked_ordered_blocks(self):
        remote=Remote();remote.fail_after_commit=True
        with self.assertRaises(OSError):self.run_publish(remote)
        remote.fail_after_commit=False
        with self.assertRaisesRegex(ArtifactError,'WITHOUT_BLOCK_PROOFS'):
            self.run_publish(remote,Journal(self.root/'unproved',self.psha,URL))
        self.assertEqual(self.run_publish(remote)['objects'][0]['tier'],'Archive')
    def test_changed_property_or_block_order_prevents_archive(self):
        for field in ('corrupt_md5','reverse'):
            with self.subTest(field=field),patch('investigator.resumable_archive.BLOCK_BYTES',80):
                remote=Remote();setattr(remote,field,True)
                with self.assertRaises(ArtifactError):self.run_publish(remote,Journal(self.root/field,self.psha,URL))
                self.assertNotIn('ARCHIVE',remote.calls)
    def test_measured_cap_precedes_any_remote_operation(self):
        remote=Remote()
        with self.assertRaisesRegex(ArtifactError,'TRANSFER_BYTE_CAP'):self.run_publish(remote,cap=1)
        self.assertEqual(remote.calls,[])
    def test_transport_requires_checksum_and_cool_immutable_commit(self):
        g=gateway();body=b'fixture';identity=base64.b64encode(b'a'*64).decode()
        with bind(g,'archive',URL,KEY,'STAGE_CHECKED',body=body,block_id=identity) as (method,url,headers):
            self.assertEqual(headers['content-md5'],base64.b64encode(hashlib.md5(body).digest()).decode())
            self.assertTrue(permits(g,'archive',method,url,body,headers))
            self.assertFalse(permits(g,'archive',method,url,body,{}))
        with bind(g,'archive',URL,KEY,'COMMIT_COOL',body=b'<BlockList/>',blob_md5=base64.b64encode(b'x'*16).decode()) as (_,_,headers):
            self.assertEqual(headers['x-ms-access-tier'],'Cool');self.assertEqual(headers['if-none-match'],'*')
            self.assertIn('content-md5',headers)


if __name__=='__main__':unittest.main()
