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
        'unclassified':'the original question'}


def build(state):
    question=state['envelope']['symptom']
    if not isinstance(question,str) or not question.strip():raise Conflict('Question account requires the original ticket')
    assessment=state.get('assessment') or {}
    observations=[o for o in state.get('observations',[]) if o.get('status')=='COMPLETED']
    roles={role for o in observations for role in o.get('process_roles',[])}
    detail=assessment.get('technical_output') or {}
    skipped=detail.get('skipped_steps',[])
    comparisons=[o for o in observations if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    subjects=[key for key,pattern in SUBJECTS.items() if re.search(pattern,question,re.I)] or ['unclassified']
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
            if 'job_history' not in roles:reason+=' Processing history was not assessed before the investigation stopped.'
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
            else:reason='No independent comparison established an answer to the requested difference.'
        checks.append({'subject':subject,'status':status,'reason':reason,'evidence_ids':refs})
    states=[c['status'] for c in checks]
    status=('ANSWERED' if all(s=='ANSWERED' for s in states) else
            'NOT_ANSWERED' if all(s=='NOT_ANSWERED' for s in states) else 'PARTLY_ANSWERED')
    return {'version':1,'question':question,'question_hash':digest(question),'status':status,
            'subjects':checks,'subject_provenance':'EXPLICIT_TEXT_MARKERS_WITH_UNCLASSIFIED_FALLBACK',
            'finding_outcome':assessment.get('classification'),'authority':'DETERMINISTIC_EVIDENCE_COVERAGE'}


def render(account):
    status={'ANSWERED':'Answered within the checked scope','PARTLY_ANSWERED':'Partly answered','NOT_ANSWERED':'Not answered'}[account['status']]
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
