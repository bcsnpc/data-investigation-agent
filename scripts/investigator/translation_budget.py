"""Meter translation proposals separately; use existing planner reservations.

No extra credits, recovery, or investigation read admission is granted here.
Provider usage is settled even when a later consumer rejects the proposal.
"""
from .onboarding import encoded
from .usage_governance import UsageHold
from .planner_recording import recording
from .process_tape import clock as tape_clock
import time


class Meter:
    def __init__(self, provider, *, governor, session_id, deadline, max_calls,
                 max_input, event, context_version, clock=time.time):
        self.provider = provider; self.governor = governor; self.session_id = session_id
        self.deadline = deadline; self.max_calls = max_calls; self.max_input = max_input
        self.event = event; self.context_version = context_version; self.clock = clock
        self.calls = 0; self.input_characters = 0

    def __call__(self, request, execute):
        # Reserve the full request, conservatively, even though provider input
        # excludes prior values. No answer-bearing payload goes to the provider.
        size = len(encoded(request)); options = self.provider.options
        if size > options['max_payload_characters']: raise UsageHold('Translation per-call input limit')
        if self.calls >= self.max_calls or self.input_characters + size > self.max_input:
            raise UsageHold('Translation cumulative call or input limit')
        if tape_clock('translation-proposal', self.clock) + options['timeout_seconds'] > self.deadline:
            raise UsageHold('Translation deadline admission')
        number = self.calls + 1; key = 'translation-proposal:' + str(number)
        with self.governor.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            self.governor.reserve(db, self.session_id, key, 'planner', size,
                output_tokens=options['max_output_tokens'])
        self.calls = number; self.input_characters += size
        self.event('TRANSLATION_PROPOSAL_RESERVED', {'call': number,
            'input_characters': size, 'reservation_key': key})
        received = False; metadata = None
        try:
            with recording({'session_id': self.session_id, 'phase': 'TRANSLATION_PROPOSAL',
                'planner_call': number, 'context_version': self.context_version,
                'reservation': {'key': key, 'input_characters': size,
                                'output_tokens': options['max_output_tokens']}}):
                value = execute(); received = True
            self.event('TRANSLATION_PROPOSAL_COMPLETED', {'call': number})
            return value
        except Exception as exc:
            from .generation_policy import failure_usage
            metadata = getattr(exc, 'provider_metadata', None)
            if metadata is None: metadata = {'usage': failure_usage(exc)}
            self.event('TRANSLATION_PROPOSAL_FAILED', {'call': number, 'error_type': type(exc).__name__})
            raise
        finally:
            metadata = self.provider.metadata or metadata
            usage = metadata.get('usage') if isinstance(metadata, dict) else None
            with self.governor.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                self.governor.settle(db, self.session_id, key, usage, uncertain=not received and not usage)
