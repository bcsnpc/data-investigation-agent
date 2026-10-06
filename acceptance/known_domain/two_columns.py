"""The same acceptance contracts on two immutable, independently recorded columns."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).parent))
from check import run_case,validate_case


def require_change_reason(before,after):
    if before.get('expected')==after.get('expected'):
        return
    if (not after.get('acceptance_change_reason','').strip()
            or before.get('acceptance_change_reason')==after.get('acceptance_change_reason')):
        raise ValueError('CHANGED_ACCEPTANCE_ANSWER_REQUIRES_NEW_REASON')


def run(archived,inferred,output,*,base_revision=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    paths=sorted((Path(__file__).parent/'cases').glob('*.json'))
    cases=[json.loads(p.read_text()) for p in paths]
    if len(cases)!=15 or len({c['ticket'] for c in cases})!=15:
        raise ValueError('Acceptance roster must conserve all fifteen tickets')
    for case,path in zip(cases,paths):
        validate_case(case)
        if base_revision:
            before=subprocess.check_output(['git','show',base_revision+':acceptance/known_domain/cases/'+path.name],text=True)
            require_change_reason(json.loads(before),case)
    columns={}
    for name,root in [('archived',Path(archived)),('inferred',Path(inferred))]:
        rows=[]
        for case in cases:
            result=run_case(case,root,output/name/case['ticket'])
            rows.append(result)
            print(json.dumps({'column':name,**result}),flush=True)
        columns[name]={'passed':sum(r['status']=='PASSED' for r in rows),'total':15,
                       'physical_requests':sum(r['physical_requests'] for r in rows),
                       'network_calls':sum(r['network_calls'] for r in rows),'results':rows}
    summary={'version':1,'basis':'Sealed producer replay with current output-contract grading; not unfamiliar-domain or global equivalence acceptance.',
             'columns':columns}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('TWO_COLUMN_GATE '+json.dumps({k:{x:v[x] for x in ('passed','total','physical_requests','network_calls')} for k,v in columns.items()}),flush=True)
    return 0 if all(c['passed']==15 and c['physical_requests']==0 and c['network_calls']==0 for c in columns.values()) else 1


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archived',type=Path,required=True)
    p.add_argument('--inferred',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--base-revision')
    args=p.parse_args();raise SystemExit(run(args.archived,args.inferred,args.output,base_revision=args.base_revision))
