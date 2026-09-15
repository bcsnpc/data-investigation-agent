from copy import deepcopy
import json
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from investigator.comparisons import assess, register, read, mapping
from investigator.admin_api import create_app
from test_native_diagnostics import fixture, database


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.model,_=fixture();self.store=MagicMock()
        def get(identity):
            if identity!='model':raise KeyError(identity)
            return self.model
        self.store.get.side_effect=get
        self.store.connect.side_effect=lambda:database(Path(self.temp.name)/'catalog.sqlite')
        self.native={'status':'COMPLETED','assessment':{'current_context':True},
          'request':{'context_id':'ctx','dimension_id':None,'measure_ids':['Unseen ratio'],
            'plan':{'filters':[{'column_id':'c','values':['USD']}]}},
          'result':{'completeness':'COMPLETE_RESPONSE','rows':[{'[m0]':{'type':'decimal','value':'5'}}]}}
        self.source={'status':'COMPLETED','local_context_current':True,
          'request':{'context_id':'ctx','plan':{'object_id':'obj','operation':'count_rows','column_id':None,
            'filters':[{'column_id':'sql_currency','values':['USD']}]}},
          'result':{'value':{'type':'decimal','value':'5'}}}
        self.npatch=patch('investigator.comparisons.native_read',side_effect=lambda *args:deepcopy(self.native))
        self.spatch=patch('investigator.comparisons.source_read',side_effect=lambda *args:deepcopy(self.source))
        self.npatch.start();self.spatch.start();self.addCleanup(self.npatch.stop);self.addCleanup(self.spatch.stop)
        self.request={'native_receipt_id':'n','source_receipt_id':'s','measure_id':'Unseen ratio','mapping_id':None}
        self.contract={'revision':3,'context_id':'ctx','measure_id':'Unseen ratio','source_object_id':'obj',
          'source_operation':'count_rows','source_column_id':None,'grain':'test entity','unit':'count',
          'date_basis':'test date role','blank_policy':'preserve',
          'filter_bindings':[{'native_column_id':'c','source_column_id':'sql_currency'}],'confirmed':True}

    def reviewed(self):
        self.request['mapping_id']=register(self.store,'model',self.contract,'test-reviewer')['id']

    def test_equal_values_without_mapping_are_not_healthy(self):
        result=assess(self.store,'model',self.request)
        self.assertIn('REVIEWED_MAPPING_REQUIRED',result['gaps'])
        self.assertIsNone(result['diagnostic_difference_native_minus_source'])
        self.assertEqual(result['outcome'],'INSUFFICIENT_EVIDENCE')

    def test_reviewed_equal_values_still_need_version_and_semantic_proof(self):
        self.reviewed();result=assess(self.store,'model',self.request)
        self.assertEqual(result['diagnostic_difference_native_minus_source'],'0')
        self.assertFalse(result['comparable']);self.assertFalse(result['delivery_eligible'])
        self.assertIn('SHARED_DATA_GENERATION_UNVERIFIED',result['gaps'])
        self.assertIn('UPSTREAM_SEMANTIC_EQUIVALENCE_UNVERIFIED',result['gaps'])

    def test_decimal_difference_not_rounded_to_float(self):
        self.reviewed();self.native['result']['rows'][0]['[m0]']['value']='123456789012345678901.0001'
        self.source['result']['value']['value']='123456789012345678901.0000'
        result=assess(self.store,'model',self.request)
        self.assertEqual(result['diagnostic_difference_native_minus_source'],'0.0001')
        self.assertFalse(result['root_cause_verified'])

    def test_blank_and_dimension_do_not_get_scalar_difference(self):
        self.reviewed();self.source['result']['value']={'type':'blank','value':None}
        result=assess(self.store,'model',self.request)
        self.assertIsNone(result['diagnostic_difference_native_minus_source'])
        self.assertIn('BLANK_OBSERVATION_NOT_NUMERIC',result['gaps'])
        self.native['request']['dimension_id']='c'
        self.assertIn('NATIVE_SCALAR_COMPLETE_RESPONSE_REQUIRED',assess(self.store,'model',self.request)['gaps'])

    def test_extra_scope_or_mismatched_scope_cannot_be_ignored(self):
        self.reviewed();self.source['request']['plan']['filters'][0]['values']=['EUR']
        self.assertIn('FILTER_SCOPES_NOT_ALIGNED',assess(self.store,'model',self.request)['gaps'])
        self.source['request']['plan']['filters'][0]['values']=['USD']
        self.native['request']['plan']['filters'].append({'column_id':'date','operator':'range','values':['2026-01-01','2027-01-01']})
        self.assertIsNone(assess(self.store,'model',self.request)['diagnostic_difference_native_minus_source'])

    def test_stale_review_and_wrong_binding_hold(self):
        self.reviewed();self.source['request']['plan']['object_id']='different'
        self.model['revision']=4
        result=assess(self.store,'model',self.request)
        self.assertIn('MAPPING_REVIEW_STALE',result['gaps']);self.assertIn('MAPPING_DOES_NOT_BIND_RECEIPTS',result['gaps'])

    def test_cannot_supply_proof_flags_or_unconfirmed_mapping(self):
        with self.assertRaises(ValueError):assess(self.store,'model',dict(self.request,comparable=True))
        with self.assertRaises(ValueError):register(self.store,'model',dict(self.contract,confirmed=False),'reviewer')

    def test_history_integrity_and_cross_model_access(self):
        self.reviewed();result=assess(self.store,'model',self.request)
        self.assertTrue(read(self.store,'model',result['id'])['input_evidence_unchanged'])
        self.source['result']['value']['value']='6'
        self.assertFalse(read(self.store,'model',result['id'])['input_evidence_unchanged'])
        self.model['enabled']=False
        self.assertFalse(read(self.store,'model',result['id'])['local_context_current'])
        with self.assertRaises(KeyError):read(self.store,'other',result['id'])
        with self.store.connect() as db:db.execute("UPDATE comparison_assessments SET hash='bad'")
        with self.assertRaises(ValueError):read(self.store,'model',result['id'])

    def test_failed_source_does_not_supply_value(self):
        self.source.update(status='FAILED',result={'error_type':'TimeoutError'})
        result=assess(self.store,'model',self.request)
        self.assertIsNone(result['observations']['source'])
        self.assertIn('SOURCE_READ_UNAVAILABLE',result['gaps'])

    def test_api_admin_only_and_no_cloud_dispatch(self):
        app=create_app(self.store,'a'*32,'r'*32);raw=json.dumps(self.request).encode()
        for token,expected in [('a'*32,'200 OK'),('r'*32,'403 Forbidden')]:
            status=[]
            result=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/comparisons','REQUEST_METHOD':'POST',
              'HTTP_AUTHORIZATION':'Bearer '+token,'CONTENT_LENGTH':str(len(raw)),'CONTENT_TYPE':'application/json',
              'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
            self.assertEqual(status[0],expected)
            if token.startswith('a'):self.assertEqual(json.loads(result)['outcome'],'INSUFFICIENT_EVIDENCE')


if __name__=='__main__':unittest.main()
