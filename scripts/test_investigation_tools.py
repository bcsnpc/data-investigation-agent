import copy,unittest
from unittest.mock import patch
from investigator.investigation_tools import InvestigationTools,schemas,evidence_ids
from investigator.process_debugging import Probe,NoValue
from investigator.context_search import MeasurePathLimit
from test_process_debugging import Adapter
from test_declared_reproduction import NeutralAdapter,SCOPE

class PersistedBoundary:
 def __init__(self):self.saved=[]
 def __call__(self,name,args,operation):
  result=operation();receipt='agent-tool:'+str(len(self.saved)+1)
  self.saved.append({'id':receipt,'name':name,'arguments':copy.deepcopy(args),'result':copy.deepcopy(result)})
  return {'receipt_id':receipt,'result':result}

class InvestigationToolTests(unittest.TestCase):
 def setUp(self):
  self.adapter=Adapter(['top','lower'],{'top':8,'lower':8});self.boundary=PersistedBoundary()
  self.targets={'target':{'measure_id':'measure','scope_id':'picked'}};self.scopes={'picked':{'filters':[]},'other':{'filters':[{'column_id':'x','values':[1]}]}}
  self.tools=InvestigationTools(self.adapter,self.targets,self.scopes,self.boundary)
 def invoke(self,name,**args):return self.tools.invoke(name,args)
 def test_transformation_tool_explains_adjacent_probe_preconditions_and_step_numbering(self):
  description=next(s['description'] for s in schemas() if s['name']=='read_transformation')
  for fact in ('Step 1 connects path layers 0 and 1','step 2 connects layers 1 and 2',
               'OBSERVED probe_layer results for both adjacent layers under the same scope',
               'no causal judgment is established','unavailable result is not proof'):
   self.assertIn(fact,description)
 def test_strict_schemas_offer_no_sql_or_free_filter_predicates(self):
  self.assertEqual({s['name'] for s in schemas()},{'reproduce','lineage','probe_layer','read_transformation','check_freshness','compare_reports','query_source'})
  for schema in schemas():self.assertFalse(schema['parameters']['additionalProperties']);self.assertNotIn('query',schema['parameters']['properties'])
 def test_metadata_receipt_is_persisted_and_asset_ids_not_native_read_ids(self):
  result=self.invoke('lineage',target_id='target')
  self.assertEqual(result['facade_evidence_id'],self.boundary.saved[0]['id']);self.assertNotIn('top',result['evidence_ids']);self.assertFalse(result['finding_authority'])
 def test_boundary_refusal_precedes_all_adapter_calls(self):
  calls=[]
  def refuse(*args):raise ValueError('budget refusal')
  self.tools.boundary=refuse
  with patch.object(self.adapter,'resolve_path',side_effect=lambda m:calls.append(m)):
   with self.assertRaisesRegex(ValueError,'budget refusal'):self.invoke('lineage',target_id='target')
  self.assertEqual(calls,[])
 def test_unpersisted_or_native_id_cannot_impersonate_facade_receipt(self):
  self.tools.boundary=lambda n,a,op:{'receipt_id':'read-top','result':op()}
  with self.assertRaisesRegex(ValueError,'persisted facade evidence'):self.invoke('lineage',target_id='target')
 def test_model_cannot_substitute_scope_or_target(self):
  for args in ({'target_id':'target','layer_id':'lower','scope_id':'other'},{'target_id':'invented','layer_id':'lower','scope_id':'picked'}):
   self.assertEqual(self.tools.invoke('probe_layer',args)['status'],'UNDECLARED')
  self.assertEqual(self.adapter.evaluated,[])
 def test_model_cannot_probe_layer_off_resolved_path(self):
  result=self.invoke('probe_layer',target_id='target',layer_id='invented',scope_id='picked')
  self.assertEqual(result['reason'],'LAYER_NOT_ON_RESOLVED_PATH');self.assertEqual(self.adapter.evaluated,[])
 def test_attested_probe_preserves_read_receipt_separately(self):
  result=self.invoke('probe_layer',target_id='target',layer_id='top',scope_id='picked')
  self.assertEqual(result['data']['value'],8);self.assertEqual(result['native_evidence_ids'],['read-top']);self.assertEqual(result['data']['evidence']['surface_attestation']['status'],'MATCHED')
 def test_contradicted_identity_cannot_expose_observed_value(self):
  self.adapter.reports={'top':{'identity':'admin','object':'top'}}
  result=self.invoke('probe_layer',target_id='target',layer_id='top',scope_id='picked')
  self.assertEqual(result['status'],'UNAVAILABLE');self.assertEqual(result['data']['value_state'],'FAILED');self.assertIsNone(result['data']['value'])
 def test_blank_is_observed_not_failed_query_or_missing_value(self):
  self.adapter.values['top']=None
  result=self.invoke('probe_layer',target_id='target',layer_id='top',scope_id='picked')
  self.assertEqual(result['status'],'AVAILABLE');self.assertEqual(result['data']['value_state'],'BLANK')
 def test_filtered_lower_refusal_remains_no_value(self):
  self.adapter.not_comparable={'lower'}
  result=self.invoke('probe_layer',target_id='target',layer_id='lower',scope_id='picked')
  self.assertEqual(result['status'],'NOT_COMPARABLE');self.assertEqual(result['data']['value_state'],'NOT_OBTAINED')
 def test_large_resolver_becomes_explicit_capability_unavailability(self):
  with patch.object(self.adapter,'resolve_path',side_effect=MeasurePathLimit(24001)):
   result=self.invoke('lineage',target_id='target')
  self.assertEqual(result['reason'],'RESOLVER_SIZE_BOUND');self.assertEqual(result['data']['limit'],24000)
 def test_reproduction_uses_real_inventory_consumer_and_reads(self):
  adapter=NeutralAdapter();tools=InvestigationTools(adapter,self.targets,{'picked':copy.deepcopy(SCOPE)},self.boundary)
  result=tools.invoke('reproduce',{'target_id':'target'})
  self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['data']['finding']['label'],'REPRODUCED')
  self.assertIn('reproduction-read-1',result['native_evidence_ids']);self.assertEqual(len(adapter.read_scopes),2)
 def test_unsupported_inventory_is_not_skipped_by_facade(self):
  class Unsupported(NeutralAdapter):
   def declared_context(inner,*args):
    result=super().declared_context(*args);result['inventory']['entries'][0]['disposition']='UNSUPPORTED';result['inventory']['entries'][0]['restrictions']=[];return result
  adapter=Unsupported();tools=InvestigationTools(adapter,self.targets,{'picked':copy.deepcopy(SCOPE)},self.boundary)
  result=tools.invoke('reproduce',{'target_id':'target'})
  self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(adapter.read_scopes,[])
 def test_missing_transformation_does_not_invoke_model_judgment(self):
  with patch.object(self.adapter,'transformation_definition',side_effect=AssertionError('not a verified definition reader')):
   result=self.invoke('read_transformation',target_id='target',step=1)
  self.assertEqual(result['status'],'UNDECLARED')
 def test_retained_contract_not_promoted_to_causal_explanation(self):
  self.adapter.layers[1]['quantity_contract']={'definition_asset_id':'step','definition_hash':'a'*64,'operations':[]}
  result=self.invoke('read_transformation',target_id='target',step=1)
  self.assertIsNone(result['data']['causal_judgment']);self.assertNotIn('step',result['native_evidence_ids'])
 def test_missing_freshness_not_defaulted_to_current(self):
  result=self.invoke('check_freshness',target_id='target');self.assertEqual(result['status'],'UNDECLARED')
 def test_freshness_keeps_audit_receipts_without_latency_verdict(self):
  old=self.adapter.capabilities
  self.adapter.capabilities=lambda:old()|{'source_delivery'}
  self.adapter.source_delivery=lambda b,s:{'status':'UNAVAILABLE','reason':'no audit','evidence':{'id':'audit-read'}}
  result=self.invoke('check_freshness',target_id='target')
  self.assertIsNone(result['data']['latency_classification']);self.assertEqual(result['data']['snapshot_alignment'],'NOT_ESTABLISHED');self.assertIn('audit-read',result['native_evidence_ids'])
 def test_source_cannot_be_guessed_from_deepest_layer(self):
  result=self.invoke('query_source',target_id='target',scope_id='picked')
  self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(self.adapter.evaluated,[])
 def test_declared_unreachable_source_never_read(self):
  old=self.adapter.resolve_path;self.adapter.resolve_path=lambda m:{**old(m),'system_of_record':{'asset_id':'lower','reachable':False}}
  result=self.invoke('query_source',target_id='target',scope_id='picked');self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(self.adapter.evaluated,[])
 def test_explicit_declared_source_reuses_attested_scoped_probe(self):
  old=self.adapter.resolve_path;self.adapter.resolve_path=lambda m:{**old(m),'system_of_record':{'asset_id':'lower'}}
  self.adapter.config={'layer_roles':[{'asset_id':'lower','role':'APPLICATION','business_name':'Application'}]}
  result=self.invoke('query_source',target_id='target',scope_id='picked');self.assertEqual(result['status'],'AVAILABLE');self.assertEqual(result['native_evidence_ids'],['read-lower'])
 def test_compare_reports_does_not_invent_shared_semantics(self):
  targets={'a':{'measure_id':'a','scope_id':'a'},'b':{'measure_id':'b','scope_id':'b'}}
  scopes={key:{**copy.deepcopy(SCOPE),'report_binding':{'report_id':key}} for key in ('a','b')}
  adapter=NeutralAdapter();tools=InvestigationTools(adapter,targets,scopes,self.boundary)
  with patch('investigator.investigation_tools.declared_reproduction.run',return_value={'status':'UNAVAILABLE','reason':'report context unavailable','observations':[]}):result=tools.invoke('compare_reports',{'a':'a','b':'b'})
  self.assertEqual(result['data']['first_shared_declared_layer'],'top');self.assertIsNone(result['data']['comparison_verdict']);self.assertEqual(result['data']['cross_report_equivalence'],'NOT_ESTABLISHED')
 def test_arguments_cannot_carry_query_write_or_new_filters(self):
  with self.assertRaisesRegex(ValueError,'shape differs'):self.tools.invoke('probe_layer',{'target_id':'target','layer_id':'top','scope_id':'picked','query':'UPDATE t SET x=1'})
  self.assertEqual(self.boundary.saved,[])
 def test_original_registered_scope_and_inputs_remain_unchanged(self):
  targets=copy.deepcopy(self.targets);scopes=copy.deepcopy(self.scopes);self.invoke('probe_layer',target_id='target',layer_id='top',scope_id='picked');self.assertEqual(targets,self.targets);self.assertEqual(scopes,self.scopes)

