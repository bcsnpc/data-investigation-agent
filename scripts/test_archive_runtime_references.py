import tempfile,unittest
from pathlib import Path
from archive_runtime_references import reference_ids,held_parents

class Tests(unittest.TestCase):
    def test_stream_boundary_and_duplicate_captures_all_held(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'runtime.json';identity='08086928-0113-4a0c-9c4e-8061f3980b14'
            p.write_bytes(b' '*(1024*1024-12)+identity.encode()+b'\n')
            facts=reference_ids([p,p]);self.assertEqual(facts['scanned_files'],1)
            files=['.local/process-tapes/'+identity+'/catalog.sqlite','.local/old-copy/'+identity+'/tape.json','.local/other/cold/tape.json']
            held=held_parents(files,facts['references']);self.assertEqual(len(held),2)
            self.assertNotIn('.local/other/cold',held)

    def test_referenced_capture_excluded_before_body_planning(self):
        from plan_archive_batches import batch
        from investigator.artifact_store import canonical
        import time
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);identity='08086928-0113-4a0c-9c4e-8061f3980b14'
            for name in [identity,'cold']:
                folder=root/'.local/round-five'/name;folder.mkdir(parents=True)
                (folder/'tape.json').write_bytes(canonical({'events':[]}))
            result=batch(root,time.time()+1,max_original_bytes=10000,max_files=20,protected=[],runtime_reference_ids={identity:['current-test.py']})
            self.assertEqual(len(result['entries']),1)
            self.assertIn('/cold/',result['entries'][0]['path'])
            self.assertEqual(result['excluded'][0]['reason'],'CURRENT_RUNTIME_REFERENCE')

if __name__=='__main__':unittest.main()
