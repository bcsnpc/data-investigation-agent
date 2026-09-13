import unittest
from pathlib import Path
import re
from decimal import Decimal
import duckdb
from unittest.mock import patch

from cross_layer_investigation import boundaries, metric_observation, acquire
import json
import sqlite3
import tempfile
from contextlib import closing
from investigation_query_worker import dax, execute, extract_dax
from lineage_graph import Graph
from test_investigation_checks import evidence


class CrossLayerTests(unittest.TestCase):
    def graph(self):
        g = Graph([dict(id=x, parent=None, name=x, kind='Table', hash='hash', meta={}) for x in ('a', 'b', 'c')])
        g.edge('a', 'b', 'data', 'a', {})
        g.edge('b', 'c', 'data', 'b', {})
        return g

    def chain(self, values):
        return [evidence(value, asset, status='AVAILABLE') for asset, value in zip(('a', 'b', 'c'), values)]

    def test_first_comparable_divergence(self):
        result = boundaries(self.graph(), self.chain(['10', '10', '9']))
        self.assertEqual(result['first_verified_divergence'], {'upstream': 'b', 'downstream': 'c'})
        self.assertEqual(result['classification'], 'UNRESOLVED')

    def test_missing_snapshot_is_only_observed_difference(self):
        chain = self.chain(['10', '10', '9'])
        for item in chain:
            item['source_snapshot'] = None
        result = boundaries(self.graph(), chain)
        self.assertIsNone(result['first_verified_divergence'])
        self.assertEqual(result['first_observed_difference'], {'upstream': 'b', 'downstream': 'c'})
        self.assertTrue(all(x['status'] == 'NOT_COMPARABLE' for x in result['boundaries']))

    def test_missing_earlier_read_blocks_first_boundary(self):
        chain = self.chain(['10', '10', '9'])
        chain[0]['status'] = 'UNAVAILABLE'
        result = boundaries(self.graph(), chain)
        self.assertIsNone(result['first_verified_divergence'])
        self.assertIsNone(result['first_observed_difference'])
        self.assertEqual(result['boundaries'][1]['status'], 'MISMATCH')

    def test_different_filters_do_not_show_observed_difference(self):
        chain = self.chain(['10', '10', '9'])
        chain[1]['filters'] = {}
        result = boundaries(self.graph(), chain)
        self.assertTrue(all(x['observed_value'] == 'UNKNOWN' for x in result['boundaries']))

    def test_lineage_gap_blocks_verified_divergence(self):
        g = self.graph(); g.gap('a', 'unresolved dependency', {})
        result = boundaries(g, self.chain(['10', '10', '9']))
        self.assertIsNone(result['first_verified_divergence'])

    def test_reversed_or_repeated_path_rejected(self):
        for chain in (self.chain(['1', '2', '3'])[::-1], [evidence('1', 'a')]*2):
            with self.assertRaises(ValueError):
                boundaries(self.graph(), chain)

    def test_empty_scope_query_has_explicit_blank_contract(self):
        query = dax('USD', None)
        self.assertIn('COALESCE([Order Count],0)', query)
        self.assertIn('COALESCE([Net Cash],0)', query)
        self.assertNotIn('FactOrder[order_id]', query)
        self.assertIn('"en-US"', query)

    def test_injection_rejected_before_transport(self):
        for currency, order in [('USD"', None), ('USD', 'ORD-000002"})'), ('USD', ''), ('usd', None)]:
            with self.assertRaises(ValueError):
                dax(currency, order)
        with patch('investigation_query_worker.subprocess.run') as run:
            with self.assertRaises(ValueError):
                execute({'layer': 'delete', 'currency': 'USD'})
            run.assert_not_called()

    def test_api_partial_error_is_not_a_valid_zero(self):
        good = {'results': [{'tables': [{'rows': [{'[order_count]': '1', '[net_cash]': '1529.6400'}]}]}]}
        self.assertEqual(extract_dax(good)['net_cash'], '1529.6400')
        good['results'][0]['error'] = {'message': 'partial'}
        with self.assertRaises(ValueError):
            extract_dax(good)

    def test_query_evidence_is_hashed_snapshot_not_invented(self):
        result = {'values': {'net_cash': '1529.6400'}, 'query': 'fixed query', 'captured_at': '2026-09-13T12:00:00Z'}
        item = metric_observation('a', 'net_cash', result, 'USD', 'ORD-000002', 'sql')
        self.assertIsNone(item['source_snapshot'])
        self.assertEqual(len(item['query_id']), 64)
        self.assertEqual(item['data'], '1529.6400')

    def test_fixed_source_query_paid_cancellation_partial_refund_and_currency(self):
        source = (Path(__file__).resolve().parents[1]/'infra/scripts/Read-InvestigationMetric.ps1').read_text()
        query = re.findall(r"CommandText=@'\n(.*?)\n'@", source, re.S)[0]
        # Execute the actual fixed source query in the existing offline SQL test engine.
        query = query.replace('COUNT_BIG', 'COUNT').replace('@currency', '$currency').replace('@order_id', '$order_id')
        with duckdb.connect() as db:
            db.execute('CREATE SCHEMA app')
            db.execute('CREATE TABLE app.orders(order_id VARCHAR, currency VARCHAR)')
            db.execute('CREATE TABLE app.payments(order_id VARCHAR,payment_status VARCHAR,amount DECIMAL(19,4))')
            db.execute('CREATE TABLE app.refunds(order_id VARCHAR,refund_amount DECIMAL(19,4))')
            db.execute("INSERT INTO app.orders VALUES ('ORD-000001','USD'),('ORD-000002','USD'),('ORD-000003','EUR')")
            db.execute("INSERT INTO app.payments VALUES ('ORD-000001','CAPTURED',100),('ORD-000002','CAPTURED',1682.64),('ORD-000002','FAILED',1682.64),('ORD-000003','CAPTURED',900)")
            db.execute("INSERT INTO app.refunds VALUES ('ORD-000001',100),('ORD-000002',100),('ORD-000002',53)")
            self.assertEqual(db.execute(query, {'currency':'USD','order_id':None}).fetchone(), (2, Decimal('1529.6400')))
            self.assertEqual(db.execute(query, {'currency':'USD','order_id':'ORD-000001'}).fetchone(), (1, Decimal('0.0000')))
            self.assertEqual(db.execute(query, {'currency':'USD','order_id':'ORD-999999'}).fetchone(), (0, Decimal('0.0000')))

    def test_acquisition_retains_failed_read_and_successful_neighbors(self):
        ids = ['sql', 'bronze', 'silver', 'gold', 'semantic']
        graph = Graph([dict(id=x, parent=None, name=x, kind='Table', hash='hash', meta={}) for x in ids])
        for a,b in zip(ids,ids[1:]):
            graph.edge(a,b,'data',a,{})
        with tempfile.TemporaryDirectory() as folder:
            config = {'fabric': {'workspace_id':'w','auth':{'python':'python','tenant_id':'t'}},
                      'sql': {'server':'server','database':'db','auth':{'credential_file':'ignored-local-path'}},
                      'storage': {'database': str(Path(folder)/'evidence.sqlite')}}
            estate = {'workspace_id':'w','semantic_model_id':'model', **{layer+'_lakehouse_id':layer for layer in ids[1:4]}}
            def query(config, request):
                if request['layer']=='silver':
                    raise RuntimeError('private error detail must not be stored')
                return {'values':{'order_count':'1','net_cash':'2.0000'},'query':'fixed','captured_at':'2026-09-13T12:00:00Z'}
            with patch('cross_layer_investigation.load_graph', return_value=graph), patch('cross_layer_investigation.asset_path', return_value=ids), patch('cross_layer_investigation.WorkerTransport') as http:
                http.return_value.return_value = {'text':{'properties':{'sqlEndpointProperties':{'connectionString':'host','id':'endpoint'}}}}
                result = acquire(config,estate,'pinned','USD',None,query)
            self.assertEqual(result['values']['silver']['error'], 'QUERY_UNAVAILABLE')
            self.assertEqual(result['values']['gold']['net_cash'], '2.0000')
            self.assertIsNone(result['metrics']['net_cash']['first_verified_divergence'])
            with closing(sqlite3.connect(config['storage']['database'])) as db:
                stored = db.execute('select request,result from investigation_runs').fetchone()
            self.assertNotIn('private error detail', ''.join(stored))
            self.assertNotIn('ignored-local-path', ''.join(stored))
            self.assertEqual(len(json.loads(stored[0])['adapter_hashes']),2)


if __name__ == '__main__':
    unittest.main()
