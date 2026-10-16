import copy
import unittest
from jsonschema import Draft202012Validator
from investigator.agent_wire import schema
from investigator.agent_loop import decision_schema
from investigator.agent_intake_tools import SCHEMAS
from investigator.agent_intake_settlement import SCHEMA
from investigator.investigation_tools import schemas


class WireTests(unittest.TestCase):
    def test_complete_registered_contract_is_provider_subset_without_mutation(self):
        tools = {**SCHEMAS, **{d['name']: d['parameters'] for d in schemas()}, 'resolve_ticket': SCHEMA}
        consumer = {'type': 'object', 'additionalProperties': False,
                    'properties': {'decision': decision_schema(tools, ['HELD'])}, 'required': ['decision']}
        before = copy.deepcopy(consumer)
        wire = schema(consumer)
        self.assertEqual(consumer, before)
        def check(node):
            if isinstance(node, dict):
                self.assertNotIn('uniqueItems', node)
                self.assertNotIn('const', node)
                for child in node.values(): check(child)
            elif isinstance(node, list):
                for child in node: check(child)
        check(wire)
        text = str(wire)
        self.assertIn('uniqueItems', text)  # field description retains obligation

    def test_duplicate_and_oversized_values_still_refused_by_consumer(self):
        consumer = {'type': 'object', 'additionalProperties': False, 'required': ['ids'],
            'properties': {'ids': {'type': 'array', 'uniqueItems': True, 'maxItems': 2,
                                  'items': {'type': 'string', 'enum': ['a', 'b']}}}}
        wire = schema(consumer)
        for value in ({'ids': ['a', 'a']}, {'ids': ['a', 'b', 'a']}):
            Draft202012Validator(wire).validate(value)
            self.assertFalse(Draft202012Validator(consumer).is_valid(value))

    def test_native_enum_changes_still_rejected_on_wire(self):
        consumer = {'type': 'object', 'additionalProperties': False, 'required': ['kind'],
                    'properties': {'kind': {'type': 'string', 'enum': ['READ']}}}
        self.assertFalse(Draft202012Validator(schema(consumer)).is_valid({'kind': 'WRITE'}))
