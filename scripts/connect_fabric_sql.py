"""Explicit user-run SQL audience sign-in; no tokens printed or exported."""
import argparse
from pathlib import Path

from metadata_config import ROOT, load_config
from metadata_auth import FabricCliTokens


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'infra/metadata/development.json')
    args = parser.parse_args()
    config = load_config(args.config)
    from fabric_cli.core.fab_auth import FabAuth
    # Explicit interactive sign-in only in this helper, never in background queries.
    FabAuth().get_access_token(['https://database.windows.net/.default'], interactive_renew=True)
    FabricCliTokens(config['fabric']['auth']['tenant_id']).get_token('https://database.windows.net/.default')
    print('Fabric SQL sign-in verified for the configured enterprise tenant. No token exported.')
