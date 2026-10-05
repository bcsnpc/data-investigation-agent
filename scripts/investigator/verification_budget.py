"""Approval/reader verification is distinct from investigation diagnostics.

Physical admissions still flow through the caller's ordinary rolling/round
governor. This counter grants no physical credit and changes no investigation cap.
"""
from .usage_governance import UsageHold


class VerificationBudget:
    def __init__(self, budgets, binding_count, *, record):
        if type(binding_count) is not int or binding_count < 0:
            raise ValueError('Binding count must be a nonnegative integer')
        policy = budgets.get('binding_verification', {})
        metadata=policy.get('metadata_probes',3)
        limit=policy.get('session_cap',2*binding_count+metadata)
        if (policy.get('probes_per_binding',2)!=2 or type(metadata) is not int
                or not 0<=metadata<=32 or type(limit) is not int or not 1<=limit<=2048):
            raise ValueError('Invalid approval-time verification budget')
        self.cap=min(2*binding_count+metadata,limit)
        self.count = 0
        self.record = record

    def read(self, kind, execute):
        if kind not in ('TARGET', 'SOURCE', 'METADATA'):
            raise ValueError('Unknown verification read kind')
        if self.count >= self.cap:
            self.record({'event': 'VERIFICATION_CAP', 'decision': 'REFUSED',
                         'count': self.count, 'cap': self.cap, 'kind': kind})
            raise UsageHold('Approval-time binding verification cap')
        self.count += 1
        self.record({'event': 'VERIFICATION_CAP', 'decision': 'ADMITTED',
                     'count': self.count, 'cap': self.cap, 'kind': kind})
        return execute()
