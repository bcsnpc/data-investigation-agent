import copy
import hashlib
import json
import unittest
from report_drillthrough_context import assess,FIELD

PAGE='definition/pages/details/page.json'

def fixture():
    page={'pageBinding':{'type':'Drillthrough','parameters':[{'name':'p','boundFilter':'order','fieldExpr':FIELD}]},
          'filterConfig':{'filters':[{'name':'order','field':FIELD,'type':'Categorical','howCreated':'Drillthrough'}]}}
    value={'scan_id':'scan','report':{'id':'report'},'binding_status':'RESOLVED_EXPLICIT_ID','gaps':[],
           'report_definitions':[{'name':PAGE,'id':'part','metadata':{'content':json.dumps(page)}}]}
    return signed(value)

def signed(value):
    value.pop('bundle_hash',None)
    value['bundle_hash']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    return value

class DrillthroughTests(unittest.TestCase):
    def test_missing_context_requests_order(self):
        result=assess(fixture(),PAGE)
        self.assertEqual(result['status'],'NEEDS_INPUT')
        self.assertEqual(result['required_context'],['order_id'])
    def test_provided_context_is_not_runtime_proof(self):
        result=assess(fixture(),PAGE,'ORD-000001')
        self.assertEqual(result['status'],'CONTEXT_SUPPLIED')
        self.assertFalse(result['runtime_filter_verified'])
        self.assertFalse(result['root_cause_verified'])
        self.assertEqual(result['classification'],'UNRESOLVED')
    def test_changed_bundle_and_invalid_order_rejected(self):
        value=fixture();value['gaps']=['changed']
        with self.assertRaises(ValueError):assess(value,PAGE)
        for order in ['1','ORD-1',True]:
            with self.assertRaises(ValueError):assess(fixture(),PAGE,order)
    def test_unknown_page_or_missing_binding_is_unsupported(self):
        self.assertEqual(assess(fixture(),'unknown')['status'],'UNSUPPORTED')
        value=fixture();value['binding_status']='UNRESOLVED'
        self.assertEqual(assess(signed(value),PAGE)['status'],'UNSUPPORTED')
    def test_extra_predicate_and_wrong_binding_are_unsupported(self):
        for mutation in ('predicate','binding','null'):
            value=fixture();page=json.loads(value['report_definitions'][0]['metadata']['content'])
            if mutation=='predicate':page['filterConfig']['filters'][0]['filter']={'Where':[]}
            elif mutation=='binding':page['pageBinding']['parameters'][0]['boundFilter']='other'
            else:page['filterConfig']=None
            value['report_definitions'][0]['metadata']['content']=json.dumps(page)
            self.assertEqual(assess(signed(value),PAGE)['status'],'UNSUPPORTED')