class GovernedTapedFacadeTests(unittest.TestCase):
 def test_real_budget_and_tape_preserve_probe_and_refusal_on_replay(self):
  import json,sqlite3,tempfile
  from contextlib import closing
  from pathlib import Path
  from read_budget import Catalog
  from investigator.usage_governance import UsageGovernor,UsageHold
  from investigator.process_tape import Tape,active,event
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);path=root/'tool-tape.json'
   bootstrap={'entry_point':'investigation_tool_synthetic_test','context_identity':'synthetic','config':{},'profile':{},'usage_policy':None,'engine_hash':'synthetic','state':{}}
   native_calls=[]
   def execute(tape,catalog_name,recording):
    runtime=Catalog(root/catalog_name,'synthetic-estate')
    policy={'environment':'synthetic-estate','daily_limits':{'planner_calls':20,'cloud_calls':1,'input_characters':100000,'output_tokens':30000},'max_inflight_planners':1,'no_progress_limit':2}
    governor=UsageGovernor(runtime,policy,lambda:172799.0)
    adapter=Adapter(['top'],{'top':8});base=adapter.evaluate;number=0
    def evaluate(layer,measure,scope):
     nonlocal number
     number+=1
     def transport():
      if recording:native_calls.append(layer['id'])
      return base(layer,measure,scope)
     return governor.metered_read('tool-session','probe:'+str(number),transport)
    adapter.evaluate=evaluate
    result_db=root/(catalog_name+'.results')
    with closing(sqlite3.connect(result_db)) as db,db:db.execute('CREATE TABLE tool_evidence(id TEXT PRIMARY KEY,body TEXT)')
    counter=0
    def boundary(name,args,operation):
     nonlocal counter
     counter+=1;receipt='agent-tool:'+str(counter)
     event('OPERATION_START',{'operation':'investigation_tool','name':name,'arguments':args})
     try:result=operation()
     except UsageHold:
      event('OPERATION_END',{'name':name,'operation':'investigation_tool','status':'BUDGET_HOLD'});raise
     with closing(sqlite3.connect(result_db)) as db,db:db.execute('INSERT INTO tool_evidence VALUES(?,?)',(receipt,json.dumps(result,sort_keys=True)))
     event('OPERATION_END',{'name':name,'operation':'investigation_tool','receipt_id':receipt,'result':result})
     return {'receipt_id':receipt,'result':result}
    tools=InvestigationTools(adapter,{'target':{'measure_id':'measure','scope_id':'scope'}},{'scope':{}},boundary)
    with active(tape):
     result=tools.invoke('probe_layer',{'target_id':'target','layer_id':'top','scope_id':'scope'})
     with self.assertRaises(UsageHold):tools.invoke('probe_layer',{'target_id':'target','layer_id':'top','scope_id':'scope'})
     tape.finish(result)
    with closing(sqlite3.connect(result_db)) as db,db:self.assertEqual(db.execute('SELECT id FROM tool_evidence').fetchall(),[(result['facade_evidence_id'],)])
    self.assertEqual(governor.snapshot()['read_allowance']['ordinary_charged'],1)
    return result
   recorded=execute(Tape(path,bootstrap),'recorded.sqlite',True)
   replayed=execute(Tape(path),'replayed.sqlite',False)
   self.assertEqual(recorded,replayed);self.assertEqual(native_calls,['top'])

