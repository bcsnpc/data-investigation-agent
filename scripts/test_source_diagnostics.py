from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock
from io import BytesIO
import json

from metadata_inventory import Inventory
from investigator.source_diagnostics import build, run, snapshot, evidence
from investigator.admin_api import create_app
from run_source_diagnostic import SourceReadError
from test_native_diagnostics import fixture, database


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.model,_=fixture();self.store=MagicMock()
        self.store.inventory=Path(self.temp.name)/'inventory.sqlite'
        self.store.connect.side_effect=lambda:database(Path(self.temp.name)/'catalog.sqlite')
        def get(identity):
            if identity != self.model['id']:raise KeyError(identity)
            return self.model
        self.store.get.side_effect=get
        self.config={'sql':{'server':'host','database':'db','visibility_schema':'app','auth':{}},'fabric':{'workspace_id':'workspace'}}
        self.root='sql://host/db';self.obj=self.root+'/object/1'
        inv=Inventory(self.store.inventory)
        inv.asset(self.obj,'SqlObject','app.Sales','test',{'schema_name':'app','name':'Sales','type_desc':'USER_TABLE'},self.root)
        for name,kind,scale in [('currency','nvarchar',0),('amount','decimal',2)]:
            inv.asset(self.obj+'/'+name,'SqlColumn',name,'test',{'name':name,'data_type':kind,'scale':scale},self.obj)
        inv.observe(self.root,'catalog_visibility','AVAILABLE','test',{})
        inv.finish();self.model['context']['scan_id']=inv.scan;inv.db.close()
        self.plan={'model_id':'model','revision':3,'context_id':'ctx','object_id':self.obj,
                   'operation':'count_rows','column_id':None,'filters':[{'column_id':self.obj+'/currency','values':['USD']}]}

    def test_value_parameterization_and_read_only_query(self):
        self.plan['filters'][0]['values']=["USD'; DROP TABLE Sales; --"]
        req=build(self.store,self.plan,self.config)
        self.assertNotIn('DROP',req['query']);self.assertIn('@p0',req['query'])
        self.assertEqual(req['parameters'][0]['value'],self.plan['filters'][0]['values'][0])
        self.assertTrue(req['query'].startswith('SELECT COUNT_BIG(*)'))

    def test_sum_null_and_count_semantics(self):
        self.plan.update(operation='sum',column_id=self.obj+'/amount')
        query=build(self.store,self.plan,self.config)['query']
        self.assertIn('SUM(CAST([amount] AS decimal(38,2)))',query)
        for result in [{'value':None,'row_count':'2','nonblank_count':'0'},
                       {'value':'0.00','row_count':'2','nonblank_count':'2'}]:
            receipt=run(self.store,self.plan,self.config,lambda req:result.copy())
            self.assertEqual(receipt['status'],'COMPLETED')
            self.assertEqual(receipt['result']['value']['type'],'blank' if result['value'] is None else 'decimal')
            self.assertFalse(receipt['result']['measure_equivalence_verified'])

    def test_inconsistent_results_fail_not_zero(self):
        for response in [{'value':'2','row_count':'1','nonblank_count':'1'},
                         {'value':'NaN','row_count':'1','nonblank_count':'1'},
                         {'value':None,'row_count':'0','nonblank_count':'0'},{}]:
            self.assertEqual(run(self.store,self.plan,self.config,lambda req:response.copy())['status'],'FAILED')

    def test_unknown_objects_operations_columns_and_missing_scope_rejected(self):
        for changes in [{'object_id':'other'},{'operation':'delete'},{'column_id':'other'},
                        {'operation':'sum','column_id':self.obj+'/currency'},{'filters':[]},{'query':'SQL'},{'revision':1}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):build(self.store,dict(self.plan,**changes),self.config)

    def test_metadata_tamper_and_denied_visibility(self):
        with database(self.store.inventory) as db:
            db.execute("UPDATE observations SET status='UNAVAILABLE'")
        with self.assertRaises(ValueError):build(self.store,self.plan,self.config)
        with database(self.store.inventory) as db:
            db.execute("UPDATE observations SET status='AVAILABLE'")
            db.execute("UPDATE assets SET content_hash='bad'")
        with self.assertRaises(ValueError):build(self.store,self.plan,self.config)

    def test_connection_and_disable_gates(self):
        config=dict(self.config,fabric={'workspace_id':'other'})
        with self.assertRaises(ValueError):build(self.store,self.plan,config)
        self.model['enabled']=False
        with self.assertRaises(ValueError):build(self.store,self.plan,self.config)

    def test_receipt_precedes_dispatch_and_history_survives_disable(self):
        def execute(req):
            self.assertEqual(evidence(self.store,'model')[0]['status'],'RUNNING')
            return {'value':'3','row_count':'3','nonblank_count':'3'}
        receipt=run(self.store,self.plan,self.config,execute)
        self.assertTrue(evidence(self.store,'model',receipt['id'])['local_context_current'])
        self.model['enabled']=False
        self.assertFalse(evidence(self.store,'model',receipt['id'])['local_context_current'])
        with self.assertRaises(KeyError):evidence(self.store,'other',receipt['id'])

    def test_midflight_change_and_timeout(self):
        def execute(req):
            self.model['revision']+=1
            return {'value':'1','row_count':'1','nonblank_count':'1'}
        self.assertEqual(run(self.store,self.plan,self.config,execute)['status'],'HELD')
        self.model['revision']=3
        call=MagicMock(side_effect=TimeoutError('secret'))
        result=run(self.store,self.plan,self.config,call)
        self.assertEqual(result['status'],'INTERRUPTED');call.assert_called_once()
        self.assertNotIn('secret',str(result))
        result=run(self.store,self.plan,self.config,MagicMock(side_effect=SourceReadError(-2,'SqlException')))
        self.assertEqual(result['status'],'INTERRUPTED')
        self.assertEqual(result['result']['error_number'],-2)

    def test_api_receipt_authorization_and_missing_result(self):
        app=create_app(self.store,'a'*32,'r'*32)
        for token,expected in [('a'*32,'200 OK'),('r'*32,'403 Forbidden'),('','401 Unauthorized')]:
            status=[]
            raw=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/source-diagnostics','REQUEST_METHOD':'GET',
                'HTTP_AUTHORIZATION':'Bearer '+token,'wsgi.input':BytesIO()},lambda s,h:status.append(s)))
            self.assertEqual(status[0],expected)
            if token.startswith('a'):self.assertEqual(json.loads(raw),[])
        with self.assertRaises(KeyError):evidence(self.store,'model','missing')

    def test_parameter_utf16_budget_and_malformed_numeric_output(self):
        self.plan['filters'][0]['values']=['\U0001f600'*101]
        with self.assertRaises(ValueError):build(self.store,self.plan,self.config)
        self.plan['filters'][0]['values']=['USD']
        result=run(self.store,self.plan,self.config,lambda req:{'value':'1e9999999','row_count':'1e9999999','nonblank_count':'1'})
        self.assertEqual(result['status'],'FAILED')


if __name__=='__main__':unittest.main()
