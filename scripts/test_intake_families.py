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
from investigator.question_intake import azure_resolve,validate
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
            return httpx.Response(200,json=case['response'])
        return patch('openai.DefaultHttpxClient',side_effect=lambda **kw:DefaultHttpxClient(transport=httpx.MockTransport(transport),**kw))

    def test_twelve_recorded_payloads_and_responses_roundtrip(self):
        self.assertEqual({c['family'] for c in self.data['cases'] if c['expected_action']=='PROPOSE'},set('ABCDEFGHI'))
        for case in self.data['cases']:
            with self.subTest(case=case['id']):
                requests=[]
                with self.provider(case,requests):decision,_=azure_resolve(copy.deepcopy(case['payload']))
                validate(decision,case['payload'])
                self.assertEqual(requests,[case['request']])
                self.assertEqual(decision,case['decision'])
                self.assertTrue(score(case,decision)['passed'])

    def test_all_nine_families_reach_reviewed_investigation_and_a_read(self):
        for case in self.data['cases']:
            if case['expected_action']!='PROPOSE':continue
            with self.subTest(family=case['family']):
                helper=IntakeFixture();helper.setUp()
                try:
                    requests=[]
                    with self.provider(case,requests):
                        saved=helper.workspace.intake.resolve({'text':case['payload']['text'],'request_key':'family-'+case['id'],'parent_id':None})
                    self.assertEqual(saved['status'],'PROPOSED',saved.get('error'))
                    self.assertIsNone(saved['question'])
                    proposal=saved['proposal']
                    review=helper.workspace.preview({k:proposal[k] for k in ('model_id','measure_id','filters','dimension_ids')} |
                        {'symptom':saved['text'],'predecessor':None,'intake_id':saved['id']})
                    session=helper.workspace.start(review['id'])
                    helper.workspace.run_once()
                    state=helper.agent.get(session['id'])
                    self.assertNotEqual(state['status'],'HELD')
                    self.assertEqual(state['trajectory_metrics']['reads_per_run'],1)
                    self.assertIn('['+case['metric']+']',helper.helper.native_calls[0]['query'])
                    self.assertEqual(state['envelope']['symptom'],case['payload']['text'])
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
