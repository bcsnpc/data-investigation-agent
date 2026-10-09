"""Sealed, human-approved conversational evaluator. Never runtime scope input.

The simulator can select an offered answer only from approved truth. Scoring
does not turn an adoption into correctness or a budget/transport stop into a
semantic refusal. Original one-shot scoring remains a separate historical test.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path
from .onboarding import digest
from . import reported_figure


def load(directory):
    directory=Path(directory)
    seal=json.loads((directory/'oracle-seal.json').read_text(encoding='utf-8'))
    if seal['version']!='conversational-oracle-seal-v1' or not all(seal.get(k) for k in ('owner','reviewer','approved_at')):
        raise ValueError('Oracle requires dated owner and reviewer approval')
    if seal['artifact']!='oracle-draft.json':raise ValueError('Unknown oracle artifact')
    data=(directory/seal['artifact']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=seal['sha256']:raise ValueError('Oracle seal mismatch')
    oracle=json.loads(data)
    split=directory.parent/'model_steps/intake-round-ten-f-split.json'
    raw=split.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=seal['source_split_sha256'] or oracle['source_split_sha256']!=seal['source_split_sha256']:
        raise ValueError('Oracle split seal mismatch')
    expected={r['id']:(part,r['record_hash']) for part in ('dev','held_out') for r in json.loads(raw)[part]}
    actual={r['id']:(r['partition'],r['golden_record_hash']) for r in oracle['records']}
    if len(actual)!=len(oracle['records']) or actual!=expected:raise ValueError('Oracle records do not conserve sealed split')
    return oracle,seal


def figure_matches(truth, actual):
    if truth['state'] in ('NOT_STATED','NOT_APPLICABLE'):
        return actual=={'state':'UNSPECIFIED'}
    if truth['state']!='DETERMINED':return False
    value=truth['value']
    return value.get('state')!='AMBIGUOUS' and all(actual.get(k)==value.get(k) for k in ('state','value','precision'))


def scope(value):
    return sorted(value,key=lambda f:json.dumps(f,sort_keys=True,separators=(',',':')))


def target_differences(oracle, proposal, models=()):
    truth=oracle['true_target_and_cell'];bad=[]
    if truth['state']=='UNDETERMINED':return ['undetermined_target_adopted']
    actual=proposal.get('target_visual') or {}
    if truth['state']=='NOT_APPLICABLE':
        return ['unexpected_visual'] if actual else []
    value=truth['value']
    if value.get('kind')=='MEASURE_AT_SCOPE':
        if proposal.get('measure_id')!=value['measure_id']:bad.append('measure_id')
        if value.get('model_id') and proposal.get('model_id')!=value['model_id']:bad.append('model_id')
        if scope(proposal.get('filters',[]))!=scope(value['scope']) or proposal.get('dimension_ids',[]):bad.append('scope')
        # No chosen visual can masquerade as scope equivalence without the
        # independently reviewed complete-definition proof for that candidate.
        if actual:
            proof=oracle.get('scope_equivalence_review',{})
            scopes=proof.get('candidate_scopes',[])
            if proof.get('status')!='VERIFIED_EQUIVALENT_DECLARED_SCOPE' or actual.get('target_id') not in {s['target_id'] for s in scopes}:
                bad.append('unproved_equivalent_visual')
            if actual.get('mode') not in ('UNGROUPED','TOTAL'):bad.append('cell_mode')
        return bad
    if actual.get('target_id')!=value['target_id']:bad.append('target_id')
    if actual.get('mode')!=value['mode']:bad.append('cell_mode')
    if scope(proposal.get('filters',[]))!=scope(value.get('selected_filters',[])):bad.append('filters')
    if proposal.get('dimension_ids',[])!=value.get('dimension_ids',[]):bad.append('dimension_ids')
    if value.get('cell_keys'):
        keys={f['column_id']:f['values'][0] for f in proposal.get('filters',[])
              if f['operator']=='in' and len(f['values'])==1}
        if any(keys.get(k['column_id'])!=k['value'] for k in value['cell_keys']):bad.append('cell_keys')
    return bad


def answer_batch(ticket, oracle, models):
    answers=[];abstentions=[]
    legitimate={q['field']:q for q in oracle['legitimate_questions']}
    for question in ticket['questions']:
        field=question['field'];matches=[]
        # Illegitimate offers are not answered to manufacture a settlement.
        if field in legitimate:
            for choice in question['choices']:
                value=ticket['choice_values'][digest(question)+'/'+choice['id']]
                good=False
                if field=='NUMBER':
                    visual=next(((m,v) for m in models for v in m.get('visuals',[]) if v['target_id']==value['target_id']),None)
                    if visual:
                        m,v=visual
                        expected=oracle['true_target_and_cell'].get('value',{})
                        good=(expected.get('target_id')==value['target_id'] and expected.get('mode')==value['mode'])
                        source=value['figure_source']
                        try:figure=reported_figure.from_candidates([source],oracle['ticket']) if source else {'state':'UNSPECIFIED'}
                        except ValueError:good=False
                        else:good=good and figure_matches(oracle['true_reported_figure'],figure)
                elif field=='FIGURE':
                    try:figure=reported_figure.from_candidates([value['figure_source']],oracle['ticket'])
                    except ValueError:good=False
                    else:good=figure_matches(oracle['true_reported_figure'],figure)
                elif field in ('REPORT_PAGE','REPORT_OR_SCREENSHOT'):
                    truth=oracle['true_report_and_page']
                    good=truth['state']=='DETERMINED' and all(value.get(k)==truth['value'].get(k) for k in ('report_id','page_id'))
                elif field=='COMPARISON':
                    truth=oracle['true_comparison_route']
                    good=truth['state']=='DETERMINED' and value['route']==truth['value']
                if good:matches.append(choice)
        if len(matches)==1:answers.append({'question_id':question['id'],'choice_id':matches[0]['id']})
        else:abstentions.append({'field':field,'matches':len(matches),'reason':'APPROVED_ORACLE_DOES_NOT_AUTHORIZE_ONE_OFFERED_CHOICE'})
    return {'answers':answers,'abstentions':abstentions,'oracle_record_hash':digest(oracle)}


def score(records, rows, *, catalogs=None):
    indexed={r['id']:r for r in rows}
    if len(indexed)!=len(rows) or set(indexed)-{o['id'] for o in records}:raise ValueError('Duplicate or unknown evaluated record')
    results=[];classes={}
    for oracle in records:
        row=indexed.get(oracle['id']);bad=[];illegitimate=[];settled=False
        history=row.get('ticket_history',[]) if row else []
        offered=[q for e in history for q in e.get('detail',{}).get('questions',[])]
        forbidden={q['field'] for q in oracle['illegitimate_questions']}
        legitimate={q['field'] for q in oracle['legitimate_questions']}
        illegitimate=[q['field'] for q in offered if q['field'] in forbidden or q['field'] not in legitimate]
        disposition=oracle['required_disposition']['value']
        if row and row.get('adopted'):
            proposal=row.get('proposal') or {}
            bad=target_differences(oracle,proposal,(catalogs or {}).get(oracle['id'],[]))
            if not figure_matches(oracle['true_reported_figure'],proposal.get('reported_figure',{})):bad.append('reported_figure')
            truth=oracle['true_comparison_route']
            route=((row.get('ticket') or {}).get('settled',{}).get('COMPARISON',{}).get('value') or {}).get('route')
            expected_route=truth.get('value') if truth['state']=='DETERMINED' else 'DECLARED_SUBJECT' if truth['state']=='NOT_APPLICABLE' else None
            if route!=expected_route:bad.append('comparison_route')
            if disposition.startswith('HOLD_') or disposition in ('BUSINESS_VALIDATION','UNSUPPORTED_ROUTE'):bad.append('forbidden_admission')
            settled=not bad
        elif row and not row.get('failure') and row.get('ticket_state') in ('HELD','BUSINESS_VALIDATION') and history:
            detail=history[-1].get('detail',{});reason=json.dumps(detail,sort_keys=True).upper()
            # The actual refusal must name the approved reason. No credit for
            # transport/budget/provider stops, nor unrelated ambiguous targets.
            if disposition=='BUSINESS_VALIDATION':settled=detail.get('route')=='BUSINESS_VALIDATION' or row['ticket_state']=='BUSINESS_VALIDATION'
            elif disposition=='UNSUPPORTED_ROUTE':settled='UNIMPLEMENTED_ROUTE' in reason or 'CHANGE_OVER_TIME' in reason
            elif disposition=='HOLD_TWO_REPORTED_FIGURES':settled='FIGURE' in reason and ('AMBIGU' in reason or 'MULTIPLE' in reason)
            elif disposition=='HOLD_UNIDENTIFIED_REFERENT':settled='TARGET_UNRESOLVED' in reason or 'USER_INFORMATION_UNAVAILABLE' in reason
            elif disposition in ('HOLD_UNSUPPORTED_FILTER','HOLD_NONEXISTENT_COLUMN','HOLD_UNLESS_RELATIVE_DATE_TRANSLATION_VERIFIED'):
                settled=any(s in reason for s in ('UNSUPPORTED_FILTER','UNSUPPORTED_SELECTION','COLUMN_UNRESOLVED','COLUMN_NOT_FOUND','RELATIVE_DATE'))
        count=row['questions'] if row else 0;rounds=row['rounds'] if row else 0
        result={'id':oracle['id'],'evaluated':row is not None,'settled_within_one_round':bool(settled and rounds<=1),
                'questions':count,'illegitimate_questions':illegitimate,'harmful_admission_fields':bad,
                'required_disposition':disposition,'state':row.get('ticket_state') if row else None}
        results.append(result);group=classes.setdefault(oracle['class'],Counter())
        group['tickets']+=1;group['evaluated']+=row is not None;group['settled_within_one_round']+=result['settled_within_one_round']
        group['questions']+=count;group['illegitimate_questions']+=len(illegitimate);group['harmful_admissions']+=bool(bad)
    n=len(records);settlements=sum(r['settled_within_one_round'] for r in results);questions=sum(r['questions'] for r in results)
    harm=sum(bool(r['harmful_admission_fields']) for r in results);unfair=sum(len(r['illegitimate_questions']) for r in results)
    return {'tickets':n,'evaluated':len(rows),'settled_within_one_round':settlements,'one_round_rate':settlements/n if n else 0,
            'questions':questions,'mean_questions':questions/n if n else 0,'harmful_admissions':harm,
            'illegitimate_questions':unfair,'per_class':dict(classes),'rows':results,
            'gate':'PASSED' if len(rows)==n and settlements/n>=.85 and questions/n<=1 and not harm and not unfair else 'FAILED',
            'lifecycle_gate':'SEPARATE_TEST_REQUIRED'}
