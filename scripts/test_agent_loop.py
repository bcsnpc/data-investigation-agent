import unittest
from investigator.agent_loop import AgentLoop, closed_wire_schema, decision_schema
from jsonschema import Draft202012Validator


class AgentLoopTests(unittest.TestCase):
    def test_repeat_returns_original_evidence_without_tool_or_read_admission(self):
        from unittest.mock import Mock
        loop, rows, calls = self.loop([self.tool(), self.tool(), self.answer()])
        handler = Mock(return_value={'status':'OBSERVED','evidence_ids':['read:1'],'value':7})
        loop.tools['lookup'] = handler
        loop.admit = Mock()
        out = self.run_loop(loop)
        self.assertEqual(out['status'], 'COMPLETED')
        handler.assert_called_once_with()
        self.assertEqual([c.args[0] for c in loop.admit.call_args_list].count('TOOL'), 1)
        reused = next(r for r in rows if r['event'] == 'TOOL_REUSED')
        self.assertEqual(reused['evidence_ids'], ['read:1'])
        self.assertEqual(reused['original_receipt_id'], 'event:3')
        self.assertEqual(calls[2]['feedback']['status'], 'ALREADY_OBTAINED')
        self.assertEqual(sum(r['event']=='TOOL_RESULT' for r in rows), 1)

    def test_argument_order_reuses_but_changed_content_executes(self):
        from unittest.mock import Mock
        decisions = [dict(self.tool(), arguments=a) for a in
                     ({'a':1,'b':2}, {'b':2,'a':1}, {'a':2,'b':2})]
        loop, rows, calls = self.loop(decisions, cap=3)
        loop.validator = Mock(iter_errors=lambda d: [])
        handler = Mock(side_effect=[{'evidence_ids':['first']}, {'evidence_ids':['second']}])
        loop.tools['lookup'] = handler
        self.run_loop(loop)
        self.assertEqual(handler.call_count, 2)
        self.assertEqual(sum(r['event']=='TOOL_REUSED' for r in rows), 1)

    def test_pre_admission_refusal_does_not_poison_admitted_call(self):
        from unittest.mock import Mock
        loop, rows, _ = self.loop([self.tool(), self.tool()], cap=2)
        loop.tools['lookup'] = Mock(side_effect=[
            {'status':'NOT_ADMITTED','evidence_ids':['refusal']},
            {'status':'OBSERVED','evidence_ids':['read:1']}])
        self.run_loop(loop)
        self.assertEqual(loop.tools['lookup'].call_count, 2)
        self.assertFalse(any(r['event']=='TOOL_REUSED' for r in rows))

    def test_repeat_fetch_is_note_and_keeps_original_full_evidence(self):
        fetch = {'action':'TOOL','tool':'get_evidence','arguments':{'id':'read:1'},'summary':'Inspect receipt.'}
        loop, rows, calls = self.loop([self.tool(), fetch, fetch, self.answer()])
        self.assertEqual(self.run_loop(loop)['status'], 'COMPLETED')
        self.assertEqual(sum(r['event']=='EVIDENCE_FETCH' for r in rows), 1)
        self.assertEqual(calls[2]['fetched_evidence']['result']['value'], 7)
        self.assertEqual(calls[3]['fetched_evidence'], calls[2]['fetched_evidence'])
        self.assertEqual(calls[3]['feedback']['evidence_ids'], ['read:1'])

    def test_reselecting_fetched_evidence_after_another_step_is_local_and_lossless(self):
        from unittest.mock import Mock
        fetch = {'action':'TOOL','tool':'get_evidence','arguments':{'id':'read:1'},'summary':'Inspect receipt.'}
        loop, rows, calls = self.loop([self.tool(), fetch, self.tool(), fetch, self.answer()], cap=5)
        handler = Mock(return_value={'status':'OBSERVED','evidence_ids':['read:1'],'value':7})
        loop.tools['lookup'] = handler
        loop.admit = Mock()
        self.assertEqual(self.run_loop(loop)['status'], 'COMPLETED')
        handler.assert_called_once_with()
        self.assertEqual(sum(c.args[0]=='TOOL' for c in loop.admit.call_args_list), 2)
        self.assertEqual(sum(r['event']=='EVIDENCE_FETCH' for r in rows), 1)
        self.assertEqual(calls[4]['fetched_evidence'], calls[2]['fetched_evidence'])
        self.assertEqual(calls[4]['feedback']['status'], 'ALREADY_OBTAINED')

    def test_provider_decision_has_typed_scalar_enums_and_same_allowed_values(self):
        wire = decision_schema({'lookup': {'type': 'object', 'additionalProperties': False,
            'properties': {}, 'required': []}}, {'CONSISTENT_TO_BOUNDARY'})
        def visit(value):
            if isinstance(value, dict):
                self.assertNotIn('const', value)
                if 'enum' in value: self.assertIn('type', value)
                for item in value.values(): visit(item)
            elif isinstance(value, list):
                for item in value: visit(item)
        visit(wire)
        self.assertTrue(Draft202012Validator(wire).is_valid(self.tool()))
        invalid = self.tool(); invalid['action'] = 'WRITE'
        self.assertFalse(Draft202012Validator(wire).is_valid(invalid))

    def test_strict_wire_preserves_optional_argument_shapes_without_null_defaults(self):
        consumer = {'type': 'object', 'additionalProperties': False,
                    'properties': {'id': {'type': 'string'}, 'choices': {'type': 'array', 'items': {'type': 'string'}}},
                    'required': ['id']}
        wire = closed_wire_schema(consumer)
        for shape in wire['anyOf']:
            self.assertEqual(set(shape['required']), set(shape['properties']))
        for value in ({'id': 'a'}, {'id': 'a', 'choices': []}, {'id': 'a', 'choices': None}, {}, {'id': 'a', 'extra': 1}):
            self.assertEqual(Draft202012Validator(consumer).is_valid(value),
                             Draft202012Validator(wire).is_valid(value))

    def loop(self, decisions, *, result=None, validate=None, cap=4, clock=lambda: 0):
        rows=[]; calls=[]; choices=iter(decisions)
        def decide(payload, **kw):
            calls.append(payload);return next(choices)
        def persist(event):
            rows.append(event);return 'event:'+str(len(rows))
        loop=AgentLoop(tools={'lookup':lambda: result or {'status':'OBSERVED','evidence_ids':['read:1'],'value':7}},
            schemas={'lookup':{'type':'object','additionalProperties':False,'properties':{}}},
            decide=decide,persist=persist,validate_delivery=validate or (lambda *a,**k:{'validated':True,'outputs':{'text':'Checked.'}}),
            outcomes={'CONSISTENT_TO_BOUNDARY'},admit=lambda *a:None,step_cap=cap,clock=clock)
        return loop,rows,calls

    def tool(self):return {'action':'TOOL','summary':'Read the selected object.','tool':'lookup','arguments':{}}
    def answer(self, ref='read:1'):return {'action':'ANSWER','summary':'Report the evidence.','outcome':'CONSISTENT_TO_BOUNDARY','claims':[{'text':'Observed agreement.','evidence_ids':[ref]}]}
    def run_loop(self, loop):return loop.run({'description':'Untrusted ticket'},fixed_facts={'visual_id':'picked'},context_id='context:1')

    def test_tool_then_validated_delivery(self):
        loop,rows,calls=self.loop([self.tool(),self.answer()]);out=self.run_loop(loop)
        self.assertEqual(out['status'],'COMPLETED');self.assertEqual(calls[1]['fixed_facts'],{'visual_id':'picked'})
        self.assertIn('read:1',calls[1]['evidence']);self.assertEqual(rows[-1]['event'],'DELIVERED')

    def test_uncited_answer_rejected_then_holds(self):
        loop,rows,_=self.loop([self.answer('invented'),{'action':'HOLD','summary':'Cannot establish it.','reason':'No evidence'}])
        out=self.run_loop(loop);self.assertEqual(out['status'],'HELD');self.assertIn('CLAIM_REJECTED',[r['event'] for r in rows])

    def test_overclaim_validator_cannot_be_bypassed(self):
        def reject(*a,**k):raise ValueError('COVERAGE_EXCEEDS_EVIDENCE')
        loop,rows,calls=self.loop([self.tool(),self.answer(),{'action':'HOLD','summary':'Scope not proven.','reason':'Coverage refused'}],validate=reject)
        self.assertEqual(self.run_loop(loop)['status'],'HELD');self.assertEqual(calls[2]['feedback']['reason'],'COVERAGE_EXCEEDS_EVIDENCE')

    def test_step_cap_preserves_progress(self):
        loop,rows,_=self.loop([self.tool()],cap=1);out=self.run_loop(loop)
        self.assertEqual(out['reason'],'AGENT_STEP_CAP');self.assertEqual(out['evidence_ids'],['read:1'])

    def test_pending_question_does_not_invent_user_answer(self):
        loop,rows,calls=self.loop([self.tool()],result={'status':'WAITING_FOR_USER','evidence_ids':['comment:1']})
        self.assertEqual(self.run_loop(loop)['status'],'WAITING_FOR_USER');self.assertEqual(len(calls),1)

    def test_no_delivery_validator_refuses_construction(self):
        with self.assertRaises(ValueError):AgentLoop(tools={},schemas={},decide=None,persist=None,validate_delivery=None,outcomes=[],admit=None)

    def test_untrusted_tool_and_extra_args_rejected(self):
        d=self.tool();d['arguments']={'query':'DROP TABLE X'}
        loop,rows,_=self.loop([d],cap=1);out=self.run_loop(loop)
        self.assertEqual(out['status'],'HELD');self.assertNotIn('TOOL_RESULT',[r['event'] for r in rows])

    def test_empty_outputs_cannot_be_a_completed_delivery(self):
        loop,rows,_=self.loop([self.tool(),self.answer()], cap=2,
            validate=lambda *a,**k:{'validated':True,'outputs':None})
        self.assertEqual(self.run_loop(loop)['status'],'HELD')
        self.assertNotIn('DELIVERED',[r['event'] for r in rows])

    def test_tool_without_evidence_is_unavailable(self):
        loop,rows,_=self.loop([self.tool()], cap=1,
            result={'status':'AVAILABLE','evidence_ids':[]})
        self.assertEqual(self.run_loop(loop)['evidence_ids'],[])
        self.assertIn('TOOL_FAILED',[r['event'] for r in rows])

    def test_deadline_after_model_prevents_tool_dispatch(self):
        times=iter([0,0,1000])
        loop,rows,_=self.loop([self.tool()],clock=lambda:next(times))
        self.assertEqual(self.run_loop(loop)['reason'],'AGENT_WALL_LIMIT')
        self.assertNotIn('TOOL_RESULT',[r['event'] for r in rows])

if __name__=='__main__':unittest.main()
