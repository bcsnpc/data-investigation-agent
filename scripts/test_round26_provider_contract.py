from copy import deepcopy
import unittest
from investigator.adapters.provider_contract import Usage, anthropic_reply, openai_reply, openai_request


class ProviderContractTests(unittest.TestCase):
    def response(self):
        return {'id': 'r', 'model': 'synthetic', 'status': 'completed', 'output': [
            {'type': 'function_call', 'call_id': 'call1', 'name': 'run_sql', 'arguments': '{"query":"SELECT 1"}'}],
            'usage': {'input_tokens': 100, 'input_tokens_details': {'cached_tokens': 80, 'cache_write_tokens': 10}, 'output_tokens': 4}}

    def test_openai_cache_counts_are_subsets_not_double_counted(self):
        reply = openai_reply(self.response())
        self.assertEqual(reply.usage.budget_usage(), {'input_tokens': 10, 'cache_read_input_tokens': 80,
                         'cache_creation_input_tokens': 10, 'output_tokens': 4})
        self.assertEqual(reply.usage.cache_read_ratio, .8)
        self.assertEqual(reply.compatible()['content'][0]['input'], {'query': 'SELECT 1'})

    def test_anthropic_cache_counts_are_additive(self):
        reply = anthropic_reply({'id': 'r', 'model': 'a', 'content': [], 'stop_reason': 'end_turn',
            'usage': {'input_tokens': 10, 'cache_read_input_tokens': 80, 'cache_creation_input_tokens': 10, 'output_tokens': 4}})
        self.assertEqual(reply.usage.input_tokens, 100)

    def test_call_result_ids_and_tool_schema_survive_roundtrip(self):
        messages = [{'role': 'assistant', 'content': [{'type': 'tool_use', 'id': 'call1', 'name': 'run_sql', 'input': {'query': 'SELECT 1'}}]},
                    {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': 'call1', 'content': 'one'}]}]
        tools = [{'name': 'run_sql', 'description': 'Read', 'input_schema': {'type': 'object'}}]
        original = deepcopy(messages)
        body = openai_request(model='m', system='stable', messages=messages, tools=tools, max_tokens=10, explicit_cache=True)
        self.assertEqual(body['input'][1]['call_id'], body['input'][2]['call_id'])
        self.assertEqual(body['tools'][0]['parameters'], tools[0]['input_schema'])
        self.assertEqual(messages, original)
        self.assertFalse(body['store'])
        self.assertIn('prompt_cache_breakpoint', body['input'][0]['content'][0])

    def test_content_change_does_not_get_hidden_by_codec(self):
        a = self.response(); b = deepcopy(a); b['output'][0]['arguments'] = '{"query":"SELECT 2"}'
        self.assertNotEqual(openai_reply(a).content, openai_reply(b).content)

    def test_invalid_usage_and_unfinished_responses_refuse(self):
        for counts in ((10, 11, 0, 1), (10, 0, 0, -1), (True, 0, 0, 0)):
            with self.assertRaises(ValueError): Usage(*counts)
        r = self.response(); r['status'] = 'failed'
        with self.assertRaises(ValueError): openai_reply(r)
