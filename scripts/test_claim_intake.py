import copy,sqlite3,tempfile,unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.claim_intake import ClaimIntake
from investigator import claim_facts as facts,claim_clarification as policy
from investigator.onboarding import digest,Conflict

CAT={'models':[{'id':'model','measures':[{'id':'quantity','name':'Quantity'}],'reports':[{'id':'report','name':'Activity Report'}],
 'visuals':[{'target_id':'card','report_id':'report','page_id':'page','names':['Global card'],'page_names':['Overview'],'measure_ids':['quantity']},
 {'target_id':'other','report_id':'report','page_id':'page','names':['Regional card'],'page_names':['Overview'],'measure_ids':['quantity']}]}]}
class Store:
 def __init__(self,path):self.database=path
 @contextmanager
 def connect(self):
  db=sqlite3.connect(self.database)
  try:
   with db:yield db
  finally:db.close()
class ClaimTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.workspace=SimpleNamespace(store=Store(Path(self.tmp.name)/'db.sqlite'),agent=SimpleNamespace(config={},planner_profile={'adapter':'injected'}))
  self.controller=ClaimIntake(self.workspace)
  self.patch=patch('investigator.claim_intake.ClaimIntake._catalog',return_value=copy.deepcopy(CAT));self.patch.start();self.addCleanup(self.patch.stop)
 def request(self,**changes):
  claim={'metric_phrase':'Quantity','observations':[{'observed':950,'expected':1000}], 'direction':'LESS','comparator':'OWN_COUNT','scope':{'kind':'VISUALS','report_id':'report','page_id':'page','visual_ids':['card','other']}}
  claim.update(changes);return {'request_key':'one','claim':claim}
 def test_global_multiplicity_does_not_require_an_example_key(self):
  result=self.controller.submit(self.request(scope={'kind':'RECORDS','model_id':'model'},direction='MORE'))
  self.assertEqual(result['status'],'AWAITING_CONFIRMATION');self.assertEqual(result['questions'],[])
 def test_missing_records_still_require_an_example_or_a_compiled_comparator_set(self):
  result=self.controller.submit(self.request(scope={'kind':'RECORDS','model_id':'model'},direction='LESS'))
  self.assertEqual(result['questions'][0]['field'],'examples')
 def test_model_only_claim_disambiguates_shared_measure_name_without_report(self):
  catalog=copy.deepcopy(CAT);catalog['models'][0]['name']='Operations model';catalog['models'].append({'id':'foreign','name':'Billing model','measures':[{'id':'other-quantity','name':'Quantity'}],'reports':[],'visuals':[]})
  with patch.object(self.controller,'_catalog',return_value=catalog):
   req=self.request(scope={'kind':'RECORDS','model_id':'model'},examples=[42]);r=self.controller.submit(req)
   self.assertEqual(r['status'],'AWAITING_CONFIRMATION');self.assertEqual(r['claim']['selected_binding']['model_id'],'model')
   self.assertIn('Operations model',r['interpretation']['text']);self.assertEqual(r['questions'],[])
   req['request_key']='bad-model';req['claim']['scope']['model_id']='unknown'
   with self.assertRaisesRegex(ValueError,'unknown model'):self.controller.submit(req)
 def test_typed_field_and_dimension_require_retained_identity_and_render_names(self):
  catalog=copy.deepcopy(CAT);catalog['models'][0]['columns']=[{'column_id':'field-secret-id','name':'Status'},{'column_id':'dimension-secret-id','name':'Region'}]
  with patch.object(self.controller,'_catalog',return_value=catalog):
   request=self.request();request['claim']['scope'].update(field_id='field-secret-id',dimension_id='dimension-secret-id')
   result=self.controller.submit(request)
   self.assertIn('Field to trace: Status.',result['interpretation']['text']);self.assertIn('Breakdown by: Region.',result['interpretation']['text'])
   self.assertNotIn('secret-id',result['interpretation']['text'])
   request['request_key']='bad';request['claim']['scope']['field_id']='unknown'
   with self.assertRaisesRegex(ValueError,'unknown'):self.controller.submit(request)
   catalog['models'].append({'id':'other-model','measures':[],'columns':[{'column_id':'foreign-field','name':'Foreign'}]})
   request['claim']['scope']['field_id']='foreign-field'
   with self.assertRaisesRegex(ValueError,'outside'):self.controller.submit(request)
 def test_plural_claim_requires_confirmation_and_never_executes(self):
  result=self.controller.submit(self.request())
  self.assertEqual(result['status'],'AWAITING_CONFIRMATION');self.assertEqual(result['questions'],[])
  self.assertEqual(result['claim']['selected_binding']['target_ids'],['card','other'])
  self.assertIsNone(result['engine_admission']);self.assertIn('all 2',result['interpretation']['text'])
  done=self.controller.confirm({'id':result['id'],'revision':0,'accepted':True,'request_key':'confirm'})
  self.assertEqual(done['status'],'CONFIRMED');self.assertEqual(done['engine_admission']['kind'],'PLAN_ONLY');self.assertFalse(done['engine_admission']['executed'])
 def test_page_freshness_never_asks_metric_or_value(self):
  req={'request_key':'stale','claim':{'direction':'STALE','scope':{'kind':'PAGE','report_id':'report','page_id':'page'}}}
  result=self.controller.submit(req);self.assertEqual(result['status'],'AWAITING_CONFIRMATION');self.assertEqual(result['questions'],[])
 def test_settled_report_page_not_reasked_and_scope_refinement_keeps_original(self):
  req=self.request();req['claim'].pop('comparator')
  result=self.controller.submit(req);q=result['questions'][0];self.assertEqual(q['field'],'comparator')
  done=self.controller.reply({'id':result['id'],'revision':0,'request_key':'reply','answers':[{'question_id':q['id'],'choice_id':q['choices'][0]['id']}]})
  self.assertEqual(done['status'],'AWAITING_CONFIRMATION');self.assertEqual(done['claim']['settled']['scope']['report_id'],'report')
  self.assertEqual(len(done['claim']['facts']),len(result['claim']['facts'])+1)
 def test_wrong_page_visual_refuses_without_selection(self):
  with self.assertRaisesRegex(ValueError,'outside'):self.controller.submit(self.request(scope={'kind':'VISUALS','report_id':'report','page_id':'page','visual_ids':['wrong']}))
 def test_submitted_metric_ambiguity_asks_binding_not_supplied_metric(self):
  result=self.controller.submit(self.request(metric_phrase='Unknown measure'))
  self.assertIn('definition',result['questions'][0]['question']);self.assertEqual(result['claim']['settled']['metric'],[{'phrase':'Unknown measure'}])
 def test_confirmation_covers_all_settled_facts(self):
  result=self.controller.submit(self.request(time='Yesterday',filters=['North'],examples=['Record 22'],guessed_cause='Join'))
  for fragment in ('Yesterday','North','Record 22','Join','your own count'):self.assertIn(fragment,result['interpretation']['text'])
  self.assertEqual(set(result['interpretation']['fact_ids']),{f['id']for f in result['claim']['facts']})
 def test_wrong_type_enum_refuses(self):
  with self.assertRaises(ValueError):self.controller.submit(self.request(direction={'kind':'LESS'}))
 def test_invalid_reference_and_context_number_remain_distinct(self):
  text='950 shown, 1000 expected'
  raw={'facts':[{'field':'observation','reference':[1,1],'symbol':'OBSERVED','metric_reference':None},{'field':'observation','reference':[4,4],'symbol':'EXPECTED','metric_reference':None}]}
  result=facts.extraction(raw,text,'doc');self.assertEqual([f['value']['role']for f in result],['OBSERVED','EXPECTED'])
  raw['facts'][0]['reference']=[99,99]
  with self.assertRaises(ValueError):facts.extraction(raw,text,'doc')
 def test_idempotent_request_and_stale_confirmation(self):
  first=self.controller.submit(self.request());self.assertEqual(first,self.controller.submit(self.request()))
  with self.assertRaises(Conflict):self.controller.confirm({'id':first['id'],'revision':5,'accepted':True})
 def test_projected_claim_refuses_before_raw_persistence(self):
  self.workspace.agent.config={'_estate':{'recording':{'tape_class':'PRIVACY_PROJECTED'}}}
  with self.assertRaises(Exception):self.controller.submit(self.request(metric_phrase='RAW_SECRET_SENTINEL'))
  with self.workspace.store.connect()as db:self.assertEqual(db.execute('SELECT count(*)FROM claim_intakes').fetchone()[0],0)
 def test_scope_facts_combine_without_overwriting_conflict(self):
  fs=[facts.fact('scope',{'kind':'PAGE'},{'kind':'USER'},authority='USER_SUBMITTED'),facts.fact('scope',{'kind':'PAGE','report_id':'report'},{'kind':'USER2'},authority='USER_SUBMITTED')]
  settled,conflicts=facts.settled(fs);self.assertEqual(conflicts,[]);self.assertEqual(settled['scope'],{'kind':'PAGE','report_id':'report'})
  fs.append(facts.fact('scope',{'kind':'REPORT'},{'kind':'USER3'},authority='USER_SUBMITTED'));self.assertIn('scope',facts.settled(fs)[1])
 def test_free_text_span_scope_uses_catalog_names_and_plural_targets(self):
  text='Both Global card and Regional card on Overview in Activity Report are lower.'
  extracted=[facts.fact('metric',{'phrase':'Quantity'},{'kind':'TOKEN_SPAN'},authority='USER_TEXT'),facts.fact('scope',{'kind':'VISUALS','phrase':text},{'kind':'TOKEN_SPAN'},authority='USER_TEXT'),facts.fact('direction','LESS',{'kind':'TOKEN_SPAN'},authority='USER_TEXT'),facts.fact('comparator','APPLICATION',{'kind':'TOKEN_SPAN'},authority='USER_TEXT')]
  with patch('investigator.claim_provider.extract',return_value=(extracted,{'calls':1,'rejections':[]}))as model:
   result=self.controller.submit({'text':text,'request_key':'text'})
  model.assert_called_once();self.assertEqual(result['status'],'AWAITING_CONFIRMATION')
  self.assertEqual(result['claim']['settled']['scope']['visual_ids'],['card','other'])
 def test_changed_catalog_same_stable_objects_revalidates_without_reasking(self):
  result=self.controller.submit(self.request());changed=copy.deepcopy(CAT);changed['models'][0]['revision']=2
  with patch.object(self.controller,'_catalog',return_value=changed):
   done=self.controller.confirm({'id':result['id'],'revision':0,'accepted':True})
  self.assertEqual(done['status'],'CONFIRMED');self.assertEqual(done['history'][-2]['status'],'SAME_STABLE_OBJECTS')
 def test_changed_catalog_missing_target_asks_once_preserving_old_pin(self):
  result=self.controller.submit(self.request());changed=copy.deepcopy(CAT);changed['models'][0]['visuals']=[]
  with patch.object(self.controller,'_catalog',return_value=changed):done=self.controller.confirm({'id':result['id'],'revision':0,'accepted':True})
  self.assertEqual(done['status'],'CLARIFYING');self.assertEqual(len(done['questions']),1);self.assertIsNone(done['engine_admission'])
 def test_interpretation_renders_enums_and_filter_column_names_not_ids_or_json(self):
  catalog=copy.deepcopy(CAT);catalog['models'][0]['columns']=[{'column_id':'internal-column','name':'Region'}]
  with patch.object(self.controller,'_catalog',return_value=catalog):result=self.controller.submit(self.request(filters=[{'column_id':'internal-column','operator':'EQ','value':'North'}]))
  text=result['interpretation']['text'];self.assertIn('Region equals North',text)
  for hidden in('internal-column','OWN_COUNT','VISUALS','{','}'):self.assertNotIn(hidden,text)
 def test_two_metrics_on_two_cards_remain_plural_not_forced_to_one(self):
  catalog=copy.deepcopy(CAT);catalog['models'][0]['measures'].append({'id':'money','name':'Revenue'});catalog['models'][0]['visuals'][1]['measure_ids']=['money']
  req=self.request();req['claim'].pop('metric_phrase')
  extracted=[facts.fact('metric',{'phrase':p},{'kind':'TOKEN_SPAN','n':i},authority='USER_TEXT')for i,p in enumerate(('Quantity','Revenue'))]
  with patch.object(self.controller,'_catalog',return_value=catalog),patch('investigator.claim_provider.extract',return_value=(extracted,{'calls':1,'rejections':[]})):
   req['text']='Both Quantity and Revenue cards';result=self.controller.submit(req)
  self.assertEqual(result['status'],'AWAITING_CONFIRMATION');self.assertEqual(result['claim']['selected_binding']['kind'],'MULTIPLE')
  self.assertEqual([b['measure_id']for b in result['claim']['selected_binding']['bindings']],['quantity','money'])
 def test_catalog_changed_visible_name_requires_new_interpretation_confirmation(self):
  result=self.controller.submit(self.request());changed=copy.deepcopy(CAT);changed['models'][0]['reports'][0]['name']='Renamed Report'
  with patch.object(self.controller,'_catalog',return_value=changed):done=self.controller.confirm({'id':result['id'],'revision':0,'accepted':True})
  self.assertEqual(done['status'],'AWAITING_CONFIRMATION');self.assertEqual(done['revision'],1);self.assertIsNone(done['engine_admission'])
  self.assertIn('Renamed Report',done['interpretation']['text'])
 def test_explicit_user_correction_supersedes_fact_without_deleting_provenance(self):
  result=self.controller.submit(self.request());rejected=self.controller.confirm({'id':result['id'],'revision':0,'accepted':False})
  done=self.controller.reply({'id':result['id'],'revision':1,'answers':[{'question_id':rejected['questions'][0]['id']}],'claim':{'direction':'MORE'}})
  self.assertEqual(done['status'],'AWAITING_CONFIRMATION');self.assertEqual(done['claim']['settled']['direction'],'MORE')
  old=next(f for f in done['claim']['facts']if f['field']=='direction'and f['value']=='LESS');self.assertTrue(old['superseded_by'])
 def test_explicit_report_page_visual_lines_are_preserved_before_model(self):
  req=self.request();req['claim'].pop('scope');req['text']='Report: Activity Report\nPage: Overview\nVisual: Global card'
  with patch('investigator.claim_provider.extract',return_value=([],{'calls':1,'rejections':[]})):
   result=self.controller.submit(req)
  self.assertEqual(result['status'],'AWAITING_CONFIRMATION');self.assertEqual(result['claim']['settled']['scope']['visual_ids'],['card'])
  supplied=[f for f in result['claim']['facts']if f['source'].get('explicit_label')]
  self.assertEqual(len(supplied),3)
 def test_submitted_figure_content_must_match_its_stated_precision_and_quote(self):
  from investigator import reported_figure
  figure=reported_figure.from_candidates([{'start':0,'end':3,'quote':'950'}],'950');figure['value']='16'
  req=self.request();req['claim']['observations']=[{'observed':figure}]
  with self.assertRaisesRegex(ValueError,'precision differs'):self.controller.submit(req)
class QuestionInvariantTests(unittest.TestCase):
 def test_settled_metric_report_page_and_comparator_cannot_be_reasked(self):
  claim={'settled':{'metric':[{'phrase':'Revenue'}],'comparator':'APPLICATION','scope':{'kind':'PAGE','report_id':'report','page_id':'page'}},'conflicts':[]}
  for field in('metric','report','page','comparator'):
   with self.assertRaisesRegex(ValueError,'REASKS'):policy.validate_question(claim,{'field':field})
  policy.validate_question(claim,{'field':'binding'})
 def test_record_complaint_asks_only_one_example_and_page_does_not(self):
  base={'facts':[],'settled':{'metric':[{'phrase':'Quantity'}],'direction':'LESS','comparator':'APPLICATION','scope':{'kind':'RECORDS'}},'conflicts':[],'candidate_bindings':[{'model_id':'model','measure_id':'quantity','label':'Quantity'}]}
  q,_=policy.plan(base,CAT);self.assertEqual(q['field'],'examples')
if __name__=='__main__':unittest.main()
