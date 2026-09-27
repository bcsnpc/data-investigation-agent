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
    def __init__(self,path,environment):
        self.path=path;self.store=SimpleNamespace(environment=environment)

    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path);db.row_factory=sqlite3.Row
        try:
            with db:yield db
        finally:db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',required=True)
    parser.add_argument('--policy',required=True)
    parser.add_argument('--approval',help='JSON human approval; omit to inspect only')
    args=parser.parse_args()
    from pathlib import Path
    if not Path(args.database).is_file():parser.error('Existing catalog required')
    policy=json.loads(Path(args.policy).read_text(encoding='utf-8-sig'))
    governor=UsageGovernor(Catalog(args.database,policy['environment']),policy,time.time)
    if args.approval:
        governor.grant_batch(json.loads(Path(args.approval).read_text(encoding='utf-8-sig')))
    print(json.dumps(governor.snapshot(),indent=2))


if __name__=='__main__':main()
