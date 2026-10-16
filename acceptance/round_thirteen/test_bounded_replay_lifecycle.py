import tempfile,unittest
from pathlib import Path
from bounded_replay_lifecycle import *
class Tests(unittest.TestCase):
 def test_only_owned_scratch_removed_and_logs_retained(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);original=root/'native.sqlite';original.write_bytes(b'native');old=root/'old';old.mkdir();(old/'keep').write_text('keep')
   assets=[{'id':x,'ciphertext_bytes':10,'uncompressed_bytes':20} for x in ('a','b')]
   suite={'assets':assets,'operations':[{'id':x,'tape':{'asset':x}} for x in ('a','b')]};seen=[]
   def hydrate(repo,s,m):seen.append([a['id'] for a in s['assets']]);m.mkdir();(m/'native.sqlite').write_bytes(b'clone')
   def run(s,m,w,r,operation_ids):
    w.mkdir();(w/'catalog.sqlite').write_bytes(b'mutable');(w/'failure.log').write_text('retained failure');return {'status':'REPLAY_BLOCKED'}
   out=run_bounded(suite,root/'out',root,root,validate=lambda s:None,consumers=lambda r,s:None,hydrate=hydrate,run=run,free=lambda p:10**12,available_memory=lambda:10**12)
   self.assertEqual(seen,[['a'],['b']]);self.assertEqual(len(out['operations']),2)
   self.assertEqual(original.read_bytes(),b'native');self.assertEqual((old/'keep').read_text(),'keep')
   self.assertEqual((root/'out/a/failure.log').read_text(),'retained failure');self.assertFalse((root/'out/a/catalog.sqlite').exists());self.assertFalse(list(root.glob('dia-suite-scratch-*')))
 def test_disk_refusal_never_hydrates(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);s={'assets':[{'id':'a','ciphertext_bytes':1,'uncompressed_bytes':2}], 'operations':[{'id':'a','tape':{'asset':'a'}}]}
   def forbidden(*a,**k):raise AssertionError('must not admit')
   out=run_bounded(s,root/'out',root,root,validate=lambda s:None,consumers=lambda r,s:None,hydrate=forbidden,run=forbidden,free=lambda p:FLOOR,available_memory=lambda:10**12)
   self.assertEqual(out['operations'][0]['status'],'RESOURCE_ADMISSION_REFUSED');self.assertFalse(out['roster_matched'])
 def test_missing_size_and_existing_output_refuse(self):
  with self.assertRaisesRegex(ValueError,'SIZE_PIN'):peak({'assets':[{'id':'a'}]}, {'tape':{'asset':'a'}})
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   with self.assertRaisesRegex(ValueError,'ALREADY_EXISTS'):run_bounded({},root,root,root,validate=lambda s:None,consumers=lambda r,s:None,hydrate=None,run=None)
 def test_hydration_failure_keeps_failure_not_pass(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);s={'assets':[], 'operations':[{'id':'a'}]}
   def bad(*args):raise ValueError('cipher hash mismatch')
   out=run_bounded(s,root/'out',root,root,validate=lambda s:None,consumers=lambda r,s:None,hydrate=bad,run=None,free=lambda p:10**12,available_memory=lambda:10**12)
   self.assertEqual(out['operations'][0]['status'],'REPLAY_TRANSPORT_BLOCKED');self.assertFalse(list(root.glob('dia-suite-scratch-*')))
 def test_large_member_memory_refusal_before_decryption(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);s={'assets':[{'id':'a','ciphertext_bytes':256*1024**2,'uncompressed_bytes':3*1024**3}], 'operations':[{'id':'a','tape':{'asset':'a'}}]}
   def forbidden(*args):raise AssertionError('not admitted')
   out=run_bounded(s,root/'out',root,root,validate=lambda s:None,consumers=lambda r,s:None,hydrate=forbidden,run=forbidden,free=lambda p:10**12,available_memory=lambda:2560*1024**2)
   self.assertEqual(out['operations'][0]['status'],'RESOURCE_ADMISSION_REFUSED');self.assertFalse(out['roster_matched'])
 def test_existing_output_junction_or_symlink_refuses(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/'s';source.mkdir();(source/'data').write_bytes(b'x')
   with patch.object(Path,'is_symlink',return_value=True):
    with self.assertRaisesRegex(ValueError,'SYMLINK'):retain(source,root/'out')
if __name__=='__main__':unittest.main()
