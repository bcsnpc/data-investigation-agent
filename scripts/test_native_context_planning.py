from contextlib import closing
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4
from metadata_inventory import Inventory,expand_definition
from lineage_graph import Graph
from ticket_workflow import TicketStore,Conflict
from ticket_planner import plan_ticket
from review_ticket_plan import approve
from report_drillthrough_context import FIELD

PAGE='definition/pages/details/page.json'

class NativePlanningTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name);self.database=root/'metadata.sqlite';self.store=TicketStore(root/'workflow.sqlite')
        self.lineage=str(uuid4());self.report='fabric://workspace/report'
        inventory=Inventory(self.database);scan=inventory.scan
        inventory.asset(self.report,'Report','Orders','endpoint',{},'fabric://workspace')
        model='fabric://workspace/22222222-2222-4222-8222-222222222222'
        inventory.asset(model,'SemanticModel','Model','endpoint',{},'fabric://workspace')
        page={'pageBinding':{'type':'Drillthrough','parameters':[{'name':'p','boundFilter':'order','fieldExpr':FIELD}]},'filterConfig':{'filters':[{'name':'order','field':FIELD,'type':'Categorical','howCreated':'Drillthrough'}]}}
        expand_definition(inventory,self.report,'Report',{'definition.pbir':json.dumps({'datasetReference':{'byConnection':{'connectionString':'semanticmodelid=22222222-2222-4222-8222-222222222222'}}}),'definition/report.json':'{}',PAGE:json.dumps(page)},'endpoint')
        expand_definition(inventory,model,'SemanticModel',{'model.bim':json.dumps({'model':{'tables':[]}})},'endpoint')
        inventory.db.execute('CREATE TABLE lineage_runs(id TEXT,scan_id TEXT)')
        inventory.db.execute('INSERT INTO lineage_runs VALUES(?,?)',(self.lineage,scan));inventory.finish();inventory.db.close()
        self.graph=Graph([{'id':self.report,'kind':'Report','name':'Orders'},{'id':'cash','kind':'Measure','name':'Net Cash'}])
        self.graph.edge('cash',self.report,'binding',self.report,'test')
        self.config={'storage':{'database':str(self.database)}};self.estate={'investigation':{'lineage_run':self.lineage}}
    def draft(self,order=None,inferred=None):
        body={'title':'Check cash','description':'Order details','report':'Orders','metric':'Net Cash','currency':'USD'}
        if order:body['order_id']=order
        ticket,_=self.store.submit(body,str(uuid4()),self.lineage)
        value={'report_id':self.report,'metric':'Net Cash','currency':'USD','order_id':order or inferred,'questions':[]}
        result=plan_ticket(self.store,ticket,self.graph,lambda _:(copy.deepcopy(value),{'mode':'fixture'}),native_page=PAGE,metadata_database=self.database)
        return ticket,result
    def approve(self,record):
        with patch('review_ticket_plan.load_graph',return_value=self.graph):
            return approve(self.store,record['id'],self.config,self.estate,'test-reviewer')
    def test_missing_order_blocks_approval(self):
        ticket,record=self.draft()
        self.assertEqual(record['status'],'NEEDS_INPUT')
        self.assertEqual(record['native_context']['status'],'NEEDS_INPUT')
        with self.assertRaises(Conflict):self.approve(record)
        self.assertEqual(self.store.get(ticket)['status'],'QUEUED')
    def test_explicit_order_approves_bounded_child(self):
        ticket,record=self.draft('ORD-000001')
        self.assertEqual(record['status'],'DRAFT_REQUIRES_REVIEW')
        child=self.approve(record)['ticket_id']
        self.assertEqual(self.store.get(child)['ticket']['order_id'],'ORD-000001')
        self.assertFalse(record['native_context']['runtime_filter_verified'])
        self.assertEqual(self.store.get(ticket)['status'],'QUEUED')
    def test_inferred_order_does_not_satisfy_explicit_context(self):
        _,record=self.draft(inferred='ORD-000001')
        self.assertEqual(record['status'],'NEEDS_INPUT')
        with self.assertRaises(Conflict):self.approve(record)
    def test_definition_change_after_plan_blocks_approval(self):
        _,record=self.draft('ORD-000001')
        with closing(sqlite3.connect(self.database)) as db:
            db.execute("UPDATE assets SET metadata='{}' WHERE kind='ReportPage'");db.commit()
        with self.assertRaises(Conflict):self.approve(record)
    def test_wrong_lineage_scan_fails_closed(self):
        with closing(sqlite3.connect(self.database)) as db:
            db.execute('UPDATE lineage_runs SET scan_id=?',(str(uuid4()),));db.commit()
        _,record=self.draft('ORD-000001')
        self.assertEqual(record['status'],'PLANNING_FAILED')
