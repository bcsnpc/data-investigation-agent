import copy
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from investigation_checks import canonical, compare, freshness, run_checks, resolve_context
from lineage_graph import Graph


def evidence(data, asset='source', **changes):
    result = dict(asset=asset, captured_at='2026-09-13T12:00:00Z', query_id='versioned-query-v1',
                  data=data, result_hash=hashlib.sha256(canonical(data).encode()).hexdigest(),
                  metric_contract='net-sales-v1', grain='order', currency='USD',
                  filters={'order_id': 'ORD-000002'}, source_snapshot={'sql-extract': 'batch-1'}, complete=True)
    result.update(changes)
    return result


class Checks(unittest.TestCase):
    def test_exact_decimal_and_large_value(self):
        result = compare(evidence('100000000000000000000000000000.01'), evidence('100000000000000000000000000000.02'), 'total')
        self.assertEqual(result['downstream_minus_upstream'], '0.01')
        self.assertEqual(compare(evidence('153.00'), evidence('153'), 'total')['status'], 'MATCH')

    def test_invalid_numbers_do_not_become_zero(self):
        for value in (None, True, 0.1, 'NaN', 'Infinity', 'abc'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                compare(evidence(value), evidence('0'), 'total')

    def test_context_and_snapshot_mismatch(self):
        for key, value in [('currency', 'EUR'), ('grain', 'line'), ('filters', {}),
                           ('source_snapshot', None), ('metric_contract', 'net-cash-v1')]:
            with self.subTest(key=key):
                self.assertEqual(compare(evidence('1'), evidence('1', **{key: value}), 'total')['status'], 'NOT_COMPARABLE')

    def test_hash_tampering_rejected(self):
        bad = evidence('1'); bad['data'] = '2'
        with self.assertRaises(ValueError):
            compare(bad, evidence('2'), 'total')

    def test_keys_detect_duplicates_and_missing(self):
        result = compare(evidence([['a'], ['b']]), evidence([['a'], ['a']]), 'keys')
        self.assertEqual((result['missing_count'], result['extra_count'], result['downstream_duplicate_count']), (1, 1, 1))
        self.assertEqual(result['missing_sample'], [['b']])

    def test_keys_types_composite_and_truncation(self):
        self.assertEqual(compare(evidence([[1, 'a']]), evidence([['1', 'a']]), 'keys')['status'], 'MISMATCH')
        self.assertEqual(compare(evidence([]), evidence([], complete=False), 'keys')['status'], 'NOT_COMPARABLE')
        with self.assertRaises(ValueError):
            compare(evidence([[None]]), evidence([]), 'keys')

    def test_freshness_policy_and_missing_history(self):
        item = evidence({'last_success_at': '2026-09-13T11:00:00Z'})
        self.assertEqual(freshness(item, item['captured_at'])['status'], 'UNKNOWN')
        self.assertEqual(freshness(item, item['captured_at'], 3600)['status'], 'WITHIN_POLICY')
        self.assertEqual(freshness(item, item['captured_at'], 3599)['status'], 'STALE')
        self.assertEqual(freshness(evidence({}), item['captured_at'], 3600)['status'], 'UNKNOWN')

    def test_future_refresh_and_timezone(self):
        item = evidence({'last_success_at': '2026-09-14T11:00:00Z'})
        self.assertEqual(freshness(item, item['captured_at'], 3600)['status'], 'UNKNOWN')
        with self.assertRaises(ValueError):
            freshness(item, '2026-09-13T12:00:00', 3600)

    def graph(self):
        graph = Graph([dict(id=x, parent=None, kind='SqlObject', name=x, meta={}, hash='hash') for x in ('source', 'dest', 'other')])
        graph.edge('source', 'dest', 'data', 'source', {})
        return graph

    def test_persistence_retains_evidence_and_never_classifies_bug(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder)/'evidence.sqlite'
            request = dict(lineage_run='pinned', as_of='2026-09-13T13:00:00Z', checks=[dict(kind='total', upstream=evidence('1'), downstream=evidence('2', 'dest'))])
            with patch('investigation_checks.load_graph', return_value=self.graph()):
                result = run_checks(database, request)
            self.assertEqual(result['classification'], 'UNRESOLVED')
            self.assertEqual(result['checks'][0]['result']['status'], 'MISMATCH')
            with closing(sqlite3.connect(database)) as db:
                row = db.execute('select request,result from investigation_runs').fetchone()
            self.assertEqual(json.loads(row[0]), request)
            self.assertEqual(json.loads(row[1]), result)

    def test_disconnected_and_invalid_batch_not_persisted(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder)/'evidence.sqlite'
            good = dict(kind='total', upstream=evidence('1'), downstream=evidence('1', 'dest'))
            bad = copy.deepcopy(good); bad['downstream']['asset'] = 'other'
            request = dict(lineage_run='pinned', as_of='2026-09-13T13:00:00Z', checks=[good, bad])
            with patch('investigation_checks.load_graph', return_value=self.graph()), self.assertRaises(ValueError):
                run_checks(database, request)
            self.assertFalse(database.exists())

    def test_report_context_is_scoped_and_ambiguity_explicit(self):
        graph = self.graph()
        for name, kind in [('report', 'Report'), ('metric1', 'Measure'), ('metric2', 'Measure')]:
            graph.assets[name] = dict(id=name, kind=kind, name='Net Sales', parent=None, meta={}, hash='hash')
        graph.edge('metric1', 'report', 'binding', 'report', {})
        with patch('investigation_checks.load_graph', return_value=graph):
            self.assertEqual(resolve_context('unused', 'pinned', 'report', 'Net Sales')['status'], 'RESOLVED')
            graph.edge('metric2', 'report', 'binding', 'report', {})
            self.assertEqual(resolve_context('unused', 'pinned', 'report', 'Net Sales')['status'], 'UNRESOLVED')
            with self.assertRaises(ValueError):
                resolve_context('unused', 'pinned', 'source', 'Net Sales')

    def test_future_observation_rejected(self):
        request = dict(lineage_run='pinned', as_of='2026-09-12T13:00:00Z', checks=[dict(kind='total', upstream=evidence('1'), downstream=evidence('1', 'dest'))])
        with patch('investigation_checks.load_graph', return_value=self.graph()), self.assertRaises(ValueError):
            run_checks('unused', request)


if __name__ == '__main__':
    unittest.main()
