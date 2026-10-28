import unittest,copy
from investigator.daily_smoke import guided_demo_matches
from investigator.graph_health import analyze
class SmokeTests(unittest.TestCase):
 def test_model_claims_do_not_replace_native_boundary_reads(self):
  expected={'verdict':'transformation logic','reads':{'silver':'7661','gold':'8765'}}
  result={'status':'ANSWERED','verdict':'transformation logic','outputs':{'business':'answer','technical':'proof'},'case':{'queries':[{'status':'SUCCEEDED','layer':asset,'asset_ids':[asset],'result':{'rows':[{'n':value}]}}for asset,value in expected['reads'].items()]}}
  self.assertTrue(guided_demo_matches(result,expected))
  delivered=copy.deepcopy(result);delivered['technical']={'verdict':delivered.pop('verdict')};self.assertTrue(guided_demo_matches(delivered,expected))
  delivered['technical']['verdict']='observed value';self.assertFalse(guided_demo_matches(delivered,expected))
  missing=copy.deepcopy(result);missing['case']['queries'].pop();missing['numbers']=[7661,8765];self.assertFalse(guided_demo_matches(missing,expected))
  blank=copy.deepcopy(result);blank['case']['queries'][0]['result']['rows'][0]['n']=None;self.assertFalse(guided_demo_matches(blank,expected))
  same=copy.deepcopy(result)
  for q in same['case']['queries']:q['layer']='same'
  self.assertFalse(guided_demo_matches(same,expected))
class GraphTests(unittest.TestCase):
 def test_full_path_needs_producer_source_and_no_broken_branches(self):
  nodes=[{'id':i,'kind':kind,'label':i,'properties':{'system_of_record':True}if i=='s'else{}}for i,kind in [('r','REPORT'),('p','PAGE'),('v','VISUAL'),('m','MEASURE'),('t','TABLE'),('job','PIPELINE'),('s','SOURCE')]]
  edges=[{'source':a,'target':b,'kind':kind}for a,b,kind in [('r','p','CONTAINS'),('p','v','CONTAINS'),('v','m','COMPUTED_FROM'),('m','t','COMPUTED_FROM'),('t','job','DERIVED_IN_STEP'),('job','s','COMPUTED_FROM')]]
  data={'nodes':nodes,'edges':edges};self.assertEqual(analyze(data)['overall']['percentage'],100)
  broken=copy.deepcopy(data);broken['edges'].pop();self.assertEqual(analyze(broken)['overall']['percentage'],0)
  self.assertEqual(analyze({'nodes':nodes,'edges':edges+[{'source':'t','target':'missing','kind':'COMPUTED_FROM'}]})['overall']['percentage'],0)
if __name__=='__main__':unittest.main()
