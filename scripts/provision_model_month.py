"""Owner-only monthly policy setup; grants no privilege and prints no token."""
import argparse
import json
import subprocess
import time


def round23_policy(state,now):
    """Existing owner path: update only the approved monthly policy ceiling."""
    from investigator.build_phase import ensure_model_account,MODEL_MICRODOLLARS
    from investigator.shared_state import amount,encoded,sha
    account=ensure_model_account(state,now,provision=True)
    with state.transaction() as db:
        before=state._snapshot(db,account)
        if (before['unit']!='MICRODOLLARS' or amount(before['protected'])!=0
                or amount(before['ceiling']) not in (40000000,150000000)):
            raise ValueError('MONTHLY_POLICY_DIFFERS_FROM_OWNER_APPROVED_40_TO_150')
        state.sql(db,'UPDATE state_accounts SET ceiling=? WHERE identity=?',(MODEL_MICRODOLLARS,account))
        after=state._snapshot(db,account)
        # No charges, reservations, violation flags or opening balance change.
        if {k:v for k,v in before.items() if k!='ceiling'}!={k:v for k,v in after.items() if k!='ceiling'}:
            raise ValueError('POLICY_UPDATE_CHANGED_ACCOUNTING')
        record={'approval':'owner-approved 2026-10-26','purpose':'Round23 investigator monthly USD40 to USD150',
                'account':account,'before':before,'after':after}
        identity=account+':round23-150'
        previous=state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',
                           ('owner_budget_decisions',identity)).fetchone()
        if previous is None:
            state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',
                      ('owner_budget_decisions',identity,0,encoded(record),sha(record)))
    return record



def round23_request_policy(state, now):
    """Owner-only perpetual monthly request ceiling; counters are never rewritten."""
    from investigator.shared_state import encoded,sha
    from investigator.build_phase import shared_physical_rows,physical_status
    import json
    policy={'approval':'owner-approved 2026-10-26','effective_at':'2026-10-26T00:00:00+00:00',
            'total_limit':9000,'limits':{'SCAN':2000,'INVESTIGATION':6905,'RESTORATION':95},
            'period':'UTC calendar month; October starts at build adoption',
            'restoration_use':'restores only'}
    with state.transaction() as db:
        row=state.sql(db,'SELECT revision,body FROM state_documents WHERE namespace=? AND identity=?',
                      ('build_phase_policy','monthly-physical')).fetchone()
        before=json.loads(row[1]) if row else {'total_limit':6000,'limits':{'SCAN':2000,'INVESTIGATION':3905,'RESTORATION':95},'source':'preexisting build-phase source policy; no separate monthly cloud document'}
        if row and before.get('total_limit') not in (6000,9000):raise ValueError('UNEXPECTED_REQUEST_POLICY')
        if 'restoration_reset' in before:policy['restoration_reset']=before['restoration_reset']
        retained,alloc=shared_physical_rows(state,db,now)
        usage_before=sha({'rows':retained,'allocations':alloc})
        if row:
            state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                      (row[0]+1,encoded(policy),sha(policy),'build_phase_policy','monthly-physical'))
        else:
            state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',
                      ('build_phase_policy','monthly-physical',0,encoded(policy),sha(policy)))
        after=json.loads(state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',
                                  ('build_phase_policy','monthly-physical')).fetchone()[0])
        retained_after,alloc_after=shared_physical_rows(state,db,now)
        if usage_before!=sha({'rows':retained_after,'allocations':alloc_after}):raise ValueError('REQUEST_COUNTERS_CHANGED')
        receipt={'approval':policy['approval'],'before':before,'after':after,'usage_sha256_unchanged':usage_before,
                 'usage':physical_status(retained_after,alloc_after,now)}
        identity='round23-monthly-physical-9000'
        if not state.sql(db,'SELECT 1 FROM state_documents WHERE namespace=? AND identity=?',('owner_budget_decisions',identity)).fetchone():
            state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('owner_budget_decisions',identity,0,encoded(receipt),sha(receipt)))
    return receipt


