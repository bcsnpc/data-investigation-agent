from pathlib import Path
import tempfile,json,unittest
from investigator.archive_migration import plan
from investigator.artifact_store import canonical,digest,ArtifactError
from investigator.streaming_archive_bundle import prepare
from investigator.checksum_archive import publish
from investigator.resumable_archive import Journal
from test_checksum_archive import Remote,URL
from prepare_checksum_cleanup import append_checksum,verify_remote

class Tests(unittest.TestCase):
    def test_checked_proof_members_and_journal_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'.local/round-five/x.json';p.parent.mkdir(parents=True);p.write_bytes(b'fixture')
            manifest=plan(root,[p.relative_to(root).as_posix()],protected=[],finished_statement='synthetic');msha=digest(canonical(manifest))
            bundle,_=prepare(manifest,msha);bsha=digest(canonical(bundle));journal=Journal(root/'journal',bsha,URL);remote=Remote()
            receipt=publish(bundle,bsha,manifest,msha,{'status':'APPROVED','manifest_sha256':msha,'reviewer':'test','basis':'synthetic'},remote,journal,max_stored_bytes=100000)
            def pin(name,data):
                path=root/name;path.write_bytes(data);return {'path':str(path),'sha256':digest(data)}
            mp=pin('manifest',canonical(manifest));rp=pin('receipt',canonical(receipt));jp={'path':str(journal.path),'sha256':digest(journal.path.read_bytes())};bp=pin('bundle',canonical(bundle))
            base={'workspace':str(root),'account_url':URL,'files':[],'blobs':[]}
            result=append_checksum(base,mp,rp,jp,bp,protected_parents=['.local/round-five'])
            self.assertTrue(result['files'][0]['runtime_protected']);self.assertNotIn('readback_sha256',result['blobs'][0])
            self.assertEqual(verify_remote(result,remote)['status'],'UNCHANGED_ARCHIVED_PROOFS')
            remote.md5='different'
            with self.assertRaisesRegex(ArtifactError,'REMOTE_CHANGED'):verify_remote(result,remote)
            p.write_bytes(b'changed')
            with self.assertRaises(ArtifactError):append_checksum(base,mp,rp,jp,bp,protected_parents=[])
            p.write_bytes(b'fixture')
            damaged=journal.path.read_bytes().replace(b'BLOCK_CHECKSUM_VALIDATED',b'BLOCK_CHECKSUM_NOTVALIDD')
            badpin=pin('badjournal',damaged)
            with self.assertRaisesRegex(ArtifactError,'JOURNAL_CHAIN'):append_checksum(base,mp,rp,badpin,bp,protected_parents=[])
            receipt['objects'][0]['sha256']='f'*64
            with self.assertRaisesRegex(ArtifactError,'MEMBER_PROOF'):append_checksum(base,mp,pin('changedreceipt',canonical(receipt)),jp,bp,protected_parents=[])

if __name__=='__main__':unittest.main()
