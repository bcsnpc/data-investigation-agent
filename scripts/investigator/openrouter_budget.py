"""Synthetic DEV quota; free daily calls and conditional lifetime $10 are separate."""
import json
import time
from datetime import datetime, timezone
from .nvidia_free_budget import FreeBudget as NvidiaBudget, FreeRateCard
from .reasoning_budget import TicketBudget, RateCard
from .shared_state import amount, encoded, sha
from .model_spend import SpendHold

PAID_ACCOUNT = 'provider-openrouter-microdollars:lifetime'
QUEUE_ID = 'all-openrouter-dispatches'


def account_for(now):
    return 'openrouter-free-calls:' + datetime.fromtimestamp(now, timezone.utc).date().isoformat()


def provision(state, now, key_info):
    """Owner path only. Store safe counters, never the key or its label."""
    quota=key_info.get('free_model_daily_requests') or {}
    limit, used=quota.get('limit'), quota.get('used')
    if (type(limit)is not int or not 0<limit<=1000 or type(used)is not int or used<0
            or key_info.get('limit')!=10 or key_info.get('limit_remaining') is None):
        raise SpendHold('OPENROUTER_VERIFIED_KEY_QUOTA_REQUIRED')
    account=account_for(now)
    with state.transaction() as db:
        prior=state.sql(db,'SELECT unit,ceiling FROM state_accounts WHERE identity=?',(account,)).fetchone()
        if prior:
            if prior[0]!='CALLS' or amount(prior[1])!=limit:raise SpendHold('OPENROUTER_DAILY_POLICY_DIFFERS')
        else:
            state.sql(db,'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',(account,'CALLS',limit,used,0,0))
        body={'observed_at':now,'daily_account':account,'limit':limit,'remote_used':used,
              'remote_remaining':quota.get('remaining'),'key_limit_usd':10,
              'key_limit_reset':key_info.get('limit_reset'),'key_remaining_usd':key_info['limit_remaining'],
              'key_usage_usd':key_info.get('usage',0)}
        prior=state.sql(db,'SELECT revision FROM state_documents WHERE namespace=? AND identity=?',('openrouter-key-quota',account)).fetchone()
        if prior:state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',(prior[0]+1,encoded(body),sha(body),'openrouter-key-quota',account))
        else:state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('openrouter-key-quota',account,0,encoded(body),sha(body)))
        if not state.sql(db,'SELECT 1 FROM state_accounts WHERE identity=?',(PAID_ACCOUNT,)).fetchone():
            usage=key_info.get('usage',0)
            opening=int(amount(usage)*1000000)
            state.sql(db,'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',(PAID_ACCOUNT,'MICRODOLLARS',10000000,opening,0,0))
    return account


class FreeBudget(NvidiaBudget):
    provider='openrouter'
    interval=3
    concurrency=2
    account_for=staticmethod(account_for)

    def queue_identity(self,account):
        return QUEUE_ID

    def __init__(self,*args,provider='openrouter',**kwargs):
        super().__init__(*args,provider=provider,**kwargs)
        if not self.rate.model.endswith(':free'):raise SpendHold('OPENROUTER_FREE_MODEL_SUFFIX_REQUIRED')
        self.check_policy()

    def check_policy(self):
        from .provider_budget import policy
        approved=policy('openrouter')
        if (approved.get('free_daily_call_allowance')!=1000 or approved.get('minimum_dispatch_interval_seconds')!=3
                or approved.get('maximum_concurrent_calls')!=2 or approved.get('synthetic_only')is not True
                or approved.get('quality_scope')!='DEV_ONLY'):
            raise SpendHold('OPENROUTER_FREE_CONFIGURATION_POLICY_DIFFERS')
        def read(db):
            row=self.state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',('openrouter-key-quota',account_for(self.clock()))).fetchone()
            return json.loads(row[0]) if row else None
        observed=self.state._read_transaction(read)
        if not observed or not 0<=self.clock()-observed['observed_at']<86400:
            raise SpendHold('OPENROUTER_FRESH_KEY_QUOTA_REQUIRED')
        self.allowance=observed['limit']

    def status(self):
        value=super().status()
        day=value.pop('month_account');used=value.pop('monthly_calls_used');value.pop('monthly_call_allowance')
        return {**value,'charge_basis':'OPENROUTER_FREE_ALLOCATION_NOT_INVOICE',
                'day_account':day,'daily_calls_used':used,
                'daily_call_allowance':self.allowance}

    def active_count(self,db,account):
        return self.state.sql(db,"SELECT COUNT(*) FROM state_reservations WHERE (account LIKE ? OR account=?) AND status='RESERVED'",('openrouter-free-calls:%',PAID_ACCOUNT)).fetchone()[0]


