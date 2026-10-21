import copy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from cloud_value_execution import COVERAGE,_compile,_file,_native,run,replay
from test_cloud_dax_authorization import FakeMeter,REQUEST,READER,AUTH,WORKSPACE,MODEL,TENANT


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.records=[]
        self.context=SimpleNamespace(root=self.root,record=lambda kind,value:self.records.append((kind,value)))
        self.model={'id':'model','context_id':'context','workspace':WORKSPACE,'native_id':MODEL}
        self.config={'fabric':{'workspace_id':WORKSPACE,'native_reader':READER,'auth':AUTH}}
        self.compiled={'native_statement':'EVALUATE ROW("quantity",SUM(\'Activity\'[units]))',
            'layers':[{'layer_id':'GOLD','statement':'SELECT SUM([x]) quantity FROM [dbo].[data]'}],
            'tolerance':{'kind':'ABSOLUTE','value':'0','source':'exact integral'},'qualifications':['SNAPSHOT_UNVERIFIED']}
        self.plan={'manifest':'estate','options':{'model':{'path':'model','sha256':'a'*64},'mappings':{'path':'maps','sha256':'b'*64},
            'measure_id':'measure','target_id':'target','tolerance':self.compiled['tolerance'],'budget':{'environment':'test'},'max_requests':12}}
        for name,value in [('investigator.estate_manifest.load',{}),('investigator.adapters.estate_installation.configuration',self.config),
                           ('investigator.shared_state.configured_state',object())]:
            p=patch(name,return_value=value);p.start();self.addCleanup(p.stop)
        p=patch('scan_estate_graph.Meter',FakeMeter);p.start();self.addCleanup(p.stop)

    def test_typed_registry_contains_value_route(self):
        from investigator.unified_runner import KINDS,handlers
        self.assertIn('value-verification',KINDS);self.assertIn('value-verification',handlers())

    def test_hashed_reference_refuses_changed_body(self):
        path=self.root/'input.json';path.write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError,'VALUE_INPUT_HASH_DIFFERS'):_file({'path':str(path),'sha256':'0'*64})
        self.assertEqual(_file({'path':str(path),'sha256':hashlib.sha256(b'{}').hexdigest()}),{})

    def test_compiler_adds_identity_without_info_metadata(self):
        with patch('cloud_value_execution.build',return_value=copy.deepcopy(self.compiled)):
            result=_compile({},[],self.plan['options'])
        self.assertIn('USERPRINCIPALNAME()',result['native_statement']);self.assertNotIn('INFO.',result['native_statement'])

    def test_native_http_401_preserves_error_no_false_attestation(self):
        error=HTTPError('https://fixed',401,'Unauthorized',{},io.BytesIO(b'{"error":{"code":"PowerBINotAuthorizedException"}}'))
        with patch('metadata_config.worker_configuration',return_value=self.config),patch('run_native_diagnostic.execute',side_effect=error):
            result=_native(self.config,self.model,self.compiled['native_statement'])
        self.assertEqual(result['error']['http_status'],401);self.assertEqual(result['status'],'FAILED')
        self.assertNotIn('attestation',result)

    def test_native_principal_report_is_partial_not_full_attestation(self):
        body=json.dumps({'results':[{'tables':[{'rows':[{'[quantity]':16,'[surface_identity]':READER['account']}]}]}]})
        with patch('metadata_config.worker_configuration',return_value=self.config),patch('run_native_diagnostic.execute',return_value=body):
            result=_native(self.config,self.model,self.compiled['native_statement'])
        self.assertEqual(result['attestation_result']['status'],'PARTIAL')
        self.assertEqual(result['attestation_result']['attested_fields'],['identity'])
        self.assertFalse(result['confidence_awarded'])

    def test_native_failure_seals_and_replays_no_lower_reads(self):
        failure={'status':'FAILED','error':{'http_status':401,'service_error_code':'Denied'}}
        with patch('cloud_value_execution._file',side_effect=lambda ref:self.model if ref['path']=='model' else []),patch('cloud_value_execution._compile',return_value=self.compiled),patch('cloud_value_execution._native',return_value=failure),patch('cloud_value_execution._lower') as lower:
            result=run(self.plan,self.context)
            self.assertEqual(result['reason'],'NATIVE_VISUAL_READ_FAILED');self.assertEqual(result['physical_requests'],1)
            lower.assert_not_called()
            with patch('cloud_value_execution._native',side_effect=AssertionError('no live replay')):
                actual=replay(result['tape'])
        self.assertTrue(actual['matched']);self.assertEqual(actual['coverage'],COVERAGE)
        self.assertEqual(actual['network_requests'],0)
        self.assertEqual(actual['result']['reads'][0]['receipt'],failure)

    def test_matching_values_still_never_self_award_graph_confidence(self):
        with patch('cloud_value_execution._file',side_effect=lambda ref:self.model if ref['path']=='model' else []),patch('cloud_value_execution._compile',return_value=self.compiled),patch('cloud_value_execution._native',return_value={'status':'SUCCEEDED','value':16}),patch('cloud_value_execution._lower',return_value={'status':'SUCCEEDED','value':16}):
            result=run(self.plan,self.context)
        self.assertEqual(result['status'],'VALUES_AGREE_UNDER_MAPPING')
        self.assertFalse(result['confidence_awarded']);self.assertIn('TRUSTED_GRAPH_RESOLVER',result['grade'])

    def test_gateway_refusal_remains_hard_not_auth_or_value_result(self):
        from investigator.live_gateway import GatewayDenied
        with patch('cloud_value_execution._file',side_effect=lambda ref:self.model if ref['path']=='model' else []),patch('cloud_value_execution._compile',return_value=self.compiled),patch('cloud_value_execution._native',side_effect=GatewayDenied('bounded guard refusal')):
            with self.assertRaises(GatewayDenied):run(self.plan,self.context)

    def test_budget_category_exhaustion_is_not_a_failed_native_finding(self):
        from investigator.usage_governance import UsageHold
        with patch('cloud_value_execution._file',side_effect=lambda ref:self.model if ref['path']=='model' else []),patch('cloud_value_execution._compile',return_value=self.compiled),patch('cloud_value_execution._native',side_effect=UsageHold('Monthly category exhausted')):
            with self.assertRaisesRegex(UsageHold,'Monthly category exhausted'):run(self.plan,self.context)

    def test_native_budget_exception_not_wrapped_as_http_failure(self):
        from investigator.usage_governance import UsageHold
        with patch('metadata_config.worker_configuration',return_value=self.config),patch('run_native_diagnostic.execute',side_effect=UsageHold('Monthly limit')):
            with self.assertRaisesRegex(UsageHold,'Monthly limit'):_native(self.config,self.model,self.compiled['native_statement'])


if __name__=='__main__':unittest.main()
