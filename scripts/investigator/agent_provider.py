"""Agent decisions use the same daily, dollar and taped provider boundaries."""
import copy
import os
from .onboarding import encoded, digest
from .generation_policy import failure_usage
from .privacy_capture import input_characters


class GovernedDecision:
    def __init__(self, runtime, session_id, *, generate=None):
        if runtime.governor is None:
            raise ValueError('AGENT_USAGE_GOVERNOR_REQUIRED')
        if generate is None:
            from .agent_dollar_guard import declare
            from .process_tape import ACTIVE, event
            self.dollar_authority = declare(tape=ACTIVE.get(), emit=event)
        self.runtime, self.session_id = runtime, session_id
        self.generate = generate
        self.calls = 0

    def __call__(self, payload, *, instructions, schema):
        from ticket_planner import _azure_generate, provider_body
        from .agent_wire import schema as wire_schema
        from .planner_recording import recording
        options = copy.deepcopy(self.runtime.generation_options)
        # Responses strict schemas require an object at the root. The union
        # remains the same consumer-owned decision contract inside that object.
        wrapped = {'type': 'object', 'additionalProperties': False,
                   'properties': {'decision': schema}, 'required': ['decision']}
        # Enum vocabularies remain in the exact wire schema. Other consumer
        # constraints are derived into field descriptions, never hand copied.
        prompt = instructions
        wire = wire_schema(wrapped)
        body = provider_body(payload, prompt, wire, 'verified_agent_decision',
                             generation_options=options)
        size = input_characters(body)
        if size > options['max_payload_characters']:
            raise ValueError('AGENT_PROVIDER_REQUEST_BOUND')
        with self.runtime.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            self.calls = db.execute("SELECT count(*) FROM adaptive_usage WHERE session_id=? AND reservation_key LIKE 'agent-model:%'", (self.session_id,)).fetchone()[0] + 1
            if self.calls > 25:
                raise ValueError('AGENT_MODEL_CALL_CAP')
            key = 'agent-model:' + str(self.calls)
            self.runtime.governor.reserve(db, self.session_id, key, 'planner', size,
                                         output_tokens=options['max_output_tokens'])
        received = False; metadata = None
        try:
            with recording(lambda: {'session_id': self.session_id, 'agent_call': self.calls,
                    'payload_hash': digest(payload), 'schema_hash': digest(wrapped),
                    'reservation': {'key': key, 'input_characters': size,
                                    'output_tokens': options['max_output_tokens']}}):
                value, metadata = (self.generate or _azure_generate)(payload,
                    instructions=prompt, schema=wire, name='verified_agent_decision',
                    generation_options=options, max_request_characters=options['max_payload_characters'])
            received = True
            if not isinstance(value, dict) or set(value) != {'decision'}:
                raise ValueError('AGENT_PROVIDER_WRAPPER')
            return value['decision']
        except BaseException as exc:
            with self.runtime.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                usage = metadata.get('usage') if received and isinstance(metadata, dict) else failure_usage(exc)
                self.runtime.governor.settle(db, self.session_id, key, usage,
                                            uncertain=not received and usage is None)
            raise
        finally:
            if received:
                with self.runtime.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE')
                    self.runtime.governor.settle(db, self.session_id, key,
                        metadata.get('usage') if isinstance(metadata, dict) else None)
