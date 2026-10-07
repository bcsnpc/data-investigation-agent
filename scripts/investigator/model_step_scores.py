"""Score recorded model-step decisions, never fabricate responses or grades."""
import copy
import hashlib
import json
from collections import Counter


def intake_record(saved):
    proposal=saved.get('proposal') or {}
    figure=proposal.get('reported_figure') or {'state':'UNSPECIFIED'}
    selected=proposal.get('target_request') or proposal.get('selection_request') or {}
    value_source=selected.get('value_source') or selected.get('source') or {}
    return {'action':'PROPOSE' if saved.get('status')=='PROPOSED' else 'ASK' if saved.get('status')=='NEEDS_INPUT' else None,
            'model_id':proposal.get('model_id'),'measure_id':proposal.get('measure_id'),
            'ticket_shape':proposal.get('ticket_shape'),'comparison_mode':proposal.get('comparison_mode'),
            'question_kind':(proposal.get('question_kind') or {}).get('kind'),
            'dimension_ids':proposal.get('dimension_ids',[]),'filters':proposal.get('filters',[]),
            'figure_state':figure['state'],'figure_value':figure.get('value'),
            'figure_precision':figure.get('precision'),'selection_value':value_source.get('quote')}


def score_intake(golden,records,model_version):
    if not isinstance(model_version,str) or not model_version.strip():raise ValueError('Explicit model version required')
    cases={c['id']:c for c in golden['cases']}
    if len(cases)!=len(golden['cases']):raise ValueError('Duplicate golden case')
    indexed={}
    for row in records:
        if row['case_id'] not in cases or row['case_id'] in indexed:raise ValueError('Unknown or duplicate evaluated case')
        if row['model_version']!=model_version:raise ValueError('Mixed model versions cannot share a score')
        indexed[row['case_id']]=row
    correct=Counter();totals=Counter();answered=holds=retries=correct_holds=expected_holds=0
    rows=[]
    for identity,case in cases.items():
        row=indexed.get(identity);expected=case['expected'];actual=None
        if case['should_hold']:expected_holds+=1
        if row is not None:
            saved=row['intake'];answered+=1
            if saved.get('status') in ('PROPOSED','NEEDS_INPUT'):actual=intake_record(saved)
            holds+=saved.get('status')!='PROPOSED'
            attempts=saved.get('resolution_attempts',[])
            if not isinstance(attempts,list):raise ValueError('Recorded resolution attempts must be a list')
            retries+=len(attempts)>1
            # A provider/transport/budget HELD is not a correct semantic hold.
            if case['should_hold'] and saved.get('status')=='NEEDS_INPUT':correct_holds+=1
        matched={}
        for field,value in expected.items():
            totals[field]+=1;matched[field]=actual is not None and actual.get(field)==value
            correct[field]+=matched[field]
        rows.append({'case_id':identity,'evaluated':row is not None,'fields':matched})
    return {'step':'intake','model_version':model_version,
            'suite_hash':hashlib.sha256(json.dumps(golden,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
            'cases':len(cases),'evaluated':answered,
            'status':'COMPLETE' if answered==len(cases) else 'INCOMPLETE',
            'per_field_accuracy':{k:correct[k]/v for k,v in totals.items()},
            'score':sum(correct.values())/sum(totals.values()),
            'retry_rate':retries/answered if answered else None,
            'hold_rate':holds/answered if answered else None,
            'expected_holds':expected_holds,'correct_holds':correct_holds,
            'correct_hold_rate':correct_holds/expected_holds if expected_holds else None,
            'results':rows}


def compare(score,previous,threshold):
    if not isinstance(threshold.get('reason'),str) or not threshold['reason'].strip():raise ValueError('Threshold reason required')
    limit=threshold['maximum_drop']
    if type(limit) not in (int,float) or not 0<=limit<=1:raise ValueError('Invalid score-drop threshold')
    result=copy.deepcopy(score);result['delta']=None
    if previous is not None:
        if (previous['step']!=score['step'] or previous['cases']!=score['cases']
                or not score.get('suite_hash') or previous.get('suite_hash')!=score['suite_hash']):raise ValueError('Comparison suite differs')
        if previous['status']!='COMPLETE':raise ValueError('Incomplete baseline is not a quality baseline')
        result['delta']=score['score']-previous['score']
    result['gate']='FAILED' if score['status']!='COMPLETE' or score.get('provider_failures',0) or result['delta'] is not None and result['delta'] < -limit else 'PASSED'
    result['threshold']=copy.deepcopy(threshold)
    return result


def score_reader(golden,records,model_version):
    """Binding precision/recall before reader verification; no value oracle."""
    from .lineage_binding import validate
    cases={c['id']:c for c in golden['cases']};indexed={}
    if len(cases)!=len(golden['cases']):raise ValueError('Duplicate golden case')
    for row in records:
        if row['case_id'] not in cases or row['case_id'] in indexed:raise ValueError('Unknown or duplicate evaluated case')
        if row['model_version']!=model_version:raise ValueError('Mixed model versions cannot share a score')
        indexed[row['case_id']]=row
    def signature(p):
        return json.dumps({k:p[k] for k in ('sources','target','expression')},sort_keys=True,separators=(',',':'))
    tp=fp=expected_count=correct_refusals=provider_failures=validation_failures=0;rows=[]
    for identity,case in cases.items():
        expected=Counter(signature(p) for p in case['expected_bindings']);expected_count+=sum(expected.values())
        row=indexed.get(identity);actual=Counter();invalid=0
        if row is not None:
            provider_failures+=bool(row.get('provider_error'))
            validation_failures+=bool(row.get('validation_error'))
            if not isinstance(row['proposals'],list):raise ValueError('Reader proposals must be a list')
            for proposal in row['proposals']:
                try:
                    p=validate(proposal)
                    if p['extractor']!='MODEL':raise ValueError('MODEL provenance required')
                    actual[signature(p)]+=1
                except ValueError:invalid+=1
            if case['should_refuse'] and not row['proposals'] and row.get('semantic_refusal') is True:correct_refusals+=1
        matches=sum((actual & expected).values());extra=sum(actual.values())-matches+invalid
        tp+=matches;fp+=extra
        rows.append({'case_id':identity,'evaluated':row is not None,'true_positive':matches,'false_positive':extra,
                     'false_negative':sum(expected.values())-matches})
    precision=tp/(tp+fp) if tp+fp else 0;recall=tp/expected_count if expected_count else 0
    return {'step':'reader','model_version':model_version,'cases':len(cases),'evaluated':len(indexed),
            'suite_hash':hashlib.sha256(json.dumps(golden,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
            'status':'COMPLETE' if len(indexed)==len(cases) else 'INCOMPLETE',
            'precision':precision,'recall':recall,'score':2*precision*recall/(precision+recall) if precision+recall else 0,
            'correct_semantic_refusals':correct_refusals,'expected_refusals':sum(c['should_refuse'] for c in cases.values()),
            'provider_failures':provider_failures,'validation_failures':validation_failures,
            'results':rows,'verification_performed':False}
