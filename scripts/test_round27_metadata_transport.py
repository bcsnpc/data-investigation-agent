"""Transport regression for pure metadata reads; no network or credentials."""
import copy,os,unittest
from unittest.mock import patch
from investigator.investigation_metadata import sql
from investigator.live_gateway import authorize_sql_payload,configured,GatewayDenied

class MetadataTransportTests(unittest.TestCase):
 def setUp(self):
  self.env=patch.dict(os.environ,{'DIA_GATEWAY_SQL_IDENTITY':'reader','DIA_LIVE_ACCESS_DISABLED':'0'});self.env.start();self.addCleanup(self.env.stop)
  self.policy={'version':1,'live_enabled':True,'identities':{'reader':{'sql':[{'server':'server','database':'database','objects':['dbo.Items'],'controls':['CATALOG'],'read_only':True,'row_cap':251,'timeout_seconds':30}]}}}
 def payload(self,text='SELECT name,temporal_type_desc FROM sys.tables'):
  b=sql(text,{'objects':[{'id':'table'}]},250)
  return {k:b[k]for k in ('query','parameters','max_rows','result_columns')}|{'server':'server','database':'database','read_only_objects':['dbo.Items']}
 def test_catalog_information_schema_and_dmv_reads_keep_user_route_guards(self):
  for q in ['SELECT name,temporal_type_desc FROM sys.tables','SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES','SELECT * FROM sys.dm_db_log_stats(DB_ID())']:
   with self.subTest(q=q),configured(self.policy):
    v=authorize_sql_payload(self.payload(q));self.assertTrue(v['require_read_only']);self.assertEqual(v['read_only_objects'],['dbo.Items'])
 def test_catalog_control_is_required(self):
  p=copy.deepcopy(self.policy);p['identities']['reader']['sql'][0]['controls']=[]
  with configured(p),self.assertRaises(GatewayDenied):authorize_sql_payload(self.payload())
 def test_anchor_and_endpoint_must_already_be_admitted(self):
  for change in [{'read_only_objects':['dbo.Secret']},{'server':'another'},{'database':'another'},{'max_rows':252}]:
   with self.subTest(change=change),configured(self.policy),self.assertRaises(GatewayDenied):authorize_sql_payload(self.payload()|change)
 def test_flag_cannot_authorize_mixed_or_writing_queries(self):
  for q in ['SELECT s.name FROM sys.tables s JOIN dbo.Secret x ON 1=1','SELECT name INTO dbo.X FROM sys.tables','DELETE FROM sys.tables','EXEC sp_executesql N\'SELECT 1\'','SELECT name FROM Other.sys.tables','SELECT name FROM sys.tables; SELECT * FROM dbo.Secret']:
   with self.subTest(q=q),configured(self.policy),self.assertRaises((GatewayDenied,ValueError)):authorize_sql_payload(self.payload()|{'query':q,'metadata_scope':{'not_a_business_table_read':True}})
 def test_parameters_and_result_shape_cannot_bypass_revalidation(self):
  for change in [{'parameters':[1]},{'result_columns':['fake']},{'max_rows':True}]:
   with self.subTest(change=change),configured(self.policy),self.assertRaises((GatewayDenied,ValueError)):authorize_sql_payload(self.payload()|change)

if __name__=='__main__':unittest.main()
