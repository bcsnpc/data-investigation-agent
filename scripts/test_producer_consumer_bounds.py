"""Every bounded wire field must fit the consuming field, without truncation."""
import copy,unittest
from jsonschema import Draft202012Validator
from investigator import proposal_limits as L,transformation_judgment as judge
from investigator import assessment_support as support,dynamic_reasoning as dynamic
from investigator import adaptive_planner as legacy,question_intake as intake
from investigator import synthesis_narrative as narrative,screenshot_intake as image
from investigator.onboarding import text

class BoundsTests(unittest.TestCase):
    def assert_text(self,schema,bound,consumer):
        self.assertEqual(schema['maxLength'],bound)
        value='x'*(bound-1)+'.'
        Draft202012Validator(schema).validate(value);consumer(value)
        self.assertFalse(Draft202012Validator(schema).is_valid(value+'x'))
        with self.assertRaises(ValueError):consumer(value+'x')

    def test_judge_maximum_survives_actual_process_and_support_consumer(self):
        from test_process_debugging import Adapter
        from investigator.process_debugging import vertical
        for field in ('explanation','limitation'):
            value={'judgment':'EXPLAINS','explanation':'A declared rule explains the difference.', 'limitation':'Intent unknown.'}
            value[field]='x'*(L.ASSESSMENT_DETAIL-1)+'.'
            Draft202012Validator(judge.SCHEMA).validate(value);decoded=judge.validate(value)
            a=Adapter(['report','input'],dict(report=5,input=4),explain=True)
            original=a.evaluate
            def evaluate(*args):
                p=original(*args);p.evidence['test_purpose']='ESTABLISH_BASELINE';return p
            a.evaluate=evaluate
            a.transformation_definition=lambda b:{**decoded,'evidence':{'id':'definition','tool':'context','judgment':decoded}}
            result=vertical(a,'metric',{})
            support.validate(result,{o['id']:o for o in result['_observations']})
            self.assertEqual(result['support']['mechanism'],value['explanation'])
            value[field]+='x'
            self.assertFalse(Draft202012Validator(judge.SCHEMA).is_valid(value))
            with self.assertRaises(ValueError):judge.validate(value)

    def test_every_text_producer_consumer_bound(self):
        props=support.SCHEMA['properties']
        for field in ('mechanism','intent_basis','remaining_test','measure_connection_basis'):
            self.assert_text(props[field],L.ASSESSMENT_DETAIL,lambda v:text(v,L.ASSESSMENT_DETAIL))
        w=dynamic.wire_schema([],asset_handles={})
        variants=w['properties']['next']['anyOf']
        ask=next(v for v in variants if v['properties']['kind']['enum']==['ASK'])
        self.assert_text(ask['properties']['question'],L.QUESTION,lambda v:text(v,L.QUESTION))
        search=next(v for v in variants if v['properties']['kind']['enum']==['LOOKUP'])
        self.assert_text(search['properties']['value'],L.CONTEXT_TEXT,lambda v:text(v,L.CONTEXT_TEXT))
        query=next(v for v in variants if v['properties']['kind']['enum']==['QUERY'])
        self.assert_text(query['properties']['text'],L.QUERY_TEXT,lambda v:text(v,L.QUERY_TEXT))
        self.assertEqual(query['properties']['max_rows']['maximum'],L.QUERY_ROWS)
        _,wire,_=intake.wire_contract({'models':[]})
        self.assert_text(wire['properties']['metric_quote'],L.INTAKE_QUOTE,lambda v:text(v,L.INTAKE_QUOTE))
        self.assert_text(wire['properties']['filters']['items']['properties']['quote'],L.INTAKE_QUOTE,lambda v:text(v,L.INTAKE_QUOTE))
        self.assertEqual(wire['properties']['filters']['items']['properties']['values']['maxItems'],L.FILTER_VALUES)
        n=narrative.schema({'evidence':[]})
        wire=n['properties']['technical_output']['properties']['text']
        self.assertEqual(wire['maxLength'],L.ASSESSMENT_CLAIM)
        for v in ('The definition may multiply matching rows.',):Draft202012Validator(wire).validate(v);text(v,L.ASSESSMENT_CLAIM)
        wire=n['properties']['limitations']['items']['properties']['text']
        self.assertEqual(wire['maxLength'],L.ASSESSMENT_DETAIL)
        for v in ('Intended semantics remain unconfirmed.',):Draft202012Validator(wire).validate(v);text(v,L.ASSESSMENT_DETAIL)
        self.assertEqual(n['properties']['limitations']['maxItems'],L.ASSESSMENT_LIST)

    def test_filling_all_offered_keyed_hypotheses_cannot_exceed_consumer(self):
        for known_count in (0,8,16):
            known=[{'id':'h'+str(i+1),'claim':'prior','status':'OPEN','evidence_ids':[]} for i in range(known_count)]
            observations=[{'id':'receipt'}]
            s=dynamic.wire_schema([],hypotheses=known,observations=observations)
            slots=s['properties']['hypotheses']['properties']
            value={}
            for identity,slot in slots.items():
                item=slot['anyOf'][1]
                value[identity]={'claim':'x'*L.HYPOTHESIS_CLAIM,'status':item['properties']['status']['enum'][0],'evidence_ids':['receipt']}
            wire={'next':{'kind':'ASK','question':'Which scope?'},'hypotheses':value}
            Draft202012Validator(s).validate(wire)
            converted=dynamic.from_wire(wire)
            legacy.validate({k:converted[k] for k in legacy.SCHEMA['required']},{'hypotheses':known,'observations':observations,'candidates':[]})
            self.assertLessEqual(len(value),L.HYPOTHESIS_UPDATES)

    def test_screenshot_and_legacy_draft_bounds_are_in_wire(self):
        import ticket_planner
        value={'visible_text':'x'*L.SCREENSHOT_TEXT,'readable':True,'uncertainties':['x'*L.SCREENSHOT_UNCERTAINTY]*L.SCREENSHOT_UNCERTAINTIES}
        Draft202012Validator(image.SCHEMA).validate(value);image.validate(value)
        value['visible_text']+='x';self.assertFalse(Draft202012Validator(image.SCHEMA).is_valid(value))
        self.assertEqual(ticket_planner.SCHEMA['properties']['questions']['maxItems'],L.LEGACY_PLAN_QUESTIONS)
        self.assertEqual(ticket_planner.SCHEMA['properties']['questions']['items']['maxLength'],L.QUESTION)

if __name__=='__main__':unittest.main()
