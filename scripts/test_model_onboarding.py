from contextlib import closing
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

from metadata_inventory import Inventory, expand_definition
from investigator.onboarding import ModelStore, Conflict
from investigator.admin_api import create_app


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.inventory=self.root/'inventory.sqlite'
        self.workspace=str(uuid4());self.model=str(uuid4());self.report=str(uuid4())
        self.store=ModelStore(self.root/'catalog.sqlite',self.inventory,'development')
        self.body={'name':'Finance','workspace':self.workspace,'model_id':self.model,'report_ids':[self.report]}
        self.business={k:'Confirmed example' for k in ['definition','owner','date_basis','refresh_expectation','tolerance','exceptions']}

    def scan(self, measures=None, partial=False, binding=None):
        inv=Inventory(self.inventory);root='fabric://'+self.workspace
        inv.asset(root+'/'+self.report,'Report','Report','test',{},root)
        inv.asset(root+'/'+self.model,'SemanticModel','Model','test',{},root)
        expand_definition(inv,root+'/'+self.report,'Report',{
            'definition.pbir':json.dumps({'datasetReference':{'byConnection':{'connectionString':'semanticmodelid='+(binding or self.model)}}}),
            'definition/report.json':'{}','definition/pages/p/page.json':'{"name":"p"}'},'test')
        expand_definition(inv,root+'/'+self.model,'SemanticModel',{'model.bim':json.dumps({'model':{'tables':[{'name':'Sales','measures':measures or [{'name':'New metric','expression':'SUM(Sales[amount])'}]}]}})},'test')
        if partial:inv.observe(root,'coverage','UNAVAILABLE','test',{})
        inv.finish();inv.db.close();return inv.scan

    def registered(self):return self.store.register(self.body,'test-admin')
    def imported(self):
        m=self.registered();return self.store.import_scan(m['id'],m['revision'],self.scan(),'test-admin')

    def test_registration_duplicate_and_environment_isolation(self):
        m=self.registered()
        with self.assertRaises(Conflict):self.registered()
        other=ModelStore(self.root/'catalog.sqlite',self.inventory,'production')
        self.assertEqual(other.list(),[])
        with self.assertRaises(KeyError):other.get(m['id'])
        self.assertNotEqual(other.register(self.body,'admin')['id'],m['id'])

    def test_enable_requires_context_review_and_disables(self):
        m=self.registered()
        with self.assertRaises(Conflict):self.store.enable(m['id'],1,True,'admin')
        m=self.store.import_scan(m['id'],1,self.scan(),'admin')
        with self.assertRaises(Conflict):self.store.enable(m['id'],m['revision'],True,'admin')
        m=self.store.review(m['id'],m['revision'],self.business,'admin')
        m=self.store.enable(m['id'],m['revision'],True,'admin')
        self.assertEqual(len(self.store.list(True)),1)
        self.assertEqual(m['readiness'],'PARTIAL')
        self.assertEqual(m['context']['capabilities']['MODEL_QUERYABLE'],'UNKNOWN')
        m=self.store.enable(m['id'],m['revision'],False,'admin')
        self.assertEqual(self.store.list(True),[])

    def test_unseen_measure_and_change_invalidate_enablement(self):
        m=self.imported();old=m['context_id']
        m=self.store.review(m['id'],m['revision'],self.business,'admin')
        m=self.store.enable(m['id'],m['revision'],True,'admin')
        scan=self.scan([{'name':'Unknown ratio','expression':'DIVIDE([A],[B])'}])
        m=self.store.import_scan(m['id'],m['revision'],scan,'admin')
        self.assertFalse(m['enabled'])
        self.assertEqual(m['stage'],'BUSINESS_CONTEXT_REVIEW')
        self.assertEqual(m['context']['measures'][0]['name'],'Unknown ratio')
        self.assertEqual(self.store.context(m['id'],old)['measures'][0]['name'],'New metric')
        self.assertTrue(m['context']['changes']['removed'])

    def test_identical_scan_carries_review_with_event(self):
        m=self.imported();m=self.store.review(m['id'],m['revision'],self.business,'admin')
        m=self.store.enable(m['id'],m['revision'],True,'admin')
        m=self.store.import_scan(m['id'],m['revision'],self.scan(),'admin')
        self.assertTrue(m['enabled']);self.assertEqual(m['business']['confirmed_context'],m['context_id'])
        self.assertFalse(any(m['context']['changes'].values()))

    def test_stale_revision_and_duplicate_scan_rejected(self):
        m=self.imported()
        with self.assertRaises(Conflict):self.store.review(m['id'],1,self.business,'admin')
        with self.assertRaises(Conflict):self.store.import_scan(m['id'],m['revision'],m['context']['scan_id'],'admin')

    def test_partial_removal_preserves_last_good_context(self):
        m=self.imported();old=m['context_id']
        scan=self.scan([{'name':'Different','expression':'1'}],partial=True)
        with self.assertRaises(ValueError):self.store.import_scan(m['id'],m['revision'],scan,'admin')
        self.assertEqual(self.store.get(m['id'])['context_id'],old)

    def test_binding_mismatch_and_tamper_rejected(self):
        m=self.registered()
        with self.assertRaises(ValueError):self.store.import_scan(m['id'],1,self.scan(binding=str(uuid4())),'admin')
        scan=self.scan()
        with closing(sqlite3.connect(self.inventory)) as db:
            db.execute("UPDATE assets SET metadata='{}' WHERE scan_id=? AND kind='Measure'",(scan,));db.commit()
        with self.assertRaises(ValueError):self.store.import_scan(m['id'],1,scan,'admin')

    def test_context_hash_and_model_ownership_enforced(self):
        m=self.imported()
        body=dict(self.body,model_id=str(uuid4()));other=self.store.register(body,'admin')
        with self.assertRaises(KeyError):self.store.context(other['id'],m['context_id'])
        with self.store.connect() as db:db.execute("UPDATE model_contexts SET body='{}' WHERE id=?",(m['context_id'],))
        with self.assertRaises(ValueError):self.store.get(m['id'])

    def test_api_roles_limits_and_catalog(self):
        app=create_app(self.store,'a'*32,'r'*32)
        def call(path,token='',body=None,method=None):
            raw=json.dumps(body).encode() if body is not None else b'';status=[]
            data=b''.join(app({'PATH_INFO':path,'REQUEST_METHOD':method or ('POST' if body is not None else 'GET'),
                 'HTTP_AUTHORIZATION':'Bearer '+token,'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),
                 'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
            return status[0],json.loads(data)
        self.assertEqual(call('/api/v2/admin/models')[0],'401 Unauthorized')
        self.assertEqual(call('/api/v2/admin/models','r'*32)[0],'403 Forbidden')
        self.assertEqual(call('/api/v2/admin/models','a'*32,{'bad':1})[0],'400 Bad Request')
        self.assertEqual(call('/api/v2/admin/models','a'*32,dict(self.body,workspace=None))[0],'400 Bad Request')
        self.assertEqual(call('/api/v2/admin/models','a'*32,{'bad':'x'*17000})[0],'400 Bad Request')
        m=self.imported();m=self.store.review(m['id'],m['revision'],self.business,'admin');self.store.enable(m['id'],m['revision'],True,'admin')
        result=call('/api/v2/reports','r'*32)[1]['reports']
        self.assertEqual(len(result),1);self.assertFalse(result[0]['execution_available'])
        self.assertNotIn('business',result[0]);self.assertNotIn('definition',result[0])
        with self.assertRaises(ValueError):create_app(self.store,'a'*32,'a'*32)


if __name__=='__main__':unittest.main()
