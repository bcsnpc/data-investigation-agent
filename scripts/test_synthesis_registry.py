import copy,sqlite3,unittest
from contextlib import closing
from investigator.synthesis_digest import build as digest
from investigator.synthesis_spine import build as spine
from investigator import path_narrative,narrative_form
class SharedRegistryTests(unittest.TestCase):
 def fixture(self):
  labels={'a':{'role':'SERVING','name':'Serving'},'b':{'role':'LANDING','name':'Landing'},'c':{'role':'SEMANTIC','name':'Measure'},'d':{'role':'REFINED','name':'Refined'}}
  detail={'layer_labels':labels,'unverified_boundaries':[{'upper_layer':'c','lower_layer':'a'},{'upper_layer':'a','lower_layer':'d'},{'upper_layer':'d','lower_layer':'b'}]}
  state={'observations':[],'hypotheses':[],'assessment':{'classification':'CONSISTENT_TO_BOUNDARY','technical_output':detail,'limits':[]},'envelope':dict(symptom='Explain a calculation.',model_id='model',context_id='context',measure_id='measure',filters=[],dimension_ids=[])}
  with closing(sqlite3.connect(':memory:')) as db:payload=digest(state,db)
  return payload,state
 def test_digest_validator_provider_and_renderer_share_one_path_alias_map(self):
  payload,state=self.fixture();before=copy.deepcopy(payload);view=spine(payload,state,48000)
  self.assertEqual(view['layer_tokens'],{'L0 (SEMANTIC)':'c','L1 (SERVING)':'a','L2 (REFINED)':'d','L3 (LANDING)':'b'})
  commentary='The declared calculation preserves the quantity at L0 (SEMANTIC).'
  path_narrative.validate_layer_references(commentary,payload)
  rendered=narrative_form.technical(commentary,payload,state['assessment'],{'text':'Review the declared calculation.'})
  self.assertIn('Roles reached in path resolution: L0 (SEMANTIC), L1 (SERVING), L2 (REFINED), L3 (LANDING).',rendered)
  self.assertIn(commentary,rendered);self.assertEqual(payload,before)
  with self.assertRaises(path_narrative.LayerReferenceError):path_narrative.validate_layer_references('At L2 (SEMANTIC), the quantity is preserved.',payload)
 def test_registry_is_engine_derived_not_a_provider_substitution_field(self):
  from investigator.synthesis_wire import prepare
  payload,state=self.fixture();view=spine(payload,state,48000);_,contract,_=prepare(view)
  self.assertNotIn('layer_registry',contract['properties']);self.assertFalse(contract['additionalProperties'])
  changed=copy.deepcopy(state);changed['assessment']['technical_output']['unverified_boundaries'].reverse()
  with closing(sqlite3.connect(':memory:')) as db:other=digest(changed,db)
  self.assertNotEqual(payload['layer_registry'],other['layer_registry'])
 def test_actual_false_connection_blocker_is_not_a_mechanism(self):
  payload,state=self.fixture()
  text='The retained path stops before carrying the warehouse-scoped evaluation because the surface did not report the needed field connection.'
  with self.assertRaises(ValueError):narrative_form.technical(text,payload,state['assessment'],{'text':'Review the declared calculation.'})
 def test_conservative_no_operation_summary_remains_valid(self):
  path_narrative.validate_mechanism('The retained definition records a direct quantity-preserving mapping.')
if __name__=='__main__':unittest.main()
