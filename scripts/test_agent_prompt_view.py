import copy
import unittest
from types import SimpleNamespace
from investigator.agent_loop import AgentLoop
from investigator.agent_prompt_view import view, described_schema
from investigator.agent_provider import request_bound
from investigator.estate_manifest import SCHEMA
from jsonschema import Draft202012Validator


class PromptViewTests(unittest.TestCase):
    def test_specific_rejections_survive_intervening_fetch_in_compact_transcript(self):
        rejection={'event':'CLAIM_REJECTED','reason':'DELIVERY_VALIDATION_FAILED',
            'error_type':'ValueError','validation':{'stage':'TERMINAL_SUPPORT_OR_DELIVERY',
            'message':'BUSINESS_QUESTION requires flow_consistency evidence','claim_indices':[1,2]}}
        events=[rejection,{'event':'EVIDENCE_FETCH','evidence_id':'existing','receipt_id':'fetch'}]
        original=copy.deepcopy(events)
        compact=view(events,{}, {})
        self.assertEqual(compact['transcript'][0]['validation'],rejection['validation'])
        self.assertEqual(events,original)

    def test_outcome_guidance_is_derived_from_consumer_roles(self):
        from unittest.mock import patch
        with patch.dict('investigator.process_outcomes.REQUIRED_ROLES',{'BUSINESS_QUESTION':('future_role',)}):
            schema=described_schema({},['BUSINESS_QUESTION'],{})
        outcome=next(c['properties']['outcome'] for c in schema['anyOf'] if 'outcome' in c['properties'])
        self.assertIn('future_role',outcome['description'])
        self.assertNotIn('flow_consistency',outcome['description'])
        self.assertEqual(outcome['enum'],['BUSINESS_QUESTION'])
    def test_compact_input_fetch_and_delivery_preserve_original_evidence(self):
        full = {'status': 'OBSERVED', 'evidence_ids': ['native:1'], 'rows': [{'value': 'retained-detail'}]}
        decisions = iter([
            {'action':'TOOL','summary':'Read.','tool':'lookup','arguments':{}},
            {'action':'TOOL','summary':'Inspect.','tool':'get_evidence','arguments':{'id':'native:1'}},
            {'action':'ANSWER','summary':'Deliver.','outcome':'OK','claims':[{'text':'Checked.','evidence_ids':['native:1']}]}
        ])
        calls=[]; saved=[]; delivered=[]
        def decide(payload, **kw): calls.append(copy.deepcopy(payload)); return next(decisions)
        def persist(event): saved.append(copy.deepcopy(event)); return 'event:'+str(len(saved))
        def deliver(decision, evidence, **kw):
            delivered.append(evidence); return {'validated':True,'outputs':{'text':'Checked.'}}
        loop=AgentLoop(tools={'lookup':lambda:copy.deepcopy(full)}, schemas={'lookup':{'type':'object','properties':{},'additionalProperties':False}},
                       decide=decide,persist=persist,validate_delivery=deliver,outcomes=['OK'],admit=lambda *a:None,clock=lambda:0)
        result=loop.run({},fixed_facts={},context_id='context')
        self.assertEqual(result['status'],'COMPLETED')
        self.assertNotIn('retained-detail', str(calls[1]))
        self.assertEqual(calls[2]['fetched_evidence']['result'], full)
        self.assertEqual(delivered[0]['native:1']['result'], full)
        self.assertEqual(saved[2]['result'], full)
        self.assertEqual(saved[4]['evidence']['result'], full)

    def test_unknown_fetch_refuses_without_native_call(self):
        saved=[]
        loop=AgentLoop(tools={},schemas={},decide=lambda *a,**k:{'action':'TOOL','summary':'Inspect.','tool':'get_evidence','arguments':{'id':'invented'}},
            persist=lambda e:(saved.append(e) or 'receipt'),validate_delivery=lambda *a,**k:None,outcomes=[],admit=lambda *a:None,step_cap=1,clock=lambda:0)
        result=loop.run({},fixed_facts={},context_id='context')
        self.assertEqual(result['evidence_ids'],[])
        self.assertEqual(saved[2]['reason'],'UNKNOWN_EVIDENCE_ID')

    def test_only_admitted_registry_identifiers_enter_argument_descriptions(self):
        events=[{'event':'TOOL_RESULT','tool':'resolve_ticket','result':{'status':'UNRESOLVED','target_registry':{'wrong':{}},'evidence_ids':['e0']}},
                {'event':'TOOL_RESULT','tool':'resolve_ticket','result':{'status':'INTAKE_ADMITTED','target_registry':{'target:actual':{'scope_id':'scope:actual'}},'scope_registry':{'scope:actual':{}},'evidence_ids':['e1']}}]
        ids=view(events,{}, {})['valid_identifiers']
        schema=described_schema({'probe':{'type':'object','properties':{'target_id':{'type':'string'},'scope_id':{'type':'string'}},'required':['target_id','scope_id'],'additionalProperties':False}},[],ids)
        text=str(schema)
        self.assertIn('target:actual',text); self.assertIn('scope:actual',text); self.assertNotIn('wrong',text)
        self.assertEqual(ids['target_id'],['target:actual']); self.assertEqual(ids['scope_id'],['scope:actual'])

    def test_compact_summary_keeps_quantity_and_order_without_receipt_body(self):
        full={'status':'AVAILABLE','evidence_ids':['read'],'data':{'layer':'layer:one','value_state':'MEASURED','value':{'quantity':7},'evidence':{'query':'private full statement'}}}
        event={'event':'TOOL_RESULT','tool':'probe_layer','result':full}
        compact=view([event],{}, {}, {'report_id':'report:picked','page_id':'page:picked'})
        self.assertEqual(compact['transcript'][0]['summary']['value'],{'quantity':7})
        self.assertNotIn('private full statement',str(compact))
        self.assertEqual(compact['valid_identifiers']['report_id'],['report:picked'])
        self.assertEqual(full['data']['evidence']['query'],'private full statement')

    def test_agent_bound_override_does_not_change_pipeline_profile(self):
        profile={'max_payload_characters':32000}
        runtime=SimpleNamespace(config={'_estate':{'investigation':{'mode':'AGENT','input_characters_per_request':150000}}},generation_options=profile)
        self.assertEqual(request_bound(runtime),150000)
        self.assertEqual(profile['max_payload_characters'],32000)
        runtime.config['_estate']['investigation']={'mode':'PIPELINE','input_characters_per_request':150000}
        with self.assertRaisesRegex(ValueError,'AGENT_REQUEST_BOUND_MODE'): request_bound(runtime)
        node=Draft202012Validator(SCHEMA['properties']['investigation'])
        self.assertTrue(node.is_valid({'mode':'AGENT','step_cap':25,'wall_seconds':900,'input_characters_per_request':150000}))
        self.assertFalse(node.is_valid({'mode':'PIPELINE','step_cap':25,'wall_seconds':900,'input_characters_per_request':150000}))


if __name__=='__main__': unittest.main()
