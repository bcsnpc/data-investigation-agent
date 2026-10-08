"""Explicit contradictions get one recorded correction, never a patched record."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock
from investigator import intake_rules
from investigator.question_intake import Intake
from test_question_intake import proposal
import test_investigator_workspace as fixture


class IntakeRulesTests(unittest.TestCase):
    def test_explicit_reproduction_and_mismatch_are_not_business_scope(self):
        value=proposal();value['question_kind']={'kind':'FIGURE_DIFFERENCE'}
        with self.assertRaisesRegex(intake_rules.RuleViolation,'REPRODUCTION_SUBJECT_REQUIRED'):
            intake_rules.validate(value,'Can the saved context reproduce the displayed figure?')
        value.update(ticket_shape='BUSINESS_QUESTION',comparison_mode='NONE')
        with self.assertRaisesRegex(intake_rules.RuleViolation,'MISMATCH_SHAPE_REQUIRED'):
            intake_rules.validate(value,'The quantity seems overstated.')

    def test_business_rule_primary_ask_cannot_become_technical_subject(self):
        value=proposal();value['question_kind']={'kind':'TRANSFORMATION_MECHANISM'}
        with self.assertRaisesRegex(intake_rules.RuleViolation,'BUSINESS_RULE_SUBJECT_REQUIRED'):
            intake_rules.validate(value,'Please decide the business rule.')
        value['question_kind']['kind']='BUSINESS_MEANING'
        intake_rules.validate(value,'Please decide the business rule.')

    def test_sealed_business_intent_must_never_become_a_defect_answer(self):
        saved=json.loads((Path(__file__).parent/'fixtures/round_ten/business-intent-sealed-excerpt.json').read_text())
        self.assertEqual(saved['observed_outcome'],'TRANSFORMATION_LOGIC')
        self.assertEqual(saved['proposal']['question_kind']['kind'],'BUSINESS_MEANING')
        intake_rules.validate(saved['proposal'],saved['ticket'])
        from investigator.question_kind import intake_route,UnimplementedRoute
        with self.assertRaisesRegex(UnimplementedRoute,'domain specialist'):
            intake_route(saved['proposal'])

    def test_explicit_selected_value_is_not_a_mention_or_subject(self):
        value=proposal();value['value_mentions']=[{'role':'SUBJECT','source':{'quote':'North'}}]
        with self.assertRaisesRegex(intake_rules.RuleViolation,'EXPLICIT_SELECTION_ROLE_REQUIRED'):
            intake_rules.validate(value,'I selected North. Explain the selected scope.')
        value['value_mentions'][0]['role']='SELECTION'
        intake_rules.validate(value,'I selected North. Explain the selected scope.')
        value['value_mentions'][0]['role']='MENTION'
        intake_rules.validate(value,'I mentioned North. Explain the global scope.')

    def test_filter_effect_and_temporal_asks_are_not_pipeline_or_business_answers(self):
        value=proposal();value['question_kind']={'kind':'FIGURE_DIFFERENCE'}
        with self.assertRaisesRegex(intake_rules.RuleViolation,'FILTER_EFFECT_SUBJECT_REQUIRED'):
            intake_rules.validate(value,'Which saved filters are hiding movements?')
        with self.assertRaisesRegex(intake_rules.RuleViolation,'TEMPORAL_COMPARISON_SUBJECT_REQUIRED'):
            intake_rules.validate(value,'Why did the quantity change between the saved states?')

    def exercise(self, repaired):
        h=fixture.WorkspaceTests();h.setUp();self.addCleanup(h.doCleanups)
        ticket='The ratio seems overstated for USD.'
        wrong=proposal();wrong.update(ticket_shape='BUSINESS_QUESTION',comparison_mode='NONE')
        metadata={'usage':{'input_tokens':10,'output_tokens':10}}
        resolver=MagicMock(side_effect=[(wrong,metadata),(proposal() if repaired else copy.deepcopy(wrong),metadata)])
        h.workspace.intake=Intake(h.workspace,resolver)
        result=h.workspace.intake.resolve({'text':ticket,'request_key':'rule-correction','parent_id':None})
        self.assertEqual(resolver.call_count,2)
        self.assertEqual(result['resolution_attempts'][0]['event'],'MISMATCH_SHAPE_REQUIRED')
        self.assertEqual(result['resolution_attempts'][1]['event'],'INTAKE_RULE_RETRY')
        self.assertIn('_intake_rule_repair',resolver.call_args.args[0])
        self.assertEqual(h.agent.governor.snapshot()['reserved_today']['planner_calls'],2)
        h.native.assert_not_called();h.source.assert_not_called()
        return result

    def test_first_invalid_shape_then_valid_shape_proceeds_without_editing_response(self):
        self.assertEqual(self.exercise(True)['status'],'PROPOSED')

    def test_two_invalid_shapes_hold_after_exactly_one_retry(self):
        result=self.exercise(False)
        self.assertEqual(result['status'],'HELD')
        self.assertEqual(result['error'],'MISMATCH_SHAPE_REQUIRED')
        self.assertIsNone(result['proposal'])


if __name__=='__main__':unittest.main()
