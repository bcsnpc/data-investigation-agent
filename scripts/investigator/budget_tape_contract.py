"""Budget replay compares decisions/counts; opaque transports still compare bytes.

Accounting v2 is assigned retrospectively to #393 (7abaabf): physical overhead
and bounded resume controls changed the accounting contract. Sealed tapes are
never rewritten. v1 and v2 accounting remain replayable under their producer.
"""
import json

ACCOUNTING_VERSION = 2
ACCOUNTING_HISTORY = {1: 'Before #393', 2: '#393 7abaabf: physical guard/control accounting and bounded resume'}

def budget_value(body):
    value=json.loads(body)
    # SQLite reservation maps are JSON text within the journal. Decode only the
    # two declared count-map positions, never arbitrary strings or identifiers.
    if isinstance(value,dict) and isinstance(value.get('state'),dict):
        reservation=value['state'].get('reservation')
        if isinstance(reservation,list) and len(reservation)==3:
            for index in (1,2):
                if isinstance(reservation[index],str):
                    counts=json.loads(reservation[index])
                    if not isinstance(counts,dict):raise ValueError('Budget count map must be an object')
                    reservation[index]=counts
    return value

def equal(left,right):
    # Canonical structured equality preserves every field, decision and count.
    # It does not normalize event ordering, omitted fields or physical bodies.
    return json.dumps(budget_value(left),sort_keys=True,separators=(',',':')) == json.dumps(budget_value(right),sort_keys=True,separators=(',',':'))

def install(journal):
    """Versioned transport consumer for archived producers, not engine rewriting."""
    previous=journal.Tape.event
    def event(self,kind,body):
        if getattr(self,'replay_first_error',None) is not None:
            raise self.replay_first_error
        try:
            if self.replaying and kind=='BUDGET':
                if not equal(self.take(kind),body):raise journal.TapeError('TAPE_BUDGET_DECISION_DIFFERS')
                return
            return previous(self,kind,body)
        except journal.TapeError as exc:
            # Finally settlement must not disguise an earlier byte mismatch.
            if self.replaying:self.replay_first_error=exc
            raise
    journal.Tape.event=event
