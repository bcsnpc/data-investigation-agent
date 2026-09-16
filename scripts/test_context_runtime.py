import copy
import unittest

from import_fixture import build
from investigator.onboarding import Conflict
from verify_dependency_context import run
from test_reader_execution import config, MODEL
import test_reader_runtime as fixture


class ContextRuntimeTests(unittest.TestCase):
    def setUp(self):
        h = fixture.ReaderRuntimeTests(); h.setUp(); self.addCleanup(h.doCleanups); self.h = h
        spec = copy.deepcopy(h.bundle['spec'])
        spec['tables'][0]['measures'].append({'name': 'Filtered Count', 'expression': 'CALCULATE([New Metric],Events[Flag]=TRUE())'})
        self.bundle = build(spec)
        self.cases = [{'measure': 'Filtered Count', 'context_path': []},
                      {'measure': 'New Metric', 'context_path': ['Filtered Count', 'New Metric']}]

    def execute(self, **kwargs):
        return run(config(), self.bundle, MODEL, self.h.scope, self.cases, self.h.database, 'context', execute=self.h.transport, **kwargs)

    def test_runtime_retains_native_context_and_replays_without_queries(self):
        result = self.execute()
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertIsNone(result['cases'][0]['dependency_context'])
        self.assertEqual(len(result['cases'][1]['dependency_context']['path']), 2)
        self.assertFalse(result['cause_verified']); self.assertFalse(result['live_acceptance_ready'])
        self.assertEqual(self.execute(status_only=True), result)
        self.assertEqual(self.execute(), result)
        self.assertEqual(self.h.transport.call_count, 2)

    def test_bad_case_is_rejected_before_dispatch(self):
        self.cases[1]['context_path'] = ['Filtered Count', 'Missing']
        with self.assertRaises(KeyError): self.execute()
        self.h.transport.assert_not_called()

    def test_changed_scope_cannot_reuse_verification_key(self):
        self.execute(); self.cases.pop()
        with self.assertRaises(Conflict): self.execute(status_only=True)
        self.assertEqual(self.h.transport.call_count, 2)


if __name__ == '__main__': unittest.main()
