from contextlib import closing
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

from lineage_graph import Graph
from ticket_workflow import TicketStore, Conflict
from ticket_planner import plan_ticket
from review_ticket_plan import approve
from evidence_summary import summarize


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = TicketStore(Path(self.temp.name) / 'workflow.sqlite')
        self.lineage = str(uuid4())
        self.estate = {'investigation': {'lineage_run': self.lineage}}
        self.config = {'storage': {'database': 'unused'}}
        self.graph = Graph([dict(id='r', kind='Report', name='Executive Sales'),
                            dict(id='m', kind='Measure', name='Net Cash')])
        self.graph.edge('m', 'r', 'binding', 'r', 'test')
        self.original, _ = self.store.submit(dict(title='Test', report='Executive Sales',
            description='Net Cash USD for ORD-000002'), str(uuid4()), self.lineage)
        self.record = plan_ticket(self.store, self.original, self.graph,
            lambda _: (dict(report_id='r', metric='Net Cash', currency='USD', order_id='ORD-000002', questions=[]), {}))

    def call(self):
        return approve(self.store, self.record['id'], self.config, self.estate, 'test operator')

    def test_concurrent_approval_creates_one_linked_ticket(self):
        with patch('review_ticket_plan.load_graph', return_value=self.graph), ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda _: self.call(), range(2)))
        self.assertEqual(sum(r['created'] for r in results), 1)
        self.assertEqual(results[0]['ticket_id'], results[1]['ticket_id'])
        child = self.store.get(results[0]['ticket_id'])
        self.assertEqual(child['ticket']['order_id'], 'ORD-000002')
        self.assertEqual(child['timeline'][0]['detail']['original_ticket_id'], self.original)
        self.assertEqual(self.store.get(self.original)['status'], 'QUEUED')

    def test_stale_lineage_rejected(self):
        self.estate['investigation']['lineage_run'] = str(uuid4())
        with self.assertRaises(Conflict): self.call()

    def test_changed_catalog_rejected_without_new_ticket(self):
        self.graph.assets['r']['name'] = 'Changed'
        with patch('review_ticket_plan.load_graph', return_value=self.graph), self.assertRaises(Conflict):
            self.call()
        with closing(self.store.connect()) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0], 1)

    def test_needs_input_cannot_be_approved(self):
        record = dict(self.record, status='NEEDS_INPUT')
        with closing(self.store.connect()) as db:
            db.execute('UPDATE ticket_plans SET record=? WHERE id=?', (json.dumps(record), record['id']))
            db.commit()
        with self.assertRaises(Conflict): self.call()

    def test_failed_event_rolls_back_child_and_approval(self):
        with patch('review_ticket_plan.load_graph', return_value=self.graph), \
                patch.object(self.store, 'event', side_effect=RuntimeError('test failure')), \
                self.assertRaises(RuntimeError):
            self.call()
        with closing(self.store.connect()) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM plan_approvals').fetchone()[0], 0)

    def test_summary_preserves_partial_evidence_and_exact_decimal(self):
        item = dict(id=str(uuid4()), classification='UNRESOLVED',
                    request={'observations': {'net_cash': [
                        dict(layer='sql', status='UNAVAILABLE', data='fake'),
                        dict(layer='gold', status='AVAILABLE', data='64892824.4900')]}},
                    result={'metrics': {'net_cash': {'boundaries': [{'status': 'NOT_COMPARABLE'},
                                                                  {'status': 'INSUFFICIENT_EVIDENCE'}]}}})
        summary = summarize(item)
        self.assertEqual(summary['classification'], 'UNRESOLVED')
        self.assertIsNone(summary['observations'][0]['value'])
        self.assertEqual(summary['observations'][1]['value'], '64892824.4900')
        self.assertIn('NOT_COMPARABLE', summary['text'])
        self.assertIn('INSUFFICIENT_EVIDENCE', summary['text'])
        self.assertFalse(summary['automatic_defect_routing'])


if __name__ == '__main__': unittest.main()
