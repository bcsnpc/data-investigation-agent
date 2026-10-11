import copy,runpy,unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
T=runpy.run_path(str(Path(__file__).with_name('test_replay_suite.py')))
M=T['M']
class Tests(unittest.TestCase):
 setUp=T['Tests'].setUp
 tearDown=T['Tests'].tearDown
 run_suite=T['Tests'].run_suite
 metadata_case=T['Tests'].metadata_case
 def split(self,op):
  ref=op['catalog'];src=M['member'](self.members,ref);dest=self.members/'catalog-shard'/ref['member'];dest.parent.mkdir(parents=True);dest.write_bytes(src.read_bytes())
  self.suite['assets'].append({'id':'catalog-shard','url':'https://github.com/o/r/releases/download/immutable/cat','ciphertext_sha256':'e'*64,'inventory':{ref['member']:ref['sha256']}});op['catalog']={**ref,'asset':'catalog-shard'}
 def test_ordinary_split_shard_reaches_replay_with_exact_sibling(self):
  op=self.suite['operations'][0];self.split(op);calls=[]
  def replay(path,*args,**kwargs):
   self.assertTrue((path.parent/'catalog.sqlite').is_file());calls.append(path);return {'matched':True}
  result=self.run_suite(replay=replay);self.assertTrue(result['roster_matched']);self.assertEqual(len(calls),2)
 def test_mutating_sealed_catalog_is_not_a_success(self):
  self.split(self.suite['operations'][0])
  def replay(path,*a,**k):(path.parent/'catalog.sqlite').write_bytes(b'changed');return {'matched':True}
  result=self.run_suite(replay=replay);self.assertFalse(result['roster_matched']);self.assertEqual(result['counts']['CAPTURE_CHANGED_DURING_REPLAY'],2)
 def metadata_split(self,v2):
  op=self.metadata_case();self.split(op)
  if v2:
   op['dispatcher']=M['METADATA_V2_DISPATCHER'];self.suite['consumer_hashes'].pop('acceptance/round_thirteen/metadata_revision.py')
   self.suite['consumer_hashes'].update({n:{'git_blob_sha256':'b'*64,'checkout_sha256':{'LF':'b'*64,'CRLF':'c'*64}} for n in M['METADATA_V2_CONSUMERS']})
  def replay(path,*a,**k):
   self.assertTrue((path.parent/'catalog.sqlite').is_file());self.assertTrue((path.parent/'metadata_capture.py').is_file());return {'matched':True}
  fake=SimpleNamespace(replay_metadata_revision=replay,replay_metadata_v2_revision=replay)
  loader=lambda path:SimpleNamespace(engine_revision=None,bootstrap={'config':{},'state':{'engine_revision':'d'*40},'entry_point':'billing_metadata_collection'})
  # Versioned handler invocation seam; no child/provider/socket/auth calls.
  original_sha=M['run'].__globals__['sha']
  hash_fn=lambda p:'f'*64 if Path(p).name in ('metadata_worker_v2.py','replay_metadata_v2.py') else original_sha(p)
  with patch('importlib.util.spec_from_file_location',lambda *a:SimpleNamespace(loader=SimpleNamespace(exec_module=lambda m:None))),patch('importlib.util.module_from_spec',lambda s:fake),patch.dict(M['run'].__globals__,{'sha':hash_fn}):
   result=self.run_suite(loader=loader)
  self.assertTrue(result['roster_matched'])
 def test_metadata_v1_split_shard_reaches_handler(self):self.metadata_split(False)
 def test_metadata_v2_split_shard_reaches_handler(self):self.metadata_split(True)
if __name__=='__main__':unittest.main()
