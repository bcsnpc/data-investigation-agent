import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import gzip

from investigator import archive_migration as archive
from investigator.artifact_store import ArtifactError, Files, LocalObjects, canonical, digest
from investigator.process_tape import Tape, bytes_of


class Remote:
    def __init__(self,corrupt=False):self.calls=[];self.data={};self.tiers={};self.corrupt=corrupt
    def upload_hot(self,key,path):
        self.calls.append('upload_hot');self.data[key]=path.read_bytes();self.tiers[key]='Hot'
    def download_chunks(self,key):
        self.calls.append('download');yield self.data[key]+(b'bad' if self.corrupt else b'')
    def properties(self,key):return {'tier':self.tiers[key],'etag':'etag-'+self.tiers[key]}
    def archive(self,key,etag):
        assert etag=='etag-Hot'
        self.calls.append('archive');self.tiers[key]='Archive'


class CompressedRemote(Remote):
    def upload_hot(self,key,path,encoding='identity'):
        self.calls.append('upload_hot');stats={}
        self.data[key]=b''.join(archive.encoded_chunks(path,encoding,stats));self.tiers[key]='Hot'
        return stats
    def download_chunks(self,key):
        self.calls.append('download')
        data=self.data[key]
        if self.corrupt:data=data[:-3]+b'bad'
        for start in range(0,len(data),17):yield data[start:start+17]


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def put(self,path,body=b'fixture evidence'):
        target=self.root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body);return target
    def plan(self,paths,protected=None):
        return archive.plan(self.root,paths,protected=protected or [],finished_statement='Owner: finished rounds, no active workers')
    def review(self,manifest):
        identity=digest(canonical(manifest))
        return identity,{'status':'APPROVED','manifest_sha256':identity,'reviewer':'owner','basis':'Fixture-only content examined'}

    def test_plan_protects_shared_state_and_quarantines_credentials(self):
        names=['.local/round-thirteen/model-spend.sqlite','.local/round-nine/catalog.sqlite',
               '.local/round-seven/shared.sqlite','.local/round-nine/secret.json',
               '.local/round-nine/config.json','.local/round-sixteen/tape.json','.local/round-five/receipt.json']
        for path in names:self.put(path,b'password=really-private-value' if path.endswith('config.json') else b'fixture')
        result=self.plan(names,['.local/round-seven/shared.sqlite'])
        self.assertEqual([e['path'] for e in result['entries']],['.local/round-five/receipt.json'])
        self.assertEqual(len(result['excluded']),6)
        self.assertEqual(result['privacy_status'],'QUARANTINED_PENDING_REVIEW')

    def test_explicit_sha_and_review_required(self):
        self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);path=self.put('manifest.json',canonical(plan))
        sha,review=self.review(plan)
        self.assertEqual(archive.load_pinned(path,sha),plan)
        with self.assertRaisesRegex(ArtifactError,'SHA_DIFFERS'):archive.load_pinned(path,'0'*64)
        remote=Remote()
        with self.assertRaisesRegex(ArtifactError,'PRIVACY_REVIEW'):archive.publish(plan,sha,{},remote)
        self.assertEqual(remote.calls,[])

    def test_hot_download_hash_then_archive_receipt_then_cleanup_script(self):
        self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);sha,review=self.review(plan);remote=Remote()
        receipt=archive.publish(plan,sha,review,remote)
        self.assertEqual(remote.calls,['upload_hot','download','archive'])
        row=receipt['objects'][0];self.assertEqual(row['tier'],'Archive')
        self.assertEqual(row['sha256'],row['download_verified_sha256']);self.assertEqual(row['etag'],'etag-Archive')
        script=archive.cleanup_script(plan,sha,receipt)
        self.assertIn('Get-FileHash',script);self.assertIn('ReparsePoint',script)
        self.assertIn('Remove-Item -LiteralPath',script);self.assertNotIn('-Recurse',script)
        self.assertTrue((self.root/'.local/round-five/receipt.json').exists())

    def test_remote_corruption_never_archives_or_permits_cleanup(self):
        self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);sha,review=self.review(plan);remote=Remote(corrupt=True)
        with self.assertRaisesRegex(ArtifactError,'REMOTE_HASH'):archive.publish(plan,sha,review,remote)
        self.assertNotIn('archive',remote.calls)

    def test_remote_etag_change_after_download_never_archives(self):
        self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);sha,review=self.review(plan);remote=Remote()
        original=remote.properties
        def changed(key):
            result=original(key)
            if 'download' in remote.calls:result['etag']='changed'
            return result
        remote.properties=changed
        with self.assertRaisesRegex(ArtifactError,'OBJECT_CHANGED'):
            archive.publish(plan,sha,review,remote)
        self.assertNotIn('archive',remote.calls)

    def test_changed_local_file_and_outside_path_refused(self):
        path=self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);sha,review=self.review(plan)
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(ArtifactError,'LOCAL_HASH'):archive.publish(plan,sha,review,Remote())
        with self.assertRaises(ArtifactError):self.plan(['../escape'])

    def test_unsealed_catalog_cannot_hide_in_a_tape_directory(self):
        self.put('.local/process-tapes/active/catalog.sqlite')
        result=self.plan(['.local/process-tapes/active/catalog.sqlite'])
        self.assertEqual(result['entries'],[])
        self.assertEqual(result['excluded'][0]['reason'],'SNAPSHOT_WITHOUT_VALID_SEALED_TAPE')

    def test_manifest_mutation_after_review_is_not_accepted(self):
        self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);sha,review=self.review(plan)
        plan['finished_statement']='changed after review'
        with self.assertRaisesRegex(ArtifactError,'MANIFEST_SHA_DIFFERS'):
            archive.publish(plan,sha,review,Remote())

    def test_receipt_cannot_add_a_file_or_lie_about_tier(self):
        self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);sha,review=self.review(plan)
        receipt=archive.publish(plan,sha,review,Remote());receipt['objects'][0]['tier']='Hot'
        with self.assertRaisesRegex(ArtifactError,'NOT_VERIFIED'):archive.cleanup_script(plan,sha,receipt)

    def test_conversion_restores_bytes_but_does_not_claim_engine_replay(self):
        folder=self.root/'original';folder.mkdir()
        for name in ('catalog.sqlite','inventory.sqlite'):(folder/name).write_bytes(b'synthetic snapshot')
        tape=Tape(folder/'tape.json',{'entry_point':'synthetic','context_identity':'test','config':{},'profile':{},
                   'usage_policy':{},'engine_hash':'test','state':{}})
        tape.event('BOUNDED_REQUEST',bytes_of({'x':1}))
        tape.event('BOUNDED_RESPONSE',bytes_of({'x':2}));tape.finish({'status':'COMPLETED'})
        before={p.name:p.read_bytes() for p in folder.iterdir()}
        result=archive.convert_tape(folder,Files(LocalObjects(self.root/'objects')))
        self.assertEqual(result['verification']['byte_restoration'],'PASSED')
        self.assertEqual(result['verification']['engine_replay'],'NOT_RUN')
        self.assertEqual(before,{p.name:p.read_bytes() for p in folder.iterdir()})

    def test_gzip_stream_verifies_original_and_reports_both_sizes(self):
        raw=b'synthetic fixture values\n'*(150000)
        source=self.put('.local/round-five/receipt.json',raw)
        plan=archive.plan(self.root,['.local/round-five/receipt.json'],protected=[],finished_statement='Finished',storage_encoding='gzip')
        sha,review=self.review(plan);remote=CompressedRemote()
        receipt=archive.publish(plan,sha,review,remote)
        row=receipt['objects'][0]
        self.assertEqual(row['storage_encoding'],'gzip');self.assertTrue(row['blob'].endswith('.gz'))
        self.assertEqual(receipt['original_bytes'],len(raw));self.assertEqual(row['original_bytes'],len(raw))
        self.assertLess(receipt['stored_bytes'],len(raw)//10)
        self.assertEqual(row['stored_sha256'],digest(remote.data[row['blob']]))
        self.assertEqual(gzip.decompress(remote.data[row['blob']]),raw)
        self.assertEqual(source.read_bytes(),raw)
        self.assertIn('Remove-Item -LiteralPath',archive.cleanup_script(plan,sha,receipt))
        row.pop('stored_sha256')
        with self.assertRaises(ArtifactError):archive.cleanup_script(plan,sha,receipt)

    def test_gzip_corruption_prevents_archive(self):
        self.put('.local/round-five/receipt.json',b'fixture'*100)
        plan=archive.plan(self.root,['.local/round-five/receipt.json'],protected=[],finished_statement='Finished',storage_encoding='gzip')
        sha,review=self.review(plan);remote=CompressedRemote(corrupt=True)
        with self.assertRaisesRegex(ArtifactError,'GZIP_CORRUPT'):archive.publish(plan,sha,review,remote)
        self.assertNotIn('archive',remote.calls)

    def test_gzip_bounds_hash_truncation_and_extra_members(self):
        raw=b'original'*300000;encoded=gzip.compress(raw,mtime=0)
        entry={'bytes':len(raw),'sha256':digest(raw)}
        for altered,expected,reason in (
            (encoded,{**entry,'bytes':len(raw)-1},'SIZE_EXCEEDED'),
            (encoded,{**entry,'bytes':len(raw)+1},'HASH_DIFFERS'),
            (encoded,{**entry,'sha256':'0'*64},'HASH_DIFFERS'),
            (encoded[:-1],entry,'INCOMPLETE'),
            (encoded+gzip.compress(b'',mtime=0),entry,'TRAILING_BYTES')):
            with self.subTest(reason=reason),self.assertRaisesRegex(ArtifactError,reason):
                archive.verify_download(iter([altered]),'gzip',expected)

    def test_encoder_reads_bounded_chunks_and_no_temporary_archive(self):
        path=self.put('input',b'x'*(archive.STREAM_BLOCK*3));stats={}
        with patch.object(Path,'read_bytes',side_effect=AssertionError('Whole file read forbidden')):
            parts=list(archive.encoded_chunks(path,'gzip',stats))
        self.assertEqual(gzip.decompress(b''.join(parts)),b'x'*(archive.STREAM_BLOCK*3))
        self.assertTrue(stats['stream_complete'])
        self.assertEqual(list(self.root.iterdir()),[path])

    def test_old_raw_manifest_and_receipt_remain_usable(self):
        self.put('.local/round-five/receipt.json')
        plan=self.plan(['.local/round-five/receipt.json']);self.assertNotIn('storage_encoding',plan)
        sha,review=self.review(plan);receipt=archive.publish(plan,sha,review,Remote())
        row=receipt['objects'][0]
        for key in ('storage_encoding','original_bytes','stored_bytes','stored_sha256'):row.pop(key)
        self.assertIn('Get-FileHash',archive.cleanup_script(plan,sha,receipt))


if __name__=='__main__':unittest.main()
