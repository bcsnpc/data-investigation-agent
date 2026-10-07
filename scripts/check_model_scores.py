"""Replay recorded model decisions into local scorers; never call a provider."""
import argparse,json
from pathlib import Path
from investigator.model_step_scores import score_intake,score_reader,compare
from investigator.synthesis_scores import score as score_synthesis,score_human,review_item
from investigator.translation_eval import score as score_translation,verify
from investigator.onboarding import digest
from investigator.generation_policy import error_summary
from jsonschema.exceptions import ValidationError


def translation_records(golden, records):
    """Rejected proposals are scored failures, never scorer crashes or omissions."""
    cases={c['id']:c for c in golden['cases']};result=[]
    for row in records:
        current=dict(row)
        if row.get('proposal') is not None:
            try:current['evaluation']=verify(cases[row['case_id']],row['proposal'])
            except (ValueError, ValidationError) as exc:
                current['evaluation']=None
                current['offline_validation_error']=error_summary(exc)
        result.append(current)
    return result


def evaluate(root,config):
    def read(path):return json.loads((root/path).read_text(encoding='utf8'))
    thresholds=read(config['thresholds']);results=[]
    for entry in config['steps']:
        step=entry['step'];records=read(entry['records']);version=entry['model_version']
        if step=='synthesis':
            rows=records['records'];scored_rows=rows
            if entry.get('revisions'):
                from investigator.mechanism_revision import effective_records
                scored_rows=effective_records(rows,read(entry['revisions']))
            current=score_synthesis(scored_rows,version)
            if scored_rows is not rows:
                current['basis']='RECORDED_RESPONSES_WITH_AUTHORISED_MECHANISM_ONLY_SUPERSESSIONS'
                current['original_response_score']=score_synthesis(rows,version)['score']
                current['supersession_reason']=read(entry['revisions'])['reason']
            current.update(evaluated=len(rows),status='COMPLETE' if len(rows)==15 and len({r['case_id'] for r in rows})==15 else 'INCOMPLETE',
                suite_hash=digest([{'case_id':r['case_id'],'requests':[{'payload':a['payload'],'schema':a['schema']} for a in r['attempts']]} for r in rows]))
        else:
            golden=read(entry['golden'])
            if step=='translation':
                # Re-execute the saved first proposals against independent local
                # fixture statements. A forged cached VERIFIED marker cannot
                # improve the CI score. No model request or estate transport.
                records=translation_records(golden,records)
            current={'intake':score_intake,'reader':score_reader,'translation':score_translation}[step](golden,records,version)
        results.append(compare(current,read(entry['baseline']),thresholds[step]))
    human=None;human_error=None
    try:
        items=read(config['human_reviews'])['items']
        originals={r['case_id']:r for r in rows}
        for item in items:
            original=originals.get(item['case_id'])
            if original is None:raise ValueError('Human review case absent from sealed synthesis set')
            expected=review_item(original)
            if any(item.get(k)!=v for k,v in expected.items() if k not in ('human_flags','grader')):
                raise ValueError('Human review paragraph or provenance differs from sealed response')
        human=score_human(items)
    except ValueError as exc:human_error=str(exc)
    return {'basis':'RECORDED_MODEL_STEP_REGRESSION; not adjudicated accuracy or estate acceptance',
            'steps':results,'human_readability':human,'human_review_error':human_error,
            'provider_calls':0,'estate_physical_requests':0,
            'gate':'PASSED' if all(r['gate']=='PASSED' for r in results) and human is not None else 'FAILED'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=Path('acceptance/model_steps/config.json'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=evaluate(Path.cwd(),json.loads(a.config.read_text(encoding='utf8')))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'gate':result['gate'],'human_review_error':result['human_review_error'],
        'steps':[{'step':s['step'],'score':s['score'],'delta':s['delta'],'gate':s['gate']} for s in result['steps']]}))
    return 0 if result['gate']=='PASSED' else 1


if __name__=='__main__':raise SystemExit(main())
