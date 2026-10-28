"""Owner-approved Round24 policy migration; never alters charges or identities."""
from copy import deepcopy
from investigator.shared_state import encoded,sha
from investigator.build_phase import POLICY


def apply(state):
    configured=POLICY['round24']
    with state.transaction() as db:
        # Hash only immutable accounting fields; policy ceilings are the sole changes.
        def accounting():
            return sha({'reservations':[list(map(str,r))for r in state.sql(db,'SELECT * FROM state_reservations ORDER BY account,identity').fetchall()],
                'usage':[list(map(str,r))for r in state.sql(db,'SELECT * FROM state_usage ORDER BY environment,session_id,reservation_key').fetchall()]})
        conserved=accounting()
        prior=state._get(db,'build_phase_policy','monthly-physical');body=deepcopy(prior['body'])
        body.update(total_limit=12000,limits=configured['october']['limits'],limits_effective_month='2026-10',default_total_limit=9000,default_limits=configured['default']['limits'],approval=configured['approval'],effective_at=configured['effective_at'],allocation_reason='Round24 purchased credit and October-only request increase; usage unchanged.')
        state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',(prior['revision']+1,encoded(body),sha(body),'build_phase_policy','monthly-physical'))
        credit=state._get(db,'anthropic_credit','2026-10');new=deepcopy(credit['body']);new.update(normalized_ceiling_microdollars=146000000,approval=configured['approval'],round24_effective_at=configured['effective_at'])
        # Keep the original offset and grading usage; replenish protected grading to3 for this round.
        grading=state._totals(db,new['grading_account']);delta=max(0,int(grading['charged'])-new['baseline_grading_charged'])
        new['protected_grading_microdollars']=delta+3000000
        state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',(credit['revision']+1,encoded(new),sha(new),'anthropic_credit','2026-10'))
        accounts=[]
        for month,cap in [('2026-10',146000000),('2026-11',150000000)]:
            name='model-microdollars:'+month;before=state._totals(db,name)
            state.sql(db,'UPDATE state_accounts SET ceiling=?,protected=? WHERE identity=?',(cap,3000000,name));accounts.append({'before':before,'after':state._totals(db,name)})
        if accounting()!=conserved:raise AssertionError('ACCOUNTING_CHANGED')
        return {'approval':configured['approval'],'physical_before':prior,'physical_after':body,'credit_before':credit,'credit_after':new,'accounts':accounts,'accounting_sha256_unchanged':conserved}
