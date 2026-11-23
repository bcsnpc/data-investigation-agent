"""Owner-approved synthetic dev quota. Units are calls, never paid dollars."""
import json
import time
from decimal import Decimal
from .shared_state import encoded, sha, amount
from .process_tape import uuid4
from .build_phase import month_window
from .model_spend import SpendHold

MONTHLY_CALLS = 1000
INTERVAL = 1.5
CONCURRENCY = 2


class FreeRateCard:
    def __init__(self, *, model, input_rate, output_rate, source, observed_at,
                 base_input_rate=0, cache_read_rate=0, cache_write_rate=0):
        if not model or not source.startswith('https://') or not observed_at:
            raise ValueError('DOCUMENTED_FREE_TIER_REQUIRED')
        values = (input_rate, output_rate, base_input_rate, cache_read_rate, cache_write_rate)
        if any(Decimal(str(v)) != 0 for v in values):
            raise ValueError('NVIDIA_FREE_ZERO_RATES_REQUIRED')
        self.model, self.source, self.observed_at = model, source, observed_at
        self.input_rate = self.output_rate = self.base_input_rate = self.cache_read_rate = self.cache_write_rate = Decimal(0)

    def price(self, inputs, outputs):
        if any(type(v) is not int or v < 0 for v in (inputs, outputs)):
            raise ValueError('EXACT_TOKEN_COUNTS_REQUIRED')
        return 0

    def usage_price(self, usage):
        for k in ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'):
            if type(usage.get(k, 0)) is not int or usage.get(k, 0) < 0:
                raise ValueError('EXACT_TOKEN_COUNTS_REQUIRED')
        return 0


def account_for(now):
    return 'nvidia-free-calls:' + month_window(now)[0]


def provision(state, now):
    account = account_for(now)
    with state.transaction() as db:
        row = state.sql(db, 'SELECT unit,ceiling FROM state_accounts WHERE identity=?', (account,)).fetchone()
        if row:
            if row[0] != 'CALLS' or amount(row[1]) != MONTHLY_CALLS:
                raise SpendHold('NVIDIA_FREE_POLICY_DIFFERS')
        else:
            state.sql(db, 'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)', (account, 'CALLS', MONTHLY_CALLS, 0, 0, 0))
    return account


