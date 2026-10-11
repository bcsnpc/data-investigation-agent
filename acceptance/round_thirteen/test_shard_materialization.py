import hashlib,runpy,tempfile,unittest
from pathlib import Path
M=runpy.run_path(str(Path(__file__).with_name('replay_suite.py')))
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.out=self.root/'out';self.out.mkdir();self.members=self.root/'members';self.refs={}
  for i,name in enumerate(('tape.json','catalog.sqlite','metadata_capture.py','catalog-after.sqlite')):
   p=self.members/str(i)/'native'/name;p.parent.mkdir(parents=True);p.write_bytes(name.encode());self.refs[name]={'asset':str(i),'member':'native/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  self.op={'id':'one','tape':self.refs['tape.json'],'catalog':self.refs['catalog.sqlite'],'capture_support':{'metadata_capture.py':self.refs['metadata_capture.py']},'after_artifacts':{'catalog-after.sqlite':self.refs['catalog-after.sqlite']}}
 def tearDown(self):self.tmp.cleanup()
 def test_separate_shards_assemble_exact_siblings_with_originals_unchanged(self):
  before={n:M['member'](self.members,r).read_bytes() for n,r in self.refs.items()};capture=M['materialize_capture'](self.members,self.op,self.out)
  for n,raw in before.items():
   self.assertEqual((capture/n).read_bytes(),raw);self.assertEqual(M['member'](self.members,self.refs[n]).read_bytes(),raw)
  self.assertEqual((capture/'tape.json').parent,(capture/'catalog.sqlite').parent)
 def test_changed_source_blocks_before_replay(self):
  p=M['member'](self.members,self.refs['catalog.sqlite']);p.write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'SUITE_MEMBER_CHANGED'):M['materialize_capture'](self.members,self.op,self.out)
 def test_wrong_basename_blocks_not_renamed(self):
  self.op['catalog']=self.refs['tape.json']
  with self.assertRaisesRegex(ValueError,'BASENAME'):M['materialize_capture'](self.members,self.op,self.out)
 def test_capture_collision_refused(self):
  self.op['capture_support']['catalog.sqlite']=self.refs['tape.json']
  with self.assertRaisesRegex(ValueError,'COLLISION'):M['materialize_capture'](self.members,self.op,self.out)
if __name__=='__main__':unittest.main()
