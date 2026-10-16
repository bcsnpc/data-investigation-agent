import unittest
from types import SimpleNamespace as N
from investigator.agent_response import final_text
from investigator.generation_policy import ProviderResponseError


def message(text, phase=None, **changes):
    return N(**{'type': 'message', 'phase': phase, 'status': 'completed',
                'role': 'assistant', 'content': [N(type='output_text', text=text)], **changes})


class Tests(unittest.TestCase):
    def test_commentary_is_not_a_decision_even_if_it_is_valid_json(self):
        response = N(output=[message('{"decision":"wrong"}', 'commentary'),
                             message('{"decision":"final"}', 'final_answer')])
        self.assertEqual(final_text(response), '{"decision":"final"}')

    def test_duplicate_native_decisions_decode_once_by_phase(self):
        value = '{"decision":{"action":"TOOL"}}'
        self.assertEqual(final_text(N(output=[message(value, 'commentary'),
                                             message(value, 'final_answer')])), value)

    def test_ambiguous_or_missing_final_refuses_without_content_deduplication(self):
        for messages in ([message('{}', 'commentary')],
                         [message('{}', 'final_answer'), message('{}', 'final_answer')],
                         [message('{}'), message('{}')],
                         [message('{}', 'final_answer'), message('{}')]):
            with self.subTest(messages=len(messages)), self.assertRaises(ProviderResponseError):
                final_text(N(output=messages), {'output_tokens': 8})

    def test_single_legacy_message_and_final_content_chunks(self):
        self.assertEqual(final_text(N(output=[message('{}')])), '{}')
        m = message('', 'final_answer'); m.content = [N(type='output_text', text='{'), N(type='output_text', text='}')]
        self.assertEqual(final_text(N(output=[m])), '{}')

    def test_incomplete_final_and_non_assistant_refuse(self):
        for changes in ({'status': 'incomplete'}, {'role': 'user'}):
            with self.subTest(changes=changes), self.assertRaises(ProviderResponseError):
                final_text(N(output=[message('{}', 'final_answer', **changes)]))

    def test_unexpected_function_call_is_not_silently_ignored(self):
        with self.assertRaises(ProviderResponseError):
            final_text(N(output=[N(type='function_call'), message('{}', 'final_answer')]))
