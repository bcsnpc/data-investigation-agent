import unittest
from investigator import estate_manifest, usage_limits
from investigator.usage_governance import UsageGovernor
from test_investigator_workspace import WorkspaceTests


class DailyInputConfigurationTests(unittest.TestCase):
    def test_configuration_and_governor_share_input_bound_without_granting_it(self):
        maximum=usage_limits.DAILY_MAXIMUM['input_characters']
        schema=estate_manifest.SCHEMA['properties']['budgets']['properties']['planner_daily']['properties']['input_characters']
        self.assertEqual(schema['maximum'],maximum)
        h=WorkspaceTests();h.setUp();self.addCleanup(h.doCleanups)
        original=h.agent.governor.snapshot()['reserved_today']
        policy=dict(h.agent.governor.policy)
        policy['daily_limits']=dict(policy['daily_limits'],input_characters=25000000)
        governor=UsageGovernor(h.agent.runtime,policy,h.agent.clock)
        self.assertEqual(governor.snapshot()['reserved_today'],original)
        self.assertEqual(governor.snapshot()['limits']['input_characters'],25000000)
        policy['daily_limits']['input_characters']=maximum+1
        with self.assertRaises(ValueError):UsageGovernor(h.agent.runtime,policy,h.agent.clock)


if __name__=='__main__':unittest.main()