if __name__=='__main__':unittest.main()

class TerminalSupportTests(unittest.TestCase):
 setUp=InvestigationToolTests.setUp
 invoke=InvestigationToolTests.invoke
 def prepare(self,equal=True):
  from dataclasses import replace
  original=self.adapter.evaluate
  def evaluate(*args):
   probe=original(*args)
   return replace(probe,evidence=dict(probe.evidence,declared_context={'version':1,'scope':'WHOLE_ENTITY','filters':[],'dimension_ids':[]}))
  self.adapter.evaluate=evaluate;self.adapter.values['lower']=8 if equal else 5
  self.adapter.explain=True
  refs=[self.invoke('lineage',target_id='target')['facade_evidence_id']]
  for layer in ('top','lower'):refs.append(self.invoke('probe_layer',target_id='target',layer_id=layer,scope_id='picked')['facade_evidence_id'])
  return refs
 def test_consistency_support_uses_existing_gate_and_no_new_reads(self):
  refs=self.prepare();count=len(self.adapter.evaluated)
  result=self.tools.terminal_support('CONSISTENT_TO_BOUNDARY','target',refs)
  self.assertEqual(result['assessment']['classification'],'CONSISTENT_TO_BOUNDARY')
  self.assertEqual(len(self.adapter.evaluated),count);self.assertFalse(result['delivery_validated'])
 def test_agent_preserves_roles_and_names_unchecked_resolved_boundary(self):
  self.adapter.layers=[{'id':'top'},{'id':'lower'},{'id':'third'}]
  refs=self.prepare()
  path=self.tools._paths['measure'];path['stopped_by']='NO_LINEAGE'
  path['layer_labels']={'top':{'role':'SEMANTIC','name':'Measure'},'lower':{'role':'SERVING','name':'Served'}}
  result=self.tools.terminal_support('CONSISTENT_TO_BOUNDARY','target',refs)['assessment']
  self.assertEqual(result['technical_output']['layer_labels'],path['layer_labels'])
  self.assertEqual(result['support']['process']['visibility_boundary']['stopped_by'],'REACHED')
  for output in ('business_output','technical_output'):
   self.assertEqual(result[output]['unverified_boundaries'],[{'upper_layer':'lower','lower_layer':'third','reason':'Investigation terminated before this boundary'}])
   self.assertEqual(result[output]['checked_depth'],'lower')
  self.assertTrue(any('Unchecked lower -> third' in text for text in result['limits']))
 def test_unknown_citation_cannot_authorize_terminal(self):
  self.prepare()
  with self.assertRaisesRegex(ValueError,'unknown or unpersisted'):self.tools.terminal_support('DEFECT','target',['made-up'])
 def test_citations_without_mechanism_cannot_authorize_transformation(self):
  refs=self.prepare(False)
  with self.assertRaisesRegex(ValueError,'producer-supported divergence'):self.tools.terminal_support('TRANSFORMATION_LOGIC','target',refs)
 def test_real_producer_judgment_is_required_and_cached_for_terminal(self):
  refs=self.prepare(False);refs.append(self.invoke('read_transformation',target_id='target',step=1)['facade_evidence_id'])
  result=self.tools.terminal_support('TRANSFORMATION_LOGIC','target',refs)
  self.assertEqual(result['assessment']['classification'],'TRANSFORMATION_LOGIC')
 def test_differing_receipt_contexts_cannot_form_boundary(self):
  refs=self.prepare()
  from dataclasses import replace
  from investigator.onboarding import digest
  key=('measure',digest(self.scopes['picked']),'lower');probe=self.tools._probe_ledger[key]
  self.tools._probe_ledger[key]=replace(probe,evidence=dict(probe.evidence,declared_context={'filters':['different']}))
  with self.assertRaisesRegex(ValueError,'flow_consistency'):self.tools.terminal_support('CONSISTENT_TO_BOUNDARY','target',refs)

 def test_consistency_cannot_ignore_an_also_observed_divergence(self):
  self.adapter.layers=[{'id':'top'},{'id':'lower'},{'id':'third'}];self.adapter.values['third']=4
  refs=self.prepare();refs.append(self.invoke('probe_layer',target_id='target',layer_id='third',scope_id='picked')['facade_evidence_id'])
  with self.assertRaisesRegex(ValueError,'suppress an observed divergent'):self.tools.terminal_support('CONSISTENT_TO_BOUNDARY','target',refs)

 def test_missing_optional_tool_calls_are_not_an_invented_capability_barrier(self):
  refs=self.prepare()
  with self.assertRaisesRegex(ValueError,'actual recorded named barrier'):self.tools.terminal_support('NO_KNOWN_PATTERN','target',refs)

