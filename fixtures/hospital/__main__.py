"""One-command deterministic source rebuild into a NEW output directory.

Existing artifacts are never silently overwritten or deleted.
"""
import argparse
import json
from .generate import generate,Settings
from .verify import verify
from .marts import build_local


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    parser.add_argument('--seed',type=int,default=20261030)
    parser.add_argument('--patients',type=int,default=60000)
    parser.add_argument('--encounters',type=int,default=250000)
    parser.add_argument('--orders',type=int,default=1500000)
    args=parser.parse_args()
    generated=generate(args.output,Settings(args.seed,args.patients,args.encounters,args.orders))
    report=verify(args.output)
    if report['all_passed']:build_local(args.output)
    print(json.dumps({'output':args.output,'seed':args.seed,'checks_passed':report['all_passed'],'volumes':{s:{t:v['rows']for t,v in tables.items()}for s,tables in generated['tables'].items()}},indent=2))
    if not report['all_passed']:raise SystemExit(1)


if __name__=='__main__':main()
