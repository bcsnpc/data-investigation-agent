"""Claude reasoning charges use the investigator account, never enrichment.

Reservations live in the existing shared authority and stay charged if the
provider outcome is unknown. Only counts, model and case IDs enter this ledger.
"""
from decimal import Decimal, ROUND_CEILING
import json
import time
from contextvars import ContextVar
from contextlib import contextmanager

PURPOSE=ContextVar("anthropic_ai_step",default="INVESTIGATOR")

@contextmanager
def ai_step(name):
    token=PURPOSE.set(name)
    try:yield
    finally:PURPOSE.reset(token)

from .build_phase import (MODEL_MICRODOLLARS,TICKET_MODEL_MICRODOLLARS,
                          TICKET_MODEL_WARNING_MICRODOLLARS,ensure_model_account)
from .model_spend import SpendHold
from .shared_state import amount, encoded
from .process_tape import uuid4


class RateCard:
    def __init__(self,*,model,input_rate,output_rate,source,observed_at,base_input_rate=None,cache_read_rate=None):
        if not model or not source.startswith('https://') or not observed_at:
            raise ValueError('DOCUMENTED_MODEL_RATE_REQUIRED')
        self.model=model;self.input_rate=Decimal(str(input_rate));self.output_rate=Decimal(str(output_rate))
        if any(not v.is_finite() or v<=0 for v in (self.input_rate,self.output_rate)):
            raise ValueError('POSITIVE_EXACT_MODEL_RATE_REQUIRED')
        self.source,self.observed_at=source,observed_at
        self.base_input_rate=Decimal(str(base_input_rate)) if base_input_rate is not None else self.input_rate
        self.cache_read_rate=Decimal(str(cache_read_rate)) if cache_read_rate is not None else self.input_rate
        if any(not v.is_finite() or v<0 or v>self.input_rate for v in (self.base_input_rate,self.cache_read_rate)):
            raise ValueError('INPUT_RESERVATION_RATE_MUST_BOUND_CACHE_AND_BASE_RATES')

    def price(self,inputs,outputs):
        if any(type(v) is not int or v<0 for v in (inputs,outputs)):raise ValueError('EXACT_TOKEN_COUNTS_REQUIRED')
        # USD per million tokens equals microdollars per token. Input rate
        # must bound cache writes too if the provider enables prompt caching.
        return int((inputs*self.input_rate+outputs*self.output_rate).to_integral_value(rounding=ROUND_CEILING))

    def usage_price(self,usage):
        counts={k:usage.get(k,0) for k in ('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')}
        if any(type(v) is not int or v<0 for v in counts.values()):raise ValueError('EXACT_USAGE_COUNTS_REQUIRED')
        total=(counts['input_tokens']*self.base_input_rate+counts['output_tokens']*self.output_rate+
               counts['cache_creation_input_tokens']*self.input_rate+counts['cache_read_input_tokens']*self.cache_read_rate)
        return int(total.to_integral_value(rounding=ROUND_CEILING))


