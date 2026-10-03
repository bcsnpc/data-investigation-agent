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
        payload={'outcome':'NO_COMPARABLE_PATH','evidence':[{'id':'receipt-A'}]}
        answer={'technical_output':{'text':'The calculation was checked.','evidence_ids':['r0']}}
        with patch('ticket_planner.azure_generate',return_value=(answer,{})) as provider:
            evidence_synthesis.azure_synthesize(payload,{})
            sent=provider.call_args.kwargs
            supplied=json.loads(sent['instructions'].split('fields:\n')[1])
            self.assertEqual(supplied,vocabulary.enumerations(sent['schema']))
            self.assertIn('Return only the technical mechanism',sent['instructions'])
            self.assertNotIn('Copy the business wording',sent['instructions'])
        value={'judgment':'INDETERMINATE','explanation':'The definition is incomplete.','limitation':'Coverage remains unknown.'}
        with patch('ticket_planner._azure_generate',return_value=(value,{})) as provider:
            judge.azure_judge({}, {})
            self.assertEqual(provider.call_args.kwargs['instructions'],vocabulary.instructions(judge.INSTRUCTIONS,provider.call_args.kwargs['schema']))

    def test_synthesis_has_no_limitations_channel_and_judge_limits_remain_prose(self):
        self.assertNotIn('limitations',narrative.schema({'evidence':[]})['properties'])
        wire=judge.SCHEMA['properties']['limitation']
        self.assertNotIn('enum',wire)
        for text in ('Actual repeated matches have not been established.','Intended business semantics are not confirmed.'):
            Draft202012Validator(wire).validate(text)
        mechanism=narrative.schema({'evidence':[]})['properties']['technical_output']['properties']['text']
        with self.assertRaises(Exception):Draft202012Validator(mechanism).validate('The fixed boundary account states the results.')