def reset_round23_restoration(state, now):
    """Explicit owner allocation; all70 original cleanup requests remain charged."""
    from investigator.build_phase import POLICY,shared_physical_rows,physical_status
    from investigator.shared_state import encoded,sha
    import copy,json
    with state.transaction() as db:
        row=state.sql(db,'SELECT revision,body FROM state_documents WHERE namespace=? AND identity=?',
                      ('build_phase_policy','monthly-physical')).fetchone()
        if row is None:raise ValueError('MONTHLY_POLICY_MISSING')
        before=json.loads(row[1]);after=copy.deepcopy(before)
        after['restoration_reset']=POLICY['restoration_reset']
        retained,alloc=shared_physical_rows(state,db,now)
        unchanged=sha({'rows':retained,'allocations':alloc})
        status=physical_status(retained,alloc,now)
        if status['historical_restoration_requests']!=70:raise ValueError('OWNER_RESET_BASELINE_DIFFERS')
        identity='round23-october-restoration-reset'
        prior=state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',
                        ('owner_budget_decisions',identity)).fetchone()
        if prior:
            if before!=after:raise ValueError('RESET_ALREADY_APPLIED_WITH_DIFFERENT_POLICY')
            return json.loads(prior[0])
        state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                  (row[0]+1,encoded(after),sha(after),'build_phase_policy','monthly-physical'))
        observed=json.loads(state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',
                            ('build_phase_policy','monthly-physical')).fetchone()[0])
        rows_after,alloc_after=shared_physical_rows(state,db,now)
        if observed!=after or unchanged!=sha({'rows':rows_after,'allocations':alloc_after}):raise ValueError('RESET_ACCOUNTING_CHANGED')
        receipt={'approval':'owner-approved 2026-10-26','before':before,'after':observed,
                 'request_rows_and_allocations_sha256_unchanged':unchanged,'status':status,
                 'interpretation':'70 stays in gross October physical total; restoration allowance is fresh95, protected within unchanged9000 total'}
        state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',
                  ('owner_budget_decisions',identity,0,encoded(receipt),sha(receipt)))
    return receipt

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',required=True)
    parser.add_argument('--database',required=True)
    parser.add_argument('--owner',required=True)
    parser.add_argument('--round23',action='store_true',help='Approved USD40 to USD150 policy change; plan unless --apply')
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.round23 and not args.apply:
        print(json.dumps({'mode':'PLAN','approval':'owner-approved 2026-10-26',
            'change':'Current investigator month ceiling 40000000 -> 150000000 microdollars only',
            'preserved':['opening','charged','reservations','violation latch','enrichment','physical pot','reserve']}))
        return
    if args.round23:
        from investigator.round23_calendar import require_live_window
        require_live_window()
    import certifi
    from investigator.postgres_connection import connect as postgres_connect
    from investigator.shared_state import SharedState
    from investigator.build_phase import ensure_model_account
    token=subprocess.run(['az','account','get-access-token','--resource',
        'https://ossrdbms-aad.database.windows.net','--query','accessToken','-o','tsv',
        '--only-show-errors'],capture_output=True,text=True,check=True).stdout.strip()
    def connect():
        return postgres_connect(host=args.host,dbname=args.database,user=args.owner,password=token,
            sslmode='verify-full',sslrootcert=certifi.where(),connect_timeout=20,
            options='-c search_path=dia_state,pg_catalog -c statement_timeout=30000 -c lock_timeout=5000')
    state=SharedState(connect,backend='postgresql',mode='live')
    if args.round23:
        receipt=round23_policy(state,time.time())
        print(json.dumps({'approval':receipt['approval'],'account':receipt['account'],
                          'before':{k:receipt['before'][k] for k in ('ceiling','charged','opening','violated')},
                          'after':{k:receipt['after'][k] for k in ('ceiling','charged','opening','violated')}}))
        return
    account=ensure_model_account(state,time.time(),provision=True)
    snapshot=state.snapshot(account)
    print(json.dumps({k:snapshot[k]for k in ('identity','unit','ceiling','protected','opening','charged')}))


if __name__=='__main__':main()
