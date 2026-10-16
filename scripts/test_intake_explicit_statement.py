"""An explicit shown state cannot disappear into UNSPECIFIED at intake."""
import copy
import unittest
from unittest.mock import MagicMock,patch
from investigator.question_intake import Intake,azure_resolve_legacy as azure_resolve
from investigator import reported_figure as figure
from investigator import intake_statement_registry as registry
import test_question_intake as fixture

EMPTY_TICKET='In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows nothing (the visual is empty) for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.'


class ExplicitIntakeTests(unittest.TestCase):
    def setUp(self):
        self.h=fixture.IntakeTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.request=copy.deepcopy(self.h.request)

    def resolve(self,ticket,responses):
        self.request['text']=ticket
        resolver=MagicMock(side_effect=[(r,{'usage':{'output_tokens':20}}) for r in responses])
        self.h.workspace.intake=Intake(self.h.workspace,resolver)
        return self.h.workspace.intake.resolve(self.request),resolver

    def test_exact_empty_ticket_omitted_twice_holds_before_reads(self):
        result,resolver=self.resolve(EMPTY_TICKET,[fixture.proposal(),fixture.proposal()])
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['error'],'INTAKE_OMITTED_EXPLICIT_STATEMENT')
        self.assertIn('nothing',result['refusal_reason'])
        self.assertEqual(resolver.call_count,2)
        self.assertIn('_explicit_statement_repair',resolver.call_args.args[0])
        self.assertEqual([r['event'] for r in result['resolution_attempts']],
                         ['INTAKE_OMITTED_EXPLICIT_STATEMENT','EXPLICIT_STATEMENT_RETRY'])
        self.assertEqual(self.h.h.agent.governor.snapshot()['reservation_states'],{'SETTLED':2})
        self.h.h.native.assert_not_called();self.h.h.source.assert_not_called()
        self.assertEqual(self.h.workspace.intake.resolve(self.request),result)
        self.assertEqual(resolver.call_count,2)

    def test_empty_retry_with_exact_quote_proceeds(self):
        ticket='The ratio visual is empty for USD.';quote='visual is empty';start=ticket.index(quote)
        second=fixture.proposal();second['reported_figure']=figure.from_candidates(
            [{'start':start,'end':start+len(quote),'quote':quote}],ticket)
        result,resolver=self.resolve(ticket,[fixture.proposal(),second])
        self.assertEqual(result['status'],'PROPOSED');self.assertEqual(resolver.call_count,2)
        self.assertEqual(result['proposal']['reported_figure']['state'],'EMPTY')

    def test_without_explicit_state_unspecified_passes_without_retry(self):
        result,resolver=self.resolve('The ratio looks low for USD.',[fixture.proposal()])
        self.assertEqual(result['status'],'PROPOSED');resolver.assert_called_once()

    def test_reported_numeral_omission_retries_and_holds(self):
        result,resolver=self.resolve('The ratio shows 16 for USD.',[fixture.proposal(),fixture.proposal()])
        self.assertEqual(result['error'],'INTAKE_OMITTED_EXPLICIT_STATEMENT')
        self.assertEqual(result['explicit_statements'][0]['source']['quote'],'16')
        self.assertEqual(resolver.call_count,2)

    def test_shown_numeral_retry_keeps_stated_precision(self):
        ticket='The ratio shows about 3.4M for USD.';quote='about 3.4M';start=ticket.index(quote)
        second=fixture.proposal();second['reported_figure']=figure.from_candidates(
            [{'start':start,'end':start+len(quote),'quote':quote}],ticket)
        result,_=self.resolve(ticket,[fixture.proposal(),second])
        self.assertEqual(result['status'],'PROPOSED')
        self.assertEqual(result['proposal']['reported_figure']['precision'],{'state':'STATED_PLACE','place':5})

    def test_one_planner_allowance_refuses_retry_without_refund(self):
        self.h.h.agent.governor.policy['daily_limits']['planner_calls']=1
        result,resolver=self.resolve('The ratio visual is empty for USD.',[fixture.proposal()])
        self.assertEqual(result['status'],'HELD');resolver.assert_called_once()
        self.assertEqual(self.h.h.agent.governor.snapshot()['reserved_today']['planner_calls'],1)


