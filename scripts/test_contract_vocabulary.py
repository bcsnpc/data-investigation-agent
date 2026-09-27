import copy,json,unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator
from investigator import contract_vocabulary as vocabulary
from investigator import synthesis_narrative as narrative,transformation_judgment as judge,evidence_synthesis


class ContractVocabularyTests(unittest.TestCase):
    def test_every_synthesis_and_judge_enum_is_supplied_from_validator_schema(self):
        payload={'evidence':[{'id':'receipt-A'},{'id':'receipt-B'}]}
        for wire in (narrative.schema(payload),judge.SCHEMA):
            supplied=json.loads(vocabulary.instructions('base',wire).split('fields:\n')[1])
            self.assertEqual(supplied,vocabulary.enumerations(wire))
            self.assertTrue(supplied)
            for path,values in supplied.items():
                node=wire
                for part in path.split('/')[1:]:node=node[int(part)] if isinstance(node,list) else node[part]
                self.assertEqual(values,node['enum'])
                for value in values:Draft202012Validator(node).validate(value)
            changed=copy.deepcopy(wire)
            changed['properties']['future']={'type':'string','enum':['NEW_TERM']}
            self.assertIn('NEW_TERM',vocabulary.instructions('base',changed))

    def test_live_providers_send_the_exact_schema_vocabulary(self):
        payload={'evidence':[]}
        with patch('ticket_planner.azure_generate',return_value=({},{})) as provider:
            evidence_synthesis.azure_synthesize(payload,{})
            self.assertEqual(provider.call_args.kwargs['instructions'],vocabulary.instructions(narrative.INSTRUCTIONS,provider.call_args.kwargs['schema']))
        value={'judgment':'INDETERMINATE','explanation':'The definition is incomplete.','limitation':'Coverage remains unknown.'}
        with patch('ticket_planner._azure_generate',return_value=(value,{})) as provider:
            judge.azure_judge({}, {})
            self.assertEqual(provider.call_args.kwargs['instructions'],vocabulary.instructions(judge.INSTRUCTIONS,provider.call_args.kwargs['schema']))

    def test_additional_limits_are_not_a_false_closed_vocabulary(self):
        wire=narrative.schema({'evidence':[]})['properties']['limitations']['items']['properties']['text']
        self.assertNotIn('enum',wire)
        for text in ('Actual repeated matches have not been established.','Intended business semantics are not confirmed.'):
            Draft202012Validator(wire).validate(text)
        with self.assertRaises(Exception):Draft202012Validator(wire).validate('The fixed boundary account states the results.')
