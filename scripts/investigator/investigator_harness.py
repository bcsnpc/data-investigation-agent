"""Submit/poll/outcome harness over the existing dia run user entry point."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.request import Request, urlopen

from .estate_graph_contract import digest
from .planner_recording import _safe
from .process_tape import bytes_of
from .shared_state import StateConflict


class RunStillActive(RuntimeError):
    pass


class CaseLog:
    def __init__(self, path):
        self.path = Path(path); self.events = []; previous = None
        if self.path.exists():
            for raw in self.path.read_bytes().splitlines():
                value = json.loads(raw); body = {k: v for k, v in value.items() if k != 'sha256'}
                if value['sha256'] != digest(body) or body['previous'] != previous or body['sequence']!=len(self.events):
                    raise StateConflict('HARNESS_CASE_LOG_HASH_DIFFERS')
                self.events.append(value); previous = value['sha256']

    def append(self, event, value):
        body = {'sequence': len(self.events), 'previous': self.events[-1]['sha256'] if self.events else None,
                'event': event, 'value': copy.deepcopy(value)}
        body['sha256'] = digest(body); raw = bytes_of(body); _safe(raw)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('ab') as stream:
            stream.write(raw+b'\n'); stream.flush(); os.fsync(stream.fileno())
        self.events.append(body)


class RunHarness:
    def __init__(self, user, log, *, admit, clock=time.monotonic, sleep=time.sleep):
        if not callable(admit): raise ValueError('HARNESS_ADMISSION_REQUIRED')
        self.user, self.log, self.admit, self.clock, self.sleep = user, log, admit, clock, sleep

    def run(self, ticket, *, timeout_seconds=4200, poll_seconds=5):
        identity = digest(ticket); started = self.clock()
        if self.log.events:
            if self.log.events[0]['value']['ticket_sha256'] != identity:
                raise StateConflict('HARNESS_LOG_BELONGS_TO_DIFFERENT_TICKET')
            outcomes = [v['value'] for v in self.log.events if v['event'] == 'OUTCOME']
            if outcomes: return outcomes[-1]['result']
        else: self.log.append('CASE_OPEN', {'ticket_sha256': identity, 'ticket': ticket})
        submitted = [v['value'] for v in self.log.events if v['event'] == 'SUBMITTED']
        if submitted:
            run = submitted[-1]; self.log.append('RESUME_POLLING', run)
        else:
            if any(v['event']=='SUBMIT_ATTEMPT'for v in self.log.events):
                raise RunStillActive('SUBMISSION_UNCERTAIN_RECONCILE_BEFORE_RETRY')
            self.admit(ticket); self.log.append('SUBMIT_ATTEMPT', {'ticket_sha256': identity})
            try: run = self.user.submit(ticket)
            except Exception as error:
                self.log.append('BLOCK', {'stage': 'SUBMIT', 'error_type': type(error).__name__, 'reason': str(error)})
                raise
            self.log.append('SUBMITTED', run)
        while True:
            try:state = self.user.poll(run)
            except Exception as error:
                self.log.append('BLOCK',{'stage':'POLL','error_type':type(error).__name__,'reason':str(error)});raise
            self.log.append('POLL', state)
            if state['status'] not in ('Pending', 'Running', 'Processing'):
                try:result = self.user.outcome(run, state)
                except Exception as error:
                    self.log.append('BLOCK',{'stage':'OUTCOME','error_type':type(error).__name__,'reason':str(error)});raise
                delivered=result.get('result',result)
                if ticket.get('text')is not None and delivered.get('ticket',{}).get('text')!=ticket['text']:
                    self.log.append('BLOCK',{'stage':'OUTCOME_BINDING','reason':'DELIVERED_TICKET_TEXT_DIFFERS'})
                    raise StateConflict('DELIVERED_TICKET_TEXT_DIFFERS')
                self.log.append('OUTCOME', {'result': result, 'elapsed_seconds': self.clock()-started,
                                           'execution_status': state['status']})
                return result
            if self.clock()-started >= timeout_seconds:
                self.log.append('BLOCK', {'stage': 'POLL', 'reason': 'RUN_STILL_ACTIVE', 'run': run})
                raise RunStillActive('RUN_STILL_ACTIVE_NO_FOLLOWING_ADMISSION')
            self.sleep(poll_seconds)


class AzureCLIUser:
    """No alternate engine path: submit through dia run, read its sealed result."""
    def __init__(self, runner, *, execute=subprocess.run, fetch=None, control=lambda _: None, baseline=False):
        from .unified_runner import load
        from .adapters.runner_deployment import existing_job, input_policy_preflight
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
        command = [sys.executable, str(Path(__file__).resolve().parents[1]/'dia.py'), 'run', target,
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
        from .run_capture import record_value
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
