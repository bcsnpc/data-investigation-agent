"""Agent decisions use the same daily, dollar and taped provider boundaries."""
import copy
import os
from .onboarding import encoded, digest
from .generation_policy import failure_usage
from .privacy_capture import input_characters


class GovernedDecision:
    def __init__(self, runtime, session_id, *, generate=None, deadline=None):
        if runtime.governor is None:
            raise ValueError('AGENT_USAGE_GOVERNOR_REQUIRED')
        if generate is None:
            from .agent_dollar_guard import declare
            from .process_tape import ACTIVE, event
            self.dollar_authority = declare(tape=ACTIVE.get(), emit=event)
        self.runtime, self.session_id = runtime, session_id
        self.generate = generate
        self.calls = 0
        self.deadline=deadline

    def __call__(self, payload, *, instructions, schema):
        from .provider_selection import agent_selection
        with agent_selection(self.runtime):
            return self._call(payload, instructions=instructions, schema=schema)

    def _call(self, payload, *, instructions, schema):
        from ticket_planner import _azure_generate, provider_body
        from .agent_wire import schema as wire_schema
        from .agent_shared_input import encode as share_input, decode as expand_input
        from .planner_recording import recording
        options = copy.deepcopy(self.runtime.generation_options)
        # Responses strict schemas require an object at the root. The union
        # remains the same consumer-owned decision contract inside that object.
        wrapped = {'type': 'object', 'additionalProperties': False,
                   'properties': {'decision': schema}, 'required': ['decision']}
        # Enum vocabularies remain in the exact wire schema. Other consumer
        # constraints are derived into field descriptions, never hand copied.
        prompt = instructions + '\nInput uses lossless shared-value references. Replace an object containing only $agent_shared_ref with that entry from shared_values; all original fields are retained. Tool arguments must use the actual identifiers, not references.'
        wire = wire_schema(wrapped)
        shared = share_input(payload)
        if expand_input(shared) != payload:
            raise ValueError('AGENT_SHARED_INPUT_CONSERVATION')
        body = provider_body(shared, prompt, wire, 'verified_agent_decision',
                             generation_options=options)
        size = input_characters(body)
        bound = request_bound(self.runtime)
        if size > bound:
            raise ValueError('AGENT_PROVIDER_REQUEST_BOUND')
        with self.runtime.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            self.calls = db.execute("SELECT count(*) FROM adaptive_usage WHERE session_id=? AND reservation_key LIKE 'agent-model:%'", (self.session_id,)).fetchone()[0] + 1
            if self.calls > 25:
                raise ValueError('AGENT_MODEL_CALL_CAP')
            key = 'agent-model:' + str(self.calls)
            self.runtime.governor.reserve(db, self.session_id, key, 'planner', size,
                                         output_tokens=options['max_output_tokens'])
        from .model_transport_retry import scope
        def admit_retry(db,retry_key,characters,tokens):
            from .usage_governance import UsageHold
            calls=db.execute("SELECT count(*) FROM adaptive_usage WHERE session_id=? AND reservation_key LIKE 'agent-model:%'",(self.session_id,)).fetchone()[0]
            if calls>=25:raise UsageHold('AGENT_MODEL_CALL_CAP')
            if self.deadline is not None and self.runtime.clock()>=self.deadline:
                raise UsageHold('Agent transport retry deadline')
        received = False; metadata = None
        try:
            with scope(self.runtime.governor,self.session_id,key,size,options['max_output_tokens'],
                    admit_extra=admit_retry,deadline=self.deadline,clock=getattr(self.runtime,'clock',__import__('time').time),
                    metadata={'phase':'AGENT_TRANSPORT_RETRY'}), recording(lambda: {'session_id': self.session_id, 'agent_call': self.calls,
                    'payload_hash': digest(payload), 'schema_hash': digest(wrapped),
                    'reservation': {'key': key, 'input_characters': size,
                                    'output_tokens': options['max_output_tokens']}}):
                generate = self.generate or _azure_generate
                response_options = {} if self.generate is not None else {'agent_final_answer': True}
                value, metadata = generate(shared,
                    instructions=prompt, schema=wire, name='verified_agent_decision',
                    generation_options=options, max_request_characters=bound, **response_options)
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


def request_bound(runtime):
    """Agent override is isolated from the pipeline generation profile."""
    config = runtime.config.get('_estate', {}).get('investigation', {})
    bound = config.get('input_characters_per_request', runtime.generation_options['max_payload_characters'])
    if type(bound) is not int or not 8000 <= bound <= 150000:
        raise ValueError('AGENT_REQUEST_BOUND_CONFIGURATION')
    if 'input_characters_per_request' in config and config.get('mode') not in ('AGENT','HYBRID'):
        raise ValueError('AGENT_REQUEST_BOUND_MODE')
    return bound
