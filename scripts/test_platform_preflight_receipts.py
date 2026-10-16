import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from investigator.adapters.platform_preflight_receipts import load,health_probes,authentication_facts
from test_vault_user_cache import D


class ReceiptTests(unittest.TestCase):
    def test_hash_changed_kind_and_unbounded_or_estate_receipt_refuse(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipt.json'
            value={'version':1,'kind':'PLATFORM_HEALTH','estate_reads':0,'model_calls':0}
            path.write_text(json.dumps(value),encoding='utf8')
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(load(path,digest,'PLATFORM_HEALTH')[0],value)
            for wrong_hash,kind in [('0'*64,'PLATFORM_HEALTH'),(digest,'PLATFORM_AUTH_PREFLIGHT')]:
                with self.assertRaises(ValueError):load(path,wrong_hash,kind)
            value['estate_reads']=1;path.write_text(json.dumps(value),encoding='utf8')
            with self.assertRaises(ValueError):load(path,hashlib.sha256(path.read_bytes()).hexdigest(),'PLATFORM_HEALTH')

    def test_platform_facts_establish_only_storage_and_worker_authentication(self):
        receipt={'principal_id':'worker','checks':{'blob':{'status':'PASS','immutable':True,'sha256':'a'*64},
            'postgres':{'status':'PASS'},'key_vault':{'status':'PASS','secret_read_verified':False}}}
        probes=health_probes({'worker_identity':{'principal_id':'worker'}},receipt,'sha256:receipt')
        self.assertEqual(set(probes),{'blob.access','worker_identity.authentication'})
        self.assertTrue(all(p().established for p in probes.values()))
        with self.assertRaisesRegex(ValueError,'PRINCIPAL'):
            health_probes({'worker_identity':{'principal_id':'operator'}},receipt,'sha256:receipt')

    def test_reader_auth_cannot_become_semantic_model_or_sql_permission(self):
        manifest={'adapters':[{'id':'microsoft','options':{'fabric':{'auth':D}}}]}
        receipt={'checks':[{'kind':'EXISTING_READER_AUTHENTICATION','status':'PASS',
            **{k:D[k] for k in ('scope','tenant_id','principal_id')},'audience':D['scope'].removesuffix('/.default')}]}
        facts=authentication_facts(manifest,receipt,'sha256:receipt')
        self.assertEqual(facts[0]['status'],'PASS')
        self.assertIn('no model, database',facts[0]['detail'])
        receipt['checks'][0]['principal_id']='other'
        self.assertEqual(authentication_facts(manifest,receipt,'sha256:receipt')[0]['status'],'MISSING')

    def test_cli_import_is_offline_and_readiness_stays_unearned_for_both_estates(self):
        from preflight_installation import main
        from unittest.mock import patch
        root=Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder)
            health={'version':1,'kind':'PLATFORM_HEALTH','estate_reads':0,'model_calls':0,
                'principal_id':'worker','checks':{'blob':{'status':'PASS','immutable':True,'sha256':'a'*64}}}
            receipt=folder/'health.json';receipt.write_text(json.dumps(health))
            platform=folder/'platform.json';platform.write_text(json.dumps({'worker_identity':{'principal_id':'worker'}}))
            for estate in ('fixture','billing'):
                manifest=root/'estates'/f'{estate}.json'
                output=folder/(estate+'.json')
                with patch('builtins.print'),patch('subprocess.run',side_effect=AssertionError('No live call')):
                    self.assertEqual(main(['--manifest',str(manifest),'--platform',str(platform),'--output',str(output),
                        '--platform-health-receipt',str(receipt),hashlib.sha256(receipt.read_bytes()).hexdigest()]),2)
                report=json.loads(output.read_text());checks={r['id']:r for r in report['checks']}
                self.assertEqual(checks['blob.access']['status'],'PASS')
                self.assertEqual(checks['semantic.execute_queries']['status'],'MISSING')
                self.assertEqual(report['control_operations'],0)


if __name__=='__main__':unittest.main()
