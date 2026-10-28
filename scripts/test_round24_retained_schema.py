import unittest,copy
from unittest.mock import Mock,patch
import test_round23_native_catalog as fixtures
class RetainedSchemaTests(unittest.TestCase):
 def source(self,kind='USER_TABLE'):
  h=fixtures.NativeCatalogTests();h.setUp();parent='sql://server/application';table=parent+'/object/1'
  h.assets.extend([fixtures.asset(parent,'SqlDatabase',None,'application',{}),fixtures.asset(table,'SqlObject',parent,'Items',{'schema_name':'dbo','name':'Items','type_desc':kind,'columns':[{'name':'quantity','data_type':'int'}]})]);h.nodes.append({'id':'source','kind':'TABLE','properties':{'asset_id':table}})
  c=h.build();c.source_read=Mock();identity=next(i for i,r in c.routes.items()if r['kind']=='SOURCE_SQL');return c,identity
 def test_exact_retained_source_table_schema_does_not_require_a_second_catalog_read(self):
  c,identity=self.source();route=c.prepare(identity);c.source_read.assert_not_called();m=route['objects'][0]['metadata']
  self.assertEqual(m['schema_basis'],'RETAINED_EXACT_NATIVE_CATALOG');self.assertNotIn('fresh_native_schema',m);self.assertIn('read-only enforcement',m['schema_qualification'])
 def test_source_views_and_missing_column_types_still_require_native_dependency_metadata(self):
  for kind in ('VIEW','USER_TABLE'):
   c,identity=self.source(kind)
   c.routes[identity]['objects'][0]['metadata']['schema_basis']='RETAINED_EXACT_NATIVE_CATALOG'
   if kind=='USER_TABLE':c.routes[identity]['objects'][0]['metadata']['columns'][0].pop('data_type')
   with patch('investigator.adapters.binding_catalog.read_many',side_effect=RuntimeError('Native dependency metadata requested'))as native:
    with self.assertRaisesRegex(RuntimeError,'Native dependency'):c.prepare(identity)
   native.assert_called_once()
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
