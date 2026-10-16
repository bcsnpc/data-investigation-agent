import io
import json
import unittest
from unittest.mock import Mock,patch
from urllib.error import HTTPError
from investigator.adapters.graph_change_collector import FabricChanges
from investigator.adapters.metadata_error import MetadataUnavailable,safe_failure
from metadata_auth import MetadataHttp

class GraphSafeFailureTests(unittest.TestCase):
    def test_http_error_keeps_only_bounded_status_and_known_code(self):
        error=HTTPError('https://secret-url',403,'secret reason',{'Authorization':'secret-header'},
            io.BytesIO(json.dumps({'error':{'code':'InsufficientPrivileges','message':'secret-value'}}).encode()))
        with patch('investigator.live_gateway.open_http',side_effect=error):
            try:MetadataHttp(Mock())._send(Mock())
            except MetadataUnavailable as caught:detail=safe_failure(caught)
            else:self.fail('must refuse')
        self.assertEqual(detail['http_status'],403)
        self.assertEqual(detail['provider_code'],'InsufficientPrivileges')
        self.assertNotIn('secret',json.dumps(detail))

    def test_unknown_provider_code_and_dynamic_exception_text_withheld(self):
        error=MetadataUnavailable(403,{'errorCode':'secret-value','message':'secret-message'})
        detail=safe_failure(error)
        self.assertNotIn('provider_code',detail)
        self.assertNotIn('secret',json.dumps(detail))
        self.assertNotIn('secret',json.dumps(safe_failure(RuntimeError('secret-token'))))

    def test_definition_refusal_retains_safe_code_without_keyerror(self):
        item='00000000-0000-0000-0000-000000000002'
        call=Mock(side_effect=[{'status_code':200,'text':{'value':[{'id':item,'type':'Report','displayName':'Report'}]}},
            {'status_code':403,'headers':{'secret':'secret'},'text':{'errorCode':'InsufficientPrivileges','message':'secret'}}])
        source=FabricChanges('00000000-0000-0000-0000-000000000001',[item],call)
        signal=source.list_changes()['items'][0]
        try:source.fetch(signal['owner'])
        except MetadataUnavailable as error:detail=safe_failure(error)
        else:self.fail('must refuse')
        self.assertEqual(detail['http_status'],403)
        self.assertEqual(detail['provider_code'],'InsufficientPrivileges')
        self.assertNotIn('secret',json.dumps(detail))

if __name__=='__main__':unittest.main()
