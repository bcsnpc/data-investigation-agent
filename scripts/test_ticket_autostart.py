"""The interactive composition root starts settled tickets; dry evals never read."""
import copy
import unittest
from unittest.mock import patch
from investigator.onboarding import Conflict
import test_smart_intake

class TicketAutoStartTests(unittest.TestCase):
    def setUp(self):
        self.h=test_smart_intake.SmartIntakeTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.controller=self.h.controller;self.workspace=self.h.workspace
        self.controller.auto_start=True
        self.previews=[];self.starts=[]
        def preview(request):
            self.previews.append(copy.deepcopy(request))
            return {'id':'preview','envelope':{'limits':{'cloud_calls':12,'planner_calls':12}}}
        def start(identity):
            self.starts.append(identity);return {'id':'run'}
        def session(identity):
            ticket=self.controller.tickets.list()['tickets'][0]['ticket']
            return {'intake':{'id':ticket['intake_id']}}
        for name,func in [('preview',preview),('start',start),('session',session)]:
            p=patch.object(self.workspace,name,side_effect=func);p.start();self.addCleanup(p.stop)

    def settled(self):
        offer=self.h.submit()
        self.assertEqual(offer['ticket']['state'],'CLARIFYING')
        self.assertEqual(self.starts,[])
        return self.controller.reply(self.h.reply(offer))

    def test_settled_reply_queues_once_from_exact_adopted_scope_and_same_caps(self):
        saved=self.settled();ticket=saved['ticket']
        self.assertEqual(ticket['state'],'INVESTIGATING');self.assertEqual(ticket['session_id'],'run')
        p=self.workspace.intake.get(ticket['intake_id'])['proposal']
        self.assertEqual({k:self.previews[0][k] for k in ('model_id','measure_id','filters','dimension_ids')},
                         {k:p[k] for k in ('model_id','measure_id','filters','dimension_ids')})
        self.assertEqual(self.previews[0]['intake_id'],ticket['intake_id'])
        self.assertEqual(self.starts,['preview'])
        limits=next(e['detail']['limits'] for e in ticket['history'] if e['detail'].get('reason')=='AUTO_START_RESERVED')
        self.assertEqual(limits,{'cloud_calls':12,'planner_calls':12})
        self.h.h.native.assert_not_called();self.h.h.source.assert_not_called()
        self.assertEqual(self.h.calls,1)

    def test_repeated_submit_does_not_dispatch_twice(self):
        saved=self.settled();self.assertEqual(self.h.submit(),saved)
        self.assertEqual(self.starts,['preview']);self.assertEqual(len(self.previews),1)

    def test_intake_only_host_names_gate_without_start(self):
        offer=self.h.submit()
        self.workspace.execution_enabled=False
        saved=self.controller.reply(self.h.reply(offer))
        self.assertEqual(saved['ticket']['state'],'HELD')
        self.assertEqual(saved['ticket']['history'][-1]['detail']['reason'],'INTAKE_ONLY_HOST')
        self.assertEqual(self.previews,[]);self.assertEqual(self.starts,[])

    def test_approval_or_budget_refusal_is_retained_and_not_bypassed(self):
        with patch.object(self.workspace,'preview',side_effect=Conflict('Discovery approval is stale')):
            saved=self.settled()
        detail=saved['ticket']['history'][-1]['detail']
        self.assertEqual(detail['reason'],'AUTO_START_REFUSED')
        self.assertEqual(detail['message'],'Discovery approval is stale')
        self.assertEqual(self.starts,[])

    def test_start_refusal_keeps_reserved_preview_and_never_retries(self):
        with patch.object(self.workspace,'start',side_effect=Conflict('Another investigation is active')) as start:
            saved=self.settled();again=self.h.submit()
        self.assertEqual(again,saved);self.assertEqual(start.call_count,1)
        self.assertEqual(saved['ticket']['history'][-1]['detail']['preview_id'],'preview')
        self.assertEqual(saved['ticket']['state'],'HELD')

    def test_user_cannot_tell_never_starts(self):
        offer=self.h.submit();answers=[{'question_id':q['id'],'unavailable':True} for q in offer['ticket']['questions']]
        saved=self.controller.reply({'ticket_id':offer['ticket']['id'],'revision':offer['revision'],
                                    'answers':answers,'request_key':'unavailable'})
        self.assertEqual(saved['ticket']['state'],'HELD');self.assertEqual(self.starts,[])

    def test_default_workspace_controller_enables_governed_auto_start(self):
        del self.workspace._smart_intake
        self.assertTrue(self.workspace.smart_intake.auto_start)

if __name__=='__main__':unittest.main()

