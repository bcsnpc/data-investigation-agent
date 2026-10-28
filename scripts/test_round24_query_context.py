import unittest
from investigator.query_context import sheet
from investigator.investigative_queries import validate
from test_round23_intake_queries import sql_objects,dax_objects
class ContextTests(unittest.TestCase):
 def test_examples_validate_on_exact_native_schema_without_a_read(self):
  for dialect,objects in [('T-SQL',sql_objects()),('DAX',dax_objects())]:
   layer={'dialect':dialect,'objects':objects};result=sheet(layer)
   self.assertGreaterEqual(len(result['examples']),2)
   for example in result['examples']:self.assertTrue(validate(example,layer)['asset_ids'])
   self.assertEqual(result['sample_values'],[])
if __name__=='__main__':unittest.main()
