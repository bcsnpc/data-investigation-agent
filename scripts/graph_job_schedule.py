"""Prepare, optionally apply, the owner-approved independent graph job."""
import argparse
import json
from pathlib import Path
from investigator.adapters.runner_graph_schedule import plan,apply
from investigator.unified_runner import load


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--existing-job',type=Path,required=True)
    parser.add_argument('--runner-estate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    prepared=plan(json.loads(args.existing_job.read_bytes()),load(args.runner_estate))
    result=apply(prepared) if args.apply else prepared
    with args.output.open('x',encoding='utf8')as stream:json.dump(result,stream,indent=2)
    print(json.dumps({'status':result['status'],'resource_id':result['resource_id'],'cost':result['cost']}))


if __name__=='__main__':main()
