"""Different phrasing is not different evidence; different values still refuse."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator
from investigator import reported_figure as figure
from investigator.question_intake import azure_resolve, Intake
import test_question_intake as fixture


def spans(ticket,quotes):
    return [{'start':ticket.index(q),'end':ticket.index(q)+len(q),'quote':q} for q in quotes]


class SameReferentTests(unittest.TestCase):
    def test_empty_retains_earliest_and_supporting_spans(self):
        ticket='The visual shows nothing; the visual is empty.'
        value=figure.from_candidates(spans(ticket,['the visual is empty','shows nothing']),ticket)
        self.assertEqual(value['state'],'EMPTY')
        self.assertEqual(value['source']['quote'],'shows nothing')
        self.assertEqual(value['supporting_sources'][0]['quote'],'the visual is empty')
        self.assertTrue(Draft202012Validator(figure.SCHEMA).is_valid(value))
        self.assertIn('the visual is empty',figure.provenance(value))

    def test_distinct_values_refuse_and_name_each_group(self):
        ticket='The visual shows 16; another shows 18.'
        with self.assertRaises(figure.AmbiguousFigure) as caught:
            figure.from_candidates(spans(ticket,['shows 16','shows 18']),ticket)
        self.assertIn('shows 16',str(caught.exception));self.assertIn('shows 18',str(caught.exception))
        h=fixture.IntakeTests();h.setUp();self.addCleanup(h.doCleanups)
        def wrong(payload):raise caught.exception
        h.workspace.intake=Intake(h.workspace,wrong)
        request=copy.deepcopy(h.request);request['text']=ticket
        result=h.workspace.intake.resolve(request)
        self.assertEqual(result['status'],'NEEDS_INPUT')
        self.assertIn('shows 18',result['question'])

    def test_equal_numerals_use_coarser_recorded_precision(self):
        ticket='The visual shows 16; it also shows 16.0.'
        value=figure.from_candidates(spans(ticket,['shows 16','shows 16.0']),ticket)
        self.assertEqual(value['value'],'16')
        self.assertEqual(value['precision'],{'state':'STATED_PLACE','place':0})
        self.assertIn('weaker than an exact',figure.qualification(value)[0])
        forged=copy.deepcopy(value);forged['precision']['place']=1
        with self.assertRaises(ValueError):figure.validate(forged,ticket)

    def test_rounding_never_collapses_different_values(self):
        ticket='The visual shows 16; another shows 16.04.'
        with self.assertRaises(figure.AmbiguousFigure):
            figure.from_candidates(spans(ticket,['shows 16','shows 16.04']),ticket)

    def test_supporting_spans_are_validated_not_unchecked_attachments(self):
        ticket='The visual shows nothing; another shows 0.'
        value=figure.from_candidates(spans(ticket,['shows nothing']),ticket)
        value['supporting_sources']=spans(ticket,['shows 0'])
        with self.assertRaises(ValueError):figure.validate(value,ticket)
        value['supporting_sources']=[]
        with self.assertRaises(ValueError):figure.validate(value,ticket)

    def test_sealed_round_six_i_empty_response_under_current_consumer(self):
        sealed=json.loads((Path(__file__).parent/'fixtures/round_six_i_empty_same_referent.json').read_text())
        ticket=sealed['ticket']
        payload={'text':ticket,'models':[{'id':'model','measures':[{'id':'measure','name':'Handled Quantity'}],
            'columns':[],'reports':[{'id':'report','name':'Declared predicate fixture 20261001'}]}]}
        response={'action':'PROPOSE','model_id':'m0','measure_id':'m0v0','metric_quote':'Handled Quantity',
            'question':None,'triage':'MISMATCH_COMPLAINT:VERTICAL','filters':[],'dimension_ids':[],
            'reported_candidates':sealed['reported_candidates'],'value_mentions':[],
            'target_request':None,'report_quote':'Declared predicate fixture 20261001',
            'question_kind':{'kind':'VISUAL_CONTENT','source':{'quote':'Check whether the saved declared report context reproduces what the visual shows'}}}
        with patch('ticket_planner.azure_generate',return_value=(response,{})) as provider:
            value,_=azure_resolve(payload)
        provider.assert_called_once()
        reported=value['reported_figure']
        self.assertEqual(reported['state'],'EMPTY')
        self.assertEqual([reported['source'],*reported['supporting_sources']],
            spans(ticket,['shows nothing','the visual is empty']))
        from investigator.declared_reproduction import render
        marker={'reported_figure':reported,'undeclared_context_value':'61','reproduced_value':None,
            'label':'REPRODUCED','declarations':[],'id':'receipt','composed_restrictions':[]}
        technical=render(marker)
        self.assertIn("What the ticket said: 'shows nothing'; 'the visual is empty'.",technical)


if __name__=='__main__':unittest.main()
