"""Explicit user-run SQL audience sign-in; no tokens printed or exported."""
import argparse
from pathlib import Path

from metadata_config import ROOT, load_config
from fabric_sql_auth import sign_in, ACCOUNT


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'infra/metadata/development.json')
    args = parser.parse_args()
    config = load_config(args.config)
    print('Opening browser sign-in. Choose '+ACCOUNT+'.', flush=True)
    try:
        sign_in(config['fabric']['auth']['tenant_id'])
    except Exception as exc:
        print('SQL sign-in did not complete ('+type(exc).__name__+'). Choose '+ACCOUNT+' and retry.')
        raise SystemExit(1)
    print('Fabric SQL sign-in verified for the configured enterprise tenant. No token exported.')
