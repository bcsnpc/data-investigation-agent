import unittest,tempfile,threading
from pathlib import Path
from investigator.run_capture import DurableCapture
from test_unified_runner import HEADER
class ParallelCaptureTests(unittest.TestCase):
 def test_parallel_worker_events_never_acknowledge_an_unpublished_record(self):
  with tempfile.TemporaryDirectory()as folder:
   objects={};entered=threading.Event();release=threading.Event();second=threading.Event();release_second=threading.Event();errors=[]
   def put(key,raw):
    if key.endswith('00000003-worker-lifecycle.json'):
     entered.set();self.assertTrue(release.wait(3))
    if key.endswith('00000004-worker-lifecycle.json'):
     second.set();self.assertTrue(release_second.wait(3))
    if key in objects:self.assertEqual(objects[key],raw)
    objects[key]=raw
   capture=DurableCapture(Path(folder)/'capture',put,run_id='parallel',bootstrap=HEADER)
   def worker(label):
    try:capture.worker_lifecycle({'event':label})
    except BaseException as error:errors.append(error)
   with capture.protocol_publications():
    first=threading.Thread(target=worker,args=('first',));first.start();self.assertTrue(entered.wait(2))
    other=threading.Thread(target=worker,args=('second',));other.start()
    concurrent=second.wait(.15)
    if concurrent:
     # In the unlocked publisher, removing slot0 shifts the second
     # callback's slot1 onto this still-unpublished ordinary record.
     capture.record('physical-result',{'status':'COMPLETED'})
    release.set();first.join(3);release_second.set();other.join(3)
    self.assertFalse(first.is_alive());self.assertFalse(other.is_alive())
    if not concurrent:capture.record('physical-result',{'status':'COMPLETED'})
   self.assertTrue(all(ref['key']in objects for ref in capture.records),'An unpublished evidence record was removed from the pending queue')
   self.assertFalse(concurrent,'A second callback published while the first owned the pending queue')
   self.assertEqual(errors,[])
   self.assertTrue(all(ref['key']in objects for ref in capture.records))
   capture.seal()
if __name__=='__main__':unittest.main()
