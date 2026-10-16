import copy
import unittest
from cloud_binding_verifier import plan

class VerificationPlanTests(unittest.TestCase):
    def test_preflight_compares_whole_policy_before_resolving_objects(self):
        from cloud_binding_verifier import preflight
        from unittest.mock import patch
        spec=self.spec();spec['budgets'].update(round={'id':'OLD','physical_requests':1500,'restoration_reserved':95},rolling=3000)
        for field,value in [('round',{'id':'NEW','physical_requests':1500,'restoration_reserved':95}),('rolling',3001),('extra',1)]:
            expected=copy.deepcopy(spec['budgets']);expected[field]=value
            with self.subTest(field=field),patch('investigator.adapters.code_verification.resolve_objects')as resolve:
                with self.assertRaisesRegex(ValueError,'VERIFICATION_BUDGET_DIFFERS'):
                    preflight(spec,{}, {},receipt_path='unused',manifest_budgets=expected)
                resolve.assert_not_called()

    def spec(self):
        return {'proposals':[{'target':{'table':table,'column':str(i)},'sources':[{'table':'source'}]} for table in ('one','two','three') for i in range(6)],
            'schemas':{'source':{},'one':{},'two':{},'three':{}},'samples':{'one':{},'two':{},'three':{}},
            'target_databases':{'one':'db1','two':'db2','three':'db2'},
            'budgets':{'binding_verification':{'metadata_probes':4,'session_cap':40,'probes_per_binding':2}}}
    def test_all18pairs_plus_two_catalog_reads_leave_two_for_native_route(self):
        p=plan(self.spec());self.assertEqual(p['verification_reads_needed'],40)
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

class VerifierCatalogOwnershipTests(unittest.TestCase):
    def test_live_and_replay_use_the_explicit_accounting_catalog(self):
        import json,tempfile
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch
        from investigator import process_tape
        from investigator.onboarding import digest
        from cloud_binding_verifier import perform
        with tempfile.TemporaryDirectory() as folder:
            work=Path(folder);context={'version':'retained'};model={'context_id':'model-pin'}
            (work/'context.json').write_text(json.dumps(context));(work/'model.json').write_text(json.dumps(model))
            explicit=work/'authoritative-private-mirror.sqlite';explicit.write_bytes(b'existing')
            boot={'config':{},'state':{'environment':'estate','inputs':{'engine_fingerprint':'engine','verification_spec':VerificationPlanTests().spec(),'context_hash':digest(context),'model_context_id':'model-pin'}}}
            for path in (explicit,None):
                with process_tape.active(SimpleNamespace(replaying=False)),patch('investigator.runtime.fingerprint',return_value='engine'),patch('investigator.onboarding.ModelStore',side_effect=RuntimeError('STOP_AT_STORE')) as store:
                    with self.assertRaisesRegex(RuntimeError,'STOP_AT_STORE'):perform(boot,work,path)
                    self.assertEqual(store.call_args.args[0],explicit if path else work/'catalog.sqlite')
            self.assertFalse((work/'model-catalog.sqlite').exists())
