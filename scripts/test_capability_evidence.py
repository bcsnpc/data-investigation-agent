from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock

from investigator.capabilities import evaluate, assess
from investigator.diagnostic_evidence import receipts, read
from investigator.native_diagnostics import run
from investigator.admin_api import create_app
from test_native_diagnostics import fixture, database, response


class CapabilityEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.model,self.plan=fixture()
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=MagicMock()
        self.store.get.side_effect=self.get
        self.store.connect.side_effect=lambda:database(Path(self.temp.name)/'catalog.sqlite')

    def get(self,identity):
        if identity != self.model['id']:raise KeyError(identity)
        return self.model

    def receipt(self,execute=None):
        return run(self.store,self.plan,execute or (lambda req:response([{'[m0]':5}])))['id']

    def test_clean_graph_not_proof_and_unknown_operation_does_not_block_parent(self):
        cap=evaluate(self.model)['measures']['Unseen ratio']['capabilities']
        self.assertEqual(cap['DEPENDENCY_DISCOVERY']['state'],'SUPPORTED')
        self.assertEqual(cap['DEPENDENCY_CONTEXT']['state'],'PARTIAL')
        self.assertEqual(cap['NATIVE_EXECUTION']['state'],'UNKNOWN')
        self.assertEqual(cap['ROOT_CAUSE_VERIFICATION']['state'],'UNSUPPORTED')
        node=self.model['context']['semantic_graph']['measures']['Unseen ratio']
        node.update(dependency_state='PARTIAL',gaps=['Unknown operation'])
        self.assertTrue(assess(self.model,self.plan)['admitted'])
        self.assertFalse(assess(self.model,self.plan)['verification_eligible'])

    def test_definition_change_changes_decision_hash(self):
        first=evaluate(self.model)
        self.model['context']['measures'][0]['definition']='new expression'
        second=evaluate(self.model)
        self.assertNotEqual(first['context_hash'],second['context_hash'])
        self.assertNotEqual(first['decision_hash'],second['decision_hash'])

    def test_invalid_plan_disabled_and_different_model_rejected(self):
        with self.assertRaises(ValueError):assess(self.model,dict(self.plan,model_id='different'))
        with self.assertRaises(ValueError):assess(self.model,dict(self.plan,query='DAX'))
        self.model['enabled']=False
        with self.assertRaises(ValueError):assess(self.model,self.plan)

    def test_decision_saved_before_dispatch_and_receipt_scoped(self):
        def execute(req):
            with self.store.connect() as db:
                self.assertEqual(db.execute('SELECT count(*) FROM native_capability_decisions').fetchone()[0],1)
            return response([{'[m0]':5}])
        identity=self.receipt(execute)
        evidence=read(self.store,'model',identity)
        self.assertEqual(evidence['assessment']['native_observation']['state'],'SUPPORTED')
        self.assertFalse(evidence['assessment']['verification_eligible'])
        self.assertFalse(evidence['assessment']['future_execution_guaranteed'])
        self.assertTrue(evidence['admission']['admitted'])
        self.assertEqual(receipts(self.store,'model')[0]['id'],identity)
        with self.assertRaises(KeyError):read(self.store,'other',identity)

    def test_disable_keeps_history_but_invalidates_current_evidence(self):
        identity=self.receipt();self.model['enabled']=False
        evidence=read(self.store,'model',identity)
        self.assertEqual(evidence['result']['rows'][0]['[m0]']['value'],'5')
        self.assertFalse(evidence['assessment']['current_context'])
        self.assertEqual(evidence['assessment']['native_observation']['state'],'UNKNOWN')

    def test_timeout_not_unsupported(self):
        identity=self.receipt(MagicMock(side_effect=TimeoutError()))
        evidence=read(self.store,'model',identity)
        self.assertEqual(evidence['assessment']['native_observation']['state'],'TEMPORARILY_UNAVAILABLE')
        self.assertFalse(evidence['assessment']['root_cause_verified'])

    def test_partial_response_stays_partial(self):
        self.plan['dimension_id']='c'
        identity=self.receipt(lambda req:response([{'[m0]':i,'[dimension]':str(i)} for i in range(501)]))
        self.assertEqual(read(self.store,'model',identity)['assessment']['native_observation']['state'],'PARTIAL')

    def test_legacy_receipts_remain_readable_and_missing_is_not_found(self):
        self.assertEqual(receipts(self.store,'model'),[])
        with self.assertRaises(KeyError):read(self.store,'model','absent')
        identity=self.receipt()
        with self.store.connect() as db:db.execute('DROP TABLE native_capability_decisions')
        self.assertIsNone(read(self.store,'model',identity)['admission'])

    def test_tampered_decision_rejected(self):
        identity=self.receipt()
        with self.store.connect() as db:db.execute("UPDATE native_capability_decisions SET decision_hash='bad'")
        with self.assertRaises(ValueError):read(self.store,'model',identity)

    def test_api_auth_assessment_and_evidence_without_execution(self):
        app=create_app(self.store,'a'*32,'r'*32)
        def call(suffix,token='a'*32,body=None):
            raw=json.dumps(body).encode() if body is not None else b'';status=[]
            out=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/'+suffix,
                'REQUEST_METHOD':'POST' if body is not None else 'GET','HTTP_AUTHORIZATION':'Bearer '+token,
                'CONTENT_LENGTH':str(len(raw)),'CONTENT_TYPE':'application/json','wsgi.input':BytesIO(raw)},
                lambda code,headers:status.append(code)))
            return status[0],json.loads(out)
        self.assertEqual(call('capabilities',token='')[0],'401 Unauthorized')
        self.assertEqual(call('capabilities',token='r'*32)[0],'403 Forbidden')
        self.assertEqual(call('capabilities')[0],'200 OK')
        self.assertTrue(call('assess',body=self.plan)[1]['admitted'])
        self.assertEqual(receipts(self.store,'model'),[])
        identity=self.receipt()
        self.assertEqual(call('diagnostics/'+identity)[0],'200 OK')
        self.assertEqual(call('diagnostics/absent')[0],'404 Not Found')


if __name__=='__main__':unittest.main()
