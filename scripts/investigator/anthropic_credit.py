"""Owner's October credit envelope over the two existing dollar accounts."""
import time
from datetime import datetime,timezone


def status(state,now=None):
    month=datetime.fromtimestamp(time.time() if now is None else now,timezone.utc).strftime('%Y-%m')
    def read(db):
        try:policy=state._get(db,'anthropic_credit',month)['body']
        except KeyError:return None
        model=state._totals(db,policy['model_account'])
        grading=state._totals(db,policy['grading_account'])
        model_delta=max(0,int(model['charged'])-policy['baseline_model_charged'])
        grading_delta=max(0,int(grading['charged'])-policy['baseline_grading_charged'])
        charged=policy['baseline_higher_microdollars']+model_delta+grading_delta
        return {'month_utc':month,'ceiling_microdollars':policy['normalized_ceiling_microdollars'],
                'charged_microdollars':charged,'remaining_microdollars':policy['normalized_ceiling_microdollars']-charged,
                'grading_remaining_microdollars':max(0,policy['protected_grading_microdollars']-grading_delta),
                'model_account':model,'grading_account':grading,'reserved_maxima_included':True,
                'basis':'Larger recorded ledger/console baseline plus subsequent charges across both existing accounts.'}
    return state._read_transaction(read)


def admit(state,db,account,bound,now=None,*,purpose=None):
    """One combined envelope, under the same serialized admission transaction."""
    month=datetime.fromtimestamp(time.time() if now is None else now,timezone.utc).strftime('%Y-%m')
    try:policy=state._get(db,'anthropic_credit',month)['body']
    except KeyError:return
    if account not in (policy['model_account'],policy['grading_account']):return
    model=state._totals(db,policy['model_account']);grading=state._totals(db,policy['grading_account'])
    model_delta=max(0,int(model['charged'])-policy['baseline_model_charged'])
    grading_delta=max(0,int(grading['charged'])-policy['baseline_grading_charged'])
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