class TicketBudget:
    def __init__(self,state,*,case_id,owner,rate,clock=time.time,actual_usage_limit=None,purpose=None):
        if not case_id or not owner:raise ValueError('CASE_AND_WORKER_REQUIRED')
        if actual_usage_limit is not None and (type(actual_usage_limit)is not int or actual_usage_limit!=3_000_000):
            raise ValueError('OWNER_DIAGNOSTIC_LIMIT_REQUIRED')
        self.state,self.case_id,self.owner,self.rate,self.clock=state,case_id,owner,rate,clock
        purpose=purpose or PURPOSE.get()
        if purpose not in ('INVESTIGATOR','SCREENSHOT','ENRICHMENT','WRITER','GRADING','SMOKE'):raise ValueError('MODEL_PURPOSE_REQUIRED')
        self.purpose=purpose
        self.actual_usage_limit=actual_usage_limit
        self.reservations={}

    def _charged(self,db,account):
        selector="(detail::jsonb ->> 'case_id')" if self.state.backend=='postgresql' else "json_extract(detail,'$.case_id')"
        settled=" AND status IN ('SETTLED','UNCERTAIN')" if self.actual_usage_limit is not None else ''
        rows=self.state.sql(db,"SELECT charged FROM state_reservations WHERE account LIKE ? AND "+selector+'=?'+settled,
                            ('model-microdollars:%',self.case_id)).fetchall()
        # Per-ticket does not reset when a long-running case crosses UTC month.
        return sum((amount(row[0]) for row in rows),Decimal(0))

    def reserve(self,body,*,input_tokens_upper_bound=None):
        if body.get('model')!=self.rate.model:raise SpendHold('MODEL_DIFFERS_FROM_RATE_CARD')
        output=body.get('max_tokens')
        if type(output) is not int or not 1<=output<=16000:raise SpendHold('MODEL_OUTPUT_BOUND_REQUIRED')
        inputs=len(encoded(body).encode('utf8'))+4096 if input_tokens_upper_bound is None else input_tokens_upper_bound
        if type(inputs) is not int or inputs<1:raise SpendHold('INPUT_TOKEN_BOUND_REQUIRED')
        maximum=self.rate.price(inputs,output)
        # Ticket actual-use policy estimates a normal response plus25% margin;
        # the monthly ledger separately commits the full permitted response.
        estimated_output=min(output,2500)
        bound=self.rate.price(inputs,estimated_output) if self.actual_usage_limit is not None else maximum
        account=ensure_model_account(self.state,self.clock())
        identity='reasoning:'+str(uuid4())
        detail={'case_id':self.case_id,'model':self.rate.model,'purpose':self.purpose,
                'rate_source':self.rate.source,'rate_observed_at':self.rate.observed_at,
                'input_rate':str(self.rate.input_rate),'output_rate':str(self.rate.output_rate),
                'base_input_rate':str(self.rate.base_input_rate),'cache_read_rate':str(self.rate.cache_read_rate),
                'input_bound_source':'UTF8_BYTES_PLUS_4096' if input_tokens_upper_bound is None else 'PROVIDER_TOKEN_COUNT_PLUS_4096',
                'estimate_type':'CONSERVATIVE_RATE_CARD_NOT_INVOICE'}
        with self.state.transaction() as db:
            snapshot=self.state._totals(db,account)
            if snapshot['violated']:raise SpendHold('MODEL_ACCOUNT_VIOLATION')
            from .build_phase import model_ceiling
            monthly_ceiling=min(amount(snapshot['ceiling'])-(0 if self.purpose=='GRADING' else amount(snapshot['protected'])),model_ceiling(self.clock()))
            from .anthropic_credit import pending_exposure
            committed=pending_exposure(self.state,db,account)
            if amount(snapshot['charged'])+committed+maximum>monthly_ceiling:raise SpendHold('MONTHLY_MODEL_EXHAUSTED')
            charged=self._charged(db,account)
            if ((self.actual_usage_limit is not None and charged>=self.actual_usage_limit)
                    or (self.actual_usage_limit is None and charged+bound>TICKET_MODEL_MICRODOLLARS)):
                raise SpendHold('TICKET_MODEL_EXHAUSTED')
            if self.actual_usage_limit is not None:
                detail.update(charge_basis='ACTUAL_PROVIDER_USAGE',ticket_limit_microdollars=self.actual_usage_limit,maximum_commitment_microdollars=maximum,reservation_is_estimate=True)
            from .anthropic_credit import admit
            admit(self.state,db,account,maximum,self.clock(),purpose=self.purpose)
            self.state.sql(db,'INSERT INTO state_reservations VALUES(?,?,?,?,?,?,?)',
                (account,identity,self.owner,bound,bound,'RESERVED',encoded(detail)))
        self.reservations[identity]=account
        return identity

    def output_limit(self,inputs,requested):
        """Fit the output reservation inside both unchanged dollar ceilings."""
        if type(inputs) is not int or inputs<1 or type(requested) is not int or not 1<=requested<=16000:
            raise SpendHold('MODEL_RESERVATION_BOUND_REQUIRED')
        account=ensure_model_account(self.state,self.clock())
        with self.state.transaction(_read_only=True) as db:
            snapshot=self.state._totals(db,account)
            if snapshot['violated']:raise SpendHold('MODEL_ACCOUNT_VIOLATION')
            case_available=(self.actual_usage_limit or TICKET_MODEL_MICRODOLLARS)-self._charged(db,account)
            if case_available<=0:raise SpendHold('TICKET_MODEL_EXHAUSTED')
            from .build_phase import model_ceiling
            monthly_available=min(amount(snapshot['ceiling'])-(0 if self.purpose=='GRADING' else amount(snapshot['protected'])),model_ceiling(self.clock()))-amount(snapshot['charged'])
            available=monthly_available if self.actual_usage_limit is not None else min(case_available,monthly_available)
        result=min(requested,int((available-inputs*self.rate.input_rate)/self.rate.output_rate))
        if result<512:raise SpendHold('TICKET_MODEL_EXHAUSTED')
        return result

    def settle(self,identity,usage=None):
        account=self.reservations[identity]
        cost=None
        if isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens')):
            cost=self.rate.usage_price(usage)
        return self.state.settle(account,identity,self.owner,cost,detail={'usage':usage if cost is not None else None},full_snapshot=False)

    def status(self):
        account=ensure_model_account(self.state,self.clock())
        with self.state.transaction(_read_only=True) as db:
            charged=self._charged(db,account)
        limit=self.actual_usage_limit or TICKET_MODEL_MICRODOLLARS
        result={'charged_microdollars':int(charged),'ceiling_microdollars':limit,
                'warning':charged>=(limit//2 if self.actual_usage_limit else TICKET_MODEL_WARNING_MICRODOLLARS),'month_account':account}
        if self.actual_usage_limit is not None:
            result.update(charge_basis='ACTUAL_PROVIDER_USAGE',monthly_commitments_remain_conservative=True,
                          limit_is_actual_use_stop=True,final_inflight_call_may_cross_ticket_threshold=True)
        return result
