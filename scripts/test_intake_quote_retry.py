"""Duplicate figure repair is one independent admission, never a provider retry loop."""
import copy
import unittest
from unittest.mock import MagicMock
from investigator.question_intake import Intake, FigureQuoteAmbiguous, QuoteRefused, QuoteNotFound
import test_question_intake as fixture


class QuoteRetryTests(unittest.TestCase):
    def setUp(self):
        self.h=fixture.IntakeTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.request=copy.deepcopy(self.h.request)
        self.request['text']='The ratio shows 9 for USD; order 9.'

    def ambiguous(self):
        spans=[{'start':v,'end':v+1,'quote':'9'} for v in (16,33)]
        exc=FigureQuoteAmbiguous('9',spans)
        exc.provider_metadata={'usage':{'output_tokens':10}}
        exc.repair={'quote':'9','occurrences':spans,'response':{}}
        return exc

    def run_case(self,second):
        resolver=MagicMock(side_effect=[self.ambiguous(),second])
        self.h.workspace.intake=Intake(self.h.workspace,resolver)
        saved=self.h.workspace.intake.resolve(self.request)
        return saved,resolver

    def test_unique_repair_proceeds_and_both_calls_are_charged(self):
        p=fixture.proposal();p['reported_figure']={'state':'NUMBER','value':'9',
            'precision':{'state':'EXACT'},'source':{'start':10,'end':17,'quote':'shows 9'}}
        saved,resolver=self.run_case((p,{'usage':{'output_tokens':20}}))
        self.assertEqual(saved['status'],'PROPOSED')
        self.assertEqual(resolver.call_count,2)
        self.assertIn('_figure_quote_repair',resolver.call_args.args[0])
        self.assertEqual([v['event'] for v in saved['resolution_attempts']],
            ['REPORTED_FIGURE_QUOTE_AMBIGUOUS','REPORTED_FIGURE_QUOTE_RETRY'])
        snap=self.h.h.agent.governor.snapshot()
        self.assertEqual(snap['reserved_today']['planner_calls'],2)
        self.assertEqual(snap['reservation_states'],{'SETTLED':2})
        self.assertEqual(self.h.workspace.intake.resolve(self.request),saved)
        self.assertEqual(resolver.call_count,2)

    def test_still_duplicate_names_occurrences_without_third_call(self):
        second=self.ambiguous()
        saved,resolver=self.run_case(second)
        self.assertEqual(saved['status'],'NEEDS_INPUT')
        self.assertIn('16:17, 33:34',saved['question'])
        self.assertEqual(resolver.call_count,2)
        self.assertEqual(self.h.h.agent.governor.snapshot()['reserved_today']['planner_calls'],2)

    def test_nonverbatim_retry_refuses_without_third_call(self):
        second=QuoteRefused('Provenance quote not found verbatim in the ticket.')
        second.provider_metadata={'usage':{'output_tokens':20}}
        saved,resolver=self.run_case(second)
        self.assertEqual(saved['status'],'NEEDS_INPUT')
        self.assertIn('not found verbatim',saved['question'])
        self.assertEqual(resolver.call_count,2)

    def test_allowance_blocks_second_call_and_does_not_refund_first(self):
        self.h.h.agent.governor.policy['daily_limits']['planner_calls']=1
        saved,resolver=self.run_case((fixture.proposal(),{}))
        self.assertEqual(saved['status'],'HELD')
        self.assertEqual(resolver.call_count,1)
        self.assertEqual(self.h.h.agent.governor.snapshot()['reserved_today']['planner_calls'],1)

    def missing(self):
        exc=QuoteNotFound('invented_column','column')
        exc.provider_metadata={'usage':{'output_tokens':10}}
        exc.repair={'field':'column','quote':'invented_column','response':{}}
        return exc

    def test_nonverbatim_then_exact_proceeds_with_two_metered_calls(self):
        proposed=fixture.proposal()
        proposed['reported_figure']={'state':'NUMBER','value':'9','precision':{'state':'EXACT'},
                                    'source':{'start':10,'end':17,'quote':'shows 9'}}
        resolver=MagicMock(side_effect=[self.missing(),(proposed,{'usage':{'output_tokens':20}})])
        self.h.workspace.intake=Intake(self.h.workspace,resolver)
        saved=self.h.workspace.intake.resolve(self.request)
        self.assertEqual(saved['status'],'PROPOSED')
        self.assertEqual(resolver.call_count,2)
        self.assertIn('_provenance_quote_repair',resolver.call_args.args[0])
        self.assertEqual([v['event'] for v in saved['resolution_attempts']],
                         ['PROVENANCE_QUOTE_NOT_FOUND','PROVENANCE_QUOTE_RETRY'])
        self.assertEqual(self.h.h.agent.governor.snapshot()['reservation_states'],{'SETTLED':2})
        self.assertEqual(self.h.workspace.intake.resolve(self.request),saved)
        self.assertEqual(resolver.call_count,2)

    def test_two_nonverbatim_responses_need_input_without_third_call(self):
        resolver=MagicMock(side_effect=[self.missing(),self.missing()])
        self.h.workspace.intake=Intake(self.h.workspace,resolver)
        saved=self.h.workspace.intake.resolve(self.request)
        self.assertEqual(saved['status'],'NEEDS_INPUT')
        self.assertIn('not found verbatim',saved['question'])
        self.assertEqual(resolver.call_count,2)
        self.assertEqual(self.h.h.agent.governor.snapshot()['reserved_today']['planner_calls'],2)

    def test_nonverbatim_first_quote_is_not_retried(self):
        resolver=MagicMock(side_effect=QuoteRefused('Not found verbatim'))
        self.h.workspace.intake=Intake(self.h.workspace,resolver)
        self.assertEqual(self.h.workspace.intake.resolve(self.request)['status'],'NEEDS_INPUT')
        resolver.assert_called_once()


if __name__=='__main__':unittest.main()
