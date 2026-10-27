import base64
from copy import deepcopy
import unittest

from fixture.apply import PipelineFailureScenario
from fixture.pipeline_runtime import copy_timeout_window, source_read_after_resume
from investigator.process_tape import bytes_of


class RuntimeWindowTests(unittest.TestCase):
    def test_resume_read_keeps_both_ordinals_and_retries_only_once(self):
        calls = []; waits = []
        failed = {'exit': 1, 'body': {'error_number': 40613}}
        success = {'exit': 0, 'body': {'sets': [[{'actual': 'native'}]]}}
        def read(ordinal):
            calls.append(ordinal)
            return (failed, success)[ordinal]
        self.assertIs(source_read_after_resume(read, sleep=waits.append), success)
        self.assertEqual(calls, [0, 1]); self.assertEqual(waits, [30])
        calls.clear(); waits.clear()
        self.assertIs(source_read_after_resume(lambda n: calls.append(n) or failed,
                                             sleep=waits.append), failed)
        self.assertEqual(calls, [0, 1]); self.assertEqual(waits, [30])

    def test_permissions_and_success_are_not_resume_retried(self):
        for value in ({'exit': 1, 'body': {'error_number': 18456}},
                      {'exit': 0, 'body': {'sets': []}}):
            calls = []; waits = []
            self.assertIs(source_read_after_resume(lambda n: calls.append(n) or value,
                                                 sleep=waits.append), value)
            self.assertEqual(calls, [0]); self.assertEqual(waits, [])

    def original(self):
        content = {'properties': {'activities': [
            {'name': 'Copy', 'type': 'InvokeCopyJob',
             'policy': {'timeout': '0.00:10:00', 'retry': 0},
             'typeProperties': {'copyJobId': 'retained-copy', 'workspaceId': 'retained-workspace'}},
            {'name': 'Audit', 'type': 'Script', 'dependsOn': [{'activity': 'Copy'}],
             'policy': {'timeout': '0.00:10:00'},
             'typeProperties': {'scripts': [{'text': 'retained audit writer'}]},
             'externalReferences': {'connection': 'retained-connection'}}]}}
        return {'definition': {'parts': [
            {'path': 'pipeline-content.json', 'payloadType': 'InlineBase64',
             'payload': base64.b64encode(bytes_of(content)).decode()},
            {'path': '.platform', 'payloadType': 'InlineBase64', 'payload': 'retained'}]}}

    def test_only_copy_timeout_changes_and_original_is_immutable(self):
        original = self.original(); saved = deepcopy(original)
        changed = copy_timeout_window(original)
        actual = PipelineFailureScenario.content(changed)
        expected = PipelineFailureScenario.content(original)
        expected['properties']['activities'][0]['policy']['timeout'] = '0.00:30:00'
        self.assertEqual(actual, expected)
        self.assertEqual(original, saved)
        self.assertEqual(changed['definition']['parts'][1], original['definition']['parts'][1])

    def test_bounded_window_and_missing_copy_refuse_without_mutation(self):
        for minutes in (True, 9, 61, 30.0):
            with self.subTest(minutes=minutes), self.assertRaises(ValueError):
                copy_timeout_window(self.original(), minutes=minutes)
        original = self.original(); content = PipelineFailureScenario.content(original)
        content['properties']['activities'].pop(0)
        original['definition']['parts'][0]['payload'] = base64.b64encode(bytes_of(content)).decode()
        with self.assertRaisesRegex(ValueError, 'NATIVE_COPY_ACTIVITY_REQUIRED'):
            copy_timeout_window(original)
