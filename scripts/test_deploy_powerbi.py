import tempfile,unittest
from pathlib import Path
from deploy_powerbi import deploy

class PinnedPublicationTests(unittest.TestCase):
    def test_pinned_target_never_creates_or_substitutes_an_item(self):
        with tempfile.TemporaryDirectory()as root:
            folder=Path(root);(folder/'definition.json').write_text('{}')
            for items in ([],[{'id':'00000000-0000-0000-0000-000000000002','type':'Report','displayName':'Report'}]):
                calls=[]
                def request(*args):calls.append(args);return {'text':{'value':items}}
                with self.assertRaisesRegex(ValueError,'Pinned publication target'):
                    deploy(folder,'Report','Report',workspace='00000000-0000-0000-0000-000000000003',expected_item_id='00000000-0000-0000-0000-000000000001',request=request)
                self.assertEqual(len(calls),1)
    def test_update_and_revert_use_same_pinned_item_and_exact_file_bytes(self):
        import base64
        workspace='00000000-0000-0000-0000-000000000003';item='00000000-0000-0000-0000-000000000001';calls=[]
        def request(endpoint,*args):
            calls.append((endpoint,*args))
            return {'text':{'value':[{'id':item,'type':'Report','displayName':'Report'}]}} if not args else {'text':{}}
        with tempfile.TemporaryDirectory()as root:
            p=Path(root)/'definition.json'
            for raw in (b'{"hidden":true}',b'{"hidden":false}'):
                p.write_bytes(raw);deploy(Path(root),'Report','Report',workspace=workspace,expected_item_id=item,request=request)
                sent=calls[-1]
                self.assertEqual(sent[0],f'workspaces/{workspace}/items/{item}/updateDefinition')
                self.assertEqual(base64.b64decode(sent[2]['definition']['parts'][0]['payload']),raw)
