from copy import deepcopy
from unittest.mock import Mock, patch
import unittest
from investigator.adapters.provider_runtime import client, select, validate_graders


def config(provider='anthropic', model='synthetic'):
    return {'provider': provider, 'model': model, 'rate_card': {}, 'secret_reference': {},
            'gateway_identity': 'reader', 'worker_identity': 'worker'}


class ProviderRuntimeTests(unittest.TestCase):
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
