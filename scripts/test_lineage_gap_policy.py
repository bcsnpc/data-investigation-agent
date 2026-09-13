import unittest
import tempfile
import sqlite3
import json
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from lineage_graph import Graph
from lineage_gap_policy import eligibility,classify
from cross_layer_investigation import boundaries
from investigation_checks import run_checks
from test_investigation_checks import evidence


class GapPolicyTests(unittest.TestCase):
    def graph(self):
        g=Graph([dict(id=x,parent=None,name=x,kind=k,hash='h',meta={}) for x,k in
                 [('a','SqlObject'),('b','Table'),('c','Table'),('other','Table'),('notebook','Notebook')]])
        g.edge('a','b','data','a',{});g.edge('b','c','data','b',{})
        return g

    def test_supported_path_keeps_comparable_difference(self):
        g=self.graph()
        result=boundaries(g,[evidence('10','a',status='AVAILABLE'),evidence('9','b',status='AVAILABLE')])
        self.assertIsNotNone(result['first_verified_divergence'])
        self.assertTrue(eligibility(g,'b')['lineage_conclusions_allowed'])
        self.assertFalse(eligibility(g,'b')['automatic_defect_routing_allowed'])

    def test_unrelated_scoped_gap_does_not_block(self):
        g=self.graph();g.gap('other','Unresolved input',{})
        gate=eligibility(g,'c')
        self.assertTrue(gate['lineage_conclusions_allowed'])
        self.assertEqual(gate['unrelated_gap_count'],1)

    def test_relevant_producer_gap_blocks_even_off_data_traversal(self):
        g=self.graph();g.edge('notebook','b','produces','notebook',{})
        g.gap('notebook','Unsupported dataframe operation: custom',{})
        self.assertEqual(eligibility(g,'c')['status'],'INSUFFICIENT_EVIDENCE')

    def test_unknown_branch_not_waived_by_other_proven_outputs(self):
        g=self.graph();g.edge('notebook','other','produces','notebook',{})
        g.gap('notebook','Conditional dataflow requires runtime evidence',{})
        gap=classify(g,g.gaps[0])
        self.assertEqual(gap['scope'],'UNSCOPED')
        self.assertEqual(gap['category'],'CONDITIONAL_DATAFLOW')
        self.assertFalse(eligibility(g,'c')['lineage_conclusions_allowed'])

    def test_unscoped_write_blocks_but_keeps_numerical_diagnostic(self):
        g=self.graph();g.gap('notebook','Unresolved loop containing write',{})
        chain=[evidence(v,a,status='AVAILABLE') for a,v in [('a','10'),('b','10'),('c','9')]]
        result=boundaries(g,chain)
        self.assertIsNone(result['first_verified_divergence'])
        self.assertEqual(result['boundaries'][1]['status'],'INSUFFICIENT_EVIDENCE')
        self.assertEqual(result['boundaries'][1]['comparison_status'],'MISMATCH')
        self.assertEqual(result['classification'],'UNRESOLVED')

    def test_generic_checks_persist_blocked_status(self):
        g=self.graph();g.gap('b','Unresolved dependency',{})
        request={'lineage_run':'graph','as_of':'2026-09-13T13:00:00Z',
                 'checks':[{'kind':'total','upstream':evidence('10','a'),'downstream':evidence('9','b')}]}
        with tempfile.TemporaryDirectory() as folder,patch('investigation_checks.load_graph',return_value=g):
            database=Path(folder)/'evidence.sqlite'
            result=run_checks(database,request)
            self.assertEqual(result['checks'][0]['result']['status'],'INSUFFICIENT_EVIDENCE')
            with closing(sqlite3.connect(database)) as db:
                saved=json.loads(db.execute('SELECT result FROM investigation_runs').fetchone()[0])
            self.assertFalse(saved['checks'][0]['result']['lineage_eligibility']['lineage_conclusions_allowed'])


if __name__=='__main__':unittest.main()
