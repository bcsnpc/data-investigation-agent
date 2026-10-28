import unittest
from investigator.investigative_queries import validate
from test_round23_intake_queries import sql_objects,dax_objects
class ReadPatterns(unittest.TestCase):
 def test_safe_sql_patterns_remain_read_only_and_graph_scoped(self):
  layer={'dialect':'T-SQL','objects':sql_objects()}
  for query in ['WITH x AS (SELECT id,quantity FROM dbo.Items) SELECT SUM(quantity) AS n FROM x','SELECT SUM(TRY_CAST(quantity AS BIGINT)) AS n FROM dbo.Items','SELECT CONVERT(BIGINT,quantity) AS n FROM dbo.Items','SELECT id, SUM(quantity) OVER (PARTITION BY id) AS n FROM dbo.Items']:
   with self.subTest(query=query):self.assertEqual(validate(query,layer)['asset_ids'],['table'])
  for query in ['DELETE FROM dbo.Items','SELECT id FROM other.Items','SELECT id INTO dbo.New FROM dbo.Items']:
   with self.subTest(query=query),self.assertRaises(Exception):validate(query,layer)
 def test_dax_define_var_summarizecolumns_treatas(self):
  layer={'dialect':'DAX','objects':dax_objects()}
  for query in ['DEFINE VAR x = [Quantity] EVALUATE ROW("n",x)','EVALUATE SUMMARIZECOLUMNS(Activity[units],"n",[Quantity])','EVALUATE CALCULATETABLE(ROW("n",[Quantity]),TREATAS({1},Activity[units]))']:
   with self.subTest(query=query):self.assertTrue(validate(query,layer)['asset_ids'])
if __name__=='__main__':unittest.main()