class PathAdmissionTests(unittest.TestCase):
 setUp=InvestigationToolTests.setUp
 invoke=InvestigationToolTests.invoke
 def test_unreachable_declared_layer_is_never_probed(self):
  self.adapter.config={'_estate':{'capability_ceiling':['resolve_measure_path','evaluate_scoped_quantity'],'layers':[{'asset_id':'top','id':'semantic','reachable':True},{'asset_id':'lower','id':'landing','reachable':False}]}}
  result=self.invoke('probe_layer',target_id='target',layer_id='lower',scope_id='picked')
  self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(self.adapter.evaluated,[])
  self.assertEqual(self.tools._paths['measure']['stopped_by'],'NO_ACCESS')
 def test_inferred_binding_without_original_verification_is_not_probed(self):
  self.adapter.layers[1]['binding']={'provenance':'INFERRED_FROM_CODE'}
  result=self.invoke('probe_layer',target_id='target',layer_id='lower',scope_id='picked')
  self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(self.adapter.evaluated,[])
 def test_stale_code_hash_cannot_become_verified_path_by_label(self):
  location={'asset_id':'code'}
  self.adapter.layers[1]['binding']={'provenance':'INFERRED_FROM_CODE','lineage_verification':{'status':'VERIFIED'},'code_location':location}
  self.adapter.config={'_estate':{'capability_ceiling':['resolve_measure_path','evaluate_scoped_quantity'],'layers':[{'asset_id':'top','id':'semantic','reachable':True},{'asset_id':'lower','id':'landing','reachable':True}], 'lineage':{'inference':{'enabled':True},'code_locations':[{'from_layer':'landing','to_layer':'semantic','may_infer_from_code':True,'locations':[location]}]}}}
  checked={'status':'VERIFIED','proposal':{'boundary':{'from_layer':'landing','to_layer':'semantic'},'location':{'content_hash':'old'}}}
  with patch('investigator.lineage_binding.revalidate_verification',return_value=checked):
   result=self.invoke('probe_layer',target_id='target',layer_id='lower',scope_id='picked')
  self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(self.adapter.evaluated,[])
