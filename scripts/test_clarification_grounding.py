import copy,unittest,json
from pathlib import Path
from investigator.clarification_grounding import render,label
from investigator.onboarding import Conflict
from test_agent_intake_tools import IntakeToolTests
class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.h=IntakeToolTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.posted=[];self.h.tools.comment_port=lambda body:self.posted.append(body) or {'comment_id':'posted'}
    def test_both_false_duplicate_report_questions_cannot_be_posted(self):
        questions=[r['question'] for r in json.loads((Path(__file__).parent/'fixtures/round_fourteen/false-duplicate-report-questions.json').read_text(encoding='utf8'))]
        for text in questions:
            with self.subTest(question=text),self.assertRaises(Exception):self.h.tools.call('ask_user',{'question':text})
        self.assertEqual(self.posted,[])
    def test_grounded_question_choices_are_visible_names_with_catalog_receipt(self):
        result=self.h.tools.call('ask_user',{'field':'PAGE','report_id':'report'})
        self.assertEqual(result['question'],'Which page are you asking about?')
        self.assertNotIn('page',result['choices']);self.assertNotIn('report',result['choices'])
        self.assertEqual(result['grounding']['choices'][0]['identity'],'page')
        self.assertEqual(result['provenance']['kind'],'RETAINED_DEFINITIONS')
    def test_no_ids_or_unnamed_fallback_choice(self):
        with self.assertRaises(Conflict):label(['00000000-0000-0000-0000-000000000001'])
        for v in self.h.catalog['models'][0]['visuals']:v['page_names']=[]
        with self.assertRaises(Conflict):self.h.tools.call('ask_user',{'field':'PAGE','report_id':'report'})
        self.assertEqual(self.posted,[])
    def test_fixed_page_must_not_be_requested_again(self):
        self.h.tools._fixed={'page_id':'page','report_id':'report'}
        with self.assertRaisesRegex(Conflict,'already picked'):self.h.tools.call('ask_user',{'field':'PAGE'})
        self.assertEqual(self.posted,[])
