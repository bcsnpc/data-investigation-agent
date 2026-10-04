"""Inspect allowance or record an explicitly approved, expiring read batch.

This operator CLI is not an investigation tool and never changes the policy.
An approval file records a human decision; it does not confer data permissions.
"""
import argparse
from contextlib import contextmanager
import json
import sqlite3
import time
from types import SimpleNamespace
from investigator.usage_governance import UsageGovernor


class Catalog:
    def __init__(self,path,environment,config=None):
        self.path=path;self.store=SimpleNamespace(environment=environment)
        # This catalog also supports isolated legacy ledger unit tests. The
        # installation CLI always supplies the validated manifest projection.
        self.config={} if config is None else config

    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path);db.row_factory=sqlite3.Row
        try:
            with db:yield db
        finally:db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--approval',help='JSON human approval; omit to inspect only')
    args=parser.parse_args()
    from pathlib import Path
    from investigator.estate_manifest import load,policy
    from investigator.adapters.estate_installation import configuration
    from metadata_config import ROOT
    manifest=load(args.manifest);config=configuration(manifest)
    database=ROOT/manifest['storage']['catalog']
    if not database.is_file():parser.error('Existing catalog required')
    governor=UsageGovernor(Catalog(database,manifest['environment'],config),policy(manifest),time.time)
    if args.approval:
        governor.grant_batch(json.loads(Path(args.approval).read_text(encoding='utf-8-sig')))
    print(json.dumps(governor.snapshot(),indent=2))


if __name__=='__main__':main()
