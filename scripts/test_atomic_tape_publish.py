import json,runpy,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'scripts')
from investigator.privacy_projection import Projection,canonical
from investigator.privacy_tape import PrivacyTape
from investigator.atomic_tape_publish import publish
import investigator.atomic_tape_publish as atomic
helper={'os':atomic.os,'time':atomic.time}
class Tests(unittest.TestCase):
 def test_observer_sees_old_complete_destination_until_atomic_commit(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'tape.json';old=b'{"old":true}';new=b'{"new":true}';path.write_bytes(old)
   import os
   original=os.replace
   def observe(stage,target):
    self.assertEqual(path.read_bytes(),old);self.assertEqual(Path(stage).parent,path.parent);self.assertEqual(Path(stage).read_bytes(),new)
    return original(stage,target)
   with patch.object(helper['os'],'replace',side_effect=observe):publish(path,new)
   self.assertEqual(path.read_bytes(),new);self.assertEqual(list(path.parent.iterdir()),[path])
 def test_publication_failure_preserves_old_seal_and_cleans_stage(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'tape.json';path.write_bytes(b'unchanged-seal')
   with patch.object(helper['os'],'replace',side_effect=OSError('synthetic publish refused')):
    with self.assertRaises(OSError):publish(path,b'new-seal')
   self.assertEqual(path.read_bytes(),b'unchanged-seal');self.assertEqual(list(path.parent.iterdir()),[path])
 def test_projected_path_remains_memory_only_and_exclusive_without_raw_temp(self):
  raw='PRIVATE SYNTHETIC PERSON';column='column://synthetic/person_name'
  policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1','estate_id':'synthetic-estate','key_reference':'synthetic/key','columns':[column]}
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'tape.json';projection=Projection(policy,lambda _:b'synthetic-in-memory-key-32-bytes!!');tape=PrivacyTape(path,projection)
   tape.event('RESPONSE',canonical({'columns':[column],'rows':[[raw]]}))
   self.assertEqual(list(path.parent.iterdir()),[])
   tape.finish({'text':raw});self.assertNotIn(raw.encode(),path.read_bytes());self.assertEqual(list(path.parent.iterdir()),[path])
   # Atomic exact-tape helper never intercepts privacy's projection/exclusive writer.
   with self.assertRaises(Exception):PrivacyTape(path,projection)
 def test_native_windows_share_contention_retries_same_stage_then_succeeds(self):
  if helper['os'].name!='nt':self.skipTest('Windows-specific retry')
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'tape.json';path.write_bytes(b'old');stages=[];original=helper['os'].replace
   def replace(stage,target):
    stages.append(str(stage))
    if len(stages)<3:
     error=PermissionError(13,'synthetic share contention');error.winerror=32;raise error
    return original(stage,target)
   with patch.object(helper['os'],'replace',side_effect=replace):publish(path,b'new')
   self.assertEqual(len(set(stages)),1);self.assertEqual(path.read_bytes(),b'new');self.assertEqual(list(path.parent.iterdir()),[path])
 def test_permanent_native_block_is_bounded_and_old_seal_preserved(self):
  if helper['os'].name!='nt':self.skipTest('Windows-specific retry')
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'tape.json';path.write_bytes(b'old');clock=[0.0];waits=[]
   error=PermissionError(13,'synthetic share contention');error.winerror=5
   def wait(seconds):waits.append(seconds);clock[0]+=seconds
   with patch.object(helper['os'],'replace',side_effect=error),patch.object(helper['time'],'monotonic',side_effect=lambda:clock[0]),patch.object(helper['time'],'sleep',side_effect=wait):
    with self.assertRaises(PermissionError) as raised:publish(path,b'new')
   self.assertIs(raised.exception,error);self.assertLessEqual(clock[0],1.001);self.assertTrue(all(0<s<=.05 for s in waits));self.assertEqual(path.read_bytes(),b'old');self.assertEqual(list(path.parent.iterdir()),[path])
if __name__=='__main__':unittest.main()
