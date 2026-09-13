from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from cross_layer_investigation import acquire,selected_bronze_schema
from investigation_query_worker import execute,bronze_schema
from lineage_graph import Graph


class SelectionTests(unittest.TestCase):
    def test_schema_must_match_snapshot_uuid(self):
        snapshot={'source_snapshot_id':'11111111-1111-1111-1111-111111111111','schema':'snapshot_'+'1'*32}
        self.assertEqual(selected_bronze_schema({'snapshot_bronze':snapshot}),snapshot['schema'])
        snapshot['schema']='app'
        with self.assertRaises(ValueError):selected_bronze_schema({'snapshot_bronze':snapshot})

    def test_schema_injection_rejected_before_auth(self):
        for schema in ('app]; DROP TABLE orders;--','snapshot_abc','dbo',None):
            with self.assertRaises(ValueError):bronze_schema(schema)
        with patch('investigation_query_worker.get_sql_token') as token:
            with self.assertRaises(ValueError):execute({'layer':'bronze','currency':'USD','bronze_schema':'bad;'})
            token.assert_not_called()

    def test_configured_build_and_actual_bronze_request_are_retained(self):
        ids=['sql','bronze','silver','gold','semantic']
        graph=Graph([dict(id=x,parent=None,name=x,kind='Table',hash='h',meta={}) for x in ids])
        for a,b in zip(ids,ids[1:]):graph.edge(a,b,'data',a,{})
        schema='snapshot_'+'1'*32
        with tempfile.TemporaryDirectory() as folder:
            config={'fabric':{'workspace_id':'w','auth':{'python':'python','tenant_id':'t'}},
                    'sql':{'server':'s','database':'d','auth':{'credential_file':'secret-local-path'}},
                    'storage':{'database':str(Path(folder)/'db.sqlite')}}
            estate={'workspace_id':'w','semantic_model_id':'model','investigation':{'lineage_run':'reviewed'},
                    'snapshot_bronze':{'source_snapshot_id':'11111111-1111-1111-1111-111111111111','schema':schema},
                    **{x+'_lakehouse_id':x for x in ids[1:4]}}
            requests=[]
            def query(_,request):
                requests.append(request)
                return {'values':{'order_count':'1','net_cash':'2.0000'},'query':'fixed','captured_at':'2026-09-13T12:00:00Z'}
            with patch('cross_layer_investigation.load_graph',return_value=graph) as loader,patch('cross_layer_investigation.asset_path',return_value=ids),patch('cross_layer_investigation.WorkerTransport') as http:
                http.return_value.return_value={'text':{'properties':{'sqlEndpointProperties':{'connectionString':'host','id':'db'}}}}
                result=acquire(config,estate,None,'USD',None,query)
                loader.assert_called_once_with(config['storage']['database'],'reviewed')
            self.assertEqual(next(r for r in requests if r['layer']=='bronze')['bronze_schema'],schema)
            self.assertTrue(all(r['status']=='NOT_COMPARABLE' for r in result['metrics']['net_cash']['boundaries']))
            with closing(sqlite3.connect(config['storage']['database'])) as db:
                saved=json.loads(db.execute('SELECT request FROM investigation_runs').fetchone()[0])
            self.assertEqual(saved['bronze_schema'],schema)
            self.assertEqual(saved['asset_paths']['net_cash'],ids)
            self.assertNotIn('secret-local-path',json.dumps(saved))

    def test_no_implicit_latest_graph(self):
        with patch('cross_layer_investigation.load_graph') as load:
            with self.assertRaises(ValueError):acquire({'fabric':{'workspace_id':'w'}},{'workspace_id':'w'},None,'USD',None)
            load.assert_not_called()


if __name__=='__main__':unittest.main()
