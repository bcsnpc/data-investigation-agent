"""One structured-call surface for writer, graders, enrichment and summaries.

Provider/model selection belongs to installation configuration. Native adapters
record the original provider bytes and settle their own shared reservations.
"""
import json
from jsonschema import Draft202012Validator
from .adapters.provider_runtime import select, client
from .reasoning_budget import TicketBudget, RateCard
from .estate_graph_contract import canonical


class Steps:
    def __init__(self, *, configuration, tenant, state, record, client_factory=client, investigator_configuration=None):
        self.configuration, self.tenant, self.state = configuration, tenant, state
        self.record, self.client_factory = record, client_factory
        self.clients = {}
        self.investigator_configuration = investigator_configuration

    def model(self, step, case_id):
        config = select(self.configuration, tenant=self.tenant, step=step)
        if step in ('GRADING', 'SECONDARY_GRADING', 'REVIEWER'):
            if self.investigator_configuration is None:
                raise ValueError('MEASURED_INVESTIGATOR_CONFIGURATION_REQUIRED')
            measured = self.investigator_configuration
            if step == 'GRADING' and config.get('provider', 'anthropic') == measured.get('provider', 'anthropic'):
                raise ValueError('PRIMARY_GRADER_MUST_USE_DIFFERENT_PROVIDER')
            if step != 'GRADING' and (config.get('provider', 'anthropic'), config['model']) == (measured.get('provider', 'anthropic'), measured['model']):
                raise ValueError('INDEPENDENT_REVIEW_MODEL_REQUIRED')
        key = (case_id, step)
        if key not in self.clients:
            purpose = 'GRADING' if step in ('REVIEWER', 'SECONDARY_GRADING') else step
            budget = TicketBudget(self.state, case_id=case_id, owner=config['worker_identity'],
                rate=RateCard(model=config['model'], **config['rate_card']), provider=config.get('provider', 'anthropic'),
                actual_usage_limit=3000000, purpose=purpose)
            self.clients[key] = self.client_factory(config, budget=budget, record=self.record)
        return self.clients[key]

    def generate(self, *, step, case_id, instructions, payload, schema, max_tokens=4000):
        from .planner_recording import _safe
        _safe(canonical(payload).encode())
        system = instructions + '\nReturn the requested record by calling resolve_intake exactly once. A prose-only answer does not satisfy this structured interface.'
        messages = [{'role': 'user', 'content': canonical(payload)}]
        for attempt in range(2):
            response = self.model(step, case_id).complete(system=system, messages=messages,
                tools=[{'name': 'resolve_intake', 'description': 'Return only the requested structured record; no external execution.',
                        'input_schema': schema}], max_tokens=max_tokens)
            calls = [b for b in response['content'] if b['type'] == 'tool_use' and b['name'] == 'resolve_intake']
            if len(calls) == 1 and response.get('stop_reason') != 'max_tokens':
                break
            if attempt:
                raise ValueError('STRUCTURED_AI_RESULT_UNESTABLISHED')
            self.record({'event': 'STRUCTURED_AI_RETRY', 'step': step, 'reason': 'STRUCTURED_TOOL_RESULT_REQUIRED'})
            messages.append({'role': 'user', 'content': 'Use resolve_intake once with the requested record, rather than prose. Do not invent missing facts.'})
        value = calls[0]['input']
        Draft202012Validator(schema).validate(value)
        _safe(canonical(value).encode())
        return value

    def evaluate(self, source, *, case_id, grading_role='PRIMARY'):
        from .adapters.evaluation_anthropic import request_for, decode_output, output_schema
        from .shared_state import sha
        request = request_for(source, sha(source))['params']
        purpose = source['purpose']
        if grading_role not in ('PRIMARY', 'SECONDARY'):raise ValueError('GRADING_ROLE_REQUIRED')
        step = ('GRADING' if grading_role == 'PRIMARY' else 'SECONDARY_GRADING') if purpose.startswith('GRADE_') else 'REVIEWER' if purpose == 'ASSESS_FAIRNESS' else 'WRITER'
        raw = self.generate(step=step, case_id=case_id, instructions=request['system'],
            payload=json.loads(request['messages'][0]['content']), schema=request['output_config']['format']['schema'],
            max_tokens=request['max_tokens'])
        output = decode_output(source, raw)
        Draft202012Validator(output_schema(purpose)).validate(output)
        return output

    def enrich(self, source, *, case_id):
        from .adapters.enrichment_anthropic import request_for, resolve_references
        from .enrichment import SCHEMA
        from .shared_state import sha
        request = request_for(source, sha(source))
        params = request['params']
        raw = self.generate(step='ENRICHMENT', case_id=case_id, instructions=params['system'],
            payload=json.loads(params['messages'][0]['content']), schema=params['output_config']['format']['schema'],
            max_tokens=params['max_tokens'])
        output = resolve_references(raw, source, request)
        Draft202012Validator(SCHEMA).validate(output)
        return output
