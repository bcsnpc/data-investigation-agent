import copy
import unittest
from unittest.mock import Mock
from investigator.adapters.graph_container_schema import SqlContainerChanges
from test_graph_asset_catalog import CatalogTests,T


class ReaderTests(unittest.TestCase):
 def setUp(self):
  self.owner='lake';self.table='lake/table/dbo.t';self.config={'fabric':{'sql_reader':{'server':'server','account':'reader'}}}
  self.obj={'asset_id':self.table,'connection':'server','database':'db','catalog':{'metadata':{'schema_name':'dbo','name':'t'}}}
  self.assets=[{'id':self.owner,'kind':'Lakehouse','name':'Lake','parent_id':None,'metadata':{}},
   {'id':self.table,'kind':'LakehouseTable','name':'dbo.t','parent_id':self.owner,'metadata':{'location':'retained-location'}},
   {'id':self.table+'/column/old','kind':'LakehouseColumn','name':'old','parent_id':self.table,'metadata':{'name':'old'}}]
  self.execute=Mock(return_value={'read_only_verified':True,'surface_report':{'identity':'reader','object':'db','engine':'Microsoft Azure SQL Data Warehouse'},
   'rows':[{'schema_name':'dbo','table_name':'t','column_name':'new','data_type':'int','collation_name':None}]})
 def reader(self,objects=None):
  return SqlContainerChanges('investigator',self.config,{self.owner:objects or [self.obj]},
   lambda owner:{'assets':self.assets,'source_asset_ids':[]},self.execute)
 def test_exact_schema_replaces_columns_preserves_retained_parent_and_records_scope(self):
  reader=self.reader();result=reader.fetch(self.owner)
  self.assertEqual(result['assets'][:2],self.assets[:2]);self.assertEqual(reader.retained_ids[self.owner],['lake',self.table])
  self.assertEqual([a['name']for a in result['assets']if a['kind']=='LakehouseColumn'],['new'])
  proof=next(a for a in result['assets']if a['kind']=='GraphSchemaEvidence')['metadata']
  self.assertFalse(proof['complete_database_inventory']);self.assertEqual(proof['proof']['surface_report']['identity'],'reader')
  self.assertEqual(self.execute.call_args.args[1]['read_only_objects'],['[dbo].[t]'])
 def test_partial_table_coverage_refuses_before_read_and_cannot_erase(self):
  self.assets.append({'id':'lake/table/hidden','kind':'LakehouseTable','name':'dbo.hidden','parent_id':'lake','metadata':{}})
  before=copy.deepcopy(self.assets)
  with self.assertRaisesRegex(ValueError,'PARTIAL_TABLE_COVERAGE'):self.reader().fetch(self.owner)
  self.execute.assert_not_called();self.assertEqual(before,self.assets)
 def test_incomplete_columns_and_wrong_identity_refuse(self):
  baseline=copy.deepcopy(self.execute.return_value)
  for change in ('empty','limit','identity'):
   with self.subTest(change=change):
    result=copy.deepcopy(baseline)
    if change=='empty':result['rows']=[]
    elif change=='limit':result['rows']*=250
    else:result['surface_report']['identity']='scanner'
    self.execute.return_value=result
    with self.assertRaises(ValueError):self.reader().fetch(self.owner)
 def test_cross_database_and_scanner_credentials_rejected_before_read(self):
  second=copy.deepcopy(self.obj);second['database']='other'
  with self.assertRaisesRegex(ValueError,'DATABASE_DIFFERS'):self.reader([self.obj,second])
  self.config['fabric']['sql_reader']['mode']='federated_scanner'
  with self.assertRaisesRegex(ValueError,'SCANNER_SQL'):self.reader()
  self.execute.assert_not_called()
 def test_schedule_scanner_cannot_select_investigator_sql_config(self):
  from scan_estate_graph import validate
  config={'estate':'estate','workspace':'w','owners':['i'],'authentication':{'mode':'federated_scanner'},'storage':{},'definition_uri_prefix':'cas://x','budget':{},'max_requests':10,'approval':'owner',
   'container_schemas':[{'identity':'reader','config':self.config,'owners':{'fabric://w/i':[self.obj]}}]}
  with self.assertRaisesRegex(ValueError,'SCANNER_SQL'):validate(config)
  config['authentication']['mode']='federated_reader';validate(config)
  from scan_estate_graph import definition_owner_ids
  self.assertEqual(definition_owner_ids(config),[])
  config['owners'].append('report')
  self.assertEqual(definition_owner_ids(config),['report'])
 def test_sql_endpoint_cannot_borrow_lakehouse_children(self):
  self.assets[0]['kind']='SQLEndpoint';self.assets[1]['parent_id']='another-lake'
  with self.assertRaisesRegex(ValueError,'TABLE_BINDING'):self.reader().fetch(self.owner)
  self.execute.assert_not_called()


class RetainedTimesTests(CatalogTests):
 def test_exact_unchanged_retained_assets_keep_old_observation_time(self):
  payload=self.payload('lake');ids=[a['id']for a in payload['assets']]
  self.catalog.refresh('estate','lake',T[1],payload,retained_asset_ids=ids)
  _,_,_,times=self.catalog.snapshot('estate')
  self.assertTrue(all(times[key]==T[0].replace('Z','.000000Z')for key in ids))
 def test_changed_asset_cannot_claim_retained_timestamp(self):
  payload=self.payload('lake');identity=payload['assets'][0]['id'];payload['assets'][0]['name']='changed'
  before=self.catalog.snapshot('estate')[0]
  with self.assertRaisesRegex(ValueError,'RETAINED_ASSET_CONTENT'):self.catalog.refresh('estate','lake',T[1],payload,retained_asset_ids=[identity])
  self.assertEqual(before,self.catalog.snapshot('estate')[0])

if __name__=='__main__':unittest.main()
