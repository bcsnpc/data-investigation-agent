from pathlib import Path
import unittest


class PlatformTemplateTests(unittest.TestCase):
    def test_no_log_storage_uses_arm_null_not_cli_none_string(self):
        source = (Path(__file__).resolve().parents[1] / 'infra/platform/platform.bicep').read_text(encoding='utf8')
        self.assertIn('appLogsConfiguration: { destination: null }', source)
        self.assertNotIn("destination: 'none'", source)
        self.assertNotIn('Microsoft.OperationalInsights/workspaces', source)


if __name__ == '__main__':
    unittest.main()
