import unittest
from contextlib import closing
import json
from unittest.mock import patch
from test_native_context_planning import NativePlanningTests,PAGE
from native_plan_context import pages
from ticket_planner import plan_ticket
from ticket_workflow import validate_ticket,Conflict

class NativePageTests(unittest.TestCase):
    setUp=NativePlanningTests.setUp
    draft=NativePlanningTests.draft
    approve=NativePlanningTests.approve
    def test_choices_match_retained_report(self):
        self.assertEqual(pages(self.database,self.lineage),[{'report_id':self.report,'report_name':'Orders','path':PAGE,'label':'Order details'}])
    def test_ticket_page_automatically_applies(self):
        ticket,old=self.draft()
        with closing(self.store.connect()) as db:
            body=self.store.get(ticket)['ticket'];body['native_page']=PAGE
            db.execute('UPDATE tickets SET body=? WHERE id=?',(json.dumps(body),ticket));db.commit()
        value={'report_id':self.report,'metric':'Net Cash','currency':'USD','order_id':None,'questions':[]}
        record=plan_ticket(self.store,ticket,self.graph,lambda _:(value,{}),metadata_database=self.database)
        self.assertEqual(record['status'],'NEEDS_INPUT')
        self.assertEqual(record['native_context']['page_path'],PAGE)
        with self.assertRaises(Conflict):self.approve(record)
    def test_invalid_page_rejected(self):
        for page in ['../../secret','https://example.com','definition/pages/a/b/page.json']:
            with self.assertRaises(ValueError):validate_ticket({'title':'t','report':'r','description':'d','native_page':page})

del NativePlanningTests
