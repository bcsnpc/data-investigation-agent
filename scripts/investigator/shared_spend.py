"""PostgreSQL dollar guard using the shared-state transaction boundary."""
import json
import os
from .process_tape import uuid4
from .shared_state import StateConflict, amount


class SharedSpendBudget:
    def __init__(self, state, ceiling_microdollars):
        from .model_spend import SpendHold
        from . import build_phase
        import time
        self.state = state
        self.build_phase = build_phase.active()
        self.account = os.environ.get('INVESTIGATOR_MODEL_SPEND_ACCOUNT', 'model-microdollars')
        self.owner = os.environ.get('INVESTIGATOR_WORKER_ID')
        if not self.owner:
            raise SpendHold('Cloud model spending requires a worker identity')
        if self.build_phase:
            self.account = build_phase.ensure_model_account(state,time.time())
            self.ceiling = build_phase.MODEL_MICRODOLLARS
            self.monthly_reservation_accounts = {}
            return
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
            if self.build_phase:
                from .shared_state import encoded
                from .build_phase import ensure_model_account
                import time
                self.account=ensure_model_account(self.state,time.time())
                with self.state.transaction() as db:
                    snapshot=self.state._snapshot(db,self.account)
                    # The owner-managed account remains authoritative. A newer
                    # image must not silently raise an existing account's cap.
                    ceiling = min(self.ceiling, amount(snapshot['ceiling']) - amount(snapshot['protected']))
                    if amount(snapshot['charged'])+bound>ceiling:
                        raise SpendHold('MONTHLY_MODEL_EXHAUSTED')
                    self.state.sql(db,'INSERT INTO state_reservations VALUES(?,?,?,?,?,?,?)',
                        (self.account,identity,self.owner,bound,bound,'RESERVED',encoded({'model':body.get('model')})))
                self.monthly_reservation_accounts[identity]=self.account
                return identity
            return self.state.reserve(self.account,identity,self.owner,bound,detail={'model':body.get('model')})
        except StateConflict as exc:
            raise SpendHold(str(exc)) from exc

    def settle(self, identity, usage=None):
        from .model_spend import SpendBudget
        known = isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens'))
        account=self.monthly_reservation_accounts.get(identity,self.account) if self.build_phase else self.account
        row = next(r for r in self.state.snapshot(account)['reservations'] if r['identity']==identity)
        actual = SpendBudget.price(usage['input_tokens'],usage['output_tokens'],model=row['detail']['model']) if known else None
        return self.state.settle(account,identity,self.owner,actual,detail=usage if known else None)

    def snapshot(self):
        if self.build_phase:
            from .build_phase import ensure_model_account
            import time
            self.account=ensure_model_account(self.state,time.time())
        result=self.state.snapshot(self.account)
        if self.build_phase:
            from .build_phase import model_status
            result['monthly']=model_status(int(amount(result['charged'])),self.account.rsplit(':',1)[1])
        return result
