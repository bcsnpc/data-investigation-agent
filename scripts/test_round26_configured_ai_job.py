from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
import unittest
from investigator.shared_state import SharedState
from investigator.configured_ai_job import ConfiguredJob


class ConfiguredJobTests(unittest.TestCase):
    def test_guided_cache_setting_is_not_pinned_to_retired_opus_diagnostic(self):
        import cloud_guided_investigator
        import json
        value = {'version': 'guided-investigation/1', 'ticket': {}, 'assets': {},
                 'graph': {'estate': 'fixture', 'identity': 'reader', 'allowed_objects': []},
                 'max_requests': 30, 'diagnostic_prompt_cache': True}
        for model in ('gpt-6.1-sol', 'gpt-6-astra', 'claude-opus-5-5'):
            with patch('cloud_guided_investigator.reference') as ref, \
                    patch('investigator.adapters.provider_runtime.validate'):
                ref.return_value.read_bytes.return_value = json.dumps({**value, 'reasoning': {'model': model}}).encode()
                result = cloud_guided_investigator.specification({'spec': {}})
                self.assertTrue(result['diagnostic_prompt_cache'])
                self.assertNotIn('diagnostic_budget', result)

    def setUp(self):
        folder = TemporaryDirectory(); self.addCleanup(folder.cleanup)
        self.state = SharedState.offline(Path(folder.name) / 'state.sqlite'); self.state.migrate()
        self.steps = Mock(); self.steps.evaluate.return_value = {'correct': True}
        self.factory = Mock(return_value=self.steps)
        self.config = {'ai_routing': {}, 'tenant': 'fixture'}
        self.job = ConfiguredJob(self.state, self.config, Mock(), steps_factory=self.factory)

    def test_completed_evaluation_resumes_without_another_model_call(self):
        result = self.job.submit([{'case_id': 'one'}], batch_key='batch', evaluation=True)
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertEqual(result, self.job.resume('batch'))
        self.steps.evaluate.assert_called_once_with({'case_id': 'one'}, case_id='one', grading_role='PRIMARY')
        with self.assertRaisesRegex(ValueError, 'ALREADY_ADMITTED'):
            self.job.submit([{'case_id': 'one'}], batch_key='batch', evaluation=True)

    def test_failed_call_is_retained_and_resume_does_not_retry(self):
        self.steps.evaluate.side_effect = RuntimeError('provider unavailable')
        with self.assertRaises(RuntimeError):
            self.job.submit([{'case_id': 'one'}], batch_key='batch', evaluation=True)
        result = self.job.resume('batch')
        self.assertEqual(result['status'], 'INTERRUPTED')
        self.assertFalse(result['resubmitted'])
        self.assertEqual(self.steps.evaluate.call_count, 1)

    def test_configuration_cannot_change_under_a_saved_job(self):
        self.job.submit([], batch_key='batch', evaluation=True)
        self.config['tenant'] = 'other'
        with self.assertRaisesRegex(ValueError, 'CONFIGURATION_CHANGED'):
            self.job.resume('batch')

    def test_cloud_entry_accepts_configured_route_without_legacy_anthropic_secret(self):
        import cloud_enrichment
        with patch('cloud_enrichment.reference') as reference, patch('investigator.adapters.provider_runtime.select') as select:
            reference.return_value.read_bytes.return_value = b'{"ai_routing":{},"tenant":"fixture"}'
            result = cloud_enrichment.validate_options({'operation': 'evaluation-resume',
                'config': {}, 'batch_key': 'configured'})
        self.assertEqual(result[1]['tenant'], 'fixture')
        self.assertEqual(select.call_count, 5)

    def test_anthropic_cache_uses_configured_model_not_a_global_opus_pin(self):
        from investigator.adapters.reasoning_anthropic import Client
        budget = Mock(); budget.rate.model = 'claude-sonnet-4-6'
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            client = Client(model=budget.rate.model, budget=budget, identity='model',
                secret_reference={}, record=Mock(), send=Mock(), diagnostic_prompt_cache=True)
        self.assertIsNotNone(client.diagnostic_cache)
