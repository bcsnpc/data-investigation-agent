from copy import deepcopy
import unittest
from jsonschema import Draft202012Validator,ValidationError
from investigator.adapters.reasoning_anthropic import wire_tools
from investigator.ai_investigation import toolbox


class Tests(unittest.TestCase):
    def test_provider_scope_is_factored_but_local_unknown_identifiers_still_fail(self):
        layers={'native:'+'a'*20:{'dialect':'T-SQL'}}
        tools=toolbox(layers,{})
        original=deepcopy(tools);wire=wire_tools(tools)
        self.assertEqual(tools,original)
        local=next(t for t in tools if t['name']=='run_sql')['input_schema']
        presented=next(t for t in wire if t['name']=='run_sql')['input_schema']
        valid={'layer':next(iter(layers)),'query':'SELECT 1','purpose':'compare'}
        Draft202012Validator(local).validate(valid)
        invalid={**valid,'layer':'unadmitted'}
        Draft202012Validator(presented).validate(invalid)
        with self.assertRaises(ValidationError):Draft202012Validator(local).validate(invalid)
        self.assertEqual(local['properties']['purpose'],presented['properties']['purpose'])

    def test_wire_schema_stays_stable_after_layer_expansion(self):
        a={'native:'+'a'*20:{'dialect':'T-SQL'}}
        b={**a,'native:'+'b'*20:{'dialect':'T-SQL'}}
        self.assertEqual(wire_tools(toolbox(a,{})),wire_tools(toolbox(b,{})))


if __name__=='__main__':unittest.main()
