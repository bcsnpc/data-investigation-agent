import copy
import io
import json
import unittest
from unittest.mock import Mock,patch

from platform_auth_preflight import run,validate,main
from test_vault_user_cache import D,CACHE
from test_managed_identity_auth import token,CLIENT
from investigator.adapters.vault_user_cache import PBI,SQL,Tokens


CONFIG={'version':1,'readers':[{'channel':'reader:pbi','authentication':D},
        {'channel':'reader:sql','authentication':D|{'scope':SQL,'client_id':CLIENT}}],
        'model_key':{'channel':'worker:model-auth','reference':D['reference']}}


class AuthPreflightTests(unittest.TestCase):
    def test_separate_channels_and_no_token_or_key_in_outputs(self):
        factory=Mock(side_effect=lambda declaration,**kw:Mock(get_token=Mock(return_value=token(declaration['scope']))))
        secret=Mock(return_value='secret-model-key')
        result=run(CONFIG,tokens_factory=factory,secret_reader=secret)
        self.assertEqual(result['status'],'PASS')
        self.assertEqual([c.kwargs['gateway_identity'] for c in factory.call_args_list],['reader:pbi','reader:sql'])
        secret.assert_called_once_with(D['reference'],gateway_identity='worker:model-auth')
        text=json.dumps(result)
        for sensitive in ('secret-model-key',token(PBI),token(SQL),'RefreshToken','secret_version'):
            self.assertNotIn(sensitive,text)
        self.assertEqual((result['estate_reads'],result['model_calls']),(0,0))

    def test_wrong_identity_and_secret_failure_are_sanitized(self):
        factory=Mock(return_value=Mock(get_token=Mock(return_value=token(oid=CLIENT))))
        result=run(CONFIG,tokens_factory=factory,secret_reader=Mock(side_effect=RuntimeError('private-refresh-token')))
        self.assertEqual(result['status'],'FAIL')
        self.assertTrue(all(row['status']=='FAIL' for row in result['checks']))
        self.assertNotIn('private-refresh',json.dumps(result))

    def test_same_client_endpoint_requires_distinct_logical_channels(self):
        config=copy.deepcopy(CONFIG);config['readers'][1]['channel']='reader:pbi'
        with self.assertRaisesRegex(ValueError,'DISTINCT'):validate(config)

    def test_named_channel_reaches_vault_and_msal_without_disk(self):
        loader=Mock(return_value=json.dumps(CACHE));app=Mock()
        app.get_accounts.return_value=[CACHE['cache']['Account']['one']]
        app.acquire_token_silent.return_value={'access_token':token()}
        application=Mock(return_value=app)
        Tokens(D,loader=loader,application=application,gateway_identity='reader:pbi').get_token(PBI)
        loader.assert_called_once_with(D['reference'],gateway_identity='reader:pbi')
        self.assertEqual(application.call_args.kwargs['http_client'].gateway_identity,'reader:pbi')

    def test_runtime_channels_separate_clients_sharing_the_same_token_endpoint(self):
        from investigator.adapters.vault_user_cache import channel
        self.assertEqual(channel(D),'user-cache:'+D['client_id']+':powerbi')
        self.assertEqual(channel(D|{'scope':SQL}),'user-cache:'+D['client_id']+':sql')
        for declaration in (D,D|{'scope':SQL}):
            provider=Tokens(declaration)
            self.assertEqual(provider.gateway_identity,channel(declaration))

    def test_cli_errors_never_print_environment_or_provider_details(self):
        output=io.StringIO()
        with patch('sys.argv',['platform_auth_preflight.py','--environment-config']), \
                patch.dict('os.environ',{'DIA_PLATFORM_AUTH_CONFIG':'raw-private-value'}),patch('sys.stdout',output):
            self.assertEqual(main(),1)
        self.assertNotIn('raw-private-value',output.getvalue())


if __name__=='__main__':unittest.main()
