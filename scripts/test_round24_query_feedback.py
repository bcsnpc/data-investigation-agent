import unittest
from unittest.mock import Mock
from investigator.investigative_queries import Queries
from test_round23_intake_queries import sql_objects
class FeedbackTests(unittest.TestCase):
 def make(self,execute):return Queries({'x':{'dialect':'T-SQL','objects':sql_objects()}},execute=execute,reserve=Mock(),save=Mock())
 def test_invalid_read_has_exact_query_error_schema_and_no_native_request(self):
  execute=Mock();q=self.make(execute);r=q.run('x','SELECT missing FROM dbo.Items',kind='sql',purpose='compare')
  self.assertEqual(r['status'],'ERROR');self.assertIn('missing',r['text']);self.assertTrue(r['error']);self.assertEqual(r['schema_slice'][0]['name'],'Items');self.assertFalse(r['native_dispatched']);execute.assert_not_called()
 def test_native_error_preserved_and_only_two_corrections_allowed(self):
  execute=Mock(side_effect=RuntimeError('SQL native error 207: Invalid column name event_day'));q=self.make(execute)
  for _ in range(3):r=q.run('x','SELECT id FROM dbo.Items',kind='sql',purpose='compare')
  self.assertEqual(r['error'],'SQL native error 207: Invalid column name event_day');self.assertTrue(r['native_dispatched']);self.assertEqual(r['failure_class'],'wrong column or table')
  self.assertEqual(q.run('x','SELECT id FROM dbo.Items',kind='sql',purpose='compare')['error'],'QUERY_CORRECTION_LIMIT');self.assertEqual(execute.call_count,3)
 def test_exact_success_is_reused_even_after_other_queries_use_corrections(self):
  execute=Mock(return_value={'rows':[{'id':1}]});q=self.make(execute);first=q.run('x','SELECT id FROM dbo.Items',kind='sql',purpose='compare')
  for _ in range(3):q.run('x','SELECT missing FROM dbo.Items',kind='sql',purpose='compare')
  self.assertEqual(q.run('x','SELECT id FROM dbo.Items',kind='sql',purpose='compare')['already_have'],first['id']);self.assertEqual(execute.call_count,1)
 def test_write_still_raises_before_dispatch(self):
  execute=Mock();q=self.make(execute)
  with self.assertRaises(ValueError):q.run('x','DELETE FROM dbo.Items',kind='sql',purpose='compare')
  execute.assert_not_called()
if __name__=='__main__':unittest.main()