class FreeBudget:
    provider = 'nvidia'

    def __init__(self, state, *, case_id, owner, rate, clock=time.time, sleep=time.sleep,
                 actual_usage_limit=None, purpose=None, provider='nvidia'):
        if provider != 'nvidia' or not isinstance(rate, FreeRateCard) or not case_id or not owner.startswith('round27-free-'):
            raise ValueError('SYNTHETIC_DEV_FREE_BUDGET_REQUIRED')
        self.state, self.case_id, self.owner, self.rate = state, case_id, owner, rate
        from .reasoning_budget import PURPOSE
        self.clock, self.sleep, self.purpose = clock, sleep, purpose or PURPOSE.get()
        if self.purpose not in ('INTAKE', 'INVESTIGATOR', 'EVALUATOR', 'SCREENSHOT', 'SUMMARY', 'GRADING', 'SMOKE'):
            raise ValueError('NVIDIA_DEV_PURPOSE_REQUIRED')
        self.reservations = {}

    def reserve(self, body, *, input_tokens_upper_bound=None):
        from .provider_budget import check_credit
        check_credit('nvidia', self.clock(), owner=self.owner, purpose=self.purpose)
        if body.get('model') != self.rate.model or type(body.get('max_tokens')) is not int or not 1 <= body['max_tokens'] <= 16000:
            raise SpendHold('NVIDIA_PINNED_MODEL_OUTPUT_BOUND')
        identity = 'nvidia-free:' + str(uuid4())
        request_hash = sha(body)
        account = account_for(self.clock())
        while True:
            result = self.state._retry_connection_operation('IDEMPOTENT_NVIDIA_FREE_CALL',
                lambda: self._reserve_attempt(identity, account, request_hash))
            if result is None:
                self.reservations[identity] = account
                return identity
            self.sleep(result)  # Never hold a connection across a wait or API call.

    def _reserve_attempt(self, identity, account, request_hash):
        now = self.clock()
        if account_for(now) != account:
            raise SpendHold('NVIDIA_FREE_MONTH_CHANGED_RETRY_ADMISSION')
        with self.state.transaction() as db:
            existing = self.state.sql(db, 'SELECT owner,status,detail FROM state_reservations WHERE account=? AND identity=?', (account, identity)).fetchone()
            if existing:
                detail = json.loads(existing[2])
                if (existing[0] != self.owner or existing[1] != 'RESERVED' or
                        detail.get('request_hash') != request_hash or detail.get('case_id') != self.case_id):
                    raise SpendHold('NVIDIA_FREE_RESERVATION_ID_CONFLICT')
                return None  # Commit acknowledgement was lost; never charge twice.
            try: totals = self.state._totals(db, account)
            except KeyError: raise SpendHold('NVIDIA_FREE_ACCOUNT_NOT_PROVISIONED') from None
            if totals['unit'] != 'CALLS' or amount(totals['ceiling']) != MONTHLY_CALLS:
                raise SpendHold('NVIDIA_FREE_POLICY_DIFFERS')
            if totals['violated'] or amount(totals['charged']) >= MONTHLY_CALLS:
                raise SpendHold('NVIDIA_FREE_MONTHLY_CALL_ALLOWANCE_EXHAUSTED')
            active = self.state.sql(db, "SELECT COUNT(*) FROM state_reservations WHERE account=? AND status='RESERVED'", (account,)).fetchone()[0]
            prior = self.state.sql(db, 'SELECT revision,body FROM state_documents WHERE namespace=? AND identity=?', ('nvidia-free-queue', account)).fetchone()
            next_at = json.loads(prior[1])['next_dispatch_at'] if prior else 0
            if active < CONCURRENCY and now >= next_at:
                detail = {'case_id': self.case_id, 'model': self.rate.model, 'provider': 'nvidia',
                          'label': 'nvidia-free', 'quality_scope': 'DEV_ONLY', 'purpose': self.purpose,
                          'cost_microdollars': 0, 'created_at': now, 'request_hash': request_hash}
                self.state.sql(db, 'INSERT INTO state_reservations VALUES(?,?,?,?,?,?,?)',
                               (account, identity, self.owner, 1, 1, 'RESERVED', encoded(detail)))
                queue = {'next_dispatch_at': now + INTERVAL}
                if prior:
                    self.state.sql(db, 'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                                   (prior[0] + 1, encoded(queue), sha(queue), 'nvidia-free-queue', account))
                else:
                    self.state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)', ('nvidia-free-queue', account, 0, encoded(queue), sha(queue)))
                return None
            return max(INTERVAL if active >= CONCURRENCY else .01, next_at - now)

    def settle(self, identity, usage=None):
        known = isinstance(usage, dict) and all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens'))
        return self.state.settle(self.reservations[identity], identity, self.owner, 1 if known else None,
                                detail={'label': 'nvidia-free', 'cost_microdollars': 0, 'usage': usage if known else None}, full_snapshot=False)

    def output_limit(self, inputs, requested):
        if type(requested) is not int or not 1 <= requested <= 16000: raise SpendHold('MODEL_OUTPUT_BOUND_REQUIRED')
        return requested

    def status(self):
        totals = self.state.totals(account_for(self.clock()))
        return {'charged_microdollars': 0, 'ceiling_microdollars': 3000000, 'warning': False,
                'charge_basis': 'NVIDIA_FREE_ALLOCATION_NOT_INVOICE', 'quality_scope': 'DEV_ONLY',
                'month_account': account_for(self.clock()), 'monthly_calls_used': int(amount(totals['charged'])),
                'monthly_call_allowance': MONTHLY_CALLS}
