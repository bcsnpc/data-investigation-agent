import copy
import json
from pathlib import Path
import tempfile
import unittest
from investigator.cloud_preflight import result,Observation


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.manifest=json.loads((Path(__file__).parents[1]/'infra/estates/fixture.json').read_text())
        self.platform={'worker_identity':{'mode':'managed_identity','client_id':'configured-client','principal_id':'configured-object','tenant_id':'configured-tenant'},
                       'postgres':{'host':'pg.example.test','database':'tool','user':'worker'},'gateway_policy':{'version':1,'live_enabled':True,'identities':{}}}

    def report(self,**kwargs):
        return result(self.manifest,platform=self.platform,gateway_validator=lambda p:p,**kwargs)

    def test_valid_manifest_never_proves_permissions(self):
        report=self.report()
        self.assertEqual(report['status'],'NOT_READY')
        self.assertEqual(report['estate_reads'],0)
        checks={c['id']:c for c in report['checks']}
        self.assertEqual(checks['manifest']['status'],'PASS')
        self.assertEqual(checks['semantic.execute_queries']['status'],'MISSING')
        self.assertEqual(checks['worker_identity.authentication']['status'],'MISSING')
        self.assertTrue(all(c['fix']for c in report['checks']))

    def test_wrong_identity_cannot_establish_capability(self):
        report=self.report(probes={'semantic.execute_queries':lambda:Observation('operator','receipt',True,'HTTP200')})
        self.assertEqual(next(c for c in report['checks']if c['id']=='semantic.execute_queries')['status'],'FAIL')

    def test_receipt_required_and_refusal_kept(self):
        report=self.report(probes={'semantic.execute_queries':lambda:Observation('configured-object','receipt403',False,'HTTP403 retained in receipt403')})
        check=next(c for c in report['checks']if c['id']=='semantic.execute_queries')
        self.assertEqual(check['status'],'FAIL');self.assertEqual(check['evidence']['id'],'receipt403')
        report=self.report(probes={'semantic.execute_queries':lambda:Observation('configured-object','',True,'invented')})
        self.assertEqual(next(c for c in report['checks']if c['id']=='semantic.execute_queries')['status'],'FAIL')

    def test_observed_check_passes_only_that_check(self):
        report=self.report(probes={'semantic.execute_queries':lambda:Observation('configured-object','receipt200',True,'Attested query returned')})
        self.assertEqual(next(c for c in report['checks']if c['id']=='semantic.execute_queries')['status'],'PASS')
        self.assertEqual(report['status'],'NOT_READY')

    def test_projected_cloud_storage_never_falls_back_to_exact(self):
        self.manifest['recording']={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1','estate_id':'synthetic','key_reference':'secret/synthetic','columns':['column://synthetic/value']}
        report=self.report()
        self.assertEqual(next(c for c in report['checks']if c['id']=='recording.configuration')['status'],'FAIL')

    def test_delegated_semantic_reader_is_distinct_from_vault_fetching_worker(self):
        fabric=self.manifest['adapters'][0]['options']['fabric']
        native=fabric['native_reader']
        fabric['auth']={'mode':'key_vault_user_cache','tenant_id':native['tenant_id'],
                        'account':native['account'],'principal_id':native['principal_id']}
        def report(identity):
            return self.report(manifest_validator=lambda _:None,probes={'semantic.execute_queries':
                lambda:Observation(identity,'reader-receipt',True,'Synthetic reader response')})
        row=lambda r:next(c for c in r['checks']if c['id']=='semantic.execute_queries')
        self.assertEqual(row(report(native['principal_id']))['status'],'PASS')
        self.assertEqual(row(report(self.platform['worker_identity']['principal_id']))['status'],'FAIL')
        self.assertEqual(row(self.report(manifest_validator=lambda _:None))['status'],'MISSING')
        fabric['auth']['principal_id']='wrong-principal'
        self.assertEqual(row(report(native['principal_id']))['status'],'FAIL')
        from unittest.mock import Mock
        forbidden_probe=Mock(side_effect=AssertionError('Unbound identity must not run'))
        refused=self.report(manifest_validator=lambda _:None,
                            probes={'semantic.execute_queries':forbidden_probe})
        self.assertEqual(row(refused)['status'],'FAIL')
        forbidden_probe.assert_not_called()

    def test_exception_summary_does_not_leak_secret(self):
        def fail():raise RuntimeError('password=PRIVATE_VALUE')
        report=self.report(probes={'network.access':fail})
        self.assertNotIn('PRIVATE_VALUE',json.dumps(report))

    def test_federated_reader_permission_is_not_worker_permission(self):
        fabric=self.manifest['adapters'][0]['options']['fabric'];native=fabric['native_reader']
        native['mode']='federated_reader'
        fabric['auth']={'mode':'federated_reader','tenant_id':native['tenant_id'],'principal_id':native['principal_id']}
        def check(principal):
            report=self.report(manifest_validator=lambda _:None,probes={'semantic.execute_queries':lambda:Observation(principal,'receipt',True,'Bound principal')})
            return next(row for row in report['checks'] if row['id']=='semantic.execute_queries')['status']
        self.assertEqual(check(native['principal_id']),'PASS')
        self.assertEqual(check(self.platform['worker_identity']['principal_id']),'FAIL')
        fabric['auth']['tenant_id']='other'
        self.assertEqual(check(native['principal_id']),'FAIL')

    def test_cli_is_offline_and_preserves_previous_output(self):
        from preflight_installation import main
        from unittest.mock import patch
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);platform=root/'platform.json';platform.write_text(json.dumps({}))
            args=['--manifest',str(Path(__file__).parents[1]/'infra/estates/fixture.json'),'--platform',str(platform),'--output',str(root/'result.json')]
            with patch('builtins.print'):self.assertEqual(main(args),2)
            with patch('builtins.print'),self.assertRaises(SystemExit):main(args)


if __name__=='__main__':unittest.main()
