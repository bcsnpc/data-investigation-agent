import unittest
from investigator.investigation_tools import schemas
from investigator.agent_intake_settlement import DESCRIPTION


class Tests(unittest.TestCase):
    def test_registered_id_sources_are_supplied_at_each_argument(self):
        for tool in schemas():
            for name, schema in tool['parameters']['properties'].items():
                if name in ('target_id', 'a', 'b'):
                    self.assertIn('target_registry', schema['description'])
                    self.assertIn('not an asset or visual ID', schema['description'])
                if name == 'scope_id':self.assertIn('scope_registry', schema['description'])

    def test_quote_source_and_measurement_versus_reproduction_are_explicit(self):
        self.assertIn('normal primary/comparison/context', DESCRIPTION)
        self.assertIn('never copied quotes', DESCRIPTION)
        reproduce=next(tool for tool in schemas() if tool['name']=='reproduce')
        self.assertIn('no reproduction verdict', reproduce['description'])
        self.assertIn('probe_layer', reproduce['description'])
