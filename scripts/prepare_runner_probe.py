"""Prepare public runner configuration from retained evidence; no live calls."""
import argparse,json
from pathlib import Path
from investigator.runner_prepare import probe_plan

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('job','gateway','probe','slim','output'):p.add_argument('--'+key,type=Path,required=True)
    for key in ('image','run-id','cli-python','budget-environment'):p.add_argument('--'+key,required=True)
    p.add_argument('--platform-cost-observation',type=Path)
    a=p.parse_args()
    values=[json.loads(getattr(a,k).read_bytes()) for k in ('job','gateway','probe','slim')]
    cost=json.loads(a.platform_cost_observation.read_bytes()) if a.platform_cost_observation else None
    plan=probe_plan(*values,image=a.image,run_id=a.run_id,cli=[a.cli_python,'-m','azure.cli'],budget_environment=a.budget_environment,platform_cost_observation=cost)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('xb') as stream:stream.write(json.dumps(plan,sort_keys=True,indent=2).encode())
    print(json.dumps({'status':'PREPARED_NO_LAUNCH','path':str(a.output),'run_id':a.run_id,'image':a.image}))

if __name__=='__main__':main()
