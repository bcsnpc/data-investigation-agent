import copy
import unittest
from cloud_binding_verifier import plan

class VerificationPlanTests(unittest.TestCase):
    def spec(self):
        return {'proposals':[{'target':{'table':table,'column':str(i)},'sources':[{'table':'source'}]} for table in ('one','two','three') for i in range(6)],
            'schemas':{'source':{},'one':{},'two':{},'three':{}},'samples':{'one':{},'two':{},'three':{}},
            'target_databases':{'one':'db1','two':'db2','three':'db2'},
            'budgets':{'binding_verification':{'metadata_probes':4,'session_cap':40,'probes_per_binding':2}}}
    def test_all18pairs_plus_two_catalog_reads_leave_two_for_native_route(self):
        p=plan(self.spec());self.assertEqual(p['verification_reads_needed'],38)
        self.assertEqual(p['verification_cap'],40);self.assertTrue(p['admissible'])
    def test_missing_schema_or_sample_is_not_silently_omitted(self):
        for field in ('schemas','samples'):
            s=self.spec();s[field].pop('one')
            with self.assertRaises(ValueError):plan(s)
    def test_insufficient_cap_is_not_raised(self):
        s=self.spec();s['budgets']['binding_verification']['session_cap']=12
        p=plan(s);self.assertFalse(p['admissible']);self.assertEqual(p['verification_cap'],12)
    def test_duplicate_binding_rejected(self):
        s=self.spec();s['proposals'].append(copy.deepcopy(s['proposals'][0]))
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):plan(s)
