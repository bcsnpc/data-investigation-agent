"""Engine-rendered relationship to the original question, never model prose.

Text markers identify explicit requests only; they do not certify full intent.
Unknown wording has no completion proof. Outcome labels alone never prove that a
question was answered. Historical source records are not rewritten.
"""
import copy,re
from .onboarding import digest,Conflict

SUBJECTS={
    'currency':r'\b(?:stale|staleness|freshness|refresh|currency|up.to.date)\b',
    'meaning':r'\b(?:mean|means|meaning|business intent|business rule|should)\b',
    'definitions':r'\b(?:definition|definitions|numerator|denominator|components)\b',
    'comparison':r'\b(?:compare|comparison|differs|difference|discrepancy|disagree|higher|lower|overstated)\b',
}
LABELS={'currency':'whether the reported information is current','meaning':'business meaning and intended treatment',
        'definitions':'the requested definitions and components','comparison':'the requested comparison',
        'unclassified':'the original question','delivery':'whether the application information was delivered',
        'mechanism':'the implemented transformation','expectation':'the expected behaviour'}

# Closed consumer-owned mapping: typed intake subjects, never wording guesses.
KIND_SUBJECTS={'VISUAL_CONTENT':'comparison','FRESHNESS':'currency',
    'SOURCE_CORRECTNESS':'delivery','FIGURE_DIFFERENCE':'comparison',
    'METRIC_COMPONENTS':'definitions','DERIVED_CALCULATION':'definitions',
    'TRANSFORMATION_MECHANISM':'mechanism','BUSINESS_MEANING':'meaning',
    'EXPECTED_BEHAVIOR':'expectation','FILTER_EFFECT':'comparison','TEMPORAL_COMPARISON':'comparison'}
DELIVERY_OUTCOMES={'INGESTION_GAP':'GAP','LOAD_LATENCY':'LATENT'}


