from pathlib import Path
import unittest


class PlatformTemplateTests(unittest.TestCase):
    def test_compute_only_preserves_explicit_existing_database_host(self):
        from deploy_platform import validate_staged_postgres
        with self.assertRaisesRegex(ValueError, 'EXPLICIT_POSTGRES_HOST'):
            validate_staged_postgres({'deployCompute': True, 'deployPostgres': False})
        validate_staged_postgres({'deployCompute': True, 'deployPostgres': False,
                                 'existingPostgresHost': 'example.postgres.database.azure.com'})
        validate_staged_postgres({'deployCompute': False, 'deployPostgres': False})
        source = (Path(__file__).resolve().parents[1] / 'infra/platform/platform.bicep').read_text(encoding='utf8')
        self.assertIn('postgres!.properties.fullyQualifiedDomainName : existingPostgresHost', source)

    def test_no_log_storage_uses_arm_null_not_cli_none_string(self):
        source = (Path(__file__).resolve().parents[1] / 'infra/platform/platform.bicep').read_text(encoding='utf8')
        self.assertIn('appLogsConfiguration: { destination: null }', source)
        self.assertNotIn("destination: 'none'", source)
        self.assertNotIn('Microsoft.OperationalInsights/workspaces', source)


if __name__ == '__main__':
    unittest.main()
