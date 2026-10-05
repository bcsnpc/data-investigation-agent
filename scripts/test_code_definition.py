import base64,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from investigator.code_sources import read
from investigator.adapters.code_definition import fetch
from investigator import process_tape as journal

class CodeDefinitionTests(unittest.TestCase):
    source={'id':'code','kind':'PLATFORM_ITEM_API','identity':'separate-code-account',
        'workspace':'11111111-1111-1111-1111-111111111111','item_ids':['22222222-2222-2222-2222-222222222222']}
    path='22222222-2222-2222-2222-222222222222/notebook-content.py'
    def response(self):
        return {'status':200,'headers':{},'body':{'definition':{'parts':[
            {'path':'notebook-content.py','payload':base64.b64encode(b'x=1\n').decode(),'payloadType':'InlineBase64'},
            {'path':'.platform','payload':base64.b64encode(b'{"config":{"logicalId":"logical-not-native-id"}}').decode(),'payloadType':'InlineBase64'}]}}}
    def test_one_call_and_native_identity_distinct_from_logical(self):
        request=Mock(return_value=self.response());count=[]
        unit,receipt=read(self.source,self.path,meter=lambda fn:(count.append(1),fn())[1],
            item_fetch=lambda source,path,meter:fetch(source,path,meter,request))
        self.assertEqual(len(count),1);self.assertEqual(request.call_count,1)
        self.assertEqual(unit['item_identity']['item_id'],self.source['item_ids'][0])
        self.assertEqual(unit['item_identity']['logical_id'],'logical-not-native-id')
        self.assertEqual(receipt['identity'],'separate-code-account')
    def test_unlisted_item_and_external_polling_refuse(self):
        request=Mock()
        with self.assertRaisesRegex(ValueError,'outside declared source'):fetch(self.source,'other/notebook-content.py',lambda fn:fn(),request)
        request.assert_not_called()
        request.return_value={'status':202,'headers':{'Location':'https://other.test/v1/operations/x'},'body':{}}
        with self.assertRaisesRegex(ValueError,'outside declared API'):fetch(self.source,self.path,lambda fn:fn(),request)
    def test_refusal_retains_exact_http_error(self):
        request=Mock(return_value={'status':403,'headers':{},'body':{'errorCode':'InsufficientPrivileges','message':'refused'}})
        with self.assertRaisesRegex(RuntimeError,'Definition HTTP 403.*InsufficientPrivileges'):fetch(self.source,self.path,lambda fn:fn(),request)
    def test_regional_operation_uses_public_api_and_documented_retry_interval(self):
        operation='33333333-3333-3333-3333-333333333333'
        request=Mock(side_effect=[{'status':202,'headers':{'Location':'https://wabi-region.analysis.windows.net/v1/operations/'+operation,'Retry-After':'20'},'body':{}},
            {'status':200,'headers':{},'body':{'status':'Succeeded'}},self.response()])
        wait=Mock();fetch(self.source,self.path,lambda fn:fn(),request,wait=wait)
        wait.assert_called_once_with(20)
        self.assertEqual(request.call_args_list[1].args,('GET','operations/'+operation))
        self.assertEqual(request.call_args_list[2].args,('GET','operations/'+operation+'/result'))
    def test_api_tape_replays_without_request(self):
        with tempfile.TemporaryDirectory() as d:
            bootstrap={'entry_point':'code_reader','context_identity':'offline','config':{},'profile':{},'usage_policy':None,'engine_hash':'offline','state':{}}
            tape=journal.Tape(Path(d)/'tape.json',bootstrap=bootstrap)
            with journal.active(tape):
                result=read(self.source,self.path,meter=lambda fn:fn(),item_fetch=lambda s,p,m:fetch(s,p,m,Mock(return_value=self.response())))
                tape.finish({'read':result})
            no_network=Mock(side_effect=AssertionError('Unexpected live request'))
            replay=journal.Tape(Path(d)/'tape.json')
            with journal.active(replay):
                actual=read(self.source,self.path,meter=lambda fn:fn(),item_fetch=lambda s,p,m:fetch(s,p,m,no_network))
                replay.finish({'read':actual})
            self.assertEqual(result,actual);no_network.assert_not_called()
if __name__=='__main__':unittest.main()
