"""Permission on a policy table is not proof the month's policy exists."""
import unittest
from unittest.mock import Mock,patch
from investigator.adapters.access_probes import LiveProbes,ProbeFailure


class Tests(unittest.TestCase):
    def run_probe(self, exists):
        db=Mock()
        db.execute.side_effect=[Mock(fetchone=lambda:('investigator','id-dia-worker','on',True)),
                                Mock(fetchone=lambda:('id-dia-worker',exists))]
        connect=Mock();connect.return_value.__enter__=Mock(return_value=db)
        connect.return_value.__exit__=Mock(return_value=False)
        token=Mock(get_token=lambda *args:'synthetic-token-not-a-credential')
        bindings={'host':'platform.postgres.database.azure.com','database':'investigator','user':'id-dia-worker',
                  'channel':'worker:state','table':'dia_state.state_accounts','budget_period':'current'}
        with patch('investigator.adapters.vault_user_cache.provider',return_value=token),\
             patch('investigator.postgres_connection.connect',connect),\
             patch('investigator.live_gateway.authorize_platform_database'),\
             patch('investigator.adapters.platform_credentials.trust_roots',return_value='synthetic-ca'):
            result=LiveProbes({})._postgres(bindings,{'mode':'managed_identity'})
        return result,db

    def test_existing_current_policy_is_checked_read_only_as_worker(self):
        result,db=self.run_probe(True)
        self.assertTrue(result['budget_account_exists'])
        self.assertTrue(result['budget_account'].startswith('model-microdollars:'))
        self.assertEqual(db.execute.call_count,2)
        for args in db.execute.call_args_list:
            self.assertTrue(args.args[0].startswith('SELECT '))
            self.assertNotIn('INSERT',args.args[0])

    def test_permission_without_current_policy_refuses_instead_of_creating(self):
        with self.assertRaisesRegex(ProbeFailure,'MONTHLY_MODEL_ACCOUNT_NOT_PROVISIONED'):
            self.run_probe(False)


if __name__=='__main__':unittest.main()
