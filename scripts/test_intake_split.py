import unittest
from seal_intake_split import split
class SplitTests(unittest.TestCase):
 def test_family_conservation_stratification_and_response_independence(self):
  rows=[{'id':'family-'+f+str(i),'family':f} for f,n in zip('ABCDEFGHI',[4,3,3,3,4,3,4,3,3]) for i in range(n)]
  rows += [{'id':'family-'+f,'family':f} for f in 'ABCDEFGHI']
  rows += [{'id':c+'-'+str(i),'family':None} for c,n in [('question',4),('refusal',10),('visual',6)] for i in range(n)]
  rebuilt={'cases':[{'id':'family-'+f,'family':f} for f in 'ABCDEFGHI']}
  value=split({'cases':rows},rebuilt)
  self.assertEqual((len(value['dev']),len(value['held_out'])),(40,28))
  self.assertEqual(len({r['id'] for r in value['dev']+value['held_out']}),68)
  self.assertFalse({r['family'] for r in value['dev'] if r['family']} & {r['family'] for r in value['held_out'] if r['family']})
  changed=split({'cases':[dict(r,expected={'wrong':'irrelevant'}) for r in rows]},rebuilt)
  self.assertEqual([r['id'] for r in value['held_out']],[r['id'] for r in changed['held_out']])