def typed_check(kind,assessment,observations):
    """An outcome needs its completed evidence; unknown intent stays unknown."""
    from .question_kind import KINDS
    if kind not in KINDS or set(KIND_SUBJECTS)!=set(KINDS):raise Conflict('Question-kind answer map is incomplete')
    subject=KIND_SUBJECTS[kind];outcome=assessment.get('classification')
    refs=[];status='NOT_ANSWERED';reason='The completed checks did not establish an answer for this question kind.'
    from .declared_reproduction import NO_FIGURE
    no_figure = [o for o in observations
                 if o.get('check_kind') == 'DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE'
                 and o.get('reason') == NO_FIGURE]
    if outcome == 'NO_COMPARABLE_PATH' and no_figure:
        return {'subject':subject, 'status':'NO_REPORTED_FIGURE',
                'reason':'There is no reported figure to compare; no reproduction verdict was established.',
                'evidence_ids':[o['id'] for o in no_figure]}
    delivery=[o for o in observations if o.get('check_kind')=='SOURCE_DELIVERY'
              and o.get('delivery_result',{}).get('status')==DELIVERY_OUTCOMES.get(outcome)] if outcome in DELIVERY_OUTCOMES else []
    comparisons=[o for o in observations if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    if kind in ('SOURCE_CORRECTNESS','FIGURE_DIFFERENCE') and delivery:
        refs=[o['id'] for o in delivery];status='ANSWERED'
        reason=('The completed load was followed by a delivery difference in the independently read application and landing information.'
            if outcome=='INGESTION_GAP' else 'The application changed after the last successful load; delivery must be checked again after the next load.')
        reason+=' This answers the delivery condition within the recorded scope; matching data versions and the precise point of loss were not established.'
    elif kind in ('SOURCE_CORRECTNESS','FIGURE_DIFFERENCE','EXPECTED_BEHAVIOR') and comparisons:
        refs=[o['id'] for o in comparisons];status='PARTLY_ANSWERED'
        reason='Independent quantities were compared within the checked scope; remaining boundaries, timing and business intent are limited by the recorded evidence.'
        if outcome=='CONSISTENT_TO_SOURCE':
            status='ANSWERED';reason='The compared path agreed through the declared application source, with the requested record membership checked. The remaining expectation belongs to the application owner; currency is not established.'
        elif outcome=='CONSISTENT_TO_BOUNDARY':
            reason='The compared path agreed through the named checked depth; the application beyond it was not read, so the remaining question belongs to the application owner.'
    elif kind=='TRANSFORMATION_MECHANISM':
        refs=[o['id'] for o in observations if set(o.get('process_roles',[])) & {'transformation_definition','mechanism'}]
        if refs and outcome in ('TRANSFORMATION_LOGIC','DEFECT'):
            status='PARTLY_ANSWERED';reason='The retained definition was judged against the observed difference; the supported mechanism and its evidence limits are reported, without deciding business intent.'
    elif kind in ('METRIC_COMPONENTS','DERIVED_CALCULATION'):
        refs=[o['id'] for o in observations if set(o.get('process_roles',[])) & {'transformation_definition','left_definition','right_definition','presentation_definition'}]
        if refs:status='PARTLY_ANSWERED';reason='Definitions were inspected; coverage of every requested component or calculation is limited to the retained evidence.'
    elif kind=='BUSINESS_MEANING':
        reason='Technical flow evidence cannot establish authoritative business meaning; the remaining question requires a domain specialist.'
    elif kind=='VISUAL_CONTENT':
        reason='No completed declared-context reproduction established the requested visual result.'
    return {'subject':subject,'status':status,'reason':reason,'evidence_ids':refs}


def build(state):
    question=state['envelope']['symptom']
    if not isinstance(question,str) or not question.strip():raise Conflict('Question account requires the original ticket')
    assessment=state.get('assessment') or {}
    kind=(state['envelope'].get('question_kind') or {}).get('kind')
    from .reproduction_composition import select,answer,requested
    lead=select(state.get('observations',[])) if kind=='VISUAL_CONTENT' or requested(question) else None
    if lead is not None:
        return {'version':2,'question':question,'question_hash':digest(question),
            'status':'ANSWERED' if lead['label'] else 'NOT_ANSWERED',
            'subjects':[],'reproduction_answer':answer(lead),'answering_cell_receipt_id':lead['id'],
            'subject_provenance':'COMPLETED_DECLARED_CONTEXT_PROCEDURE',
            'finding_outcome':assessment.get('classification'),'authority':'DETERMINISTIC_EVIDENCE_COVERAGE'}
    observations=[o for o in state.get('observations',[]) if o.get('status')=='COMPLETED']
    roles={role for o in observations for role in o.get('process_roles',[])}
    detail=assessment.get('technical_output') or {}
    skipped=detail.get('skipped_steps',[])
    comparisons=[o for o in observations if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    kind=(state['envelope'].get('question_kind') or {}).get('kind')
    subjects=([KIND_SUBJECTS[kind]] if kind in KIND_SUBJECTS else
        [key for key,pattern in SUBJECTS.items() if re.search(pattern,question,re.I)] or ['unclassified'])
    checks=[]
    for subject in subjects:
        status='NOT_ANSWERED';reason='No recorded completion check establishes an answer to this request.'
        refs=[]
        if subject=='currency':
            refs=[o['id'] for o in observations if set(o.get('process_roles',[])) & {'freshness','job_history','ingestion'}]
            if refs:
                status='PARTLY_ANSWERED';reason='Timing or processing evidence was inspected, but it does not establish that the reported information is current.'
            else:reason='No completed currency check establishes whether the reported information is current.'
            if any(x.get('capability') in ('presentation_freshness','refresh_timing') for x in skipped):
                reason+=' Refresh history was unavailable to the diagnostic reader.'
            attempts=[o for o in observations if o.get('check_kind')=='FRESHNESS_ATTEMPT']
            if attempts:
                refs=sorted(set(refs+[o['id'] for o in attempts]))
                for attempt in attempts:
                    attempted_checks=attempt['freshness_attempt']['checks']
                    job=attempted_checks['job_history']
                    if job['status']=='CURRENT':
                        status='PARTLY_ANSWERED'
                        reason+=(' The load accounting was read and established a successful completed load; that alone does not establish currency.'
                            if job.get('accounting_observed') else ' Processing history was read and established successful completion; it did not return the load\'s own accounting.')
                    else:reason+=' Load accounting was attempted and found '+job['status'].lower()+': '+(job.get('reason') or 'No successful completion was established.')
                    delivery=attempted_checks['source_delivery']
                    if delivery['status'] in ('GAP','LATENT'):
                        status='PARTLY_ANSWERED';reason+=(' Source delivery evidence established a delivery gap.' if delivery['status']=='GAP' else ' Source delivery evidence established that the source changed after the last load.')
                    else:reason+=' Source delivery was attempted and found '+delivery['status'].lower()+': '+(delivery.get('reason') or 'No delivery condition was established.')
            elif 'job_history' not in roles:reason+=' Processing history was not assessed before the investigation stopped.'
        elif subject=='meaning':
            reason='No authoritative business meaning or intended rule was established; a technical finding cannot supply it.'
        elif subject=='definitions':
            refs=[o['id'] for o in observations if set(o.get('process_roles',[])) & {'transformation_definition','left_definition','right_definition','presentation_definition'}]
            if refs:
                status='PARTLY_ANSWERED';reason='A definition was inspected, but coverage of all requested definitions and components was not established.'
            else:reason='The requested definitions and component explanation were not established by the completed checks.'
        elif subject=='comparison':
            refs=[o['id'] for o in comparisons]
            if refs:
                status='PARTLY_ANSWERED';reason='Independent quantities were compared, but unchecked scope or evidence limits prevent a complete answer.'
                # Text recognition is not a complete intent/obligation contract.
                # Do not promote it to ANSWERED even when a comparison is aligned.
            else:
                from .declared_reproduction import KIND,LABELS
                reproductions=[o for o in observations if o.get('check_kind')==KIND]
                judged=[o for o in reproductions if o.get('label') in LABELS]
                if judged:
                    status='PARTLY_ANSWERED';refs=[o['id'] for o in judged]
                    reason='Declared selections were tested against the reported figure within one calculation service. Active selections and independent comparisons further back remain unestablished.'
                elif reproductions:
                    refs=[o['id'] for o in reproductions]
                    reason='Declared selections were evaluated, but no reported figure was supplied; no reproduction verdict or independent comparison was established.'
                else:
                    from .declared_reproduction import NO_FIGURE
                    refusals=[o for o in observations if o.get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE']
                    if any(o.get('reason')==NO_FIGURE for o in refusals):
                        refs=[o['id'] for o in refusals if o.get('reason')==NO_FIGURE]
                        reason='There is no reported figure to compare; no reproduction verdict was established.'
                    else:reason='No independent comparison established an answer to the requested difference.'
        checks.append(typed_check(kind,assessment,observations) if kind and kind!='FRESHNESS' else
            {'subject':subject,'status':status,'reason':reason,'evidence_ids':refs})
    states=[c['status'] for c in checks]
    status=('NO_REPORTED_FIGURE' if all(s=='NO_REPORTED_FIGURE' for s in states) else
            'ANSWERED' if all(s=='ANSWERED' for s in states) else
            'NOT_ANSWERED' if all(s=='NOT_ANSWERED' for s in states) else 'PARTLY_ANSWERED')
    return {'version':1,'question':question,'question_hash':digest(question),'status':status,
            'subjects':checks,'subject_provenance':'DECLARED_QUESTION_KIND' if kind else 'EXPLICIT_TEXT_MARKERS_WITH_UNCLASSIFIED_FALLBACK',
            'finding_outcome':assessment.get('classification'),'authority':'DETERMINISTIC_EVIDENCE_COVERAGE'}


def render(account):
    if 'reproduction_answer' in account:
        return 'You asked: '+account['question']+'\nAnswer to your question: '+account['reproduction_answer']
    status={'ANSWERED':'Answered within the checked scope','PARTLY_ANSWERED':'Partly answered',
            'NOT_ANSWERED':'Not answered','NO_REPORTED_FIGURE':'No verdict: no reported figure supplied'}[account['status']]
    lines=['You asked: '+account['question'],'Answer to your question: '+status+'.']
    for check in account['subjects']:
        lines.append('Regarding '+LABELS[check['subject']]+': '+check['reason'])
    lines.append('What was found instead:' if account['status']=='NOT_ANSWERED' else 'What the investigation established:')
    return '\n'.join(lines)


def attach(outputs,state):
    account=build(state);prefix=render(account)
    from .narrative_form import validate as validate_form
    for key in ('business_output','technical_output'):
        entry=outputs[key]
        entry['question_account']=copy.deepcopy(account)
        entry['explanation']['text']=prefix+'\n\n'+entry['explanation']['text']
        validate_form(entry['explanation']['text'],key=='business_output')
    validate(outputs,state)
    return outputs


def validate(outputs,state):
    expected=build(state);prefix=render(expected)+'\n\n'
    for key in ('business_output','technical_output'):
        entry=outputs.get(key,{})
        if entry.get('question_account')!=expected or not entry.get('explanation',{}).get('text','').startswith(prefix):
            raise Conflict('Narrative omits or changes the engine question/answer account')
