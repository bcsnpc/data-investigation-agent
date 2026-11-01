from copy import deepcopy
import unittest
from unittest.mock import patch

from investigator.live_gateway import Gateway, GatewayDenied


@patch.dict('os.environ', {'DIA_LIVE_ACCESS_DISABLED':'0'})
class ConfiguredAnthropicTests(unittest.TestCase):
    def gateway(self, identity='writer'):
        return Gateway({'version':1,'live_enabled':True,'identities':{identity:{
            'role':'model','ai_providers':{'anthropic':{'endpoint':'https://api.anthropic.com',
                'models':['synthetic-model'],'tools':['resolve_intake']}},
            'http':[{'method':'POST','url':'https://api.anthropic.com/v1/'+suffix,'purpose':'configured_ai'}
                    for suffix in ('messages','messages/count_tokens')]}}})

    def body(self):
        return {'model':'synthetic-model','system':[{'type':'text','text':'Fixed instructions',
            'cache_control':{'type':'ephemeral'}}],'messages':[{'role':'user','content':'Synthetic facts'}],
            'tools':[{'name':'resolve_intake','description':'Return data only','input_schema':{'type':'object'}}],
            'max_tokens':100}

    def test_every_component_accepts_only_its_configured_anthropic_model_and_tools(self):
        for identity in ('investigator','intake','screenshot','summary','enrichment','writer','grader','reviewer','smoke'):
            with self.subTest(identity=identity):
                gateway=self.gateway(identity);body=self.body();before=deepcopy(body)
                gateway.http(identity,'POST','https://api.anthropic.com/v1/messages',body)
                counted=deepcopy(body);counted.pop('max_tokens')
                gateway.http(identity,'POST','https://api.anthropic.com/v1/messages/count_tokens',counted)
                self.assertEqual(body,before)
                for key,value in [('model','not-configured'),('tools',[{**body['tools'][0],'name':'run_sql'}])]:
                    wrong={**body,key:value}
                    with self.assertRaises(GatewayDenied):
                        gateway.http(identity,'POST','https://api.anthropic.com/v1/messages',wrong)

    def test_configured_route_does_not_fall_back_to_legacy_or_another_vendor(self):
        from investigator.adapters.configured_ai_policy import authorize_body
        with self.assertRaisesRegex(ValueError,'PROVIDER_NOT_CONFIGURED'):
            authorize_body({'reasoning_models':['synthetic-model']},'POST',
                           'https://api.anthropic.com/v1/messages',self.body())
        with self.assertRaises(GatewayDenied):
            self.gateway().http('writer','POST','https://api.openai.com/v1/responses',{})

    def test_process_live_disable_still_overrides_configured_provider(self):
        with patch.dict('os.environ', {'DIA_LIVE_ACCESS_DISABLED':'1'}):
            with self.assertRaisesRegex(GatewayDenied, 'LIVE_ACCESS_DISABLED'):
                self.gateway().http('writer','POST','https://api.anthropic.com/v1/messages',self.body())


if __name__=='__main__':unittest.main()
