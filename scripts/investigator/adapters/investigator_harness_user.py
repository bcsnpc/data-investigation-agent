"""Existing cloud CLI implementation of the submit/poll/outcome user port."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import Request, urlopen
from ..planner_recording import _safe
from ..process_tape import bytes_of
from ..shared_state import StateConflict

class AzureCLIUser:
    """No alternate engine path: submit through dia run, read its sealed result."""
    def __init__(self, runner, *, execute=subprocess.run, fetch=None, control=lambda _: None, baseline=False):
        from ..unified_runner import load
        from .runner_deployment import existing_job, input_policy_preflight
        self.runner = Path(runner).resolve(); self.config = load(self.runner)
        if self.config.get('per_execution')is not True:raise ValueError('HARNESS_FRESH_EXECUTION_BINDING_REQUIRED')
        input_policy_preflight(self.config)
        resource = self.config['deployment']['resource_id']
        if not existing_job(resource): raise ValueError('HARNESS_EXISTING_JOB_REQUIRED')
        self.group, self.job = resource.split('/')[4], resource.rsplit('/', 1)[-1]
        self.execute, self.control, self.baseline = execute, control, baseline
        self.cli = self.config['deployment'].get('cli', ['az'])
        self.fetch = fetch or self._fetch; self._token = None

    def _json(self, args):
        response = self.execute(args, capture_output=True, text=True, check=True)
        return json.loads(response.stdout)

    def submit(self, ticket):
        target = ticket['target']; check = self.config['checks'].get(target)
        kinds = {'legacy-baseline'} if self.baseline else {'investigation', 'ledger-investigation'}
        if not check or check['kind'] not in kinds: raise ValueError('HARNESS_DECLARED_TICKET_TARGET_REQUIRED')
        command = [sys.executable, str(Path(__file__).resolve().parents[2]/'dia.py'), 'run', target,
                   '--estate', str(self.runner), '--runtime', 'azure']
        result = self._json(command)
        if result.get('status') != 'STARTED' or not result.get('execution_name') or not result.get('run_id'):
            raise ValueError('HARNESS_SUBMISSION_NOT_ESTABLISHED')
        return result

    def poll(self, run):
        result = self._json(self.cli+['containerapp', 'job', 'execution', 'show', '-g', self.group,
                           '-n', self.job, '--job-execution-name', run['execution_name'], '-o', 'json', '--only-show-errors'])
        value = result['properties']
        return {'execution_name': run['execution_name'], **{k: value.get(k) for k in ('status', 'startTime', 'endTime')}}

    def _fetch(self, url):
        if self._token is None:
            response = self.execute(self.cli+['account', 'get-access-token', '--resource', 'https://storage.azure.com',
                                             '--query', 'accessToken', '-o', 'tsv', '--only-show-errors'],
                                    capture_output=True, text=True, check=True)
            self._token = response.stdout.strip()  # Memory only; never a log or file.
        with urlopen(Request(url, headers={'Authorization': 'Bearer '+self._token, 'x-ms-version': '2023-11-03'}), timeout=60) as response:
            raw = response.read(32*1024*1024+1)
            if len(raw) > 32*1024*1024: raise ValueError('HARNESS_CAPTURE_BOUND')
            self.control({'kind': 'PLATFORM_ARTIFACT_CONTROL', 'method': 'GET', 'url': url,
                          'http_status': response.status, 'bytes': len(raw), 'identity': 'EXISTING_OWNER_AZURE_CLI'})
            return raw

    def outcome(self, run, state):
        from ..run_capture import record_value
        identifier = run['run_id']
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', identifier): raise ValueError('HARNESS_RUN_ID')
        base = self.config['capture']['account_url']+'/captures/'+self.config['capture']['prefix'].strip('/')
        manifest = json.loads(self.fetch(base+'/'+identifier+'/run-record.json'))
        body = {k: v for k, v in manifest.items() if k != 'seal'}
        if hashlib.sha256(bytes_of(body)).hexdigest() != manifest['seal'] or body['run_id'] != identifier:
            raise StateConflict('HARNESS_CAPTURE_SEAL_DIFFERS')
        refs = [r for r in body['records'] if re.fullmatch(re.escape(identifier)+r'/[0-9]{8}-result\.json', r['key'])]
        if len(refs) != 1: raise ValueError('HARNESS_FINAL_RESULT_NOT_UNIQUE')
        ref = refs[0]; raw = self.fetch(base+'/'+ref['key'])
        if hashlib.sha256(raw).hexdigest() != ref['sha256']: raise StateConflict('HARNESS_RESULT_HASH_DIFFERS')
        result = record_value(raw, ref.get('encoding')); _safe(bytes_of(result))
        return {'execution': state, 'image': run['image'], 'capture_seal': manifest['seal'], 'result': result}
