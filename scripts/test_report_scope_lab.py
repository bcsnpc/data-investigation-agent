from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from defect_lab import initialize, validate
from report_scope_lab import investigate


class ReportScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name)/'lab.duckdb'
        self.store = Path(self.temp.name)/'evidence.sqlite'
        initialize(self.lab)

    def run_scope(self, requested, actual):
        result = investigate(self.lab, self.store, requested, actual)
        self.assertEqual(validate(self.lab)['status'], 'READY')
        self.assertFalse(result['root_cause_verified'])
        self.assertFalse(result['automatic_defect_routing'])
        return result

    def test_unintended_filter_preserves_evidence_and_impact(self):
        result = self.run_scope('all_orders', 'exclude_partial_returns')
        self.assertTrue(result['local_filter_mismatch_verified'])
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'], '-99.0000')
        self.assertEqual(result['affected_records'][0]['order_id'], 'ORD-000001')
        self.assertEqual(result['affected_records'][0]['status'], 'MISSING_IN_REPORT')
        with closing(sqlite3.connect(self.store)) as db:
            request, saved = db.execute('SELECT request,result FROM investigation_runs').fetchone()
        self.assertEqual(json.loads(saved), result)
        self.assertEqual(json.loads(request)['report_scope_evidence']['requested_scope'], 'all_orders')
        self.assertEqual(result['classification'], 'UNRESOLVED')

    def test_intended_exclusion_matches(self):
        result = self.run_scope('exclude_partial_returns', 'exclude_partial_returns')
        self.assertEqual(result['comparison_status'], 'MATCH')
        self.assertEqual(result['impact_by_currency']['USD']['report_total'], '55.0000')
        self.assertFalse(result['local_filter_mismatch_verified'])

    def test_all_orders_match(self):
        result = self.run_scope('all_orders', 'all_orders')
        self.assertEqual(result['impact_by_currency']['USD']['report_total'], '154.0000')
        self.assertEqual(result['affected_records'], [])

    def test_missing_scope_not_comparable(self):
        result = self.run_scope(None, 'exclude_partial_returns')
        self.assertEqual(result['comparison_status'], 'NOT_COMPARABLE')
        self.assertNotIn('impact_by_currency', result)

    def test_extra_records_and_invalid_scope(self):
        result = self.run_scope('exclude_partial_returns', 'all_orders')
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'], '99.0000')
        self.assertEqual(result['affected_records'][0]['status'], 'EXTRA_IN_REPORT')
        for requested, actual in [('unknown','all_orders'), ('all_orders', 'SELECT 1')]:
            with self.assertRaises(ValueError):
                self.run_scope(requested, actual)
