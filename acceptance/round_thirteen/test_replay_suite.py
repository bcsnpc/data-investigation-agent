import copy,hashlib,json,runpy,socket,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
M=runpy.run_path(str(Path(__file__).with_name('replay_suite.py')))
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.members=self.root/'members';self.members.mkdir();self.inventory={}
  for i in (1,2):
   d=self.members/'asset'/str(i);d.mkdir(parents=True)
   for name in ('tape.json','catalog.sqlite','inventory.sqlite'):
    p=d/name;p.write_text(name+str(i));self.inventory[str(i)+'/'+name]=M['sha'](p)
  def ref(i,n):return {'asset':'asset','member':str(i)+'/'+n,'sha256':self.inventory[str(i)+'/'+n]}
  self.suite={'version':M['VERSION'],'consumer_revision':'a'*40,'consumer_hashes':{n:'b'*64 for n in M['CONSUMERS']},'assets':[{'id':'asset','url':'https://github.com/o/r/releases/download/immutable/bundle','ciphertext_sha256':'c'*64,'inventory':self.inventory}],'operations':[{'id':'op'+str(i),'run_id':'run'+str(i),'case':'same-label','operation':'run','producer_revision':'d'*40,'tape_class':'EXACT','expected_status':'MATCHED_CAPTURED_OPERATION','tape':ref(i,'tape.json'),'catalog':ref(i,'catalog.sqlite'),'inventory':ref(i,'inventory.sqlite')} for i in (1,2)]}
  self.suite['consumer_hash_mode']='GIT_BLOB_WITH_DECLARED_TEXT_MATERIALIZATION_V1'
  self.suite['consumer_hashes']={n:{'git_blob_sha256':'b'*64,'checkout_sha256':{'LF':'b'*64,'CRLF':'c'*64}} for n in M['CONSUMERS']}
 def tearDown(self):self.tmp.cleanup()
 def run_suite(self,**kwargs):
  return M['run'](self.suite,self.members,self.root/'out',self.root,replay=kwargs.get('replay',lambda *a,**k:{'matched':True}),load_tape=kwargs.get('loader',lambda p:SimpleNamespace(engine_revision='d'*40,bootstrap={'config':{}})),revision_check=kwargs.get('revision',lambda *a:None),consumer_check=kwargs.get('consumer',lambda *a:None))
 def test_serial_distinct_operation_ids_and_network_refused(self):
  order=[]
  def replay(p,*args,**kw):
   order.append(p.parent.name)
   with self.assertRaisesRegex(RuntimeError,'NETWORK_FORBIDDEN'):socket.create_connection(('localhost',1))
   return {'matched':True}
  result=self.run_suite(replay=replay)
  self.assertEqual(order,['1','2']);self.assertTrue(result['roster_matched']);self.assertEqual(result['counts']['MATCHED_CAPTURED_OPERATION'],2)
 def test_fixed_blocker_retained_not_success_and_partial_map_survives(self):
  op=self.suite['operations'][0];op.update(expected_status='REPLAY_BLOCKED',expected_blocker='TAPE_EVENT_DIFFERS:CLOCK:OPERATION_END')
  def replay(p,*a,**kw):
   if p.parent.name=='1':raise ValueError(op['expected_blocker'])
   return {'matched':True}
  r=self.run_suite(replay=replay);self.assertTrue(r['roster_matched']);self.assertEqual(r['counts']['REPLAY_BLOCKED'],1);self.assertEqual(r['counts']['MATCHED_CAPTURED_OPERATION'],1)
  self.assertTrue((self.root/'out/partial-map.json').exists())
 def test_changed_tape_blocks_without_loader_or_fallback(self):
  (self.members/'asset/1/tape.json').write_text('changed')
  r=self.run_suite();self.assertFalse(r['roster_matched']);self.assertEqual(r['operations'][0]['status'],'REPLAY_BLOCKED')
 def test_changed_during_replay_refuses(self):
  def replay(p,*a,**kw):p.write_text('altered');return {'matched':True}
  r=self.run_suite(replay=replay);self.assertEqual(r['counts']['CAPTURE_CHANGED_DURING_REPLAY'],2)
 def test_missing_revision_is_blocked_no_replay(self):
  calls=[]
  def absent(*a):raise ValueError('SUITE_GIT_REVISION_MISSING')
  r=self.run_suite(revision=absent,replay=lambda *a,**k:calls.append(a));self.assertFalse(calls);self.assertEqual(r['counts']['REPLAY_BLOCKED'],2)
 def test_missing_member_has_no_fallback(self):
  (self.members/'asset/1/catalog.sqlite').unlink();r=self.run_suite();self.assertIn('SUITE_MEMBER_MISSING',r['operations'][0]['error_message'])
 def test_required_manifest_missing_when_inference_enabled(self):
  loader=lambda p:SimpleNamespace(engine_revision='d'*40,bootstrap={'config':{'_estate':{'lineage':{'code_locations':[{'may_infer_from_code':True}]}}}})
  r=self.run_suite(loader=loader);self.assertEqual(r['counts']['REPLAY_BLOCKED'],2);self.assertIn('MANIFEST_MISSING',r['operations'][0]['error_message'])
 def test_consumer_mismatch_preserved_as_preflight_failure(self):
  def bad(*a):raise ValueError('CANONICAL_CONSUMER_HASH_MISMATCH')
  r=self.run_suite(consumer=bad);self.assertEqual(r['status'],'SUITE_PREFLIGHT_BLOCKED');self.assertTrue((self.root/'out/final-map.json').exists())
 def test_traversal_and_collision_refused(self):
  for path in ('../tape','C:/tape','/tape','folder\\tape','folder/./tape'):
   with self.assertRaises(ValueError):M['relative'](path)
  self.suite['operations'][1]['id']='op1'
  with self.assertRaisesRegex(ValueError,'COLLISION'):M['validate'](self.suite)
 def test_missing_capture_counted_separately(self):
  self.suite['operations'][0].update(tape=None,catalog=None,inventory=None,expected_status='MISSING_CAPTURE')
  r=self.run_suite();self.assertTrue(r['roster_matched']);self.assertEqual(r['counts']['MISSING_CAPTURE'],1)
 def test_consumer_checkout_exact_declared_materialization_and_content_tamper(self):
  raw=b'line\nembedded\rcontent\n';digest=lambda b:hashlib.sha256(b).hexdigest()
  for n in M['CONSUMERS']:
   p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw.replace(b'\n',b'\r\n'))
   self.suite['consumer_hashes'][n]={'git_blob_sha256':digest(raw),'checkout_sha256':{'LF':digest(raw),'CRLF':digest(raw.replace(b'\n',b'\r\n'))}}
  def git(command,**kw):return 'a'*40 if command[1]=='rev-parse' else raw
  with patch('subprocess.check_output',git):M['consumers'](self.root,self.suite)
  name=next(iter(M['CONSUMERS']));(self.root/name).write_bytes(raw.replace(b'\rcontent',b'content'))
  with patch('subprocess.check_output',git),self.assertRaisesRegex(ValueError,'CHECKOUT_HASH_MISMATCH'):M['consumers'](self.root,self.suite)
 def test_decryptor_refuses_ciphertext_tamper_before_decryption(self):
  decrypt=runpy.run_path(str(Path.cwd()/'acceptance/known_domain/private_bundle.py'))['hydrate'];p=self.root/'ciphertext';p.write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'HASH_MISMATCH_BEFORE_DECRYPTION'):decrypt(p,'0'*64,b'x'*32,self.root/'decrypted')
 def metadata_case(self):
  op=self.suite['operations'][0];op.update(dispatcher=M['METADATA_DISPATCHER'],operation='billing_metadata_collection')
  self.suite['operations']=[op]
  self.suite['consumer_hashes']['acceptance/round_thirteen/metadata_revision.py']={'git_blob_sha256':'b'*64,'checkout_sha256':{'LF':'b'*64,'CRLF':'c'*64}}
  refs={}
  for n in ('metadata_capture.py','replay_metadata.py','catalog-after.sqlite','inventory-after.sqlite'):
   p=self.members/'asset/1'/n;p.write_text('synthetic sealed '+n);self.inventory['1/'+n]=M['sha'](p)
   refs[n]={'asset':'asset','member':'1/'+n,'sha256':self.inventory['1/'+n]}
  op['capture_support']={n:refs[n] for n in ('metadata_capture.py','replay_metadata.py')}
  op['after_artifacts']={n:refs[n] for n in ('catalog-after.sqlite','inventory-after.sqlite')}
  return op
 def test_metadata_support_and_canonical_handler_required(self):
  op=self.metadata_case();M['validate'](self.suite)
  del self.suite['consumer_hashes']['acceptance/round_thirteen/metadata_revision.py']
  with self.assertRaisesRegex(ValueError,'CONSUMER_SET'):M['validate'](self.suite)
  self.suite['consumer_hashes']['acceptance/round_thirteen/metadata_revision.py']={'git_blob_sha256':'b'*64,'checkout_sha256':{'LF':'b'*64,'CRLF':'c'*64}}
  del op['capture_support']['metadata_capture.py']
  with self.assertRaisesRegex(ValueError,'SUPPORT_OR_AFTER_SET'):M['validate'](self.suite)
 def test_metadata_support_tamper_refuses_before_dispatch(self):
  self.metadata_case();(self.members/'asset/1/metadata_capture.py').write_text('tampered')
  loader=lambda p:SimpleNamespace(engine_revision=None,bootstrap={'config':{},'state':{'engine_revision':'d'*40},'entry_point':'billing_metadata_collection'})
  result=self.run_suite(loader=loader)
  self.assertEqual(result['counts']['REPLAY_BLOCKED'],1);self.assertIn('SUITE_MEMBER_CHANGED',result['operations'][0]['blocker'])
 def verifier_case(self):
  op=self.suite['operations'][0];self.suite['operations']=[op]
  op.update(dispatcher=M['VERIFIER_DISPATCHER'],operation='code_verifier')
  self.suite['consumer_hashes']['acceptance/round_thirteen/code_verifier_revision.py']={'git_blob_sha256':'b'*64,'checkout_sha256':{'LF':'b'*64,'CRLF':'c'*64}}
  refs={n:op[k] for n,k in [('catalog.sqlite','catalog'),('inventory.sqlite','inventory')]}
  for n in ('code_verifier_capture.py','verification_program.py'):
   p=self.members/'asset/1'/n;p.write_text('synthetic sealed '+n);self.inventory['1/'+n]=M['sha'](p)
   refs[n]={'asset':'asset','member':'1/'+n,'sha256':self.inventory['1/'+n]}
  op['dependencies']=refs
  return op
 def test_verifier_dependencies_and_consumer_pin_required(self):
  op=self.verifier_case();M['validate'](self.suite)
  del op['dependencies']['verification_program.py']
  with self.assertRaisesRegex(ValueError,'VERIFIER_DEPENDENCIES'):M['validate'](self.suite)
 def test_verifier_support_tamper_never_replays(self):
  self.verifier_case();(self.members/'asset/1/verification_program.py').write_text('changed')
  result=self.run_suite();self.assertEqual(result['counts']['REPLAY_BLOCKED'],1);self.assertIn('SUITE_MEMBER_CHANGED',result['operations'][0]['blocker'])
if __name__=='__main__':unittest.main()
