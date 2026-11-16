"""One-time owner-approved IAM setup; never prints keys or signed requests.

Run locally after `aws login`, with the isolated owner profile. AWS CLI and
Azure CLI executables are explicit arguments; credentials are memory-only.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def run(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws', required=True)
    parser.add_argument('--azure-python', required=True)
    parser.add_argument('--local-root', type=Path, required=True)
    options = parser.parse_args(args)
    root = options.local_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    record_path = root / 'identity-setup.json'
    assert not record_path.exists(), 'Existing setup journal: reconcile, never mint a replacement key.'
    environment = dict(os.environ)
    environment.update(AWS_CONFIG_FILE=str(root / 'owner-config'), AWS_SHARED_CREDENTIALS_FILE=str(root / 'owner-credentials'),
                       AWS_LOGIN_CACHE_DIRECTORY=str(root / 'owner-login-cache'), AWS_PAGER='')
    base = [options.aws, '--profile', 'dia-owner-setup', '--region', 'us-east-1', '--no-cli-pager']
    record = {'approval': 'owner round26 resume-plus-bedrock 2026-11-01', 'started_at': datetime.now(timezone.utc).isoformat(),
              'user': 'dia-bedrock', 'policy': 'dia-bedrock-invoke', 'console_access': False, 'secret_values_recorded': False}
    def save():
        record_path.write_text(json.dumps(record, indent=2), encoding='utf-8')
    def aws(command, *, required=True, env=environment):
        result = subprocess.run(base + command + ['--output', 'json'], capture_output=True, text=True, env=env, timeout=60)
        if result.returncode:
            code = re.search(r'\(([A-Za-z0-9]+)\)', result.stderr)
            error = code.group(1) if code else 'CLI_FAILURE'
            if not required:
                return {'failed': error}
            raise RuntimeError('AWS_SETUP_' + error)
        return json.loads(result.stdout) if result.stdout.strip() else {}
    vault = 'https://kv-dia-d5dd7d65.vault.azure.net'
    token = None
    def kv(name, value=None):
        url = vault + '/secrets/' + name + '?api-version=7.4'
        request = Request(url, method='GET' if value is None else 'PUT',
                          data=None if value is None else json.dumps({'value': value}).encode(),
                          headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
        try:
            with build_opener(NoRedirect()).open(request, timeout=30) as response:
                return json.loads(response.read(1024 * 1024))
        except HTTPError as error:
            if value is None and error.code == 404:
                return None
            raise RuntimeError('KEYVAULT_SETUP_HTTP_' + str(error.code)) from None
        finally:
            request = value = None
    key = None
    try:
        owner = aws(['sts', 'get-caller-identity'])
        record['owner_arn'] = owner['Arn']
        # Existing objects require review, not a second user/key/policy or silent adoption.
        existing = aws(['iam', 'get-user', '--user-name', 'dia-bedrock'], required=False)
        if existing.get('failed') != 'NoSuchEntity':
            raise RuntimeError('AWS_USER_ALREADY_EXISTS_OR_CANNOT_ESTABLISH_ABSENCE')
        policies = aws(['iam', 'list-policies', '--scope', 'Local'])['Policies']
        if any(p['PolicyName'] == 'dia-bedrock-invoke' for p in policies):
            raise RuntimeError('AWS_POLICY_ALREADY_EXISTS_RECONCILE_ONLY')
        result = subprocess.run([options.azure_python, '-m', 'azure.cli', 'account', 'get-access-token', '--resource',
                                 'https://vault.azure.net', '-o', 'json', '--only-show-errors'], capture_output=True, text=True, timeout=45)
        if result.returncode:
            raise RuntimeError('AZURE_OWNER_VAULT_TOKEN_FAILED')
        token = json.loads(result.stdout)['accessToken']; result = None
        for name in ('aws-access-key-id', 'aws-secret-access-key', 'aws-region'):
            if kv(name) is not None:
                raise RuntimeError('AWS_KEYVAULT_SECRET_ALREADY_EXISTS_RECONCILE_ONLY')
        # Verify approved write capability before creating a key that can be returned only once.
        region = kv('aws-region', 'us-east-1')
        record['region_secret_id'] = region['id']
        models = ['arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-' + family + '-v*' for family in ('micro', 'lite', 'pro')]
        document = {'Version': '2012-10-17', 'Statement': [
            {'Effect': 'Allow', 'Action': ['bedrock:InvokeModel', 'bedrock:InvokeModelWithResponseStream'], 'Resource': models},
            {'Effect': 'Allow', 'Action': ['bedrock:ListFoundationModels'], 'Resource': '*'},
            {'Effect': 'Allow', 'Action': ['bedrock:GetFoundationModel'], 'Resource': models}]}
        record['policy_document'] = document
        record['status'] = 'POLICY_CREATE_ATTEMPTED'; save()
        policy = aws(['iam', 'create-policy', '--policy-name', 'dia-bedrock-invoke', '--policy-document', json.dumps(document)])['Policy']
        record['policy_arn'] = policy['Arn']; record['status'] = 'USER_CREATE_ATTEMPTED'; save()
        user = aws(['iam', 'create-user', '--user-name', 'dia-bedrock'])['User']
        record['user_arn'] = user['Arn']; record['before_attached'] = aws(['iam', 'list-attached-user-policies', '--user-name', 'dia-bedrock'])
        record['before_inline'] = aws(['iam', 'list-user-policies', '--user-name', 'dia-bedrock'])
        record['before_groups'] = aws(['iam', 'list-groups-for-user', '--user-name', 'dia-bedrock'])
        record['before_console'] = aws(['iam', 'get-login-profile', '--user-name', 'dia-bedrock'], required=False)
        aws(['iam', 'attach-user-policy', '--user-name', 'dia-bedrock', '--policy-arn', policy['Arn']])
        record['after_attached'] = aws(['iam', 'list-attached-user-policies', '--user-name', 'dia-bedrock'])
        assert [p['PolicyArn'] for p in record['after_attached']['AttachedPolicies']] == [policy['Arn']]
        assert not record['before_groups']['Groups'] and not record['before_inline']['PolicyNames']
        assert record['before_console']['failed'] == 'NoSuchEntity'
        record['status'] = 'ACCESS_KEY_CREATE_ATTEMPTED_NEVER_REPEAT_UNCERTAIN'; save()
        key = aws(['iam', 'create-access-key', '--user-name', 'dia-bedrock'])['AccessKey']
        record['status'] = 'KEY_IN_MEMORY_VAULT_MIGRATION_PENDING'; save()
        # A retry stores the same key; it never creates another AWS key.
        versions = {'aws-region': region['id']}
        for name, value in (('aws-access-key-id', key['AccessKeyId']), ('aws-secret-access-key', key['SecretAccessKey'])):
            for attempt in range(3):
                try:
                    versions[name] = kv(name, value)['id']; break
                except RuntimeError:
                    if attempt == 2: raise
                    time.sleep(2)
        key = None
        credentials = {name: kv(name)['value'] for name in ('aws-access-key-id', 'aws-secret-access-key', 'aws-region')}
        reader_env = {**environment, 'AWS_ACCESS_KEY_ID': credentials['aws-access-key-id'],
                      'AWS_SECRET_ACCESS_KEY': credentials['aws-secret-access-key'], 'AWS_DEFAULT_REGION': credentials['aws-region']}
        reader_env.pop('AWS_SESSION_TOKEN', None)
        # Explicit environment keys win over any owner profile; omit --profile entirely.
        result = subprocess.run([options.aws, 'sts', 'get-caller-identity', '--region', 'us-east-1', '--output', 'json', '--no-cli-pager'],
                                capture_output=True, text=True, env=reader_env, timeout=45)
        if result.returncode: raise RuntimeError('AWS_READER_STS_VERIFICATION_FAILED')
        arn = json.loads(result.stdout)['Arn']; assert arn == user['Arn']
        record.update(status='VERIFIED_VAULT_ONLY', secret_version_ids=versions, verified_reader_arn=arn)
        credentials = reader_env = result = None; save()
        print(arn)
    except Exception as error:
        record['failure_type'] = type(error).__name__
        record['failure_code'] = str(error) if isinstance(error, RuntimeError) and re.fullmatch(r'[A-Z0-9_]+', str(error)) else 'SETUP_FAILED_DETAILS_NOT_LOGGED'
        save()
        raise RuntimeError(record['failure_code']) from None
    finally:
        key = token = None
        logout = subprocess.run(base + ['logout'], capture_output=True, env=environment, timeout=45)
        record['owner_logout_exit_code'] = logout.returncode
        cache = root / 'owner-login-cache'
        record['owner_cached_credentials_remaining'] = sum(1 for p in cache.rglob('*') if p.is_file()) if cache.exists() else 0
        save()


if __name__ == '__main__':
    import sys
    run(sys.argv[1:])
