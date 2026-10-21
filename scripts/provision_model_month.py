"""Owner-only monthly policy setup; grants no privilege and prints no token."""
import argparse
import json
import subprocess
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',required=True)
    parser.add_argument('--database',required=True)
    parser.add_argument('--owner',required=True)
    args=parser.parse_args()
    import certifi
    import psycopg
    from investigator.shared_state import SharedState
    from investigator.build_phase import ensure_model_account
    token=subprocess.run(['az','account','get-access-token','--resource',
        'https://ossrdbms-aad.database.windows.net','--query','accessToken','-o','tsv',
        '--only-show-errors'],capture_output=True,text=True,check=True).stdout.strip()
    def connect():
        return psycopg.connect(host=args.host,dbname=args.database,user=args.owner,password=token,
            sslmode='verify-full',sslrootcert=certifi.where(),connect_timeout=20,
            options='-c search_path=dia_state,pg_catalog -c statement_timeout=30000 -c lock_timeout=5000')
    state=SharedState(connect,backend='postgresql',mode='live')
    account=ensure_model_account(state,time.time(),provision=True)
    snapshot=state.snapshot(account)
    print(json.dumps({k:snapshot[k]for k in ('identity','unit','ceiling','protected','opening','charged')}))


if __name__=='__main__':main()