class RegistryTests(unittest.TestCase):
    def test_every_closed_empty_form_has_exact_provenance(self):
        for word in (*registry.EMPTY_FORMS,'-'):
            with self.subTest(word=word):
                ticket='The visual shows '+word+'.'
                matches=registry.explicit_statements(ticket)
                self.assertTrue(matches)
                self.assertTrue(all(r['kind']=='EMPTY' for r in matches))
                source=matches[0]['source'];self.assertEqual(ticket[source['start']:source['end']],source['quote'])
                self.assertEqual(figure.from_candidates([source],ticket)['state'],'EMPTY')

    def test_dates_identifiers_negative_numbers_and_conceptual_mentions(self):
        for ticket in ('In Report 20261001 inspect record 900099.','The visual date is 2026-09-14.',
                       'What does empty mean?','Explain blank handling for source rows.'):
            self.assertEqual(registry.explicit_statements(ticket),[])
        self.assertEqual(registry.explicit_statements('The visual shows -5.')[0]['kind'],'NUMBER')
        self.assertEqual(figure.from_candidates([{'start':0,'end':2,'quote':'-5'}],'-5')['state'],'NUMBER')

    def test_visual_name_dash_is_not_a_shown_empty_value(self):
        self.assertEqual({r['source']['quote'] for r in registry.explicit_statements(EMPTY_TICKET)},
                         {'nothing','empty'})
        self.assertEqual(registry.explicit_statements('The card Revenue - monthly looks wrong.'),[])
        self.assertEqual(registry.explicit_statements('The card Dash looks wrong.'),[])
        for ticket in ('The card shows -.','The visual is a dash.'):
            self.assertEqual(registry.explicit_statements(ticket)[0]['kind'],'EMPTY')

    def test_ask_remains_fenced_not_forced_to_invent_a_figure(self):
        registry.validate(fixture.ask(),'The visual is empty; which measure?')

    def test_azure_producer_omission_has_usage_and_rejection_provenance(self):
        ticket='An unfamiliar value visual shows nothing.'
        payload={'text':ticket,'models':[{'id':'model','measures':[{'id':'measure','name':'Unfamiliar value'}],'columns':[]}]}
        response={'action':'PROPOSE','model_id':'m0','measure_id':'m0v0','metric_quote':'unfamiliar value',
                  'question':None,'triage':'MISMATCH_COMPLAINT:VERTICAL','filters':[],'dimension_ids':[],
                  'reported_candidates':[],'value_mentions':[],'target_request':None,'report_quote':None,
                  'question_kind':{'kind':'VISUAL_CONTENT','source':{'quote':ticket}}}
        payload['_explicit_statement_repair']={'reason':'INTAKE_OMITTED_EXPLICIT_STATEMENT',
            'statements':registry.explicit_statements(ticket)}
        with patch('ticket_planner.azure_generate',return_value=(response,{'usage':{'output_tokens':20}})) as generate:
            with self.assertRaises(registry.OmittedExplicitStatement) as caught:azure_resolve(payload)
        wire=generate.call_args.args[0];instructions=generate.call_args.kwargs['instructions']
        self.assertNotIn('_explicit_statement_repair',wire)
        self.assertEqual(wire['explicit_statement_repair'],payload['_explicit_statement_repair'])
        self.assertIn('INTAKE_OMITTED_EXPLICIT_STATEMENT',instructions)
        for word in registry.EMPTY_FORMS:self.assertIn(word,instructions)
        self.assertEqual(caught.exception.provider_metadata['usage']['output_tokens'],20)
        self.assertEqual(caught.exception.statements[0]['source']['quote'],'nothing')

    def test_correction_context_does_not_reduce_catalog_coverage(self):
        from investigator.question_intake import wire_contract
        payload={'text':'The visual shows nothing.', 'models':[
            {'id':'model','measures':[{'id':'measure','name':'Unfamiliar value'}],
             'columns':[{'column_id':'column','name':'Category','data_type':'string'}]}]}
        before=wire_contract(payload)[0]
        after=wire_contract({**payload,'_explicit_statement_repair':{
            'reason':'INTAKE_OMITTED_EXPLICIT_STATEMENT',
            'statements':registry.explicit_statements(payload['text'])}})[0]
        self.assertEqual(before['models'],after['models'])


if __name__=='__main__':unittest.main()
