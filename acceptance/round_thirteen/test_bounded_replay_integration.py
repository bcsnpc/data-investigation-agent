import runpy,tempfile,unittest,shutil,socket
from pathlib import Path
from types import SimpleNamespace
from bounded_replay_lifecycle import run_bounded
M=runpy.run_path(str(Path(__file__).with_name('replay_suite.py')))
Fixture=runpy.run_path('acceptance/round_thirteen/test_replay_suite.py')['Tests']
class Integration(unittest.TestCase):
 def test_serial_selection_runs_full_validated_contract_and_preserves_blocker(self):
  f=Fixture();f.setUp()
  try:
   s=f.suite;s['assets'][0].update(ciphertext_bytes=128,uncompressed_bytes=1024)
   s['operations'][0].update(expected_status='REPLAY_BLOCKED',expected_blocker='TAPE_EVENT_DIFFERS:CLOCK:OPERATION_END');seen=[]
   def hydrate(repo,part,dest):shutil.copytree(f.members,dest)
   def replay(p,out,rev,**kwargs):
    seen.append(p.parent.name)
    with self.assertRaisesRegex(RuntimeError,'NETWORK_FORBIDDEN'):socket.create_connection(('localhost',1))
    out.mkdir();(out/'catalog.sqlite').write_bytes(b'clone');(out/'receipt.log').write_text('receipt kept')
    if p.parent.name=='1':raise ValueError('TAPE_EVENT_DIFFERS:CLOCK:OPERATION_END')
    return {'matched':True}
   def run(s,m,o,r,operation_ids):return M['run'](s,m,o,r,operation_ids=operation_ids,replay=replay,load_tape=lambda p:SimpleNamespace(engine_revision='d'*40,bootstrap={'config':{}}),revision_check=lambda *a:None,consumer_check=lambda *a:None)
   result=run_bounded(s,f.root/'bounded',f.root,f.root,validate=M['validate'],consumers=lambda *a:None,hydrate=hydrate,run=run,free=lambda p:10**12,available_memory=lambda:10**12)
   self.assertEqual(result['counts']['REPLAY_BLOCKED'],1);self.assertEqual(result['counts']['MATCHED_CAPTURED_OPERATION'],1);self.assertTrue(result['roster_matched']);self.assertEqual(seen,['1','2']);self.assertTrue(all(x['result']['roster_matched'] for x in result['operations']))
   self.assertEqual(result['operations'][0]['result']['counts']['REPLAY_BLOCKED'],1)
   self.assertEqual(result['operations'][1]['result']['counts']['MATCHED_CAPTURED_OPERATION'],1)
   self.assertTrue((f.root/'bounded/op1/op1/receipt.log').is_file());self.assertFalse((f.root/'bounded/op1/op1/catalog.sqlite').exists())
   self.assertFalse(list(f.root.glob('dia-suite-scratch-*')));self.assertTrue((f.members/'asset/1/catalog.sqlite').is_file())
  finally:f.tearDown()
 def test_unknown_selected_operation_refuses(self):
  f=Fixture();f.setUp()
  try:
   with self.assertRaisesRegex(ValueError,'SELECTED_OPERATION_UNKNOWN'):M['run'](f.suite,f.members,f.root/'out',f.root,operation_ids={'absent'})
  finally:f.tearDown()
 def test_cli_hydration_uses_bounded_lifecycle(self):
  import json,sys
  from unittest.mock import patch
  f=Fixture();f.setUp()
  try:
   s=f.suite;s['scratch_lifecycle']='EXCLUSIVE_SERIAL_SHARDS_V1';s['consumer_hashes'][M['BOUNDED_CONSUMER']]={'git_blob_sha256':'b'*64,'checkout_sha256':{'LF':'b'*64,'CRLF':'c'*64}}
   path=f.root/'suite.json';path.write_text(json.dumps(s));g=M['main'].__globals__;original=g['consumers'];g['consumers']=lambda *a:None
   try:
    with patch.object(sys,'argv',['candidate','--suite',str(path),'--output',str(f.root/'out'),'--hydrate','--scratch-parent',str(f.root)]),patch('bounded_replay_lifecycle.run_bounded',return_value={'roster_matched':True,'operations':[]}) as bounded:
     with self.assertRaises(SystemExit) as done:M['main']()
     self.assertEqual(done.exception.code,0);bounded.assert_called_once();self.assertEqual(bounded.call_args.args[2],f.root)
   finally:g['consumers']=original
  finally:f.tearDown()
if __name__=='__main__':unittest.main()
