from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest
from investigator.ai_steps import Steps
from investigator.shared_state import SharedState


class AIStepsTests(unittest.TestCase):
    def test_all_structured_steps_use_configured_client_and_shared_case_budget(self):
        with TemporaryDirectory() as directory:
            state = SharedState.offline(Path(directory) / 'state.sqlite'); state.migrate()
            config = {'provider': 'openai', 'model': 'synthetic', 'gateway_identity': 'model', 'worker_identity': 'worker',
                      'secret_reference': {}, 'rate_card': {'input_rate': '1', 'output_rate': '2',
                      'source': 'https://example.test/pricing', 'observed_at': '2026-11-01'}}
            transport = Mock(); transport.complete.return_value = {'stop_reason': 'tool_use', 'content': [
                {'type': 'tool_use', 'name': 'resolve_intake', 'input': {'ok': True}}]}
            factory = Mock(return_value=transport)
            steps = Steps(configuration={'default': config}, tenant='test', state=state, record=Mock(), client_factory=factory,
                          investigator_configuration={**config, 'provider': 'anthropic', 'model': 'other'})
            for step in ('SCREENSHOT', 'SUMMARY', 'ENRICHMENT', 'WRITER', 'GRADING', 'REVIEWER', 'SMOKE'):
                value = steps.generate(step=step, case_id='same', instructions='fixed', payload={'data': 'synthetic'},
                    schema={'type': 'object', 'required': ['ok'], 'properties': {'ok': {'type': 'boolean'}}})
                self.assertEqual(value, {'ok': True})
                self.assertEqual(factory.call_args.kwargs['budget'].case_id, 'same')
                self.assertEqual(factory.call_args.kwargs['budget'].provider, 'openai')
            self.assertEqual(factory.call_count, 7)

    def test_live_grading_cannot_omit_measured_provider_or_grade_same_vendor(self):
        config = {'provider': 'openai', 'model': 'synthetic', 'rate_card': {}, 'secret_reference': {},
                  'gateway_identity': 'model', 'worker_identity': 'worker'}
        steps = Steps(configuration={'default': config}, tenant='t', state=None, record=Mock())
        with self.assertRaisesRegex(ValueError, 'MEASURED_INVESTIGATOR'):
            steps.model('GRADING', 'c')
        steps.investigator_configuration = config
        with self.assertRaisesRegex(ValueError, 'DIFFERENT_PROVIDER'):
            steps.model('GRADING', 'c')

    def test_invalid_structured_output_is_not_delivered(self):
        steps = Steps(configuration={}, tenant='t', state=None, record=Mock())
        model = Mock(); model.complete.return_value = {'stop_reason': 'end_turn', 'content': []}
        steps.model = Mock(return_value=model)
        with self.assertRaisesRegex(ValueError, 'UNESTABLISHED'):
            steps.generate(step='WRITER', case_id='c', instructions='s', payload={}, schema={'type': 'object'})
