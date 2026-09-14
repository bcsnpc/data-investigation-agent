from contextlib import closing
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from uuid import uuid4
from planning_request import request_plan
from ticket_workflow import TicketStore


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=TicketStore(Path(self.temp.name)/'workflow.sqlite')
        self.ticket=str(uuid4());self.key=str(uuid4());self.plan=str(uuid4())
        with closing(self.store.connect()) as db:
            db.execute('CREATE TABLE ticket_plans(id TEXT PRIMARY KEY,ticket_id TEXT,record TEXT)')
            db.execute('INSERT INTO ticket_plans VALUES(?,?,?)',(self.plan,self.ticket,'{}'));db.commit()

    def test_repeat_returns_same_plan_without_second_call(self):
        generate=Mock(return_value=self.plan)
        first=request_plan(self.store,self.ticket,self.key,generate)
        second=request_plan(self.store,self.ticket,self.key,generate)
        self.assertEqual(first['status'],'COMPLETED');self.assertEqual(second['plan_id'],self.plan)
        self.assertTrue(second['replayed']);self.assertEqual(generate.call_count,1)

    def test_failure_is_sanitized_and_not_retried(self):
        generate=Mock(side_effect=ValueError('secret error body'))
        result=request_plan(self.store,self.ticket,self.key,generate)
        self.assertEqual(result['status'],'FAILED');self.assertNotIn('secret',json.dumps(result))
        request_plan(self.store,self.ticket,self.key,generate);self.assertEqual(generate.call_count,1)

    def test_unknown_persisted_plan_is_rejected(self):
        result=request_plan(self.store,self.ticket,self.key,lambda _:str(uuid4()))
        self.assertEqual(result['status'],'FAILED')

    def test_in_progress_replay_never_calls_provider(self):
        def generate(_):
            nested=Mock()
            result=request_plan(self.store,self.ticket,self.key,nested)
            self.assertEqual(result['status'],'RUNNING');nested.assert_not_called()
            return self.plan
        self.assertEqual(request_plan(self.store,self.ticket,self.key,generate)['status'],'COMPLETED')


if __name__=='__main__':unittest.main()
