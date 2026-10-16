"""Operator-only exact row migration. No estate or model transport is invoked."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--catalog',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    parser.add_argument('--migration-id',required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    from investigator.shared_application import source,migrate
    from investigator.shared_state import configured_state,sha
    from investigator.planner_recording import _safe
    saved=source(args.catalog,args.environment)
    _safe(json.dumps(saved,ensure_ascii=False).encode())
    report={'mode':'PLAN','source_sha256':sha(saved),'environment':args.environment,
            'tables':{name:len(table['rows'])for name,table in saved['tables'].items()}}
    if args.apply:
        state=configured_state()
        if state is None:raise ValueError('POSTGRES_MIGRATION_CONFIGURATION_REQUIRED')
        report={'mode':'APPLIED','proof':migrate(state,args.migration_id,saved)}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    with args.receipt.open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':main()
