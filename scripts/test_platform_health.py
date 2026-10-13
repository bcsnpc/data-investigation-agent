import copy
import io
import json
import os
import unittest
from urllib.error import HTTPError
from unittest.mock import Mock, patch
from investigator.live_gateway import configured, GatewayDenied
from platform_health import plan, permissions, run, PG_QUERY


IDENTITY = {'mode': 'managed_identity', 'client_id': '11111111-1111-4111-8111-111111111111',
            'tenant_id': '22222222-2222-4222-8222-222222222222', 'principal_id': '33333333-3333-4333-8333-333333333333'}
CONFIG = {'version': 1, 'identity': IDENTITY, 'state_channel': 'worker:state', 'metadata_channel': 'worker:metadata',
          'postgres': {'host': 'platform.postgres.database.azure.com', 'database': 'tool_state', 'user': 'worker'},
          'blob': {'account_url': 'https://platform.blob.core.windows.net', 'container': 'captures'},
          'key_vault': {'vault_url': 'https://platform.vault.azure.net'}, 'nonce': 'abcdef0123456789', 'receipt_key': 'a' * 64}


def policy(config=CONFIG):
    grants = permissions(config)['http']
    return {'version': 1, 'live_enabled': True, 'identities': {
        'worker:state': {'role': 'platform', 'platform_databases': [{'host': config['postgres']['host'], 'database': config['postgres']['database']}],
                         'http': [{k: v for k, v in grant.items() if k != 'identity'} for grant in grants if grant['identity'] == 'worker:state']},
        'worker:metadata': {'http': [{k: v for k, v in grant.items() if k != 'identity'} for grant in grants if grant['identity'] == 'worker:metadata']}}}


class Reply(io.BytesIO):
    def __init__(self, raw, status):
        super().__init__(raw); self.status = status; self.headers = {'x-ms-request-id': 'request-id'}


class PlatformHealthTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'DIA_LIVE_ACCESS_DISABLED': '0'})
        self.env.start(); self.addCleanup(self.env.stop)

    def test_exact_policy_checked_before_any_token_or_connection(self):
        tokens = Mock(); pg = Mock(); opener = Mock()
        wrong = policy(); wrong['identities']['worker:state']['http'] = []
        with configured(wrong), self.assertRaises(GatewayDenied):
            run(CONFIG, tokens=tokens, opener=opener, pg_read=pg)
        tokens.get_token.assert_not_called(); pg.assert_not_called(); opener.open.assert_not_called()

    def test_platform_round_trip_is_bounded_and_never_reveals_secret_names_or_tokens(self):
        planned = plan(CONFIG); calls = []; saved = {}
        def opened(request, timeout):
            calls.append((request.get_method(), request.full_url))
            self.assertEqual(timeout, 30)
            if request.get_method() == 'PUT':
                if request.full_url == planned['blob_url']: self.assertEqual(request.data, planned['body'])
                saved[request.full_url] = request.data
                self.assertEqual(request.get_header('If-none-match'), '*')
                return Reply(b'', 201)
            if request.full_url in saved: return Reply(saved[request.full_url], 200)
            return Reply(json.dumps({'value': [{'id': 'https://platform.vault.azure.net/secrets/PRIVATE_SECRET_NAME'}],
                                     'nextLink': 'https://other.example/not-followed'}).encode(), 200)
        tokens = Mock(); tokens.get_token.return_value = 'PRIVATE_BEARER_TOKEN'
        pg = Mock(return_value=['tool_state', 'worker', 'on', 2, 1, 3, 4])
        with configured(policy()):
            result = run(CONFIG, tokens=tokens, opener=Mock(open=opened), pg_read=pg)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(len(calls), 5); self.assertEqual(result['control_operations'], 6)
        self.assertFalse(result['checks']['key_vault']['secret_read_verified'])
        self.assertTrue(result['checks']['key_vault']['more_pages_not_followed'])
        self.assertNotIn('PRIVATE_SECRET_NAME', json.dumps(result)); self.assertNotIn('PRIVATE_BEARER_TOKEN', json.dumps(result))
        self.assertNotIn('INSERT', PG_QUERY); self.assertNotIn('UPDATE', PG_QUERY)
        retained = json.loads(saved[planned['receipt_url']])
        self.assertEqual(retained['checks'], result['checks'])
        self.assertEqual(retained['receipts'], result['receipts'])
        self.assertTrue(result['receipt_publication']['byte_verified'])

    def test_kill_switch_and_estate_container_are_refused(self):
        config = copy.deepcopy(CONFIG); config['blob']['container'] = 'estate'
        with self.assertRaises(ValueError): plan(config)
        tokens = Mock()
        with configured(policy()), patch.dict(os.environ, {'DIA_LIVE_ACCESS_DISABLED': '1'}), self.assertRaises(GatewayDenied):
            run(CONFIG, tokens=tokens)
        tokens.get_token.assert_not_called()

    def test_forbidden_vault_is_fact_not_secret_read_capability(self):
        planned = plan(CONFIG); saved = {}
        def opened(request, timeout):
            if request.get_method() == 'PUT':
                saved[request.full_url] = request.data
                return Reply(b'', 201)
            if request.full_url in saved: return Reply(saved[request.full_url], 200)
            if request.full_url in saved: return Reply(saved[request.full_url], 200)
            raise HTTPError(request.full_url, 403, 'Forbidden', {'x-ms-request-id': 'denied-id'}, io.BytesIO(b'secret-bearing-error'))
        with configured(policy()):
            result = run(CONFIG, tokens=Mock(get_token=Mock(return_value='token')), opener=Mock(open=opened),
                         pg_read=Mock(return_value=['tool_state', 'worker', 'on', 2, 1, 3, 4]))
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['receipts'][-1]['status'], 403)
        self.assertEqual(result['receipts'][-1]['request_id'], 'denied-id')
        self.assertNotIn('secret-bearing', json.dumps(result))
        retained = json.loads(saved[planned['receipt_url']])
        self.assertEqual(retained['status'], 'FAIL')
        self.assertEqual(retained['receipts'][-1]['status'], 403)

    def test_postgres_read_only_attestation_required(self):
        planned = plan(CONFIG); saved = {}
        def opened(request, timeout):
            if request.get_method() == 'PUT':
                saved[request.full_url] = request.data
                return Reply(b'', 201)
            if request.full_url in saved: return Reply(saved[request.full_url], 200)
            return Reply(planned['body'] if request.full_url == planned['blob_url'] else b'{"value":[]}', 200)
        with configured(policy()):
            result = run(CONFIG, tokens=Mock(), opener=Mock(open=opened),
                         pg_read=Mock(return_value=['tool_state', 'worker', 'off', 2, 1, 3, 4]))
        self.assertEqual(result['checks']['postgres']['status'], 'FAIL')


if __name__ == '__main__': unittest.main()
