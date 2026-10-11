import unittest
from unittest.mock import patch
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.process_debugging import VERSION
import test_flexible_investigation as fixture

class ProcessAdapterFactoryTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixture.DynamicTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
  self.agent=AdaptiveRuntime(self.fixture.runtime,lambda p:(_ for _ in ()).throw(AssertionError('planner called')))
  envelope=dict(self.fixture.envelope,strategy=VERSION)
  self.identity=self.agent.create(envelope,'factory')['id']
 def test_native_factory_does_not_resolve_probe_or_judge(self):
  with patch('investigator.adapters.microsoft_process.MicrosoftProcessAdapter.resolve_path',side_effect=AssertionError('resolved')):
   adapter=self.agent.process_adapter(self.identity)
  self.assertFalse(adapter._runtime_local_execution)
  self.assertEqual(self.fixture.native_calls,[]);self.assertEqual(self.fixture.sql_calls,[])
 def local(self):
  self.fixture.config['_estate']={'execution':{'mode':'LOCAL_EXPORTED'}}
  # Factory unit double, not an exported-bundle approval test. Keep all
  # candidate/admission checks real except the separately tested bundle gate.
  approval=patch('investigator.local_execution_approval.validate',return_value=None)
  approval.start();self.addCleanup(approval.stop)
  from investigator.onboarding import digest
  import copy
  original_get=self.agent.store.get
  def get(*args,**kwargs):
   model=copy.deepcopy(original_get(*args,**kwargs));model['discovery']['policy_hash']=digest(self.fixture.config);return model
  patcher=patch.object(self.agent.store,'get',side_effect=get);patcher.start();self.addCleanup(patcher.stop)
  with self.agent.runtime.db() as db:
   state=self.agent.load(db,self.identity);state['config_hash']=digest(self.fixture.config);self.agent.save(db,state,'SYNTHETIC_LOCAL_CONFIG')
  from test_process_debugging import Adapter
  fake=Adapter(['top'],{'top':1})
  self.created={}
  def create(*args,**kwargs):self.created.update(kwargs);return fake
  with patch('investigator.adapters.local_process.create',side_effect=create),patch('fabric_sql_auth.session_status',side_effect=AssertionError('native auth')):
   adapter=self.agent.process_adapter(self.identity)
  return adapter
 def executing(self):
  with self.agent.runtime.db() as db:
   state=self.agent.load(db,self.identity);state['status']='EXECUTING';self.agent.save(db,state,'TEST_EXECUTING')
 def test_local_dispatch_precedes_native_auth_and_charges_diagnostic_only(self):
  adapter=self.local();self.executing();calls=[]
  result=self.created['meter_local_read']('local_exported_quantity',lambda:calls.append(1) or 17)
  self.assertEqual(result,17)
  with self.agent.runtime.db() as db:state=self.agent.load(db,self.identity)
  self.assertEqual(state['cloud_calls'],1);self.assertEqual(state.get('physical_calls',0),0)
  self.assertEqual(state['local_diagnostic_reads'],1);self.assertTrue(adapter._runtime_local_execution)
 def test_local_receipt_is_persisted_before_returning_identity(self):
  self.local();self.executing();identity=self.created['record_evidence']({'tool':'local_exported_quantity','value':17})
  with self.agent.runtime.db() as db:state=self.agent.load(db,self.identity)
  self.assertEqual(state['local_read_evidence'][0]['id'],identity)
  self.assertEqual(state['local_read_evidence'][0]['value'],17)
 def test_local_budget_refusal_precedes_quantity(self):
  from investigator.usage_governance import UsageHold
  self.local();self.executing();calls=[]
  with self.agent.runtime.db() as db:
   state=self.agent.load(db,self.identity);state['cloud_calls']=state['envelope']['limits']['cloud_calls'];self.agent.save(db,state,'TEST_EXHAUSTED')
  with self.assertRaises(UsageHold):self.created['meter_local_read']('local_exported_quantity',lambda:calls.append(1))
  self.assertEqual(calls,[])

 def test_agent_claim_does_not_walk_and_is_once_only(self):
  from investigator.onboarding import Conflict
  state=self.agent.begin_agent_process(self.identity)
  self.assertEqual(state['status'],'EXECUTING');self.assertEqual(self.fixture.native_calls,[])
  with self.assertRaises(Conflict):self.agent.begin_agent_process(self.identity)
 def test_agent_support_is_validated_but_synthesis_rejects_incomplete_original_receipts(self):
  from investigator.investigation_tools import InvestigationTools
  from investigator.definition_target import procedure_scope
  from test_process_debugging import Adapter
  from test_investigation_tools import PersistedBoundary
  from dataclasses import replace
  self.agent.begin_agent_process(self.identity)
  with self.agent.runtime.db() as db:state=self.agent.load(db,self.identity)
  adapter=Adapter(['top','lower'],{'top':8,'lower':8});adapter._runtime_session_id=self.identity
  original=adapter.evaluate
  def evaluate(*args):
   probe=original(*args);return replace(probe,evidence=dict(probe.evidence,declared_context={'version':1,'scope':'WHOLE_ENTITY','filters':[],'dimension_ids':[]}))
  adapter.evaluate=evaluate
  tools=InvestigationTools(adapter,{'target':{'measure_id':state['envelope']['measure_id'],'scope_id':'picked'}},{'picked':procedure_scope(state['envelope'])},PersistedBoundary())
  citations=[tools.invoke('lineage',{'target_id':'target'})['facade_evidence_id']]
  for layer in ('top','lower'):citations.append(tools.invoke('probe_layer',{'target_id':'target','layer_id':layer,'scope_id':'picked'})['facade_evidence_id'])
  accepted=self.agent.accept_agent_support(self.identity,tools,'CONSISTENT_TO_BOUNDARY','target',citations)
  self.assertEqual(accepted['status'],'COMPLETED')
  calls=[]
  def wrong_provider(payload,*args):calls.append(1);return {'classification':'DEFECT'},{}
  delivered=self.agent.synthesize(self.identity,wrong_provider)
  self.assertNotEqual(delivered['synthesis']['status'],'COMPLETED');self.assertEqual(delivered['synthesis']['status'],'BLOCKED');self.assertEqual(calls,[])
  self.assertEqual(delivered['outcome']['assessment']['classification'],'CONSISTENT_TO_BOUNDARY')

 def test_tool_boundary_stores_complete_result_before_returning_id(self):
  self.agent.begin_agent_process(self.identity)
  boundary=self.agent.agent_tool_boundary(self.identity)
  result=boundary('lineage',{'target_id':'target'},lambda:{'status':'AVAILABLE','data':{'evidence':{'id':'native-1','definition':'synthetic'}}})
  with self.agent.runtime.db() as db:state=self.agent.load(db,self.identity)
  stored=state['agent_tool_receipts'][0]
  self.assertEqual(stored['id'],result['receipt_id']);self.assertEqual(stored['result'],result['result'])
 def test_tool_boundary_retains_failure_and_never_returns_usable_id(self):
  self.agent.begin_agent_process(self.identity)
  boundary=self.agent.agent_tool_boundary(self.identity)
  with self.assertRaisesRegex(ValueError,'synthetic'):boundary('probe_layer',{},lambda:(_ for _ in ()).throw(ValueError('synthetic')))
  with self.agent.runtime.db() as db:state=self.agent.load(db,self.identity)
  self.assertEqual(state['agent_tool_receipts'][0]['status'],'FAILED')