def require_failed_free_tests(state):
    """Never infer paid permission from transport failure or an empty test list."""
    row=state._read_transaction(lambda db:state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',('openrouter-qualification','all-free-tool-tests')).fetchone())
    record=json.loads(row[0]) if row else {}
    candidates=record.get('discovered_free_tool_models',[])
    results=record.get('results',[])
    if (not candidates or len(set(candidates))!=len(candidates) or len(results)!=len(candidates)
            or {r.get('model')for r in results}!=set(candidates)
            or any(not m.endswith(':free')for m in candidates)
            or any(r.get('status')!='FAILED' or not r.get('capture_sha256') for r in results)):
        raise SpendHold('OPENROUTER_PAID_REQUIRES_ALL_FREE_TOOL_TESTS_FAILED')


class PaidBudget(TicketBudget):
    def __init__(self,*args,provider='openrouter',sleep=time.sleep,**kwargs):
        super().__init__(*args,provider=provider,**kwargs)
        if provider!='openrouter' or self.rate.model.endswith(':free') or not self.owner.startswith('round27-free-'):
            raise SpendHold('OPENROUTER_SYNTHETIC_DEV_PAID_CONFIGURATION_REQUIRED')
        self.sleep=sleep

    def _account(self):
        from .provider_budget import check_credit
        check_credit('openrouter',self.clock(),owner=self.owner,purpose=self.purpose)
        require_failed_free_tests(self.state)
        value=self.state.totals(PAID_ACCOUNT)
        if value['unit']!='MICRODOLLARS' or amount(value['ceiling'])!=10000000:raise SpendHold('OPENROUTER_LIFETIME_TEN_DOLLAR_CAP_REQUIRED')
        row=self.state._read_transaction(lambda db:self.state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',('openrouter-key-quota',account_for(self.clock()))).fetchone())
        observed=json.loads(row[0]) if row else {}
        if not observed or not 0<=self.clock()-observed['observed_at']<86400:raise SpendHold('OPENROUTER_FRESH_KEY_QUOTA_REQUIRED')
        charged=amount(value['charged'])
        remote_used=amount(observed['key_usage_usd'])*1000000
        remote_remaining=amount(observed['key_remaining_usd'])*1000000
        self.approved_ceiling=min(10000000,charged+remote_remaining,10000000-max(0,remote_used-charged))
        if self.approved_ceiling<=charged:raise SpendHold('OPENROUTER_LIFETIME_CREDIT_EXHAUSTED')
        return PAID_ACCOUNT

    def _ceiling(self):
        return self.approved_ceiling

    def reserve(self,body,**kwargs):
        # Same global 20 RPM dispatch queue as the free path; no connection during waits.
        self._account()
        if body.get('provider',{}).get('max_price')!={'prompt':float(self.rate.input_rate),'completion':float(self.rate.output_rate)}:
            raise SpendHold('OPENROUTER_PAID_RATE_BOUND_REQUIRED')
        while True:
            now=self.clock();account=account_for(now)
            with self.state.transaction() as db:
                prior=self.state.sql(db,'SELECT revision,body FROM state_documents WHERE namespace=? AND identity=?',('openrouter-free-queue',QUEUE_ID)).fetchone()
                next_at=json.loads(prior[1])['next_dispatch_at'] if prior else 0
                wait=next_at-now
                active=self.state.sql(db,"SELECT COUNT(*) FROM state_reservations WHERE (account LIKE ? OR account=?) AND status='RESERVED'",('openrouter-free-calls:%',PAID_ACCOUNT)).fetchone()[0]
                if active>=2:wait=max(3,wait)
                if wait<=0:
                    queue={'next_dispatch_at':now+3}
                    if prior:self.state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',(prior[0]+1,encoded(queue),sha(queue),'openrouter-free-queue',QUEUE_ID))
                    else:self.state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('openrouter-free-queue',QUEUE_ID,0,encoded(queue),sha(queue)))
            if wait<=0:break
            self.sleep(wait)
        return super().reserve(body,**kwargs)
