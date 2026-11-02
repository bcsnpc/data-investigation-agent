"""Approved IAM/KeyVault setup is narrowly scoped and never persists key values."""
import contextlib, io, json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import setup_bedrock_identity as setup

class SetupTests(unittest.TestCase):
 def test_only_one_key_nova_policy_only_and_vault_pipe_no_secret_files(self):
  with TemporaryDirectory()as d:
   root=Path(d);calls=[];vault={};arn='arn:aws:iam::123456789012:user/dia-bedrock';policy='arn:aws:iam::123456789012:policy/dia-bedrock-invoke'
   def cli(args,**kwargs):
    calls.append(args);value={};code=0;err=''
    if 'get-access-token'in args:value={'accessToken':'synthetic-vault-token'}
    elif 'get-caller-identity'in args:value={'Arn':arn if kwargs['env'].get('AWS_ACCESS_KEY_ID')else'arn:aws:iam::123456789012:user/owner'}
    elif 'get-user'in args or 'get-login-profile'in args:code=1;err='An error occurred (NoSuchEntity)'
    elif 'list-policies'in args:value={'Policies':[]}
    elif 'create-policy'in args:
     doc=json.loads(args[args.index('--policy-document')+1]);self.assertEqual(set(doc['Statement'][0]['Action']),{'bedrock:InvokeModel','bedrock:InvokeModelWithResponseStream'});self.assertTrue(all('amazon.nova-'in x for x in doc['Statement'][0]['Resource']));value={'Policy':{'Arn':policy}}
    elif 'create-user'in args:value={'User':{'Arn':arn}}
    elif 'list-attached-user-policies'in args:value={'AttachedPolicies':[{'PolicyArn':policy}]if any('attach-user-policy'in c for c in calls)else[]}
    elif 'list-user-policies'in args:value={'PolicyNames':[]}
    elif 'list-groups-for-user'in args:value={'Groups':[]}
    elif 'create-access-key'in args:value={'AccessKey':{'AccessKeyId':'synthetic-aws-id','SecretAccessKey':'synthetic-aws-secret'}}
    return SimpleNamespace(returncode=code,stdout=json.dumps(value),stderr=err)
   class Response:
    def __init__(self,value):self.value=value
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,*args):return json.dumps(self.value).encode()
   def http(request,**kwargs):
    name=request.full_url.split('/secrets/')[1].split('?')[0]
    if request.method=='PUT':vault[name]=json.loads(request.data)['value']
    if name not in vault:raise setup.HTTPError(request.full_url,404,'not found',{},None)
    return Response({'value':vault[name],'id':'https://kv-dia-d5dd7d65.vault.azure.net/secrets/'+name+'/'+'a'*32})
   output=io.StringIO()
   with patch.object(setup.subprocess,'run',side_effect=cli),patch.object(setup,'build_opener')as opener,contextlib.redirect_stdout(output):
    opener.return_value.open.side_effect=http
    setup.run(['--aws','aws','--azure-python','python','--local-root',str(root)])
   self.assertEqual(output.getvalue().strip(),arn);self.assertEqual(sum('create-access-key'in c for c in calls),1);self.assertTrue(any('logout'in c for c in calls))
   self.assertEqual(set(vault),{'aws-access-key-id','aws-secret-access-key','aws-region'})
   raw=b''.join(p.read_bytes()for p in root.rglob('*')if p.is_file())
   for secret in (b'synthetic-aws-id',b'synthetic-aws-secret',b'synthetic-vault-token'):self.assertNotIn(secret,raw)
   with self.assertRaisesRegex(AssertionError,'Existing setup journal'):setup.run(['--aws','aws','--azure-python','python','--local-root',str(root)])

if __name__=='__main__':unittest.main()
