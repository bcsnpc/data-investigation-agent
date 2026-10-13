"""Apply shared-state schema or import an operator-reviewed exact ledger snapshot.

Input is local-only JSON. Amounts must be decimal strings or integers, never JSON
floats. Run --plan first; --apply imports exactly this hash once. This command
never edits the legacy ledger, changes a cap, or creates a cloud resource.
"""
import argparse
from decimal import Decimal
import json
from pathlib import Path
from investigator.shared_state import configured_state, sha, amount


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True)
    parser.add_argument('--migration-id',required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--report',required=True)
    args=parser.parse_args(argv)
    source=json.loads(Path(args.source).read_text(encoding='utf-8-sig'))
    digest=sha(source)
    if digest != args.expected_sha256:
        parser.error('Source hash differs from approved migration input')
    # Refuse decimal floats, rather than stringifying already rounded values.
    for account in source['accounts']:
        for field in ('ceiling','protected','opening'):
            amount(account[field])
    report={'mode':'APPLY' if args.apply else 'PLAN','source_sha256':digest,
            'accounts':source['accounts'],'legacy_files_unchanged':True}
    if args.apply:
        state=configured_state()
        if state is None:
            parser.error('PostgreSQL configuration is required for apply')
        state.migrate()
        report['verification']=state.import_accounts(args.migration_id,source)
    Path(args.report).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'mode':report['mode'],'source_sha256':digest,'report':args.report}))


if __name__=='__main__':
    main()
