import copy
import unittest
from investigator import form_candidates
from investigator.onboarding import Conflict
import test_form_controller


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.f=test_form_controller.FormControllerTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.models=self.f.catalog['models'];self.request={**self.f.request,'target_id':None}
        other=copy.deepcopy(self.models[0]['visuals'][0]);other['target_id']='second';self.models[0]['visuals'].append(other)

    def reader(self,values):
        return lambda c:{'status':'OBSERVED','complete':True,'value':values[c['target_id']],
            'receipt_id':'receipt-'+c['target_id'],'query_hash':'a'*64,'execution_surface':{'engine':'engine'},
            'attestation':{'consistency':'MATCHED'}}

    def test_unique_value_match_without_question_and_original_input_preserved(self):
        self.f.workspace.form_candidate_reader=self.reader({'card':'16','second':'17'})
        saved=self.f.workspace.forms.submit(self.request)
        self.assertEqual(saved['ticket']['questions'],[])
        self.assertIsNone(saved['ticket']['form_input']['target_id'])
        p=self.f.proposal(saved)
        self.assertEqual(p['proposal']['target_visual']['target_id'],'card')
        self.assertTrue(p['form_candidate_binding'])
        request={k:p['proposal'][k] for k in ('model_id','measure_id','filters','dimension_ids')}
        request.update(symptom=p['text'],predecessor=None)
        self.f.workspace.intake.review(p['id'],request)

    def test_selected_declared_subject_is_a_form_fact(self):
        saved=self.f.submit(comparison='DECLARED_SUBJECT')
        self.assertEqual(saved['ticket']['questions'],[])
        self.assertEqual(self.f.proposal(saved)['proposal']['ticket_route']['route'],'DECLARED_SUBJECT')

    def test_testset_r1_is_constructed_from_review_not_a_value(self):
        from investigator.form_eval_inputs import construct
        oracle={'true_report_and_page':{'state':'DETERMINED','value':{'report_id':'report','page_id':'page'}},
            'true_target_and_cell':{'state':'DETERMINED','value':{'kind':'MEASURE_AT_SCOPE','measure_id':'measure'}},
            'scope_equivalence_review':{'status':'VERIFIED_EQUIVALENT_DECLARED_SCOPE','candidate_ids':['card','second']},
            'true_comparison_route':{'state':'NOT_APPLICABLE'},'true_reported_figure':{'state':'NOT_STATED'}}
        result=construct(oracle,self.models,{**self.request,'value_seen':None})
        self.assertTrue(result['complete']);self.assertEqual(result['form']['target_id'],'card')
        self.assertIsNone(result['form']['value_seen'])
        oracle['true_target_and_cell']={'state':'UNDETERMINED'}
        result=construct(oracle,self.models,{**self.request,'value_seen':None})
        self.assertFalse(result['complete']);self.assertIsNone(result['form']['target_id'])

    def test_all_matching_equivalent_scopes_settle(self):
        b,m=form_candidates.observe(self.request,self.models,self.reader({'card':'16','second':'16'}))
        self.assertEqual(m['status'],'BOUND');self.assertEqual(len(m['equivalent_target_ids']),2)

    def test_differing_matching_scopes_require_question(self):
        self.models[0]['visuals'][-1]['declared_scopes']['measure']['restrictions']=[{'field_id':'warehouse','operator':'IN','values':['North']}]
        b,m=form_candidates.observe(self.request,self.models,self.reader({'card':'16','second':'16'}))
        self.assertEqual(m['status'],'NEEDS_INPUT')

    def test_ambiguous_match_actual_choice_adopts_and_preserves_prior_probes(self):
        self.models[0]['visuals'][-1]['declared_scopes']['measure']['restrictions']=[{'field_id':'warehouse','operator':'IN','values':['North']}]
        self.f.workspace.form_candidate_reader=self.reader({'card':'16','second':'16'})
        saved=self.f.workspace.forms.submit(self.request);q=saved['ticket']['questions'][0]
        selected=next(c for c in q['choices'] if saved['ticket']['form_choices'][c['id']]['target_id']=='second')
        resumed=self.f.workspace.forms.reply({'ticket_id':saved['ticket']['id'],'revision':saved['revision'],
            'answers':[{'question_id':q['id'],'choice_id':selected['id']}],'request_key':'real-choice'})
        self.assertEqual(self.f.proposal(resumed)['proposal']['target_visual']['target_id'],'second')
        self.assertTrue(resumed['ticket']['superseded_candidate_bindings'])

    def test_missing_probe_never_counts_as_unique_match(self):
        def reader(c):return self.reader({'card':'16'})(c) if c['target_id']=='card' else {'status':'UNAVAILABLE'}
        with self.assertRaises(form_candidates.NotMeasurable):form_candidates.observe(self.request,self.models,reader)

    def test_empty_is_not_zero(self):
        request={**self.request,'value_seen':'empty'}
        b,m=form_candidates.observe(request,self.models,self.reader({'card':None,'second':'0'}))
        self.assertEqual(m['scope']['target_id'],'card')

    def test_changed_catalog_and_dropped_candidate_refused(self):
        b,m=form_candidates.observe(self.request,self.models,self.reader({'card':'16','second':'16'}))
        b['entries'].pop()
        with self.assertRaises(Conflict):form_candidates.matching(self.request,self.models,b)

    def test_no_match_never_invents_target(self):
        b,m=form_candidates.observe(self.request,self.models,self.reader({'card':'17','second':'18'}))
        self.assertEqual(m['status'],'NEEDS_INPUT')
        self.assertEqual(m['questions'][0]['reason'],'VALUE_NOT_FOUND')
        self.assertNotIn('scope',m)

    def test_no_match_click_preserves_figure_and_prior_probes(self):
        self.f.workspace.form_candidate_reader=self.reader({'card':'17','second':'18'})
        saved=self.f.workspace.forms.submit(self.request);q=saved['ticket']['questions'][0]
        self.assertIn('could not find 16',q['question'])
        selected=next(c for c in q['choices'] if saved['ticket']['form_choices'][c['id']]['target_id']=='second')
        resumed=self.f.workspace.forms.reply({'ticket_id':saved['ticket']['id'],'revision':saved['revision'],
            'answers':[{'question_id':q['id'],'choice_id':selected['id']}],'request_key':'no-match-choice'})
        p=self.f.proposal(resumed)['proposal']
        self.assertEqual(p['target_visual']['target_id'],'second')
        self.assertEqual(p['reported_figure']['value'],'16')
        self.assertTrue(resumed['ticket']['superseded_candidate_bindings'])

    def test_no_match_cannot_point_holds(self):
        self.f.workspace.form_candidate_reader=self.reader({'card':'17','second':'18'})
        saved=self.f.workspace.forms.submit(self.request);q=saved['ticket']['questions'][0]
        resumed=self.f.workspace.forms.reply({'ticket_id':saved['ticket']['id'],'revision':saved['revision'],
            'answers':[{'question_id':q['id'],'unavailable':True}],'request_key':'cannot-point'})
        self.assertEqual(resumed['ticket']['state'],'HELD')
