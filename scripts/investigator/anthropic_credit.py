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
