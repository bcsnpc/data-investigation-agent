"""Offline scoring and conservative simulated answers for sealed ticket records.

This module is an evaluator, never a runtime candidate producer. It cannot
read an estate or call a provider. An unanswered choice stays unanswered.
"""
import re
from collections import Counter
from .onboarding import digest
from . import reported_figure


def answer_batch(ticket, case, models):
    """Only information in the original sealed record can answer an offer."""
    expected=case['expected']; answers=[]; abstentions=[]
    for question in ticket['questions']:
        eligible=[]
        for choice in question['choices']:
            value=ticket['choice_values'][digest(question)+'/'+choice['id']]
            good=False
            if not case['should_hold'] and question['field']=='NUMBER':
                good=(expected.get('target_id') is not None and
                      expected['target_id']==value['target_id'] and
                      expected.get('cell_mode')==value['mode'])
                source=value['figure_source']
                if expected.get('figure_state')=='UNSPECIFIED':good=good and source is None
                elif source:
                    try:figure=reported_figure.from_candidates([source],case['text'])
                    except ValueError:good=False
                    else:good=good and all(figure.get(k)==expected.get('figure_'+k)
                                          for k in ('state','value','precision'))
                else:good=False
            elif not case['should_hold'] and question['field']=='REPORT_PAGE':
                visuals=[v for m in models for v in m.get('visuals',[])
                         if v['target_id']==expected.get('target_id')]
                # A named target may settle its container, not supply a page
                # the original request never named.
                good=bool(visuals and len({v['report_id'] for v in visuals})==1 and
                          visuals[0]['report_id']==value['report_id'] and value['page_id'] is None)
            elif question['field']=='COMPARISON':
                text=case['text']; kind=expected.get('nominated_question_kind') or expected.get('question_kind')
                route=None
                if re.search(r'\b(?:another|other|second) report\b',text,re.I):route='OTHER_REPORT'
                elif kind=='SOURCE_CORRECTNESS' and re.search(
                        r'\b(application|source (?:entries|movements|records|system|data))\b',text,re.I):route='APPLICATION'
                elif kind=='FRESHNESS' and re.search(
                        r'\b(stale|freshness|refresh|lag|how old|up[ -]to[ -]date|currency)\b',text,re.I):route='STALE'
                elif kind=='FIGURE_DIFFERENCE' and re.search(
                        r'\b(wrong|high|discrepancy|differs|higher|difference)\b',text,re.I):route='LOOKS_WRONG'
                good=route is not None and route==value['route']
            if good:eligible.append(choice)
        if len(eligible)==1:
            answers.append({'question_id':question['id'],'choice_id':eligible[0]['id']})
        else:
            abstentions.append({'field':question['field'],'matches':len(eligible),
                                'reason':'ORIGINAL_RECORD_DOES_NOT_SETTLE_ONE_CHOICE'})
    return {'answers':answers,'abstentions':abstentions,'case_hash':digest(case)}


def score(cases, records):
    """Keep original-record agreement distinct from interactive settlement.

    A correct, terminal semantic refusal can settle a ticket. A waiting
    clarification, transport failure or budget refusal cannot. Structured
    differences remain visible even where the user legitimately confirmed a
    choice under the new lifecycle.
    """
    indexed={r['id']:r for r in records}
    if len(indexed)!=len(records):raise ValueError('Duplicate evaluated ticket')
    case_ids={c['id'] for c in cases}
    if len(case_ids)!=len(cases) or set(indexed)-case_ids:raise ValueError('Unknown or duplicate sealed ticket')
    rows=[]; classes={}
    for case in cases:
        row=indexed.get(case['id']); expected=case['expected']; differences=[]
        if not isinstance(expected,dict) or not expected:raise ValueError('Sealed expected record is empty')
        if row and row['case_hash']!=digest(case):raise ValueError('Evaluated ticket differs from its seal')
        actual=row['intake_record'] if row else None
        differences=[k for k,v in expected.items() if actual is None or actual.get(k)!=v]
        history=row.get('ticket_history') if row else None
        waiting_on_user=bool(history and any(
            e.get('to')=='HELD' and e.get('detail',{}).get('reason')=='USER_INFORMATION_UNAVAILABLE'
            for e in history[-1:]))
        # A source refusal is not proof of a terminal ticket disposition.
        # Require the retained lifecycle evidence; a user who cannot answer
        # an offer has paused the ticket, not settled its consequential fields.
        appropriate_refusal=bool(row and history and not waiting_on_user and case['should_hold'] and actual and
            actual.get('error')==expected.get('error') and actual.get('status')==expected.get('status') and
            row['ticket_state'] in ('HELD','BUSINESS_VALIDATION'))
        adopted=bool(row and row.get('adopted'))
        if adopted and (actual is None or actual.get('status')!='PROPOSED'):
            raise ValueError('Adoption requires a proposed consumer record')
        settled=adopted or appropriate_refusal
        rounds=row['rounds'] if row else None
        questions=row['questions'] if row else 0
        if row and (type(rounds) is not int or rounds<0 or type(questions) is not int or questions<0):
            raise ValueError('Clarification counts must be nonnegative integers')
        flags=[]
        if adopted:
            for field in ('target_id','cell_mode','figure_state','figure_value','figure_precision','filters','dimension_ids'):
                if field in expected and actual.get(field)!=expected[field]:flags.append(field)
            # The evaluator never resolves a review flag by inventing a user
            # confirmation. Retain the actual proof for independent checking.
        result={'id':case['id'],'evaluated':row is not None,'original_record_match':not differences,
                'differences':differences,'settled':settled,'settled_within_one_round':bool(settled and rounds<=1),
                'questions':questions,'consequential_differences':flags,
                'waiting_on_user':waiting_on_user,
                'refusal_lifecycle_evidence':bool(history) if case['should_hold'] else None}
        rows.append(result)
        group=classes.setdefault(case['class'],Counter())
        group['tickets']+=1;group['evaluated']+=row is not None
        group['settled_within_one_round']+=result['settled_within_one_round'];group['questions']+=questions
        group['original_record_matches']+=not differences;group['consequential_differences']+=bool(flags)
    for group in classes.values():
        group['mean_questions']=group['questions']/group['tickets']
        group['one_round_rate']=group['settled_within_one_round']/group['tickets']
    return {'tickets':len(cases),'evaluated':len(records),'per_class':dict(classes),'rows':rows,
            'status':'COMPLETE' if len(records)==len(cases) else 'INCOMPLETE',
            'harmful_error_grade':'REQUIRES_PROVENANCE_REVIEW',
            'gate':'UNGRADABLE' if any(r['consequential_differences'] for r in rows) else 'PENDING_LIFECYCLE_AND_PROVENANCE_GATES'}
