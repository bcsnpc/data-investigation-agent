from contextlib import closing
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import duckdb
from multilayer_lab import initialize_multilayer,capture,investigate_layers,reset_multilayer,run_case
from investigation_evidence_api import EvidenceStore


class MultiLayerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name)
        self.path=self.folder/'lab.duckdb';initialize_multilayer(self.path)

    def test_matching_layers_do_not_prove_expected_behavior(self):
        result=investigate_layers(capture(self.path),self.folder/'evidence.sqlite')
        self.assertIsNone(result['first_observed_local_boundary']);self.assertEqual(result['classification'],'UNRESOLVED')
        self.assertTrue(all(b['comparison_status']=='MATCH' for b in result['boundaries']))

    def test_upstream_error_propagates_but_gold_agreement_does_not_hide_it(self):
        report=run_case(self.folder/'case');result=report['result']
        self.assertEqual(result['first_observed_local_boundary'],{'upstream':'bronze','downstream':'silver'})
        self.assertEqual(result['boundaries'][0]['impact_by_currency']['USD']['downstream_minus_upstream'],'10.0000')
        self.assertEqual(result['boundaries'][1]['comparison_status'],'MATCH')
        self.assertFalse(result['root_cause_verified']);self.assertFalse(result['automatic_defect_routing'])
        self.assertEqual(report['reset']['status'],'READY')
        item=EvidenceStore(self.folder/'case/evidence.sqlite').get(result['id'])
        self.assertNotIn('expected',item['request']);self.assertNotIn('bronze_fixture_receipt',str(item['request']))

    def test_downstream_omission_has_later_boundary(self):
        with closing(duckdb.connect(str(self.path))) as db:db.execute("DELETE FROM g_order_line_summary WHERE order_id='ORD-000001'")
        result=investigate_layers(capture(self.path),self.folder/'evidence.sqlite')
        self.assertEqual(result['first_observed_local_boundary'],{'upstream':'silver','downstream':'gold'})
        self.assertEqual(result['boundaries'][1]['affected_records'][0]['status'],'MISSING_IN_DOWNSTREAM')
        self.assertEqual(reset_multilayer(self.path)['status'],'READY')

    def test_missing_layer_and_duplicate_keys_rejected(self):
        payload=capture(self.path);bad=deepcopy(payload);del bad['layers']['bronze']
        with self.assertRaises(ValueError):investigate_layers(bad,self.folder/'evidence.sqlite')
        payload['layers']['bronze'].append(payload['layers']['bronze'][0])
        with self.assertRaises(ValueError):investigate_layers(payload,self.folder/'evidence.sqlite')

    def test_changed_bronze_cannot_be_blessed_by_reset(self):
        with closing(duckdb.connect(str(self.path))) as db:db.execute('UPDATE b_fact_order SET captured_amount=0')
        with self.assertRaises(ValueError):reset_multilayer(self.path)


if __name__=='__main__':unittest.main()
