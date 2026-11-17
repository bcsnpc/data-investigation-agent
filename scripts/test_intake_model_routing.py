import unittest
from investigator.adapters.provider_runtime import intake_selection


def config(model, provider='anthropic'):
    return {'model': model, 'provider': provider, 'rate_card': {},
            'secret_reference': 'existing-reference', 'gateway_identity': 'existing-gateway',
            'worker_identity': 'existing-worker'}


class RoutingTests(unittest.TestCase):
    def test_intake_defaults_to_investigator_not_cheap_or_fallback(self):
        routing = {'steps': {'INTAKE': config('cheap', 'openai'),
                             'INVESTIGATOR': config('opus-configured'),
                             'INTAKE_FALLBACK': config('fallback', 'openai')}}
        selected = intake_selection(routing, tenant='test')
        self.assertEqual(selected['model'], 'opus-configured')
        self.assertEqual(selected['provider'], 'anthropic')
        selected['worker_identity'] = 'mutated'
        self.assertEqual(routing['steps']['INVESTIGATOR']['worker_identity'], 'existing-worker')

    def test_config_options_remain_explicit(self):
        routing = {'steps': {'INTAKE': config('configured'), 'INVESTIGATOR': config('reasoning')}}
        for strategy in ('configured', 'cascade'):
            self.assertEqual(intake_selection(routing, tenant='test', strategy=strategy)['model'], 'configured')
        with self.assertRaisesRegex(ValueError, 'STRATEGY'):
            intake_selection(routing, tenant='test', strategy='ticket-says-so')


if __name__ == '__main__':
    unittest.main()
