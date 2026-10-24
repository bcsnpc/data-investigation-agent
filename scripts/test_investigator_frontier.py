import copy,json,unittest
from unittest.mock import Mock,patch
from investigator.investigator_case import CaseFile
import test_ledger_investigator as fixtures

class FrontierSteerTests(unittest.TestCase):
    def test_successful_exact_repeat_uses_case_result_and_short_feedback_not_dispatch(self):
        tools,engine,reader,events=fixtures.ToolLoopTests().build(step_cap=6);engine.phase_limit=6
        tools.graph.definition_of.return_value={'definition':{'text':'ORIGINAL_STORED_DEFINITION'}};payloads=[]
        original=tools.invoke;tools.invoke=Mock(wraps=original)
        def decide(payload,**kwargs):
            payloads.append(copy.deepcopy(payload))
            if len(payloads)<=2:return {'action':'TOOL','summary':'Inspect admitted definition','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'down'}}
            return {'action':'VERDICT','summary':'No cause established yet','hypotheses':['not found'],'verdict':'not found','evidence_ids':[tools.path_id]}
        engine.decide=decide;answer=engine.run({'visual':'visual'})
        self.assertEqual(sum(c.args[0]=='definition_of'for c in tools.invoke.call_args_list),1)
        self.assertIn('Already have this as evidence',payloads[2]['feedback']['detail'])
        self.assertTrue(any(e.get('reason')=='SUCCESSFUL_CALL_ALREADY_RETAINED'for e in events))
        retained=answer['case_file']['tool_results'];self.assertIn('ORIGINAL_STORED_DEFINITION',json.dumps(retained))
        self.assertNotIn('ORIGINAL_STORED_DEFINITION',json.dumps(payloads[2]['case_file']))
    def test_successful_raw_evidence_repeat_returns_only_reference_feedback_to_model(self):
        tools,engine,reader,events=fixtures.ToolLoopTests().build(step_cap=6);engine.phase_limit=9;raw='ORIGINAL_RAW_BODY_RETAINED';tools.graph.definition_of.return_value={'definition':{'source':raw}};payloads=[];ids=[];original=tools.invoke;tools.invoke=Mock(wraps=original)
        def decide(payload,**kwargs):
            payloads.append(copy.deepcopy(payload));step=len(payloads)
            if step==1:return {'action':'TOOL','summary':'Inspect definition','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'down'}}
            if step==2:ids.append(next(i for i,r in tools.evidence._values.items()if r['kind']=='GRAPH'))
            if step in(2,3):return {'action':'TOOL','summary':'Read retained evidence','hypotheses':['not found'],'tool':'get_evidence','arguments':{'id':ids[0]}}
            self.assertIn('Already have this as evidence',payload['feedback']['detail']);self.assertNotIn(raw,json.dumps(payload));return {'action':'VERDICT','summary':'Evidence is incomplete','hypotheses':['not found'],'verdict':'not found','evidence_ids':[tools.path_id]}
        engine.decide=decide;answer=engine.run({'visual':'visual'})
        self.assertEqual(sum(c.args[0]=='get_evidence'for c in tools.invoke.call_args_list),1);self.assertIn(raw,json.dumps(answer['case_file']['tool_results']));self.assertIn(raw,json.dumps(tools.evidence.get(ids[0])))

    def test_rejected_verdict_code_measures_first_unmeasured_boundary_and_delivers_checked_finding(self):
        tools,engine,reader,events=fixtures.ToolLoopTests().build(step_cap=18)
        engine.decide=Mock(return_value={'action':'VERDICT','summary':'Refresh seems stale','hypotheses':['refresh stale'],'verdict':'refresh stale','evidence_ids':[tools.path_id]})
        answer=engine.run({'visual':'visual'});self.assertEqual(answer['verdict'],'failed job');self.assertEqual(engine.decide.call_count,1)
        steps=[e for e in events if e.get('event')=='INVESTIGATOR_CODE_NEXT_STEP'];self.assertEqual(steps[0]['tool'],'compare_layers')
        self.assertTrue(all(e['allowed_tools']==[e['tool']]for e in steps));self.assertEqual(reader.call_count,4)
        self.assertEqual(answer['stop_reason'],'EVIDENCE_PROVEN_CODE_FRONTIER')
    def test_phase_limit_prevents_successful_lookup_loop_and_keeps_exact_context(self):
        tools,engine,reader,events=fixtures.ToolLoopTests().build(step_cap=18)
        tools.graph.definition_of.return_value={'definition':{'text':'one definition'}}
        engine.decide=Mock(return_value={'action':'TOOL','summary':'Inspect definition again','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'down'}})
        answer=engine.run({'visual':'visual'});self.assertEqual(answer['verdict'],'failed job');self.assertEqual(engine.decide.call_count,3)
        self.assertTrue(any(e.get('event')=='INVESTIGATOR_PHASE_LIMIT'for e in events))
        for event in events:
            if event.get('event')=='INVESTIGATOR_CODE_NEXT_STEP'and event['tool']=='compare_layers':
                self.assertEqual(event['arguments']['filters'],tools.context);self.assertEqual(event['arguments']['key'],tools.key)
    def test_phase_exhaustion_without_reads_retains_not_found_and_furthest_point(self):
        tools,engine,reader,events=fixtures.ToolLoopTests().build(step_cap=18)
        original=reader.side_effect
        def read(node,context,key):
            if node!='visual':raise TimeoutError('source timed out')
            return original(node,context,key)
        reader.side_effect=read;tools.graph.definition_of.return_value={'definition':{'text':'one definition'}}
        engine.decide=Mock(return_value={'action':'TOOL','summary':'Inspect definition','hypotheses':['not found'],'tool':'definition_of','arguments':{'node':'down'}})
        with patch('investigator.model_transport_retry.backoff',lambda *_:None):answer=engine.run({'visual':'visual'})
        self.assertEqual(answer['verdict'],'not found');self.assertEqual(answer['stop_reason'],'PHASE_PROGRESS_LIMIT');self.assertEqual(answer['furthest_measured_node'],'visual');self.assertEqual(engine.decide.call_count,3)
    def test_old_case_is_read_without_rewriting_and_new_result_is_lossless(self):
        case=CaseFile({'id':'one'});case.observe({'event':'INVESTIGATOR_TOOL','tool':'definition_of','arguments':{'node':'a'},'result':{'status':'OBSERVED','evidence_ids':['evidence:one'],'value':'original'}})
        self.assertEqual(CaseFile.loads(case.dumps()).successful_call('definition_of',{'node':'a'})['result']['value'],'original')
        returned=case.successful_call('definition_of',{'node':'a'});returned['result']['value']='changed'
        self.assertEqual(case.successful_call('definition_of',{'node':'a'})['result']['value'],'original')
        old=case.snapshot();old['version']='ledger-case-v1';old.pop('tool_results');old.pop('phase_state');raw=json.dumps(old)
        self.assertEqual(CaseFile.loads(raw).snapshot(),old)

if __name__=='__main__':unittest.main()
