from copy import deepcopy
from unittest.mock import Mock, patch
import unittest
from investigator.adapters.provider_runtime import client, select, validate_graders


def config(provider='anthropic', model='synthetic'):
    return {'provider': provider, 'model': model, 'rate_card': {}, 'secret_reference': {},
            'gateway_identity': 'reader', 'worker_identity': 'worker'}


class ProviderRuntimeTests(unittest.TestCase):
    def test_anthropic_explicit_cache_setting_reaches_transport(self):
        budget = Mock(); budget.rate.model = 'synthetic'
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            model = client({**config(), 'explicit_cache':True}, budget=budget, record=Mock())
        self.assertIsNotNone(model.transport.diagnostic_cache)

    def test_normalized_interface_reports_same_usage_and_cost_across_vendors(self):
        from investigator.reasoning_budget import RateCard
        from investigator.adapters.provider_runtime import UnifiedClient
        rate = RateCard(model='synthetic', input_rate='1.25', base_input_rate='1', cache_read_rate='.1',
                        output_rate='2', source='https://example.test/pricing', observed_at='2026-11-01')
        usage = {'input_tokens': 20, 'cache_read_input_tokens': 80, 'output_tokens': 2}
        outputs = []
        for provider in ('anthropic', 'openai'):
            transport = Mock(); transport.model = 'synthetic'; transport.budget.rate = rate
            transport.complete.return_value = {'id': 'r', 'model': 'synthetic', 'content': [], 'stop_reason': 'end_turn', 'usage': usage}
            outputs.append(UnifiedClient(transport, provider=provider, record=Mock()).complete(system='x'))
        self.assertEqual(outputs[0]['normalized_usage'], outputs[1]['normalized_usage'])
        self.assertEqual(outputs[0]['cost_microdollars'], 32)
        self.assertEqual(outputs[0]['cost_microdollars'], outputs[1]['cost_microdollars'])

    def test_every_component_supports_tenant_and_step_routing(self):
        for step in ('INVESTIGATOR', 'SCREENSHOT', 'SUMMARY', 'ENRICHMENT', 'WRITER', 'GRADING', 'REVIEWER', 'SMOKE'):
            installation = {'default': config(), 'tenants': {'client': {'steps': {step: config('openai')}}}}
            self.assertEqual(select(installation, tenant='client', step=step)['provider'], 'openai')
            self.assertEqual(select(installation, tenant='other', step=step)['provider'], 'anthropic')
            selected = select(installation, tenant='client', step=step); selected['model'] = 'changed'
            self.assertEqual(select(installation, tenant='client', step=step)['model'], 'synthetic')

    def test_cross_vendor_primary_and_different_model_reviewers(self):
        investigator = config('openai', 'investigator')
        validate_graders(investigator, config('anthropic', 'primary'), config('openai', 'secondary'), config('anthropic', 'reviewer'))
        with self.assertRaisesRegex(ValueError, 'DIFFERENT_PROVIDER'):
            validate_graders(investigator, config('openai', 'other'), config('anthropic'), config('anthropic'))
        with self.assertRaisesRegex(ValueError, 'DIFFERENT_MODEL'):
            validate_graders(investigator, config('anthropic'), investigator, config('anthropic'))

    def test_factory_dispatches_both_without_ticket_controls(self):
        budget = Mock(); budget.rate.model = 'synthetic'
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            self.assertEqual(client(config('openai'), budget=budget, record=Mock()).provider, 'openai')
            self.assertEqual(client(config(), budget=budget, record=Mock()).model, 'synthetic')
        with self.assertRaisesRegex(ValueError, 'CONFIGURATION_SHAPE'):
            client({**config(), 'ticket_provider_override': 'evil'}, budget=budget, record=Mock())
