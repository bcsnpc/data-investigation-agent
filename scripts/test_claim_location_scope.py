import copy,unittest
from types import SimpleNamespace
from investigator import claim_facts as f,claim_clarification as p
from investigator.claim_intake import ClaimIntake
from investigator.onboarding import digest
from test_claim_policy_repair import CAT


def scope(kind,quote):return f.fact('scope',{'kind':kind,'phrase':quote},{'kind':'TOKEN_SPAN','document_id':'doc','span':{'start':0,'end':len(quote),'quote':quote}},authority='USER_TEXT')


class LocationScopeTests(unittest.TestCase):
    def planner(self,facts,text='',catalog=None):
        obj=object.__new__(ClaimIntake);obj.workspace=SimpleNamespace()
        body={'claim':{'facts':facts,'selected_binding':None,'screenshot_candidates':[]},'questions':[],'history':[],
            'documents':[{'hash':'doc','request':{'text':text}}]}
        return obj._plan(body,catalog or copy.deepcopy(CAT))
    def test_report_and_page_mentions_are_location_not_extent(self):
        for kind,quote in [('PAGE','Overview page'),('REPORT','Activity report')]:
            original=scope(kind,quote);derived=f.location_fact(original,'On '+quote+', Quantity shows 16.')
            self.assertEqual(derived['field'],'location')
            self.assertEqual(original['value']['kind'],kind)
            self.assertNotIn('kind',derived['value'])
    def test_explicit_whole_page_request_keeps_extent(self):
        for text in ('Everything on this page is wrong.','The whole page is wrong.','Is this page up to date?'):
            self.assertIsNone(f.location_fact(scope('PAGE','this page'),text),text)
        self.assertIsNotNone(f.location_fact(scope('PAGE','this page'),'Is Quantity on this page wrong?'))
    def test_selected_form_container_does_not_assert_whole_page(self):
        original=f.fact('scope',{'kind':'PAGE','report_id':'report','page_id':'page'},
            {'kind':'RETAINED_FORM_PICKERS'},authority='USER_SUBMITTED')
        self.assertEqual(f.location_fact(original)['value'],{'report_id':'report','page_id':'page'})
        explicit=f.fact('scope',{'kind':'PAGE','report_id':'report','page_id':'page'},
            {'kind':'SUBMITTED_POINTER'},authority='USER_SUBMITTED')
        self.assertIsNone(f.location_fact(explicit))
    def test_unknown_extent_with_known_location_may_ask_extent(self):
        p.validate_question({'settled':{'scope':{'kind':'UNKNOWN','report_id':'report'}},'conflicts':[]},{'field':'scope'})
        with self.assertRaisesRegex(ValueError,'REASKS'):p.validate_question({'settled':{'scope':{'kind':'PAGE','report_id':'report'}},'conflicts':[]},{'field':'scope'})
    def test_same_metric_multiple_visuals_plans_checks_never_selects_representative(self):
        catalog=copy.deepcopy(CAT);catalog['models'][0]['visuals'][1]['page_id']='page';catalog['models'][0]['visuals'][1]['page_names']=['Overview']
        facts=f.submitted({'metric_phrase':'Quantity','direction':'DIFFERENT','comparator':'NONE','location':{'report_id':'report','page_id':'page'}},'input')
        result=self.planner(facts,catalog=catalog)
        self.assertEqual(result['status'],'AWAITING_CONFIRMATION')
        self.assertEqual(result['claim']['settled']['scope']['kind'],'METRIC')
        self.assertEqual(result['claim']['selected_binding']['target_ids'],['card','other'])
        self.assertEqual(result['planning_request']['kind'],'METRIC_VISUAL_CHECKS')
        self.assertEqual(result['planning_request']['status'],'AWAITING_CONFIRMED_CANDIDATE_CHECKS')
        self.assertNotIn('representative_target',result)
    def test_unidentified_metric_still_asks_and_values_are_not_fabricated(self):
        facts=f.submitted({'metric_phrase':'Unknown business metric','direction':'DIFFERENT','comparator':'NONE','location':{'report_id':'report','page_id':'page'}},'input')
        result=self.planner(facts)
        self.assertEqual(result['status'],'CLARIFYING')
        self.assertEqual(result['questions'][0]['field'],'binding')
    def test_different_pages_remain_a_location_question(self):
        facts=f.submitted({'metric_phrase':'Quantity','direction':'DIFFERENT','comparator':'NONE'},'input')
        result=self.planner(facts)
        self.assertEqual(result['questions'][0]['field'],'page')
    def test_model_only_measure_never_requires_a_report(self):
        catalog=copy.deepcopy(CAT);catalog['models'][0]['visuals']=[];catalog['models'][0]['reports']=[]
        facts=f.submitted({'metric_phrase':'Quantity','direction':'DEFINITION','comparator':'NONE',
            'scope':{'kind':'METRIC','model_id':'model'}},'input')
        result=self.planner(facts,catalog=catalog)
        self.assertEqual(result['status'],'AWAITING_CONFIRMATION')
        self.assertEqual(result['claim']['selected_binding']['measure_id'],'quantity')
        self.assertNotIn('planning_request',result)
        self.assertNotIn('report_id',result['claim']['settled']['scope'])
    def test_candidate_port_requires_validator_before_accepting_bindings(self):
        obj=object.__new__(ClaimIntake)
        obj.workspace=SimpleNamespace(claim_candidate_checks=lambda body,catalog:{'candidate_bindings':[{'model_id':'invented'}]})
        facts=f.submitted({'metric_phrase':'Quantity','direction':'DIFFERENT','comparator':'NONE',
            'location':{'report_id':'report','page_id':'page'}},'input')
        body={'claim':{'facts':facts,'selected_binding':None,'screenshot_candidates':[]},'questions':[],'history':[],'documents':[]}
        with self.assertRaisesRegex(ValueError,'validation is required'):obj._plan(body,copy.deepcopy(CAT))
    def test_candidate_inventory_does_not_guess_an_unidentified_metric(self):
        facts=f.submitted({'direction':'DIFFERENT','comparator':'NONE','location':{'report_id':'report','page_id':'page'}},'input')
        value=f.fact('observation',{'role':'OBSERVED','figure':{'state':'NUMBER','value':'16','precision':0}},
            {'kind':'SUBMITTED_POINTER'},authority='USER_SUBMITTED')
        result=self.planner(facts+[value])
        self.assertEqual(result['status'],'CLARIFYING')
        self.assertEqual(result['questions'][0]['field'],'metric')
        self.assertTrue(result['planning_request']['groups'])
        self.assertFalse(result['claim']['candidate_bindings'])
    def test_explicit_visual_identity_remains_fixed(self):
        facts=f.submitted({'metric_phrase':'Quantity','direction':'DIFFERENT','comparator':'NONE',
            'scope':{'kind':'VISUALS','report_id':'report','page_id':'page','visual_ids':['card']}},'input')
        result=self.planner(facts)
        self.assertEqual(result['claim']['selected_binding']['target_ids'],['card'])
        self.assertEqual(result['claim']['settled']['scope']['visual_ids'],['card'])


if __name__=='__main__':unittest.main()
