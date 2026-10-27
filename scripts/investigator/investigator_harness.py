"""Submit/poll/outcome harness over the existing dia run user entry point."""
import copy
import hashlib
import json
import os
from pathlib import Path
import time

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
            try:
                admission = self.admit(ticket)
                if admission is not None:self.log.append('ADMISSION', admission)
            except Exception as error:
                block = {'stage':'ADMISSION','error_type':type(error).__name__,'reason':str(error)}
                if getattr(error, 'fixture_invalid', False):
                    block['fixture_status'] = 'INVALID_NOT_AN_ENGINE_RESULT'
                self.log.append('BLOCK', block)
                raise
            self.log.append('SUBMIT_ATTEMPT', {'ticket_sha256': identity})
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
                returned_text=delivered.get('ticket',{}).get('text')
                if returned_text is None and delivered.get('ticket',{}).get('version')=='smart-ticket-v1':
                    returned_text=delivered.get('request',{}).get('text')
                if delivered.get('ticket',{}).get('version')=='IntakeRequest/1':
                    returned_text=delivered['ticket'].get('description')
                if 'intake' in ticket and bytes_of(ticket['intake'])!=bytes_of(delivered.get('ticket')):
                    self.log.append('BLOCK',{'stage':'OUTCOME_BINDING','reason':'DELIVERED_INTAKE_DIFFERS'})
                    raise StateConflict('DELIVERED_INTAKE_DIFFERS')
                if ticket.get('text')is not None and returned_text!=ticket['text']:
                    self.log.append('BLOCK',{'stage':'OUTCOME_BINDING','reason':'DELIVERED_TICKET_TEXT_DIFFERS'})
                    raise StateConflict('DELIVERED_TICKET_TEXT_DIFFERS')
                self.log.append('OUTCOME', {'result': result, 'elapsed_seconds': self.clock()-started,
                                           'execution_status': state['status']})
                return result
            if self.clock()-started >= timeout_seconds:
                self.log.append('BLOCK', {'stage': 'POLL', 'reason': 'RUN_STILL_ACTIVE', 'run': run})
                raise RunStillActive('RUN_STILL_ACTIVE_NO_FOLLOWING_ADMISSION')
            self.sleep(poll_seconds)


# Preserve the public user-port import while keeping provider details in adapters.
from .adapters.investigator_harness_user import AzureCLIUser
