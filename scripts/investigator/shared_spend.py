"""PostgreSQL dollar guard using the shared-state transaction boundary."""
import json
import os
from .process_tape import uuid4
from .shared_state import StateConflict, amount


class SharedSpendBudget:
    def __init__(self, state, ceiling_microdollars):
        from .model_spend import SpendHold
        self.state = state
        self.account = os.environ.get('INVESTIGATOR_MODEL_SPEND_ACCOUNT', 'model-microdollars')
        self.owner = os.environ.get('INVESTIGATOR_WORKER_ID')
        if not self.owner:
            raise SpendHold('Cloud model spending requires a worker identity')
        snapshot = state.snapshot(self.account)
        margin = int(os.environ.get('INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS','0'))
        if (snapshot['unit'] != 'MICRODOLLARS' or amount(snapshot['ceiling']) != ceiling_microdollars
                or amount(snapshot['protected']) != margin):
            raise SpendHold('Cloud dollar policy differs from the authoritative account')
        self.ceiling = ceiling_microdollars

    def reserve(self, body):
        from .model_spend import SpendBudget, SpendHold
        if not isinstance(body.get('input'),str):
            raise SpendHold('Dollar guard requires bounded text input; image cost is not established')
        inputs = len(json.dumps(body,ensure_ascii=False).encode('utf8'))+4096
        bound = SpendBudget.price(inputs,body['max_output_tokens'],model=body.get('model'))
        identity = 'cost-'+str(uuid4())
        try:
            return self.state.reserve(self.account,identity,self.owner,bound,detail={'model':body.get('model')})
        except StateConflict as exc:
            raise SpendHold(str(exc)) from exc

    def settle(self, identity, usage=None):
        from .model_spend import SpendBudget
        known = isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens'))
        row = next(r for r in self.state.snapshot(self.account)['reservations'] if r['identity']==identity)
        actual = SpendBudget.price(usage['input_tokens'],usage['output_tokens'],model=row['detail']['model']) if known else None
        return self.state.settle(self.account,identity,self.owner,actual,detail=usage if known else None)

    def snapshot(self):
        return self.state.snapshot(self.account)
