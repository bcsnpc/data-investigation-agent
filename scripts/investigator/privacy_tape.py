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

VERSION = 'privacy-projected-tape-v1'


class PrivacyTape:
    def __init__(self, path, projection, *, replay=False):
        self.path = Path(path)
        self.projection = projection
        self.replaying = replay
        self.events = []
        self.index = 0
        self.finished = False
        if replay:
            value = parse(self.path.read_bytes())
            if (not isinstance(value,dict)
                    or set(value) != {'version', 'projection', 'events', 'outputs', 'seal'}
                    or value['version'] != VERSION
                    or not isinstance(value['projection'],dict)
                    or value['projection'].get('tape_class') != PROJECTED):
                raise ProjectionError('PRIVACY_TAPE_SCHEMA')
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
        elif self.path.exists():
            raise ProjectionError('PRIVACY_TAPE_ALREADY_EXISTS')

    @property
    def tape_class(self):
        return PROJECTED

    def event(self, kind, body, *, base64_body=False):
        if self.finished or not isinstance(kind, str) or not kind or not isinstance(body, bytes):
            raise ProjectionError('PRIVACY_TAPE_EVENT')
        # Decode/learn in memory now. Refuse before opening any file if a
        # producer hands us a body whose sensitive columns cannot be parsed.
        projected = self.projection.body(body, base64_body=base64_body)
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
            value = {'version': VERSION, 'projection': self.projection.descriptor(),
                     'events': events, 'outputs': projected_outputs}
            value['seal'] = self.projection.sign(value)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('xb') as stream:
                stream.write(canonical(value))
            self.events = events
            self.outputs = projected_outputs
        self.finished = True
        return projected_outputs
