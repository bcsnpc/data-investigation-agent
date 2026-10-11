import copy
import json
import unittest
from unittest.mock import patch
from fixture.rebuild import plan, templates, main


class RebuildPlanTests(unittest.TestCase):
    def manifest(self):
        return {'fixture_states':[{'id':'baseline','description':'Authored fixture baseline'}]}

    def test_every_step_is_plan_only_and_has_identity_and_refusal_or_inputs(self):
        result=plan(self.manifest())
        self.assertEqual(result['platform_requests'],0)
        self.assertTrue(result['apply_implemented'])
        self.assertEqual([step['order'] for step in result['steps']], list(range(1,len(result['steps'])+1)))
        for step in result['steps']:
            with self.subTest(step=step['name']):
                self.assertTrue(step['identity']); self.assertTrue(step['operation'])
                self.assertFalse(step['apply_authorized'])
        self.assertIn('application-model', [step['name'] for step in result['steps']])
        self.assertIn('recollect-and-approve', [step['name'] for step in result['steps']])

    def test_templates_retain_copy_accounting_and_report_predicates(self):
        value=templates()
        report=json.dumps(value['predicate-report']['definition'])
        self.assertIn('bookmark',report.lower()); self.assertIn('Condition',report)
        self.assertIn('rowsCopied',json.dumps(value['audit-pipeline']))
        self.assertIn('${',json.dumps(value['copy-job']))

    def test_no_plan_argument_or_apply_is_accepted(self):
        for arguments in (['--manifest','unused'], ['--manifest','unused','--apply']):
            with self.assertRaises(SystemExit): main(arguments)

    def test_seed_and_manifest_are_not_changed_by_planning(self):
        manifest=self.manifest();before=copy.deepcopy(manifest)
        self.assertEqual(plan(manifest),plan(manifest));self.assertEqual(manifest,before)


if __name__ == '__main__': unittest.main()
