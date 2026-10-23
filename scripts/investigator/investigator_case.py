"""Code-owned investigator state. Model proposals are never direct writes."""
import copy
import hashlib
import json
from .estate_graph_contract import canonical

PLAN = ('recreate', 'quick_facts', 'investigate', 'deliver')
FIELDS = {'version', 'ticket_id', 'plan', 'current_step', 'evidence_summaries',
          'decisions', 'calls_blocked', 'errors', 'notes', 'final_outcome'}


class CaseFile:
    def __init__(self, ticket):
        identity = ticket.get('id') or hashlib.sha256(canonical(ticket).encode()).hexdigest()
        self.value = {'version': 'ledger-case-v1', 'ticket_id': identity,
                      'plan': list(PLAN), 'current_step': PLAN[0],
                      'evidence_summaries': {}, 'decisions': [], 'calls_blocked': [],
                      'errors': [], 'notes': [], 'final_outcome': None}

    @classmethod
    def loads(cls, raw):
        value = json.loads(raw)
        if (not isinstance(value, dict) or set(value) != FIELDS
                or value['version'] != 'ledger-case-v1' or value['plan'] != list(PLAN)
                or value['current_step'] not in PLAN
                or not isinstance(value['ticket_id'], str) or not value['ticket_id']
                or not isinstance(value['evidence_summaries'], dict)
                or any(not isinstance(value[key], list) for key in
                       ('decisions', 'calls_blocked', 'errors', 'notes'))
                or value['final_outcome'] is not None and not isinstance(value['final_outcome'], dict)):
            raise ValueError('CASE_FILE_CONTRACT')
        result = cls.__new__(cls)
        result.value = copy.deepcopy(value)
        return result

    def dumps(self):
        return canonical(self.value)

    def snapshot(self):
        return copy.deepcopy(self.value)

    def model_view(self):
        """Summaries and short action history; full state stays in its capture."""
        value = self.snapshot()
        value['decisions'] = [{key: row[key] for key in
                               ('action', 'tool', 'arguments', 'verdict', 'summary') if key in row}
                              for row in value['decisions'][-3:]]
        value['errors'] = [{key: row[key] for key in
                            ('event', 'reason', 'tool', 'arguments', 'error_type', 'expected') if key in row}
                           for row in value['errors']]
        value['notes'] = value['notes'][-3:]
        return value

    def advance(self, step):
        if step not in PLAN or PLAN.index(step) < PLAN.index(self.value['current_step']):
            raise ValueError('CASE_STEP_BACKWARD_OR_UNKNOWN')
        self.value['current_step'] = step

    def evidence(self, summaries):
        self.value['evidence_summaries'] = {entry['id']: copy.deepcopy(entry) for entry in summaries}

    def propose(self, update):
        # The model may annotate its plan with cited evidence. Only code may
        # change step/order, evidence, errors or outcome.
        if (not isinstance(update, dict) or set(update) != {'note', 'evidence_ids'}
                or not isinstance(update['note'], str) or not 1 <= len(update['note']) <= 500
                or not isinstance(update['evidence_ids'], list)
                or any(not isinstance(identity, str) or identity not in self.value['evidence_summaries']
                       for identity in update['evidence_ids'])):
            self.value['errors'].append({'reason': 'MODEL_CASE_UPDATE_REJECTED'})
            return False
        self.value['notes'].append(copy.deepcopy(update))
        return True

    def recite(self, value):
        expected = {'plan': self.value['plan'], 'current_step': self.value['current_step']}
        if value == expected:
            return None
        event = {'event': 'INVESTIGATOR_RECITATION_MISMATCH', 'reason': 'CODE_CASE_FILE_WINS',
                 'expected': copy.deepcopy(expected), 'received': copy.deepcopy(value)}
        self.value['errors'].append(event)
        return event

    def failed_call(self, tool, arguments):
        signature = canonical([tool, arguments])
        for error in reversed(self.value['errors']):
            if (error.get('result', {}).get('status') == 'UNAVAILABLE'
                    and canonical([error.get('tool'), error.get('arguments')]) == signature):
                return copy.deepcopy(error)
        return None

    def observe(self, event):
        kind = event.get('event')
        if kind == 'INVESTIGATOR_DECISION':
            self.value['decisions'].append(copy.deepcopy(event))
        elif kind in ('INVESTIGATOR_REJECTED', 'INVESTIGATOR_BUDGET_STOP'):
            self.value['errors'].append(copy.deepcopy(event))
        elif kind == 'INVESTIGATOR_CALL_BLOCKED':
            self.value['calls_blocked'].append(copy.deepcopy(event))
        elif kind == 'INVESTIGATOR_TOOL' and event['result'].get('status') == 'UNAVAILABLE':
            self.value['errors'].append({key: copy.deepcopy(event[key]) for key in
                                         ('tool', 'arguments', 'result')})

    def finish(self, outcome):
        self.advance('deliver')
        self.value['final_outcome'] = {key: copy.deepcopy(outcome[key]) for key in
                                     ('verdict', 'status', 'stop_reason')}
