"""Synthetic metadata reads and write/escape refusals; no estate or model calls."""
import unittest
from investigator.investigative_queries import validate,Queries
from test_round23_intake_queries import sql_objects,dax_objects


class MetadataTests(unittest.TestCase):
    def setUp(self):self.sql={'dialect':'T-SQL','objects':sql_objects()};self.dax={'dialect':'DAX','objects':dax_objects()}
    def test_native_catalog_views_and_dmvs_without_inventory_table_entries(self):
        for text in ["SELECT t.name,t.temporal_type_desc FROM sys.tables t WHERE t.object_id=OBJECT_ID(N'dbo.Items')",
                     'SELECT TABLE_NAME,COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS',
                     'SELECT name FROM sys.tables WHERE schema_id=SCHEMA_ID(\'dbo\')',
                     'SELECT * FROM sys.dm_db_log_stats(DB_ID())',
                     "SELECT OBJECT_ID(N'dbo.Items') AS object_id",
                     'SELECT t.name,s.name AS schema_name FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id']:
            with self.subTest(text=text):
                result=validate(text,self.sql)
                self.assertIn('TOP 251',result['query']);self.assertTrue(result['metadata_scope']['not_a_business_table_read'])
                self.assertEqual(result['asset_ids'],['table'])
    def test_info_rowsets_stay_on_admitted_model_without_udf_or_xmla(self):
        for text in ['EVALUATE INFO.PARTITIONS()','EVALUATE INFO.VIEW.TABLES()',
                     'EVALUATE INFO.TABLES("ID", "3")']:
            with self.subTest(text=text):
                result=validate(text,self.dax);self.assertTrue(result['query'].startswith('EVALUATE TOPN(251,INFO.'))
                self.assertIn('metadata_scope',result)
    def test_describe_delta_is_bound_to_graph_table_and_bounded(self):
        layer={**self.sql,'dialect':'Spark SQL'}
        for text in ['DESCRIBE HISTORY dbo.Items LIMIT 999','DESCRIBE DETAIL dbo.Items','DESC TABLE EXTENDED dbo.Items']:
            with self.subTest(text=text):
                result=validate(text,layer);self.assertEqual(result['asset_ids'],['table'])
                if 'HISTORY'in text:self.assertTrue(result['query'].endswith('LIMIT 251'))
        with self.assertRaises(ValueError):validate('DESCRIBE HISTORY other.Secret',layer)
    def test_writes_ddl_execution_and_cross_endpoint_escapes_still_refused(self):
        for text in ['SELECT name INTO dbo.Copy FROM sys.tables','SELECT name FROM sys.tables; DROP TABLE dbo.Items',
                     'EXEC sys.sp_executesql N\'SELECT 1\'', 'UPDATE sys.tables SET name=\'X\'',
                     'DELETE FROM sys.tables','CREATE TABLE dbo.X(id int)','SELECT * FROM other.sys.tables',
                     'SELECT dbo.run_external_code(name) FROM sys.tables','SELECT * FROM sys.xp_cmdshell(\'whoami\')',
                     'SELECT x.name FROM sys.tables x JOIN dbo.Secret s ON 1=1']:
            with self.subTest(text=text),self.assertRaises(ValueError):validate(text,self.sql)
        for text in ['EVALUATE INFO.TABLES(); EVALUATE ROW("x",1)',
                     'EVALUATE INFO.TABLES([SecretMeasure])','EVALUATE INFO.TABLES("x",)',
                     'EVALUATE INFO.TABLES','EVALUATE INFO.TABLES() + [SecretMeasure]']:
            with self.subTest(text=text),self.assertRaises(ValueError):validate(text,self.dax)
    def test_metadata_results_keep_scope_and_exact_query_evidence(self):
        events=[];q=Queries({'one':self.sql},execute=lambda *a,**k:{'rows':[{'name':'Items'}]},reserve=lambda *a:None,save=events.append)
        row=q.run('one','SELECT name FROM sys.tables',kind='sql',purpose='history')
        self.assertTrue(row['metadata_scope']['route_anchor_only'])
        self.assertEqual(row['result']['rows'],[{'name':'Items'}])
        self.assertEqual(q.run('one','SELECT name FROM sys.tables',kind='sql',purpose='history')['already_have'],row['id'])


if __name__=='__main__':unittest.main()
