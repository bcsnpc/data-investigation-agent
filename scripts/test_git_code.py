import base64,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from investigator.adapters.git_code import RepositoryReader
from investigator.code_sources import read
from investigator import process_tape as journal

class RepositoryCodeTests(unittest.TestCase):
    source={'id':'code','kind':'GIT_REPOSITORY','identity':'read-only-account',
        'repo_url':'https://github.com/example/project','ref':'fixture-code',
        'path_prefix':'fixture-code','token_reference':'actions:read-token'}
    revision='a'*40
    def request(self,method,endpoint):
        self.assertEqual(method,'GET')
        if '/git/ref/' in endpoint:return {'status':200,'body':{'object':{'type':'commit','sha':self.revision}}}
        path=endpoint.split('/contents/')[1].split('?')[0]
        raw=b'{"config":{"logicalId":"logical-id"}}' if path.endswith('/.platform') else b'x=1\n'
        return {'status':200,'body':{'type':'file','encoding':'base64','path':path,
            'size':len(raw),'content':base64.b64encode(raw).decode()}}
    def test_ref_is_pinned_once_and_every_http_request_is_counted(self):
        request=Mock(side_effect=self.request);reader=RepositoryReader(request);calls=[]
        def meter(fn):calls.append(1);return fn()
        unit,receipt=read(self.source,'unit/notebook-content.py',meter=meter,git_fetch=reader)
        self.assertEqual(len(calls),3);self.assertEqual(receipt['revision'],self.revision)
        self.assertEqual(unit['item_identity'],{'logical_id':'logical-id'})
        read(self.source,'second.py',meter=meter,git_fetch=reader)
        self.assertEqual(len(calls),4)
        self.assertEqual(sum('/git/ref/' in c.args[1] for c in request.call_args_list),1)
    def test_unsupported_host_and_symlink_refuse(self):
        source={**self.source,'repo_url':'https://other.test/example/project'}
        request=Mock()
        with self.assertRaisesRegex(ValueError,'not installed'):read(source,'unit.py',meter=lambda fn:fn(),git_fetch=RepositoryReader(request))
        request.assert_not_called()
        request.side_effect=[self.request('GET','repos/example/project/git/ref/heads/fixture-code'),{'status':200,'body':{'type':'symlink'}}]
        with self.assertRaisesRegex(ValueError,'regular file'):read(self.source,'unit.py',meter=lambda fn:fn(),git_fetch=RepositoryReader(request))
    def test_repository_tape_replays_with_no_network(self):
        with tempfile.TemporaryDirectory() as d:
            b={'entry_point':'code_reader','context_identity':'offline','config':{},'profile':{},'usage_policy':None,'engine_hash':'offline','state':{}}
            tape=journal.Tape(Path(d)/'tape.json',bootstrap=b)
            with journal.active(tape):
                result=read(self.source,'unit.py',meter=lambda fn:fn(),git_fetch=RepositoryReader(self.request))
                tape.finish({'read':result})
            no_network=Mock(side_effect=AssertionError('Live IO forbidden'));replay=journal.Tape(Path(d)/'tape.json')
            with journal.active(replay):
                actual=read(self.source,'unit.py',meter=lambda fn:fn(),git_fetch=RepositoryReader(no_network))
                replay.finish({'read':actual})
            self.assertEqual(result,actual);no_network.assert_not_called()
if __name__=='__main__':unittest.main()
