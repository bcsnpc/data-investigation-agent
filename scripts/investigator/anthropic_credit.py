"""Owner's October credit envelope over the two existing dollar accounts."""
import time,json
from datetime import datetime,timezone


def policy_for(state,db,month):
    try:return state._get(db,'anthropic_credit',month)['body']
    except KeyError:
        if month<'2026-11':return None
        # Owner's standing monthly policy; counters remain month-scoped.
        return {'model_account':'model-microdollars:'+month,'grading_account':'enrichment:round-twenty-one',
          'baseline_model_charged':0,'baseline_grading_charged':0,'baseline_higher_microdollars':0,
          'normalized_ceiling_microdollars':150000000,'protected_grading_microdollars':3000000,
          'grading_month_tag':month}


def grading_totals(state,db,account):
    try:return state._totals(db,account)
    except KeyError:return {'identity':account,'charged':'0','not_provisioned':True}


def grading_charge(state,db,policy,totals):
    if 'grading_month_tag' not in policy:return max(0,int(totals['charged'])-policy['baseline_grading_charged'])
    rows=state.sql(db,'SELECT charged,detail FROM state_reservations WHERE account=?',(policy['grading_account'],)).fetchall()
    return sum(int(charged) for charged,detail in rows if json.loads(detail).get('month_utc')==policy['grading_month_tag'])


def status(state,now=None):
    month=datetime.fromtimestamp(time.time() if now is None else now,timezone.utc).strftime('%Y-%m')
    def read(db):
        policy=policy_for(state,db,month)
        if policy is None:return None
        model=state._totals(db,policy['model_account'])
        grading=grading_totals(state,db,policy['grading_account'])
        model_delta=max(0,int(model['charged'])-policy['baseline_model_charged'])
        grading_delta=grading_charge(state,db,policy,grading)
        charged=policy['baseline_higher_microdollars']+model_delta+grading_delta
        extra=pending_exposure(state,db,policy['model_account'])+pending_exposure(state,db,policy['grading_account'])
        purposes={name:0 for name in ('INVESTIGATOR','SCREENSHOT','ENRICHMENT','WRITER','GRADING','SMOKE','UNATTRIBUTED_HISTORICAL')}
        rows=state.sql(db,'SELECT account,charged,detail FROM state_reservations WHERE account IN (?,?)',(policy['model_account'],policy['grading_account'])).fetchall()
        for account,value,detail in rows:
            detail=json.loads(detail)
            if account==policy['grading_account'] and 'grading_month_tag'in policy and detail.get('month_utc')!=month:continue
            purpose=detail.get('purpose','UNATTRIBUTED_HISTORICAL')
            if purpose=='ENRICHMENT_ONLY':purpose='ENRICHMENT'
            purposes[purpose if purpose in purposes else 'UNATTRIBUTED_HISTORICAL']+=int(value)
        # Retained console/ledger normalization is an offset, never erased.
        purposes['UNATTRIBUTED_HISTORICAL']+=charged-sum(purposes.values())

        return {'month_utc':month,'ceiling_microdollars':policy['normalized_ceiling_microdollars'],
                'charged_microdollars':charged,'additional_pending_commitment_microdollars':extra,'committed_microdollars':charged+extra,'remaining_microdollars':policy['normalized_ceiling_microdollars']-charged-extra,
                'warning':charged>=100000000,'monthly_credit_microdollars':100000000,'by_ai_step_microdollars':purposes,
                'grading_remaining_microdollars':max(0,policy['protected_grading_microdollars']-grading_delta),
                'model_account':model,'grading_account':grading,'reserved_maxima_included':True,
                'basis':'Larger recorded ledger/console baseline plus subsequent charges across both existing accounts.'}
    return state._read_transaction(read)


def admit(state,db,account,bound,now=None,*,purpose=None):
    """One combined envelope, under the same serialized admission transaction."""
    month=datetime.fromtimestamp(time.time() if now is None else now,timezone.utc).strftime('%Y-%m')
    policy=policy_for(state,db,month)
    if policy is None:return
    if account not in (policy['model_account'],policy['grading_account']):return
    model=state._totals(db,policy['model_account']);grading=grading_totals(state,db,policy['grading_account'])
    model_delta=max(0,int(model['charged'])-policy['baseline_model_charged'])
    grading_delta=grading_charge(state,db,policy,grading)
    total=policy['baseline_higher_microdollars']+model_delta+grading_delta+pending_exposure(state,db,policy['model_account'])+pending_exposure(state,db,policy['grading_account'])
    protected=max(0,policy['protected_grading_microdollars']-grading_delta) if account==policy['model_account'] and purpose!='GRADING' else 0
    if total+bound+protected>policy['normalized_ceiling_microdollars']:
        from .model_spend import SpendHold
        raise SpendHold('COMBINED_ANTHROPIC_MONTHLY_EXHAUSTED')


def pending_exposure(state,db,account):
    """Unspent maximum commitments protect the hard monthly cap across workers."""
    import json
    result=0
    for charged,detail in state.sql(db,"SELECT charged,detail FROM state_reservations WHERE account=? AND status='RESERVED'",(account,)).fetchall():
        maximum=json.loads(detail).get('maximum_commitment_microdollars')
        if maximum is not None:result+=max(0,int(maximum)-int(charged))
    return result
