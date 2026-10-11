import copy
import json
import unittest
from investigator.agent_shared_input import encode, decode, REF


class SharedInputTests(unittest.TestCase):
    def test_every_nested_field_survives_lossless_sharing_and_original_unchanged(self):
        scope = {'definition': 'exact retained prose. '*200,
                 'metadata': {'surface': 'object', 'snapshot': None},
                 'comparison': {'equal': False, 'input': 3, 'output': 4}}
        value = {'evidence': {'a': {'result': scope}}, 'transcript': [{'result': copy.deepcopy(scope)}],
                 'scope_registry': {'scope-id': copy.deepcopy(scope)}}
        original = copy.deepcopy(value)
        packet = encode(value)
        self.assertEqual(value, original)
        self.assertEqual(decode(packet), original)
        self.assertLess(len(json.dumps(packet)), len(json.dumps(value)) / 2)

    def test_unknown_and_cyclic_references_refuse(self):
        packet = encode({'x': 1})
        packet['payload'] = {REF: 'missing'}
        with self.assertRaisesRegex(ValueError, 'REFERENCE'): decode(packet)
        packet['shared_values']['missing'] = {REF: 'missing'}
        with self.assertRaisesRegex(ValueError, 'REFERENCE'): decode(packet)

    def test_untrusted_reference_collision_refuses_instead_of_reinterpreting(self):
        with self.assertRaisesRegex(ValueError, 'RESERVED_KEY'): encode({REF: 'spoofed'})
