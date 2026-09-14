from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import duckdb
from defect_lab import initialize,mutate,validate
from categorical_filter_replay import execute

PAGE='definition/pages/main/page.json'
def definitions(fields=('order_id','currency','status')):
    parts=[{'id':'page','name':PAGE,'metadata':{'content':'{}'}}]
    assets=[{'id':'table','kind':'SemanticTable','name':'FactOrder','parent_id':'model'}]
    for field in fields:
        assets.append({'id':'column/'+field,'kind':'SemanticColumn','name':field,'parent_id':'table'})
        visual={'visual':{'visualType':'slicer','query':{'queryState':{'Values':{'projections':[{'field':{'Column':{'Expression':{'SourceRef':{'Entity':'FactOrder'}},'Property':field}}}]}}}}}
        parts.append({'id':field,'name':'definition/pages/main/visuals/'+field+'/visual.json','content_hash':'fixture','metadata':{'content':json.dumps(visual)}})
    value={'scan_id':'scan','report':{'id':'report'},'binding_status':'RESOLVED_EXPLICIT_ID','gaps':[],'report_definitions':parts,'model_assets':assets}
    value['bundle_hash']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest();return value

def choices(**values):
    return {field:{'mode':'values','values':values[field]} if field in values else {'mode':'all'} for field in ('order_id','currency','status')}

class CategoricalReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name);self.lab=root/'lab.duckdb';self.database=root/'evidence.sqlite';initialize(self.lab)
    def run_case(self,selection):return execute(self.lab,definitions(),PAGE,selection,self.database)
    def test_or_within_and_across_slicers(self):
        result=self.run_case(choices(order_id=['ORD-000001','ORD-000002'],currency=['USD'],status=['PAID']))
        self.assertEqual(result['selected_records'],1)
        self.assertEqual(result['impact_by_currency']['USD']['gold_total'],'55.0000')
        self.assertEqual(validate(self.lab)['status'],'READY')
    def test_selected_defect_is_not_hidden(self):
        mutate(self.lab,'inject-double-refund')
        result=self.run_case(choices(order_id=['ORD-000001']))
        self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'-99.0000')
        self.assertEqual(result['comparison_status'],'MISMATCH')
        self.assertFalse(result['root_cause_verified'])
    def test_no_matches_is_not_a_clean_bill(self):
        result=self.run_case(choices(order_id=['ORD-999999']))
        self.assertEqual(result['comparison_status'],'NO_MATCHES')
        self.assertEqual(result['classification'],'UNRESOLVED')
    def test_persisted_capture_and_indices_hash(self):
        result=self.run_case(choices(status=['PARTIALLY_RETURNED']))
        with closing(sqlite3.connect(self.database)) as db:
            request=json.loads(db.execute('SELECT request FROM investigation_runs WHERE id=?',(result['id'],)).fetchone()[0])
        digest=request.pop('evidence_hash')
        self.assertEqual(digest,hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest())
        self.assertEqual(request['selected_row_indices'],[0])
        self.assertEqual(len(request['lab_evidence']['rows']),3)
    def test_unsupported_field_and_missing_selection_rejected(self):
        with self.assertRaises(ValueError):self.run_case({})
        with self.assertRaises(ValueError):execute(self.lab,definitions(('customer_id',)),PAGE,{'customer_id':{'mode':'all'}},self.database)
        self.assertFalse(self.database.exists())
    def test_currency_totals_are_not_combined(self):
        with closing(duckdb.connect(str(self.lab))) as db:
            db.execute("UPDATE s_fact_order SET currency='EUR' WHERE order_id='ORD-000002'")
            db.execute("UPDATE g_order_line_summary SET currency='EUR' WHERE order_id='ORD-000002'")
        result=self.run_case(choices())
        self.assertEqual(result['impact_by_currency']['USD']['gold_total'],'99.0000')
        self.assertEqual(result['impact_by_currency']['EUR']['gold_total'],'55.0000')
    def test_duplicate_attributes_fail_before_filtering(self):
        with closing(duckdb.connect(str(self.lab))) as db:
            db.execute("INSERT INTO s_fact_order SELECT * FROM s_fact_order WHERE order_id='ORD-000003'")
        with self.assertRaises(ValueError):self.run_case(choices(order_id=['ORD-000001']))
