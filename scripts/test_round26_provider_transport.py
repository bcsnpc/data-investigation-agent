from copy import deepcopy
from unittest.mock import Mock, patch
import unittest
from investigator.adapters.reasoning_openai import Client, ProviderHTTPError, authorize_body, endpoint
from investigator.adapters.provider_contract import openai_request


class ProviderTransportTests(unittest.TestCase):
    def tools(self):
        return [{'name': 'run_sql', 'description': 'Read', 'input_schema': {'type': 'object'}}]

    def response(self):
        return {'id': 'r', 'model': 'synthetic', 'status': 'completed', 'output': [],
                'usage': {'input_tokens': 100, 'output_tokens': 2,
                          'input_tokens_details': {'cached_tokens': 80}}}

    def client(self, **kwargs):
        budget = Mock(); budget.rate.model = 'synthetic'; budget.reserve.return_value = 'reservation'
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            client = Client(model='synthetic', budget=budget, identity='reader',
                            secret_reference={}, record=Mock(), **kwargs)
        return client

    def test_both_responses_endpoints_with_fake_transport(self):
        for base in ('https://api.openai.com/v1', 'https://synthetic.openai.azure.com/openai/v1'):
            send = Mock(return_value=self.response())
            client = self.client(base=base, send=send)
            result = client.complete(system='fixed', messages=[], tools=self.tools())
            self.assertEqual(send.call_args.args[:2], ('POST', base + '/responses'))
            self.assertEqual(result['usage']['input_tokens'], 20)
            client.budget.settle.assert_any_call('reservation', result['usage'])

    def test_rate_limit_retries_and_never_becomes_finding(self):
        send = Mock(side_effect=[ProviderHTTPError(429), self.response()])
        sleep = Mock(); client = self.client(send=send, sleep=sleep)
        client.complete(system='fixed', messages=[], tools=self.tools())
        self.assertEqual(send.call_count, 2)
        self.assertEqual(client.budget.reserve.call_count, 2)
        sleep.assert_called_once_with(30)

    def test_unconfigured_provider_model_server_tool_and_storage_refused(self):
        body = openai_request(model='synthetic', system='s', messages=[], tools=self.tools(), max_tokens=10)
        permissions = {'ai_providers': {'openai': {'endpoint': 'https://api.openai.com/v1',
                        'models': ['synthetic'], 'tools': ['run_sql']}}}
        authorize_body(permissions, 'POST', 'https://api.openai.com/v1/responses', body)
        authorize_body(permissions, 'GET', 'https://api.openai.com/v1/models', None)
        cases = [{}, {**body, 'model': 'not-configured'}, {**body, 'store': True},
                 {**body, 'tools': [{'type': 'web_search'}]}]
        for candidate in cases:
            with self.assertRaises(ValueError):
                authorize_body(permissions, 'POST', 'https://api.openai.com/v1/responses', candidate)
        with self.assertRaises(ValueError):
            authorize_body({}, 'POST', 'https://api.openai.com/v1/responses', body)
        for base in ('http://api.openai.com/v1', 'https://evil.test/v1', 'https://api.openai.com.evil.test/v1'):
            with self.assertRaises(ValueError): endpoint(base)

    def test_failed_request_settles_unknown_usage_without_secret_error_body(self):
        client = self.client(send=Mock(side_effect=ProviderHTTPError(401)))
        with self.assertRaisesRegex(ProviderHTTPError, '^OPENAI_HTTP_401$'):
            client.complete(system='s', messages=[], tools=self.tools())
        client.budget.settle.assert_called_with('reservation')
