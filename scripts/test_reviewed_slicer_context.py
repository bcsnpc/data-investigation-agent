from contextlib import closing
import hashlib
import json
import unittest
from uuid import uuid4
from test_native_context_planning import NativePlanningTests,PAGE
from ticket_planner import plan_ticket
from ticket_workflow import validate_ticket,Conflict
from ticket_worker import process_one

VISUAL='visual-slicer'
class ReviewedSlicerTests(unittest.TestCase):
    setUp=NativePlanningTests.setUp
    approve=NativePlanningTests.approve
    def add_slicer(self):
        with closing(self.store.connect()) as db:pass
        import sqlite3
        with closing(sqlite3.connect(self.database)) as db:
            scan=db.execute('SELECT scan_id FROM lineage_runs').fetchone()[0]
            model='fabric://workspace/22222222-2222-4222-8222-222222222222'
            visual={'visual':{'visualType':'slicer','query':{'queryState':{'Values':{'projections':[{'field':{'Column':{'Expression':{'SourceRef':{'Entity':'FactOrder'}},'Property':'order_id'}}}]}}}}}
            for aid,parent,kind,name,metadata in [('table',model,'SemanticTable','FactOrder',{}),('column','table','SemanticColumn','order_id',{}),(VISUAL,self.report,'DefinitionPart','definition/pages/details/visuals/s1/visual.json',{'content':json.dumps(visual)})]:
                raw=json.dumps(metadata,sort_keys=True)
                db.execute('INSERT INTO assets VALUES(?,?,?,?,?,?,?,?,?,?)',(scan,aid,parent,kind,name,'endpoint','now',None,hashlib.sha256(raw.encode()).hexdigest(),raw))
            db.commit()
    def ticket(self,selections=None):
        body={'title':'Check cash','description':'Order details','report':'Orders','metric':'Net Cash','currency':'USD','order_id':'ORD-000001','native_page':PAGE}
        if selections is not None:body['native_slicers']=selections
        identity,_=self.store.submit(body,str(uuid4()),self.lineage)
        value={'report_id':self.report,'metric':'Net Cash','currency':'USD','order_id':'ORD-000001','questions':[]}
        record=plan_ticket(self.store,identity,self.graph,lambda _:(value,{}),metadata_database=self.database)
        return identity,record
    def test_missing_choices_cannot_be_approved(self):
        self.add_slicer();_,record=self.ticket()
        self.assertEqual(record['slicer_context']['status'],'NEEDS_INPUT')
        with self.assertRaises(Conflict):self.approve(record)
    def test_explicit_choices_retained_but_execution_held(self):
        self.add_slicer();choices={VISUAL:{'mode':'values','values':['ORD-000001']}}
        identity,record=self.ticket(choices)
        self.assertEqual(self.store.get(identity)['ticket']['native_slicers'],choices)
        self.assertEqual(record['slicer_context']['status'],'CONTEXT_SUPPLIED')
        self.assertEqual(record['status'],'NEEDS_INPUT')
        with self.assertRaises(Conflict):self.approve(record)
    def test_worker_does_not_drop_slicer_scope(self):
        self.add_slicer();identity,_=self.ticket({VISUAL:{'mode':'all'}})
        def fail(*args):self.fail('Must not execute while slicers unsupported')
        self.assertEqual(process_one(self.store,self.config,self.estate,execute=fail)['status'],'NEEDS_INPUT')
    def test_selection_requires_page_and_bounded_shape(self):
        base={'title':'t','report':'r','description':'d'}
        with self.assertRaises(ValueError):validate_ticket(dict(base,native_slicers={}))
        for selection in [None,{'x':{'mode':'values','values':[]}}]:
            with self.assertRaises(ValueError):validate_ticket(dict(base,native_page=PAGE,native_slicers=selection))
    def test_changed_selection_conflicts_on_ticket_retry(self):
        body={'title':'t','report':'r','description':'d','native_page':PAGE,'native_slicers':{VISUAL:{'mode':'all'}}}
        key=str(uuid4());self.store.submit(body,key,self.lineage)
        body['native_slicers']={VISUAL:{'mode':'values','values':['x']}}
        with self.assertRaises(Conflict):self.store.submit(body,key,self.lineage)

del NativePlanningTests
