import copy
import unittest
from investigator import ticket_question_gate as gate, ticket_protocol as protocol
from investigator import ticket_clarification as planner, intake_confirmation
from test_intake_extraction import fixture


class QuestionGateTests(unittest.TestCase):
    def test_current_quantity_does_not_mean_freshness(self):
        raw,payload=fixture('In Report, Global card Quantity seems overstated. Investigate its current total.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertEqual(ticket['settled']['COMPARISON']['value']['route'],'LOOKS_WRONG')

    def test_source_mechanism_does_not_establish_application_comparison(self):
        raw,payload=fixture('In Report, Global card Quantity seems overstated. Explain its source mechanism.',
            kind='SOURCE_CORRECTNESS',visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertNotIn('COMPARISON',ticket['settled'])

    def test_model_freshness_nomination_needs_matching_text(self):
        raw,payload=fixture('In Report, Global card Quantity looks high.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertNotIn('COMPARISON',ticket['settled'])

    def test_policy_default_cannot_drop_uncertain_comparison_question(self):
        raw,payload=fixture('In Report, Global card Quantity needs investigation.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        config=planner.settings();config['default_route']='APPLICATION'
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,config)
        self.assertNotIn('COMPARISON',ticket['settled'])

    def test_conflicting_freshness_and_source_cues_require_question(self):
        raw,payload=fixture('In Report, Global card Quantity is stale against the application.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertNotIn('COMPARISON',ticket['settled'])

    def test_two_figures_never_add_visual_or_comparison_questions(self):
        raw,payload=fixture('In Report, Quantity shows 16 or 17.',
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        ticket=protocol.new('t');source={'retained_extraction':raw};config=planner.settings()
        offered=gate.offer(ticket,source,payload,config,planner.batch(ticket,source,payload,config))
        self.assertEqual([q['field'] for q in offered['questions']],['FIGURE'])

    def test_selected_scope_against_global_is_not_an_unknown_comparison(self):
        raw,payload=fixture('In Report, selected warehouse North Quantity differs from global value. Explain selected warehouse scope.',
            comparisons=['global value'],selections=[{'quote':'warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}])
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertEqual(ticket['settled']['COMPARISON']['value']['route'],'DECLARED_SUBJECT')

    def test_unsupported_filter_refuses_even_when_model_omits_selection(self):
        raw,payload=fixture('In Report, Quantity differs under an unknown custom filter.')
        ticket,_,blocked=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertIn('UNSUPPORTED_FILTER',blocked);self.assertEqual(ticket['questions'],[])

    def test_relative_date_selection_refuses_before_visual_questions(self):
        raw,payload=fixture('In Report, Quantity for last seven days differs.',
            selections=[{'quote':'last seven days','column':None,'value':'last seven days','role':'PRIMARY'}])
        ticket,_,blocked=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertIn('RELATIVE_DATE',blocked);self.assertEqual(ticket['questions'],[])

    def test_equivalent_complete_scopes_with_one_figure_settle_without_question(self):
        raw,payload=fixture('In Report, Quantity shows 16 and looks high.',
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        model=payload['models'][0]
        model['visuals'][1]=copy.deepcopy(model['visuals'][0]);model['visuals'][1]['target_id']='second'
        for visual in model['visuals']:
            visual['declared_scopes']={'measure':{'state':'COMPLETE','restrictions':[],
                'context_id':'context','context_hash':'c'*64,'inventory_hash':'i'*64}}
        original=copy.deepcopy(raw)
        ticket,events,blocked=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertIsNone(blocked);self.assertEqual(set(ticket['settled']),set(protocol.FIELDS))
        self.assertIsNone(ticket['settled']['NUMBER']['value']['target_visual'])
        self.assertEqual(ticket['settled']['COMPARISON']['value']['route'],'LOOKS_WRONG')
        self.assertEqual(raw,original);self.assertEqual(len(events),3)

    def test_missing_scope_proof_never_becomes_equivalence(self):
        raw,payload=fixture('In Report, Quantity shows 16.',
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertNotIn('NUMBER',ticket['settled'])

    def test_named_card_two_figures_asks_figure_without_other_target(self):
        raw,payload=fixture('In Report, Global card Quantity shows 16 or 17 and looks high.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        source={'retained_extraction':raw};config=planner.settings()
        ticket,_,_=gate.prepare(protocol.new('t'),source,payload,config)
        offered=gate.offer(ticket,source,payload,config,planner.batch(ticket,source,payload,config))
        self.assertEqual([q['field'] for q in offered['questions']],['FIGURE'])
        retained=intake_confirmation.offer(ticket,offered['questions'],offered['values'],
            request_text=payload['text'],models=payload['models'])
        q=offered['questions'][0]
        answered=protocol.answer(retained,[{'question_id':q['id'],'choice_id':q['choices'][0]['id']}])
        resolved,_,blocked=gate.prepare(answered,source,payload,config)
        self.assertIsNone(blocked)
        self.assertEqual(resolved['settled']['NUMBER']['value']['target_visual']['target_id'],'card')
        self.assertEqual(resolved['settled']['NUMBER']['value']['reported_figure']['value'],'16')

    def test_conflicting_supplied_comparison_is_not_dropped(self):
        raw,payload=fixture('In Report, Global card Quantity is stale.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        ticket,_,_=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,
            planner.settings(),comparison_conflict=True)
        self.assertNotIn('COMPARISON',ticket['settled'])

    def test_nonexistent_column_is_refusal_not_visual_question(self):
        raw,payload=fixture('In Report, selected nonexistent North Quantity differs.',
            selections=[{'quote':'nonexistent North','column':'nonexistent','value':'North','role':'PRIMARY'}])
        _,_,blocked=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertIsNotNone(blocked);self.assertIn('COLUMN',blocked)

    def test_unidentified_report_asks_only_report_once(self):
        raw,payload=fixture('Somewhere, Quantity on the Global card differs.',reports=[],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        source={'retained_extraction':raw};config=planner.settings();ticket=protocol.new('t')
        proposed=planner.batch(ticket,source,payload,config)
        offered=gate.offer(ticket,source,payload,config,proposed)
        self.assertEqual([q['field'] for q in offered['questions']],['REPORT_OR_SCREENSHOT'])
        ticket['rounds']=1
        self.assertIn('TARGET_UNRESOLVED',gate.offer(ticket,source,payload,config,proposed)['blocked'])

    def test_unavailable_figure_names_ambiguity_without_a_second_question(self):
        raw,payload=fixture('In Report, Global card Quantity shows 16 or 17.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        source={'retained_extraction':raw};config=planner.settings();ticket=protocol.new('t')
        proposed=planner.batch(ticket,source,payload,config)
        offered=gate.offer(ticket,source,payload,config,proposed)
        retained=intake_confirmation.offer(ticket,offered['questions'],offered['values'],
            request_text=payload['text'],models=payload['models'])
        answered=protocol.answer(retained,[{'question_id':q['id'],'unavailable':True} for q in offered['questions']])
        self.assertEqual(answered['state'],'HELD')
        self.assertEqual(answered['history'][-1]['detail']['reason'],'MULTIPLE_REPORTED_FIGURES_UNRESOLVED')

    def test_explicit_source_comparison_is_not_reasked_when_model_lists_it(self):
        raw,payload=fixture('In Report, Global card Quantity is higher than source.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],comparisons=['source'])
        ticket,events,blocked=gate.prepare(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings())
        self.assertIsNone(blocked)
        self.assertEqual(ticket['settled']['COMPARISON']['value']['route'],'APPLICATION')
        self.assertTrue(events)

    def test_figure_only_cannot_start_an_investigation(self):
        ticket=protocol.new('t');ticket['settled']['FIGURE']={'authority':'USER_CONFIRMED'}
        with self.assertRaisesRegex(ValueError,'Every consequential field'):
            protocol.transition(ticket,'INVESTIGATING',actor='AGENT',detail={})
