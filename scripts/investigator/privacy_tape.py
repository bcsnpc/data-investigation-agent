"""Explicit privacy-projected capture packets, independent of legacy exact tapes.

An attempt is staged in memory until sealed, so a value identified by a later
column-labelled result is removed from earlier prose too. No raw journal or
temporary file exists. This is a new replay contract, not a legacy tape rewrite.
"""
import base64
import hashlib
import hmac
from pathlib import Path
from .privacy_projection import ProjectionError, canonical, PROJECTED
from .provider_tape_contract import parse

VERSION = 'privacy-projected-tape-v2'
SUPPORTED_VERSIONS = frozenset(('privacy-projected-tape-v1',VERSION))


class PrivacyTape:
    def __init__(self, path, projection, *, replay=False):
        self.path = Path(path)
        self.projection = projection
        self.replaying = replay
        self.events = []
        self.index = 0
        self.finished = False
        self.version=VERSION
        self.exclusions=[]
        # Same recorder interface as exact tapes; bootstrap is memory-only
        # until the existing projected seal is written. No raw journal exists.
        self.bootstrap={}
        self.accounting_version=1 # Unpinned historical projected captures.
        if replay:
            value = parse(self.path.read_bytes())
            if (not isinstance(value,dict)
                    or set(value) != {'version', 'projection', 'events', 'outputs', 'seal'}
                    or value['version'] not in SUPPORTED_VERSIONS
                    or not isinstance(value['projection'],dict)
                    or value['projection'].get('tape_class') != PROJECTED):
                raise ProjectionError('PRIVACY_TAPE_SCHEMA')
            self.version=value['version']
            self.projection.require_descriptor(value['projection'])
            if not isinstance(value['seal'],str) or not hmac.compare_digest(value['seal'], self.projection.sign({
                    k: v for k, v in value.items() if k != 'seal'})):
                raise ProjectionError('PRIVACY_TAPE_SEAL')
            self.projection.trust_sealed_tokens(value)
            self.events = value['events']
            self.outputs = value['outputs']
            for ordinal, event in enumerate(self.events, 1):
                if (set(event) != {'ordinal', 'kind', 'body', 'sha256', 'base64_body'}
                        or event['ordinal'] != ordinal or not isinstance(event['kind'], str)
                        or type(event['base64_body']) is not bool):
                    raise ProjectionError('PRIVACY_TAPE_EVENT')
                try:
                    body = base64.b64decode(event['body'], validate=True)
                except (ValueError, TypeError):
                    raise ProjectionError('PRIVACY_TAPE_ENCODING') from None
                if hashlib.sha256(body).hexdigest() != event['sha256']:
                    raise ProjectionError('PRIVACY_TAPE_EVENT_SEAL')
                self.projection.trust_sealed_tokens(parse(body))
            if self.events and self.events[0]['kind']=='BOOTSTRAP':
                self._set_bootstrap(base64.b64decode(self.events[0]['body']))
        elif self.path.exists():
            raise ProjectionError('PRIVACY_TAPE_ALREADY_EXISTS')

    def _set_bootstrap(self,body):
        bootstrap=parse(body)
        from .budget_tape_contract import ACCOUNTING_HISTORY
        version=bootstrap.get('state',{}).get('accounting_version',1)
        if type(version) is not int or version not in ACCOUNTING_HISTORY:
            raise ProjectionError('PRIVACY_ACCOUNTING_VERSION')
        self.bootstrap=bootstrap;self.accounting_version=version

    def flush(self):
        # Raw/partially identified events are memory-only until finalization.
        # A legacy recorder must never use this as a raw journal fallback.
        return None

    @property
    def tape_class(self):
        return PROJECTED

    def event(self, kind, body, *, base64_body=False):
        if self.finished or not isinstance(kind, str) or not kind or not isinstance(body, bytes):
            raise ProjectionError('PRIVACY_TAPE_EVENT')
        # Decode/learn in memory now. Refuse before opening any file if a
        # producer hands us a body whose sensitive columns cannot be parsed.
        if kind=='WORKER_SEND' and body in (b'ALLOW\n',b'REUSE\n'):
            body=canonical({'worker_control':body.decode('ascii')})
        projected = self.projection.body(body, base64_body=base64_body)
        if kind=='BOOTSTRAP':
            self._set_bootstrap(body)
        if self.replaying:
            if self.index >= len(self.events):
                raise ProjectionError('PRIVACY_TAPE_EXHAUSTED')
            event = self.events[self.index]
            if event['kind'] != kind or event['base64_body'] != base64_body:
                raise ProjectionError('PRIVACY_TAPE_EVENT_DIFFERS')
            if projected != base64.b64decode(event['body']):
                raise ProjectionError('PRIVACY_PROJECTED_BYTES_DIFFER')
            self.index += 1
        else:
            self.events.append({'kind': kind, 'body': projected, 'base64_body': base64_body})

    def peek(self,kind):
        """Validate/decode the next projected event without consuming it."""
        if not self.replaying or self.index>=len(self.events):return None
        event=self.events[self.index]
        if (not isinstance(event,dict)
                or set(event)!={'ordinal','kind','body','sha256','base64_body'}
                or type(event['ordinal']) is not int or event['ordinal']!=self.index+1
                or not isinstance(event['kind'],str) or not event['kind']
                or type(event['base64_body']) is not bool):
            raise ProjectionError('PRIVACY_TAPE_EVENT')
        try:body=base64.b64decode(event['body'],validate=True)
        except (ValueError,TypeError):raise ProjectionError('PRIVACY_TAPE_ENCODING') from None
        if hashlib.sha256(body).hexdigest()!=event['sha256']:
            raise ProjectionError('PRIVACY_TAPE_EVENT_SEAL')
        return body if event['kind']==kind else None

    def take(self, kind):
        if not self.replaying or self.index >= len(self.events):
            raise ProjectionError('PRIVACY_TAPE_EXHAUSTED')
        event = self.events[self.index]
        if event['kind'] != kind:
            raise ProjectionError('PRIVACY_TAPE_EVENT_DIFFERS')
        self.index += 1
        return base64.b64decode(event['body'], validate=True)

    def finish(self, outputs):
        if self.finished:
            raise ProjectionError('PRIVACY_TAPE_ALREADY_FINISHED')
        # All typed values are known before any output/event is written. The
        # descriptor and every body enter the same exclusive durable write.
        projected_outputs = self.projection.project(outputs)
        if self.replaying:
            if self.index != len(self.events) or projected_outputs != self.outputs:
                raise ProjectionError('PRIVACY_TAPE_NOT_CONSUMED_OR_OUTPUT_DIFFERS')
        else:
            events = []
            for ordinal, event in enumerate(self.events, 1):
                body = self.projection.body(event['body'], base64_body=event['base64_body'])
                events.append({'ordinal': ordinal, 'kind': event['kind'],
                    'body': base64.b64encode(body).decode('ascii'),
                    'sha256': hashlib.sha256(body).hexdigest(),
                    'base64_body': event['base64_body']})
            value = {'version': self.version, 'projection': self.projection.descriptor(),
                     'events': events, 'outputs': projected_outputs}
            value['seal'] = self.projection.sign(value)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('xb') as stream:
                stream.write(canonical(value))
            self.events = events
            self.outputs = projected_outputs
        self.finished = True
        return projected_outputs
