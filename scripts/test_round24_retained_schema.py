import unittest,copy
import test_round23_native_catalog as fixtures
class RetainedSchemaTests(unittest.TestCase):
 def test_exact_reader_schema_reuses_types_but_still_checks_native_endpoint(self):
  h=fixtures.NativeCatalogTests();h.setUp()
  proof={'kind':'NATIVE_TARGET_CATALOG','asset_id':h.table,'database':'Bronze SQL','schema':'dbo','table':'Items','columns':[{'name':'quantity','data_type':'bigint'}]}
  h.assets.append(fixtures.asset(h.table+'/reader-schema-evidence','GraphSchemaEvidence',h.table,'Schema',{'scope':'DECLARED_RETAINED_TABLE_ONLY','proof':proof}))
  c=h.build();route=c.prepare(next(iter(c.routes)))
  h.endpoint.assert_called_once();h.read.assert_not_called()
  self.assertEqual(route['database'],'Bronze SQL');self.assertEqual(route['objects'][0]['metadata']['schema_basis'],'RETAINED_EXACT_NATIVE_CATALOG')
  self.assertNotIn('fresh_native_schema',route['objects'][0]['metadata'])
 def test_same_named_schema_from_a_different_database_is_not_reused(self):
  h=fixtures.NativeCatalogTests();h.setUp()
  proof={'kind':'NATIVE_TARGET_CATALOG','asset_id':h.table,'database':'Other database','schema':'dbo','table':'Items','columns':[{'name':'quantity','data_type':'bigint'}]}
  h.assets.append(fixtures.asset(h.table+'/reader-schema-evidence','GraphSchemaEvidence',h.table,'Schema',{'scope':'DECLARED_RETAINED_TABLE_ONLY','proof':proof}))
  c=h.build();c.prepare(next(iter(c.routes)));h.read.assert_called_once()
if __name__=='__main__':unittest.main()
