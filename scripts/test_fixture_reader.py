import base64
import json
from unittest.mock import MagicMock, patch
import unittest
from urllib.error import HTTPError

from connect_fixture_reader import token, verify

ACCOUNT = 'reader@example.test'
TENANT = '11111111-1111-1111-1111-111111111111'
SCOPE = 'https://analysis.windows.net/powerbi/api/.default'


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.get_accounts.return_value = [{'username': ACCOUNT, 'realm': TENANT}]
        self.claims = {'upn': ACCOUNT, 'tid': TENANT, 'aud': SCOPE.removesuffix('/.default')}

    def issue(self):
        value = 'test.' + base64.urlsafe_b64encode(json.dumps(self.claims).encode()).decode().rstrip('=') + '.test'
        self.app.acquire_token_silent.return_value = {'access_token': value}
        return value

    def test_silent_token_without_id_token(self):
        value = self.issue()
        self.assertEqual(token(self.app, ACCOUNT, TENANT, SCOPE), value)
        self.app.acquire_token_interactive.assert_not_called()

    def test_wrong_identity_tenant_or_audience(self):
        for field in ('upn', 'tid', 'aud'):
            with self.subTest(field=field):
                original = self.claims[field]; self.claims[field] = 'wrong'; self.issue()
                with self.assertRaises(RuntimeError): token(self.app, ACCOUNT, TENANT, SCOPE)
                self.claims[field] = original

    def test_no_silent_fallback_to_publisher(self):
        self.app.get_accounts.return_value = []
        with self.assertRaises(RuntimeError): token(self.app, ACCOUNT, TENANT, SCOPE)
        self.app.acquire_token_interactive.assert_not_called()

    def test_combined_reader_probe_requires_identity_and_denial(self):
        self.issue()
        for name, denied, expected in [(ACCOUNT, True, True), ('publisher@example.test', True, False), (ACCOUNT, False, False)]:
            with self.subTest(name=name, denied=denied):
                def opened(request, timeout):
                    if 'refreshes?' in request.full_url and denied:
                        raise HTTPError(request.full_url, 403, 'Denied', {}, None)
                    result = MagicMock(); result.status = 200
                    result.read.return_value = json.dumps({'results': [{'tables': [{'rows': [{'[reader]': name}]}]}]}).encode()
                    result.__enter__.return_value = result
                    return result
                with patch('connect_fixture_reader.urlopen', side_effect=opened):
                    result = verify(self.app, ACCOUNT, TENANT, TENANT, TENANT)
                self.assertEqual(result['fixture_reader_checks_passed'], expected)
                self.assertFalse(result['generation_proven']); self.assertFalse(result['live_acceptance_ready'])


if __name__ == '__main__': unittest.main()
