import copy
import unittest
from investigator.smart_intake_eval import answer_batch, score
from investigator.onboarding import digest


def case():
    return {'id':'sealed','class':'visual','text':'A card shows 16.', 'should_hold':False,
            'expected':{'status':'PROPOSED','target_id':'card','cell_mode':'UNGROUPED',
                        'figure_state':'NUMBER','figure_value':'16','figure_precision':{'state':'EXACT'}}}


def offer(field, values):
    q={'id':field,'field':field,'question':'Choose','choices':[
        {'id':str(i),'label':str(i),'highlight':None} for i in range(len(values))]}
    return {'questions':[q],'choice_values':{digest(q)+'/'+str(i):v for i,v in enumerate(values)}}


class SmartIntakeEvalTests(unittest.TestCase):
    def test_only_sealed_target_and_exact_figure_can_be_answered(self):
        c=case();values=[{'target_id':target,'mode':'UNGROUPED',
            'figure_source':{'start':13,'end':15,'quote':'16'}} for target in ('wrong-card','card')]
        # Exact figure spans belong to the source ticket, not catalog labels.
        start=c['text'].index('16')
        for value in values:value['figure_source'].update(start=start,end=start+2)
        result=answer_batch(offer('NUMBER',values),c,[])
        self.assertEqual(result['answers'],[{'question_id':'NUMBER','choice_id':'1'}])
        self.assertEqual(result['abstentions'],[])
        c['expected']['target_id']=None
        result=answer_batch(offer('NUMBER',values),c,[])
        self.assertEqual(result['answers'],[])

    def test_ambiguous_sealed_record_never_volunteers_a_target(self):
        c=case();c['should_hold']=True
        v={'target_id':'card','mode':'UNGROUPED','figure_source':None}
        self.assertEqual(answer_batch(offer('NUMBER',[v]),c,[])['answers'],[])

    def test_report_choices_use_complete_model_visual_inventory(self):
        c=case();models=[{'visuals':[{'target_id':'card','report_id':'report'}]}]
        values=[{'report_id':'other','page_id':None},{'report_id':'report','page_id':None},
                {'report_id':'report','page_id':'unmentioned-page'}]
        result=answer_batch(offer('REPORT_PAGE',values),c,models)
        self.assertEqual(result['answers'],[{'question_id':'REPORT_PAGE','choice_id':'1'}])

    def test_no_comparator_does_not_become_looks_wrong(self):
        c=case();c['text']='Explain the calculation.'
        c['expected']['question_kind']='DERIVED_CALCULATION'
        result=answer_batch(offer('COMPARISON',[{'route':'LOOKS_WRONG'}]),c,[])
        self.assertEqual(result['answers'],[])

    def test_sealed_target_supplies_its_actual_page_without_inventing_a_user_quote(self):
        c=case();models=[{'visuals':[{'target_id':'card','report_id':'report','page_id':'native-page'}]}]
        values=[{'report_id':'report','page_id':None},
                {'report_id':'report','page_id':'other-page'},
                {'report_id':'report','page_id':'native-page'}]
        result=answer_batch(offer('REPORT_PAGE',values),c,models)
        self.assertEqual(result['answers'],[{'question_id':'REPORT_PAGE','choice_id':'2'}])
        self.assertEqual(c['text'],'A card shows 16.')

    def test_duplicate_target_bindings_cannot_supply_a_container(self):
        c=case();visual={'target_id':'card','report_id':'report','page_id':'page'}
        models=[{'visuals':[copy.deepcopy(visual)]},{'visuals':[copy.deepcopy(visual)]}]
        result=answer_batch(offer('REPORT_PAGE',[{'report_id':'report','page_id':'page'}]),c,models)
        self.assertEqual(result['answers'],[])
        self.assertEqual(result['abstentions'][0]['matches'],0)

    def test_missing_or_held_target_cannot_supply_a_page(self):
        c=case();models=[{'visuals':[{'target_id':'card','report_id':'report','page_id':'page'}]}]
        choices=offer('REPORT_PAGE',[{'report_id':'report','page_id':'page'}])
        c['should_hold']=True
        self.assertEqual(answer_batch(choices,c,models)['answers'],[])
        c['should_hold']=False;c['expected']['target_id']=None
        self.assertEqual(answer_batch(choices,c,models)['answers'],[])

    def test_freshness_wording_can_answer_without_inventing_a_number(self):
        c=case();c['text']='Is it up to date?';c['expected']['question_kind']='FRESHNESS'
        result=answer_batch(offer('COMPARISON',[{'route':'STALE'}]),c,[])
        self.assertEqual(len(result['answers']),1)

    def test_adoption_does_not_hide_wrong_cell_or_claim_a_harmful_error_pass(self):
        c=case();actual={**c['expected'],'target_id':'wrong-card'}
        r={'id':c['id'],'case_hash':digest(c),'intake_record':actual,'ticket_state':'NEW',
           'adopted':True,'rounds':0,'questions':0}
        result=score([c],[r])
        self.assertEqual(result['rows'][0]['consequential_differences'],['target_id'])
        self.assertFalse(result['rows'][0]['original_record_match'])
        self.assertEqual(result['gate'],'UNGRADABLE')

    def test_same_cell_name_cannot_hide_a_wrong_model_measure_or_selection(self):
        c=case();c['expected'].update(model_id='model',measure_id='measure',selection_value='North')
        for field in ('model_id','measure_id','selection_value'):
            actual={**c['expected'],field:'wrong'}
            row={'id':c['id'],'case_hash':digest(c),'intake_record':actual,'ticket_state':'NEW',
                 'adopted':True,'rounds':0,'questions':0}
            result=score([c],[row])
            self.assertEqual(result['rows'][0]['consequential_differences'],[field])
            self.assertEqual(result['gate'],'UNGRADABLE')

    def test_waiting_source_refusal_is_not_a_settled_ticket(self):
        c=case();c['should_hold']=True;c['expected']={'status':'HELD','error':'TARGET_AMBIGUOUS'}
        r={'id':c['id'],'case_hash':digest(c),'intake_record':copy.deepcopy(c['expected']),
           'ticket_state':'CLARIFYING','adopted':False,'rounds':1,'questions':2}
        result=score([c],[r]);self.assertFalse(result['rows'][0]['settled'])
        self.assertEqual(result['per_class']['visual']['mean_questions'],2)
        r['ticket_state']='HELD'
        self.assertFalse(score([c],[r])['rows'][0]['settled_within_one_round'])
        r['ticket_history']=[{'from':'NEW','to':'HELD','actor':'AGENT',
                              'detail':{'reason':'TARGET_AMBIGUOUS'}}]
        self.assertTrue(score([c],[r])['rows'][0]['settled_within_one_round'])

    def test_unavailable_user_reply_is_paused_not_a_successful_one_round_settlement(self):
        c=case();c['should_hold']=True;c['expected']={'status':'HELD','error':'TARGET_AMBIGUOUS'}
        r={'id':c['id'],'case_hash':digest(c),'intake_record':copy.deepcopy(c['expected']),
           'ticket_state':'HELD','adopted':False,'rounds':1,'questions':1,
           'ticket_history':[{'from':'CLARIFYING','to':'HELD','actor':'USER',
                              'detail':{'reason':'USER_INFORMATION_UNAVAILABLE'}}]}
        result=score([c],[r]);row=result['rows'][0]
        self.assertTrue(row['original_record_match'])
        self.assertTrue(row['waiting_on_user'])
        self.assertFalse(row['settled_within_one_round'])
        self.assertFalse(row['settled'])

    def test_seals_and_complete_consumer_records_are_required(self):
        c=case();r={'id':c['id'],'case_hash':'changed','intake_record':c['expected'],
                    'ticket_state':'NEW','adopted':True,'rounds':0,'questions':0}
        with self.assertRaises(ValueError):score([c],[r])
        r['case_hash']=digest(c);r['intake_record']=None
        with self.assertRaises(ValueError):score([c],[r])
        result=score([c],[])
        self.assertEqual(result['status'],'INCOMPLETE')
        self.assertFalse(result['rows'][0]['settled'])


if __name__=='__main__':unittest.main()
