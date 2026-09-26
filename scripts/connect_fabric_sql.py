"""Explicit user-run SQL audience sign-in; no tokens printed or exported.

The account and isolated profile come from configuration: `fabric.sql_session`
(the publisher session) or `fabric.sql_reader` (the least-privilege reader).
"""
import argparse
from pathlib import Path

from metadata_config import ROOT, load_config
from fabric_sql_auth import sign_in


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--session', choices=('sql_session', 'sql_reader'), default='sql_session')
    args = parser.parse_args()
    config = load_config(args.config)
    session = config['fabric'].get(args.session)
    if session is None:
        parser.error(f'fabric.{args.session} is not configured')
    account, profile = session['account'], session['profile']
    print(f'Opening browser sign-in for profile {profile}. Choose {account}.', flush=True)
    try:
        sign_in(config['fabric']['auth']['tenant_id'], account, profile)
    except Exception as exc:
        print(f'SQL sign-in did not complete ({type(exc).__name__}). Choose {account} and retry.')
        raise SystemExit(1)
    print('Fabric SQL sign-in verified for the configured account and tenant. No token exported.')
