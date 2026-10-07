"""Extract composition examples from immutable tapes; make no provider requests."""
import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/known_domain'))
from private_bundle import tape_path
from investigator.process_tape import Tape,validate_event
from investigator.synthesis_scores import review_item,score


def extract(path,case_id):
    tape=Tape(path);operation=request=None;attempts=[];models=set()
    for event in tape.events:
        kind=event['kind']
        if kind not in ('OPERATION_START','PROVIDER_REQUEST','PROVIDER_RESPONSE'):continue
        body=json.loads(validate_event(event,event['ordinal']))
        if kind=='OPERATION_START':operation=body['name'];request=None;continue
        if operation!='synthesize':continue
        if kind=='PROVIDER_REQUEST':request=body;continue
        if request is None:raise ValueError('Composition response has no recorded request')
        response=json.loads(base64.b64decode(body['body'],validate=True))
        models.add(request['model'])
        calls=[c for c in response.get('output',[]) if c.get('type')=='function_call']
        if len(calls)!=1:raise ValueError('Composition response has no single structured call')
        args=json.loads(calls[0]['arguments'])
        tools=[t for t in request['tools'] if t['name']==calls[0]['name']]
        if len(tools)!=1:raise ValueError('Composition schema is ambiguous')
        payload=json.loads(request['input'])
        attempts.append({'payload':payload,'schema':tools[0]['parameters'],'response':args,
                         'provider_event_sha256':event['sha256']})
    if len(models)>1:raise ValueError('One case contains multiple model versions')
    return {'case_id':case_id,'model_version':next(iter(models),'NO_MODEL_CALL'),
            'tape_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'attempts':attempts}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixtures',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--review',type=Path,required=True)
    args=p.parse_args()
    for path in (args.output,args.review):
        if path.exists():raise ValueError('Evaluation exports are immutable; choose a new path')
    inputs=sorted((args.fixtures/'known-domain-runs').glob('*.json'))
    if len(inputs)!=15:raise ValueError('Exactly fifteen earned case inputs required')
    records=[]
    for path in inputs:
        run=json.loads(path.read_text(encoding='utf8'))
        record=extract(tape_path(run,args.fixtures),path.stem);records.append(record)
        print(path.stem,len(record['attempts']),'recorded composition attempts',flush=True)
    scores=[score(records,v) for v in sorted({r['model_version'] for r in records})]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'records':records,'scores':scores},indent=2),encoding='utf8')
    candidates=[review_item(r) for r in records if r['attempts']]
    if len(candidates)<10:raise ValueError('Fewer than ten model mechanisms; export retained, human review cannot be populated')
    review={'basis':'SEALED_PROVIDER_RESPONSES','grading_status':'NOT_GRADED','items':candidates[:10]}
    from investigator.planner_recording import _safe
    _safe(json.dumps(review).encode())
    args.review.parent.mkdir(parents=True,exist_ok=True)
    args.review.write_text(json.dumps(review,indent=2),encoding='utf8')
    print(json.dumps({'scores':scores,'human_review_items':10}))


if __name__=='__main__':main()
