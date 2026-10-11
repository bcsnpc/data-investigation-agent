import copy,json,runpy,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path.cwd();sys.path[:0]=[str(ROOT/'scripts')]
H=runpy.run_path(str(Path(__file__).with_name('code_verifier_capture.py')))
PROGRAM="""from pathlib import Path
import copy,json
from types import SimpleNamespace
from investigator import process_tape as journal
from investigator.onboarding import ModelStore,digest
from investigator.flexible_tools import build
from investigator.runtime import Runtime
from investigator.usage_governance import UsageGovernor
from investigator.adapters.code_approval import Controller
from investigator.transformation_approval import read_approval

def perform(b,work,budget_catalog,live):
 s=b['state'];i=s['inputs'];manifest=i['manifest'];p=Path(work)
 store=ModelStore(budget_catalog,p/'inventory.sqlite',s['environment'])
 rt=Runtime(store,b['config'],lambda r:live(r),lambda r:live(r))
 gov=UsageGovernor(rt,b['usage_policy'],lambda:journal.clock('verifier-budget'))
 n=0
 def meter(fn):
  nonlocal n
  n+=1
  return gov.metered_read('verification-test','physical-'+str(n),fn)
 class Route:
  def compile(self,proposal,side,context,cell,precision):
   # Real query request compiler hashes a columns list made from the input
   # mapping, reproducing the production insertion-order failure mechanism.
   schema=i['samples'][0]['schemas']['input-table']
   catalog=[{'id':'input-table','metadata':{'schema_name':'dbo','name':'input_table','type_desc':'USER_TABLE','columns':[{'name':name,'data_type':kind} for name,kind in schema.items()]}}]
   model={'enabled':True,'revision':1,'context_id':context,'workspace':'synthetic-workspace','context':{}}
   plan={'model_id':'synthetic-model','revision':1,'context_id':context,'query':'SELECT SUM(amount) AS quantity FROM dbo.input_table','max_rows':20}
   return build(SimpleNamespace(get=lambda identity:model),plan,{'fabric':{'workspace_id':'synthetic-workspace'}},'bounded_fabric_sql',catalog=catalog)
  def execute(self,side,plan):
   result=meter(lambda:journal.bounded_call('verification_probe',{'side':side},lambda:live(side)))
   result['evidence']['request_hash']=digest(plan)
   result['evidence']['catalog_hash']=plan['catalog_hash']
   return result
 c=Controller(manifest,p/'estate.json',p,meter=meter,route_factory=lambda sample:Route())
 approval=read_approval(c.destination,manifest)
 result=c.infer(i['samples'])
 return {'approval':approval,'reader':result,'charged':gov.snapshot()['read_allowance']['ordinary_charged']}
"""
class Tests(unittest.TestCase):
 def test_real_controller_complete_inference_ledger_and_budget_exact_replay(self):
  import test_flexible_investigation as f
  import test_lineage_binding as pf
  from investigator.adapters.code_approval import Controller
  from investigator.usage_governance import UsageGovernor
  h=f.DynamicTests();h.setUp();self.addCleanup(h.doCleanups)
  policy={'environment':h.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':50,'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
  UsageGovernor(h.runtime,policy,lambda:1000)
  v,_=pf.BindingTests().verification();sample={k:v[k] for k in ('proposal','context','cell','precision')};edge=v['proposal']['boundary']
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);program=p/'program.py';program.write_text(PROGRAM)
   unit=p/'unit.py';unit.write_text("a=spark.table('input-table')\na.write.format('delta').mode('overwrite').save('output-table')\n")
   manifest={'layers':[],'lineage':{'bindings':[dict(edge,provenance='DECLARED_BY_CONFIGURATION')],'code_sources':[{'id':'code-item','kind':'LOCAL_PATH','identity':'reader','path':'.'}],'code_locations':[dict(edge,may_infer_from_code=True,locations=[{'source':'code-item','path':'unit.py'}])]}}
   class Route:
    def compile(self,*args):return None
    def execute(self,side,plan):return copy.deepcopy(v['observations'][0 if side=='TARGET' else 1])
   c=Controller(manifest,p/'estate.json',p,meter=None,route_factory=lambda sample:Route());c.approve([sample]);(p/'estate.json').write_text(json.dumps(manifest))
   request={'boundary':edge,'source':'code-item','path':'unit.py','target_table':v['proposal']['target']['table'],'schemas':{'input-table':{'zzz':'int','amount':'int'}},**{k:sample[k] for k in ('context','cell','precision')}}
   capture=H['Capture'](p/'capture',inputs={'manifest':manifest,'samples':[request],'session_id':'verification-test','engine_fingerprint':'synthetic','enterprise_context':'synthetic','enabled_model_contexts':{'synthetic-model':v['context']}},config={},policy=policy,engine_hash='synthetic',program=program,files={'unit.py':unit,'estate.json':p/'estate.json','estate.lineage-approval.json':c.destination,'estate.lineage.jsonl':c.ledger.path},databases={'catalog.sqlite':h.store.database,'inventory.sqlite':h.store.inventory},environment=h.store.environment,context_identity='synthetic',profile_member='estate.lineage.jsonl')
   calls=[]
   self.assertEqual(list(capture.tape.bootstrap['state']['inputs']['samples'][0]['schemas']['input-table']),['amount','zzz'])
   def live(side):calls.append(side);return copy.deepcopy(v['observations'][0 if side=='TARGET' else 1])
   expected=capture.execute(live);self.assertEqual(calls,['TARGET','SOURCE','TARGET','SOURCE']);self.assertEqual(expected['result']['reader']['boundaries'][0]['verifications'][0]['status'],'VERIFIED')
   actual=H['replay'](p/'capture',p/'replay');self.assertTrue(actual['matched']);self.assertEqual(actual['result'],expected['result']);self.assertEqual(actual['profile_identity'],expected['profile_identity']);self.assertIsNotNone(actual['profile_identity']['sha256']);self.assertEqual((p/'capture/working/estate.lineage.jsonl').read_bytes(),(p/'replay/estate.lineage.jsonl').read_bytes())
   self.assertEqual(expected['accounting']['physical_requests'],5);self.assertEqual(expected['accounting']['control_requests'],0)
   isolated=runpy.run_path(str(Path(__file__).with_name('code_verifier_revision.py')))['replay_code_verifier_revision'](capture.tape.path,p/'isolated',capture.tape.engine_revision,repository=ROOT)
   self.assertTrue(isolated['matched']);self.assertEqual(isolated['profile_identity'],expected['profile_identity']);self.assertEqual(isolated['result'],expected['result'])
   publication=runpy.run_path(str(Path(__file__).with_name('publish_verifier_profile.py')))
   from investigator.lineage_binding import seal
   current={'engine_hash':'synthetic','context_identity':'synthetic','model_contexts':{'synthetic-model':v['context']},'manifest_hash':seal(manifest),'config_hash':seal({})}
   receipt=p/'isolated/portable-replay-summary.json';receipt_sha=H['sha'](receipt);baseline=c.ledger.path.read_bytes()
   with self.assertRaisesRegex(ValueError,'CURRENT_ENGINE_CONTEXT_CONFIG_DIFFERS'):publication['publish'](p/'capture',c.ledger.path,receipt,lambda:dict(current,engine_hash='changed'),p/'rejected.json',replay_receipt_sha256=receipt_sha)
   self.assertEqual(c.ledger.path.read_bytes(),baseline)
   c.ledger.path.write_bytes(baseline+b'other writer\n')
   with self.assertRaisesRegex(ValueError,'NATIVE_PREFIX_CHANGED'):publication['publish'](p/'capture',c.ledger.path,receipt,lambda:current,p/'race.json',replay_receipt_sha256=receipt_sha)
   c.ledger.path.write_bytes(baseline)
   published=publication['publish'](p/'capture',c.ledger.path,receipt,lambda:current,p/'published.json',replay_receipt_sha256=receipt_sha)
   self.assertEqual(published['status'],'PROFILE_APPEND_ACCEPTED');self.assertEqual(published['added_entries'],2);self.assertTrue(c.ledger.path.read_bytes().startswith(baseline));self.assertEqual(c.ledger.path.read_bytes(),(p/'capture/working/estate.lineage.jsonl').read_bytes());self.assertEqual(published['verification_pins']['evidence_profile_path'],str(c.ledger.path.resolve()))
   with self.assertRaisesRegex(ValueError,'PUBLICATION_RECEIPT_EXISTS'):publication['publish'](p/'capture',c.ledger.path,receipt,lambda:current,p/'published.json',replay_receipt_sha256=receipt_sha)
   failed_inputs=copy.deepcopy(capture.tape.bootstrap['state']['inputs']);failed_inputs['samples'][0]['path']='not-authorized.py';failed_inputs['session_id']='failed-verification'
   # This program's fixed synthetic physical session is not reached on refusal.
   failed=H['Capture'](p/'failure',inputs=failed_inputs,config={},policy=policy,engine_hash='synthetic',program=program,files={'unit.py':unit,'estate.json':p/'estate.json','estate.lineage-approval.json':c.destination,'estate.lineage.jsonl':c.ledger.path},databases={'catalog.sqlite':h.store.database,'inventory.sqlite':h.store.inventory},environment=h.store.environment,context_identity='synthetic',profile_member='estate.lineage.jsonl')
   failed_final=failed.execute(lambda side:self.fail('Unauthorized Controller must not probe'))
   self.assertEqual(failed_final['status'],'FAILED');self.assertEqual(failed_final['error']['error_type'],'ValueError');self.assertEqual(failed_final['accounting']['physical_requests'],0)
   failed_replay=runpy.run_path(str(Path(__file__).with_name('code_verifier_revision.py')))['replay_code_verifier_revision'](failed.tape.path,p/'failed-isolated',failed.tape.engine_revision,repository=ROOT)
   self.assertTrue(failed_replay['matched_failure']);self.assertEqual(failed_replay['error'],failed_final['error'])
   fr=p/'failed-isolated/portable-replay-summary.json'
   with self.assertRaisesRegex(ValueError,'EXACT_REPLAY_REQUIRED'):publication['publish'](p/'failure',c.ledger.path,fr,lambda:current,p/'failed-publication.json',replay_receipt_sha256=H['sha'](fr))
   (p/'capture/unit.py').write_text('changed')
   with self.assertRaisesRegex(ValueError,'VERIFIER_MEMBER_CHANGED'):H['replay'](p/'capture',p/'tamper')
 def test_large_legacy_tape_refused_before_load(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'large.json'
   with p.open('wb') as f:f.truncate(64*1024*1024+1)
   h=runpy.run_path(str(Path(__file__).with_name('code_verifier_revision.py')))
   with self.assertRaisesRegex(ValueError,'SEPARATE_LARGE_TAPE_CLASS_REQUIRED'):h['replay_code_verifier_revision'](p,Path(td)/'out','a'*40,repository=ROOT)
if __name__=='__main__':unittest.main()
