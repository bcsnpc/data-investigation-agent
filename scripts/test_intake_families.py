"""Recorded synthetic intake payloads, plus actual scope-review/start admission."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import httpx
from openai import DefaultHttpxClient
from intake_regression_fixture import IntakeFixture
from investigator import planner_recording
# Explicit historical wire-v2 decoder; current producer covered by test_intake_extraction.
from investigator.question_intake import azure_resolve_legacy as azure_resolve,validate
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/unknown_domain'))
from score_intake import score

FIXTURE=Path(__file__).parent/'fixtures/intake-nine-families.json'


class IntakeFamilyTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(FIXTURE.read_text(encoding='utf-8'))
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.addCleanup(patch.stopall)
        patch.object(planner_recording,'ROOT',Path(self.temp.name)).start()
        patch.dict(os.environ,{'INVESTIGATOR_RECORD_PLANNER':'1',
            'AZURE_OPENAI_ENDPOINT':'https://offline.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT':'offline-fixture','AZURE_OPENAI_API_KEY':'offline-placeholder-credential'}).start()
        patch('socket.socket.connect',side_effect=AssertionError('Network forbidden')).start()
        patch('socket.getaddrinfo',side_effect=AssertionError('DNS forbidden')).start()

    def provider(self,case,requests):
        def transport(request):
            requests.append(json.loads(request.content))
            current_schema=requests[-1]['tools'][0]['parameters']
            # Synthetic v1 fixtures remain immutable; adapt only the test response
            # serialization to v2. Historical live tapes are never rewritten.
            response=copy.deepcopy(case['response'])
            for output in response.get('output',[]):
                if output.get('type')!='function_call':continue
                value=json.loads(output['arguments'])
                shape=value.pop('ticket_shape');mode=value.pop('comparison_mode')
                value['triage']=shape+':'+mode if shape is not None else None
                value['target_request']=None
                value['report_quote']=None
                value['question_kind']=None if value['action']=='ASK' else {'kind':'FIGURE_DIFFERENCE','source':{'quote':case['payload']['text']}}
                value['value_mentions']=[{'role':'SELECTION','source':{'quote':f['quote']}} for f in value['filters']]
                value['reported_candidates']=[] # Explicit new synthetic response; the v1 fixture is unchanged.
                if 'visual_request' in current_schema['required']:
                    value['visual_request']=None # These synthetic cases name a model, not a report visual.
                output['arguments']=json.dumps(value)
            return httpx.Response(200,json=response)
        return patch('openai.DefaultHttpxClient',side_effect=lambda **kw:DefaultHttpxClient(transport=httpx.MockTransport(transport),**kw))

    def test_twelve_recorded_payloads_and_responses_roundtrip(self):
        self.assertEqual({c['family'] for c in self.data['cases'] if c['expected_action']=='PROPOSE'},set('ABCDEFGHI'))
        for case in self.data['cases']:
            with self.subTest(case=case['id']):
                requests=[]
                with self.provider(case,requests):decision,_=azure_resolve(copy.deepcopy(case['payload']))
                validate(decision,case['payload'])
                self.assertNotIn('report_binding',decision)
                self.assertEqual(len(requests),1)
                # Golden context and all other request settings stay byte-exact.
                # Only wire triage serialization and its field-name instructions change.
                expected=copy.deepcopy(case['request'])
                expected['instructions']=expected['instructions'].replace(
                    'ticket_shape and comparison_mode are null','triage is null').replace(
                    'both triage fields are required','triage is required')
                from investigator.question_intake import FIGURE_INSTRUCTIONS,TARGET_INSTRUCTIONS,REPORT_INSTRUCTIONS,DESCRIPTOR_INSTRUCTIONS,QUESTION_KIND_INSTRUCTIONS,SCOPE_INSTRUCTIONS,VALUE_ROLE_INSTRUCTIONS
                expected['instructions']=expected['instructions'].replace('Quotes are provenance,','Repeated measure, column and selection quotes identify the same referent; every occurrence is retained. Reported-figure quotes alone must be unique; include longer verbatim context if necessary. Never emit offsets. Quotes are provenance,')
                expected['instructions']+=FIGURE_INSTRUCTIONS+TARGET_INSTRUCTIONS+REPORT_INSTRUCTIONS+DESCRIPTOR_INSTRUCTIONS+QUESTION_KIND_INSTRUCTIONS+SCOPE_INSTRUCTIONS+VALUE_ROLE_INSTRUCTIONS
                schema=expected['tools'][0]['parameters']
                for key in ('ticket_shape','comparison_mode'):
                    schema['properties'].pop(key);schema['required'].remove(key)
                schema['properties']['triage']={'type':['string','null'],
                    'enum':['MISMATCH_COMPLAINT:VERTICAL','MISMATCH_COMPLAINT:HORIZONTAL','BUSINESS_QUESTION:NONE',None],
                    'description':'Ticket shape and comparison mode as one valid pair; null only for ASK.'}
                schema['required'].append('triage')
                from investigator.question_intake import QUOTE_SCHEMA
                from investigator.selection_descriptor import schema as descriptor_schema
                from investigator.numeral_roles import wire_schema
                schema['properties']['reported_candidates']=wire_schema(QUOTE_SCHEMA)
                schema['required'].insert(schema['required'].index('triage'),'reported_candidates')
                schema['properties']['target_request']={'anyOf':[{'type':'null'},
                    {'type':'object','additionalProperties':False,'properties':{'value_source':QUOTE_SCHEMA,
                     'column_source':{'anyOf':[{'type':'null'},QUOTE_SCHEMA]},
                     'descriptor':descriptor_schema(QUOTE_SCHEMA)},'required':['value_source','column_source','descriptor']}]}
                from investigator import proposal_limits as limits
                schema['properties']['report_quote']={'type':['string','null'],'minLength':1,'maxLength':limits.INTAKE_QUOTE}
                index=schema['required'].index('reported_candidates')
                schema['required'][index:index]=['report_quote','target_request']
                # Migrate only producer field bounds from the immutable v1 tape.
                from investigator import proposal_limits as limits
                for key,bound in (('metric_quote',limits.INTAKE_QUOTE),('question',limits.QUESTION)):
                    schema['properties'][key].update(minLength=1,maxLength=bound)
                item=schema['properties']['filters']['items']['properties']
                item['quote'].update(minLength=1,maxLength=limits.INTAKE_QUOTE)
                item['values'].update(minItems=1,maxItems=limits.FILTER_VALUES)
                scalar=item['values']['items']['anyOf']
                next(x for x in scalar if x['type']=='string')['maxLength']=limits.FILTER_STRING
                next(x for x in scalar if x['type']=='integer').update(minimum=-limits.EXACT_INTEGER,maximum=limits.EXACT_INTEGER)
                from investigator.question_intake import wire_contract
                wire,current_schema,_=wire_contract(case['payload'])
                schema['properties']['value_mentions']=current_schema['properties']['value_mentions']
                schema['required'].insert(schema['required'].index('report_quote'),'value_mentions')
                schema['properties']['question_kind']=current_schema['properties']['question_kind']
                # Explicit synthetic v1 -> current grouping provenance migration.
                # Original fixtures/tapes remain unchanged; none requests grouping.
                schema['properties']['dimension_ids']=current_schema['properties']['dimension_ids']
                schema['required'].insert(schema['required'].index('report_quote'),'question_kind')
                # Current synthetic request projection uses the producer's
                # canonical ordering; the immutable recorded fixture stays intact.
                expected['input']=json.dumps(wire,sort_keys=True)
                self.assertEqual(requests,[expected])
                self.assertEqual(decision['dimension_quotes'],[])
                self.assertEqual({k:v for k,v in decision.items() if k not in ('report_binding','question_kind','dimension_quotes','value_mentions')},{**case['decision'],'reported_figure':{'state':'UNSPECIFIED'}})
                self.assertTrue(score(case,decision)['passed'])

    def test_model_anchored_figure_questions_need_no_manufactured_report_binding(self):
        # The immutable responses are adapted to FIGURE_DIFFERENCE, not visual
        # reproduction. They can reach review without inventing report context.
        for case in self.data['cases']:
            if case['expected_action']!='PROPOSE':continue
            with self.subTest(family=case['family']):
                helper=IntakeFixture();helper.setUp()
                try:
                    requests=[]
                    with self.provider(case,requests):
                        saved=helper.workspace.intake.resolve({'text':case['payload']['text'],'request_key':'family-'+case['id'],'parent_id':None})
                    self.assertEqual(saved['status'],'PROPOSED',saved.get('error'))
                    self.assertEqual(helper.helper.native_calls,[])
                    self.assertNotIn('report_binding',saved['proposal'])
                finally:helper.doCleanups()

    def test_metadata_clarifications_are_regression_failures(self):
        for case in self.data['cases']:
            if case['expected_action']!='PROPOSE':continue
            changed=dict(case['decision'],action='ASK',question='Please confirm the definition or identify the refresh pipeline.')
            self.assertEqual(score(case,changed),{'passed':False,'reason':'UNNECESSARY_CLARIFICATION'})
        for case in self.data['cases']:
            if case['expected_action']!='ASK':continue
            changed=copy.deepcopy(case);changed['payload']['user_context']={case['missing_fact']:'provided by user'}
            self.assertEqual(score(changed,case['decision'])['reason'],'FACT_ALREADY_SUPPLIED')

    def test_material_questions_name_facts_metadata_does_not_supply(self):
        material=[c for c in self.data['cases'] if c['expected_action']=='ASK']
        self.assertEqual({c['missing_fact'] for c in material},{'user_date_boundaries','user_visual_selections','user_report_choice'})
        for case in material:
            self.assertNotIn(case['missing_fact'],case['payload'].get('user_context',{}))
            if case['missing_fact']=='user_report_choice':
                self.assertEqual(len(case['payload']['models']),2)
            # Exact questions are recorded; vague generic holds must fail this gate.
            self.assertEqual(score(case,dict(case['decision'],question='Please clarify.'))['reason'],'MATERIAL_FACT_NOT_NAMED')


if __name__=='__main__':unittest.main()
