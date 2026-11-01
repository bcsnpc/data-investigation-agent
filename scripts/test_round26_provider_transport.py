from copy import deepcopy
from unittest.mock import Mock, patch
import unittest
from investigator.adapters.reasoning_openai import Client, ProviderHTTPError, authorize_body, endpoint
from investigator.adapters.provider_contract import openai_request


class ProviderTransportTests(unittest.TestCase):
    def test_anthropic_urlerror_regression_retries_without_zeroing_unknown_usage(self):
        from investigator.adapters.reasoning_anthropic import Client as Anthropic
        from urllib.error import URLError
        budget=Mock();budget.rate.model='synthetic';budget.reserve.return_value='r'
        send=Mock(side_effect=[URLError('connection reset'),{'content':[],'usage':{'input_tokens':1,'output_tokens':1}}])
        sleep=Mock()
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            client=Anthropic(model='synthetic',budget=budget,identity='reader',secret_reference={},
                record=Mock(),send=send,sleep=sleep)
        client.complete(system='fixed',messages=[],tools=self.tools())
        self.assertEqual(budget.reserve.call_count,2)
        budget.settle.assert_any_call('r')
        sleep.assert_called_once_with(30)

    def test_count_connection_reset_retries_before_any_paid_dispatch(self):
        send=Mock(side_effect=[ConnectionResetError(),{'input_tokens':123},self.response()])
        sleep=Mock();client=self.client(send=send,count_tokens=True,sleep=sleep)
        client.complete(system='fixed',messages=[],tools=self.tools())
        self.assertEqual(client.budget.reserve.call_count,1)
        self.assertEqual(send.call_args_list[0].args[1],send.call_args_list[1].args[1])
        sleep.assert_called_once_with(30)

    def test_paid_connection_reset_keeps_unknown_charge_and_retries_with_new_reservation(self):
        send=Mock(side_effect=[ConnectionResetError(),self.response()]);sleep=Mock()
        client=self.client(send=send,sleep=sleep)
        client.complete(system='fixed',messages=[],tools=self.tools())
        self.assertEqual(client.budget.reserve.call_count,2)
        client.budget.settle.assert_any_call('reservation')
        sleep.assert_called_once_with(30)

    @patch.dict('os.environ', {'DIA_LIVE_ACCESS_DISABLED': '0'})
    def test_gateway_allows_only_tenant_configured_provider_for_every_component(self):
        from investigator.live_gateway import Gateway, GatewayDenied
        body = openai_request(model='synthetic', system='fixed', messages=[], tools=self.tools(), max_tokens=10)
        for component in ('investigator', 'screenshot', 'summary', 'enrichment', 'writer', 'grader', 'reviewer', 'smoke'):
            spec = {'endpoint': 'https://api.openai.com/v1', 'models': ['synthetic'], 'tools': ['run_sql']}
            policy = {'version': 1, 'live_enabled': True, 'identities': {component: {
                'role': 'model', 'ai_providers': {'openai': spec}, 'http': [
                    {'method': 'POST', 'url': spec['endpoint'] + '/responses', 'purpose': 'configured_ai'}]}}}
            gateway = Gateway(policy)
            gateway.http(component, 'POST', spec['endpoint'] + '/responses', __import__('json').dumps(body).encode())
            with self.assertRaises(GatewayDenied):
                gateway.http(component, 'POST', 'https://unconfigured.openai.azure.com/openai/v1/responses', b'{}')

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

    def test_native_count_is_used_for_reservation_and_rate_tier(self):
        send = Mock(side_effect=[{'input_tokens': 123}, self.response()])
        client = self.client(send=send, count_tokens=True)
        client.complete(system='s', messages=[], tools=self.tools())
        self.assertEqual(send.call_args_list[0].args[1], 'https://api.openai.com/v1/responses/input_tokens')
        self.assertEqual(client.budget.reserve.call_args.kwargs['input_tokens_upper_bound'], 4219)
        send = Mock(return_value={'input_tokens': 272001})
        client = self.client(send=send, count_tokens=True)
        with self.assertRaisesRegex(Exception, 'RATE_CONTEXT_BOUND'):
            client.complete(system='s', messages=[], tools=self.tools())
        client.budget.reserve.assert_not_called()

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

    def test_investigation_prefix_stays_stable_and_later_zero_reads_fail_assertion(self):
        from investigator.adapters.anthropic_prompt_cache import assert_cache_reads
        send = Mock(return_value=self.response())
        client = self.client(send=send, explicit_cache=True)
        tools = self.tools() + [{'name': 'submit_finding', 'description': 'Deliver', 'input_schema': {'type': 'object'}}]
        client.complete(system='original stable path', messages=[{'role': 'user', 'content': 'step1'}], tools=tools)
        first = deepcopy(send.call_args.args[2])
        client.complete(system='changed path timestamp', messages=[{'role': 'user', 'content': 'step2'}], tools=self.tools() + tools[1:])
        second = send.call_args.args[2]
        self.assertEqual(first['tools'], second['tools'])
        self.assertEqual(first['input'][0], second['input'][0])
        self.assertNotEqual(first['input'][1:], second['input'][1:])
        records = [c.args[0] for c in client.record.call_args_list if c.args[0]['event'] == 'REASONING_CACHE_USAGE']
        assert_cache_reads(records)
        records[-1]['cache_read_input_tokens'] = 0
        with self.assertRaisesRegex(AssertionError, 'ZERO_CACHE_READS'):
            assert_cache_reads(records)
