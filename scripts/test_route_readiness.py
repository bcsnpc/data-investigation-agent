"""Route admission preserves old evidence while testing current components."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from investigator.estate_readiness import PINS,sha,load_ref
from investigator.route_readiness import VERSION,COMPONENT_VERSIONS,RouteAdmission,assess_route,assess_routes,score_route


class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.pins={k:'original-'+k for k in PINS};self.current=dict(self.pins,engine_hash='unrelated-engine')
  identity=patch('investigator.route_readiness.current_engine_hash',side_effect=lambda:self.current['engine_hash'])
  identity.start();self.addCleanup(identity.stop)
  self.constraints={'kind':'WHOLE_ENTITY_QUANTITY','measure_ids':['measure'],'filters':[],'dimension_ids':[]}
  self.scope={'name':'one-route','assets':['semantic','loaded'],'constraints':self.constraints,'limits':['Versions unaligned']}
  self.original={'status':'READY','scope':self.scope,'stages':[{'stage':'discovery','status':'VERIFIED'}]}
  self.original_check=patch('investigator.route_readiness.assess_named_scope',return_value=self.original)
  self.original_check.start();self.addCleanup(self.original_check.stop)
  self.dedicated=self.save('dedicated',{'entry_point':'code_verifier','engine_hash':'capture-engine'})
  self.native=self.save('native',{'entry_point':'workspace','engine_hash':'native-engine'})
  publication=self.save('publication',{'publication':{'executions':[{'capture_ref':self.dedicated},{'capture_ref':self.native}]}})
  index=self.save('index',{'pins':self.pins,'stages':{'publication':publication}})
  scope=self.save('scope',{'pins':self.pins})
  self.certificate={'version':VERSION,'route':{'id':'one-route','label':'Quantity','measure_id':'measure'},
   'original':{'manifest_ref':self.save('manifest',{}),'index_ref':index,'scope_ref':scope},
   'component_baseline':{'versions':dict(COMPONENT_VERSIONS),'engine_hash':self.pins['engine_hash'],'authority':'COMPONENT_BASELINE_ADOPTION'},
   'verification_tapes':[self.dedicated],'native_witness_tapes':[self.native]}
  # The tape contract itself is already independently tested. Here fixture
  # locators retain real byte hashes while the sealed bootstrap port is mocked.
  def tape(ref,base):
   bootstrap=load_ref(ref,base);return {},bootstrap,ref
  p=patch('investigator.route_readiness._tape',side_effect=tape);p.start();self.addCleanup(p.stop)
  self.replay=Mock(side_effect=lambda ref,old,current,**kw:{'matched':True,'status':'COMPLETED',
   'capture_sha256':ref['sha256'],'recorded_engine_hash':old,'verification_engine_hash':current,
   'network_requests':0,'model_calls':0,'estate_reads':0,'result_sha256':'a'*64})
 def save(self,name,value):
  p=self.root/(name+'.json');p.write_text(json.dumps(value));return {'path':str(p),'sha256':sha(p.read_bytes())}
 def assess(self):
  return assess_route(self.certificate,self.current,replay_verifications=self.replay,output=self.root/'replay')
 def test_unrelated_engine_change_stays_ready_only_after_automatic_replay(self):
  before=copy.deepcopy(self.certificate);result=self.assess()
  self.assertEqual(result['status'],'READY',result);self.replay.assert_called_once()
  self.assertEqual(self.replay.call_args.args[1: ],('capture-engine','unrelated-engine'))
  self.assertEqual(self.certificate,before);self.assertEqual(result['original_pins'],self.pins)
  self.assertTrue(result['revalidation']['required'])
 def test_adapter_semantic_change_requires_new_verification(self):
  with patch.dict(COMPONENT_VERSIONS,adapter='2.0.0'):
   result=self.assess()
  self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['first_missing_step'],'component_versions')
  self.assertIn('REVERIFICATION_REQUIRED',result['detail']);self.replay.assert_not_called()
 def test_mismatching_replay_blocks_route(self):
  self.replay.side_effect=lambda *a,**k:{'matched':False,'status':'MISMATCH'}
  result=self.assess();self.assertEqual(result['status'],'BLOCKED')
  self.assertEqual(result['first_missing_step'],'offline_revalidation')
  self.assertEqual(result['detail'],'ROUTE_VERIFICATION_REPLAY_MISMATCH')
 def test_unchanged_engine_still_rechecks_original_six_stages(self):
  self.current=self.pins;self.assertEqual(self.assess()['status'],'READY');self.replay.assert_not_called()
  self.original['status']='BLOCKED';self.original['stages'][0].update(status='BLOCKED',reason='DISCOVERY_PARTIAL')
  result=self.assess();self.assertEqual(result['first_missing_step'],'discovery');self.assertEqual(result['detail'],'DISCOVERY_PARTIAL')
 def test_changed_context_or_config_does_not_carry(self):
  for pin in ('context_hash','config_hash','manifest_hash','context_identity'):
   with self.subTest(pin=pin):
    self.current=dict(self.pins,engine_hash='new',**{pin:'changed'})
    self.assertEqual(self.assess()['detail'],'CURRENT_ONBOARDING_EVIDENCE_IDENTITY_DIFFERS')
  self.replay.assert_not_called()
 def test_omitting_or_duplicating_original_tape_cannot_be_ready(self):
  for field in ('verification_tapes','native_witness_tapes'):
   original=self.certificate[field]
   for invalid in ([],original*2):
    with self.subTest(field=field,invalid=invalid):
     self.certificate[field]=invalid;self.assertEqual(self.assess()['detail'],'ROUTE_VERIFICATION_TAPE_CONSERVATION_FAILED')
   self.certificate[field]=original
  self.replay.assert_not_called()
 def test_wrong_capture_or_engine_in_replay_receipt_refuses(self):
  valid=self.replay.side_effect
  for field in ('capture_sha256','recorded_engine_hash','verification_engine_hash'):
   self.replay.side_effect=lambda *a,field=field,**k:{**valid(*a,**k),field:'wrong'}
   self.assertEqual(self.assess()['detail'],'ROUTE_VERIFICATION_REPLAY_IDENTITY_DIFFERS')
 def test_missing_or_boolean_zero_counters_are_not_offline_proof(self):
  valid=self.replay.side_effect
  for field in ('network_requests','model_calls','estate_reads'):
   for bad in (False,None,1):
    with self.subTest(field=field,bad=bad):
     self.replay.side_effect=lambda *a,field=field,bad=bad,**k:{**valid(*a,**k),field:bad}
     self.assertEqual(self.assess()['detail'],'ROUTE_VERIFICATION_REPLAY_NOT_OFFLINE')
 def test_replay_exception_is_blocker_not_result(self):
  self.replay.side_effect=RuntimeError('network forbidden')
  self.assertEqual(self.assess()['detail'],'network forbidden')
 def test_original_hash_change_blocks_before_any_replay(self):
  p=Path(self.certificate['original']['manifest_ref']['path']);p.write_text('{"changed":true}')
  self.assertEqual(self.assess()['detail'],'ORIGINAL_RECEIPT_HASH_DIFFERS');self.replay.assert_not_called()
 def test_route_cannot_claim_another_metric(self):
  self.certificate['route']['measure_id']='other';self.assertEqual(self.assess()['detail'],'ROUTE_IDENTITY_NOT_IN_VERIFIED_SCOPE')
 def test_whole_estate_block_does_not_block_exact_ready_route_scoring(self):
  score=Mock(return_value={'passed':True})
  result=assess_routes([self.certificate],self.current,replay_verifications=self.replay,output=self.root/'one',whole_estate={'status':'BLOCKED'})
  self.assertEqual(len(result['ready_routes']),1);self.assertTrue(result['whole_estate']['informational'])
  got=score_route(score,certificate=self.certificate,current_pins=self.current,requested_measure_id='measure',
   requested_scope=self.constraints,requested_assets=['semantic'],replay_verifications=self.replay,output=self.root/'two')
  self.assertEqual(got,{'passed':True})
 def test_unfiltered_route_cannot_score_filtered_or_other_metric_claim(self):
  score=Mock()
  for measure,constraints in [('other',self.constraints),('measure',dict(self.constraints,filters=[{'column':'region','value':'West'}]))]:
   result=score_route(score,certificate=self.certificate,current_pins=self.current,requested_measure_id=measure,
    requested_scope=constraints,requested_assets=['semantic'],replay_verifications=self.replay,output=self.root/'two')
   self.assertEqual(result['scoring'],'NOT_SCORED');self.assertEqual(result['reason'],"this metric isn't onboarded yet")
  score.assert_not_called()
 def test_native_witness_validation_is_not_reported_as_full_current_replay(self):
  result=self.assess();coverage=result['verification_coverage']
  self.assertEqual(coverage['retained_native_witness_tapes'],1)
  self.assertIn('not full current workspace replay',coverage['native_witness_validation'])
 def test_unregistered_metric_is_listed_with_first_missing_step(self):
  inventory=[self.certificate['route'],{'id':'other-route','label':'Another metric','measure_id':'other'}]
  result=assess_routes([self.certificate],self.current,replay_verifications=self.replay,
   output=self.root/'one',route_inventory=inventory,whole_estate={'status':'BLOCKED'})
  self.assertEqual(len(result['routes']),2)
  self.assertEqual(result['routes'][1]['first_missing_step'],'route_evidence_missing')
  self.assertEqual(len(result['ready_routes']),1)
 def admission(self):
  return RouteAdmission(self.certificate,current_identity=lambda:copy.deepcopy(self.current),
   replay_verifications=self.replay,output=self.root/'admitted')
 def admitted_score(self,admission,score):
  return admission.score(score,requested_measure_id='measure',requested_scope=self.constraints,requested_assets=['semantic'])
 def test_actual_engine_fingerprint_cannot_be_spoofed_to_skip_replay(self):
  self.current=self.pins
  with patch('investigator.route_readiness.current_engine_hash',return_value='actual-new-engine'):
   result=self.assess()
  self.assertEqual(result['detail'],'CURRENT_ROUTE_ENGINE_IDENTITY_DIFFERS');self.replay.assert_not_called()
 def test_internal_admission_replays_once_for_two_scores(self):
  admission=self.admission();score=Mock(return_value={'passed':True})
  self.assertEqual(self.admitted_score(admission,score),{'passed':True})
  self.assertEqual(self.admitted_score(admission,score),{'passed':True})
  self.assertEqual(self.replay.call_count,1);self.assertEqual(score.call_count,2)
 def test_internal_admission_refuses_engine_context_and_component_drift(self):
  for field in ('engine_hash','context_hash','config_hash'):
   with self.subTest(field=field):
    self.current=dict(self.pins,engine_hash='unrelated-engine');admission=self.admission()
    self.current[field]='changed';score=Mock()
    self.assertEqual(self.admitted_score(admission,score)['detail'],'CURRENT_ROUTE_IDENTITY_CHANGED');score.assert_not_called()
  self.current=dict(self.pins,engine_hash='unrelated-engine');admission=self.admission();score=Mock()
  with patch.dict(COMPONENT_VERSIONS,adapter='2.0.0'):
   self.assertIn('REVERIFICATION_REQUIRED',self.admitted_score(admission,score)['detail'])
  score.assert_not_called()
 def test_public_ready_report_or_original_certificate_mutation_is_not_authority(self):
  admission=self.admission();public=admission.assessment
  public['scope']['constraints']['filters']=['forged'];public['route']['measure_id']='other'
  self.certificate['route']['measure_id']='other'
  score=Mock(return_value={'passed':True});self.assertEqual(self.admitted_score(admission,score),{'passed':True})
  self.assertEqual(admission.assessment['route']['measure_id'],'measure')
 def test_blocked_internal_admission_cannot_be_promoted_by_public_label(self):
  self.replay.side_effect=lambda *a,**k:{'matched':False,'status':'MISMATCH'}
  admission=self.admission();public=admission.assessment;public['status']='READY';score=Mock()
  self.assertEqual(self.admitted_score(admission,score)['scoring'],'NOT_SCORED');score.assert_not_called()

if __name__=='__main__':unittest.main()
