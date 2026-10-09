"""Consumer-owned clarification and ticket lifecycle, independent of a UI.

Candidate generation and investigation remain governed operations. This module
never evaluates quantities, nominates a target, or turns matching values into
authority. It only accepts answers to choices the caller has already retained.
"""
import copy
from jsonschema import Draft202012Validator
from .onboarding import digest

VERSION = 'smart-ticket-v1'
FIELDS = ('NUMBER', 'REPORT_PAGE', 'COMPARISON')
ROUTES = ('APPLICATION', 'STALE', 'LOOKS_WRONG', 'OTHER_REPORT', 'BUSINESS_MEANING')
STATES = ('NEW', 'CLARIFYING', 'INVESTIGATING', 'FINDINGS_SHARED',
          'CLOSED', 'BUSINESS_VALIDATION', 'TECH_HANDOFF', 'HELD')


def obj(properties, optional=()):
    return {'type':'object', 'additionalProperties':False, 'properties':properties,
            'required':[k for k in properties if k not in optional]}


TEXT = {'type':'string', 'minLength':1, 'maxLength':2000}
ID = {'type':'string', 'minLength':1, 'maxLength':200}
CHOICE = obj({'id':ID, 'label':TEXT,
              'highlight':{'anyOf':[{'type':'null'}, obj({'image_id':ID,
                  'x':{'type':'number','minimum':0,'maximum':1},
                  'y':{'type':'number','minimum':0,'maximum':1},
                  'width':{'type':'number','exclusiveMinimum':0,'maximum':1},
                  'height':{'type':'number','exclusiveMinimum':0,'maximum':1}})]}})
QUESTION = obj({'id':ID, 'field':{'enum':list(FIELDS)}, 'question':TEXT,
                'choices':{'type':'array','minItems':1,'maxItems':100,'items':CHOICE}})
QUESTIONS = {'type':'array','minItems':1,'maxItems':3,'items':QUESTION}
ANSWER = obj({'question_id':ID, 'choice_id':ID})
ANSWERS = {'type':'array','minItems':1,'maxItems':3,'items':ANSWER}
INTAKE = obj({'comparison_choices':{'type':'array','minItems':1,'maxItems':5,
                  'items':obj({'route':{'enum':list(ROUTES)},'label':TEXT})},
              'default_route':{'enum':['ASK',*ROUTES]},
              'must_confirm':{'type':'array','uniqueItems':True,'maxItems':3,
                  'items':{'enum':list(FIELDS)}},
              'max_clarifying_rounds':{'type':'integer','minimum':1,'maximum':10},
              'screenshot_retention_days':{'type':'integer','minimum':1,'maximum':36500},
              'screenshot_redaction':{'const':'ESTATE_RECORDING_POLICY'},
              'vocabulary_aliases':{'type':'array','maxItems':512,
                  'items':obj({'alias':ID,'canonical':ID})}})
OWNERSHIP = obj({'business':{'type':'array','maxItems':512,
                   'items':obj({'measure_or_area':ID,'owner':ID})},
                'technical':{'type':'array','maxItems':512,
                   'items':obj({'layer_or_pipeline':ID,'owner':ID})}})


def validate_questions(questions):
    Draft202012Validator(QUESTIONS).validate(questions)
    for key in ('id','field'):
        if len({q[key] for q in questions})!=len(questions):
            raise ValueError('Clarification questions must have unique '+key)
    for question in questions:
        choices=question['choices']
        if len({c['id'] for c in choices})!=len(choices):
            raise ValueError('Clarification choice identities must be unique')
        for choice in choices:
            h=choice['highlight']
            if h and (h['x']+h['width']>1 or h['y']+h['height']>1):
                raise ValueError('Highlight lies outside its image')
    return copy.deepcopy(questions)


def confirmed(questions, answers):
    """Answer identity must bind a retained choice; no arbitrary scope payload."""
    validate_questions(questions)
    Draft202012Validator(ANSWERS).validate(answers)
    if len({a['question_id'] for a in answers})!=len(answers):
        raise ValueError('A question cannot receive two answers')
    if {a['question_id'] for a in answers}!={q['id'] for q in questions}:
        raise ValueError('Answer every question in the retained batch exactly once')
    result={}
    for question in questions:
        answer=next(a for a in answers if a['question_id']==question['id'])
        choice=next((c for c in question['choices'] if c['id']==answer['choice_id']),None)
        if choice is None:raise ValueError('Answer refers to an unoffered choice')
        result[question['field']]={'question_id':question['id'],
            'choice_id':choice['id'],'authority':'USER_CONFIRMED',
            'question_hash':digest(question)}
    return result


def new(identity):
    return {'version':VERSION,'id':identity,'state':'NEW','rounds':0,
            'questions':[],'confirmed':{},'settled':{},'history':[],'evidence':{}}


def transition(ticket, state, *, actor, detail):
    if ticket.get('version')!=VERSION or state not in STATES:
        raise ValueError('Unknown ticket contract or state')
    before=ticket['state']
    allowed={'NEW':{'CLARIFYING','INVESTIGATING','BUSINESS_VALIDATION','HELD'},
        'CLARIFYING':{'CLARIFYING','INVESTIGATING','BUSINESS_VALIDATION','HELD'},
        'INVESTIGATING':{'FINDINGS_SHARED','HELD'},
        'FINDINGS_SHARED':{'CLOSED','CLARIFYING','INVESTIGATING','BUSINESS_VALIDATION','TECH_HANDOFF'},
        'BUSINESS_VALIDATION':{'CLOSED','CLARIFYING','INVESTIGATING'},
        'TECH_HANDOFF':{'CLOSED','CLARIFYING','INVESTIGATING'},
        'HELD':{'CLARIFYING','INVESTIGATING','BUSINESS_VALIDATION'},'CLOSED':set()}
    if state not in allowed.get(before,set()):raise ValueError('Invalid ticket transition')
    if actor not in ('AGENT','USER','OWNER'):raise ValueError('Unknown ticket actor')
    if state=='CLOSED' and actor=='AGENT':raise ValueError('The agent cannot close a ticket')
    if state=='CLOSED' and actor=='OWNER':
        owner=detail.get('owner') if isinstance(detail,dict) else None
        assigned={e['detail'].get('owner') for e in ticket['history']
                  if e['to'] in ('BUSINESS_VALIDATION','TECH_HANDOFF')}
        if not isinstance(owner,str) or not owner or owner not in assigned:
            raise ValueError('Only the named handoff owner can close as OWNER')
    if state=='INVESTIGATING' and (ticket['questions'] or set(ticket['settled'])!=set(FIELDS)):
        raise ValueError('Every consequential field must be settled before investigation')
    result=copy.deepcopy(ticket)
    result['state']=state
    result['history'].append({'from':before,'to':state,'actor':actor,'detail':copy.deepcopy(detail)})
    return result


def ask(ticket, questions, *, maximum=2):
    questions=validate_questions(questions)
    if ticket['rounds']>=maximum:
        result=transition(ticket,'HELD',actor='AGENT',detail={'reason':'CLARIFICATION_LIMIT'})
        result['questions']=questions
        return result
    result=transition(ticket,'CLARIFYING',actor='AGENT',detail={'questions':questions})
    result['rounds']+=1;result['questions']=questions
    return result


def answer(ticket, answers):
    if ticket['state']!='CLARIFYING':raise ValueError('Ticket is not awaiting clarification')
    result=copy.deepcopy(ticket)
    choices=confirmed(ticket['questions'],answers)
    result['confirmed'].update(choices)
    result['settled'].update(choices)
    result['history'].append({'from':'CLARIFYING','to':'CLARIFYING','actor':'USER',
                             'detail':{'answers':copy.deepcopy(answers)}})
    result['questions']=[]
    # Confirmation does not authorise investigation. The caller revalidates the
    # resulting scope, including any unresolved consequential fields, first.
    return result


def settle_from_intake(ticket, proposal, payload, *, must_confirm=()):
    """Only the original consumer may establish a uniquely resolved referent.

    This is not settlement by a quantity match. Re-run the existing schema,
    provenance, referent, figure, selection and scope validators first. The
    comparison route remains independent and is never inferred from triage.
    """
    from .question_intake import validate
    if set(must_confirm)-set(FIELDS):raise ValueError('Unknown confirmation field')
    validate(proposal,payload)
    if proposal['action']!='PROPOSE':raise ValueError('A question is not a settled scope')
    result=copy.deepcopy(ticket)
    fields={'NUMBER':{k:copy.deepcopy(proposal.get(k)) for k in
        ('model_id','measure_id','target_visual','reported_figure','filters','dimension_ids')},
        'REPORT_PAGE':{k:copy.deepcopy(proposal.get(k)) for k in ('report_binding','target_visual')}}
    for field,value in fields.items():
        if field in must_confirm or field in result['confirmed']:continue
        result['settled'][field]={'authority':'VALIDATED_INTAKE_REFERENT',
            'scope_hash':digest(proposal),'value':value}
    result['history'].append({'from':result['state'],'to':result['state'],'actor':'AGENT',
        'detail':{'settled_from_intake':digest(proposal),'fields':[f for f in fields
                  if f not in must_confirm and f not in result['confirmed']]}})
    return result


def evidence_address(context, scope, cell):
    return digest({'context':context,'scope':scope,'cell':cell})


def retain(ticket, *, context, scope, cell, receipt):
    result=copy.deepcopy(ticket)
    key=evidence_address(context,scope,cell)
    if key in result['evidence'] and result['evidence'][key]!=receipt:
        raise ValueError('A proven evidence address cannot be overwritten')
    result['evidence'][key]=copy.deepcopy(receipt)
    return result


def reuse(ticket, *, context, scope, cell, purpose):
    """A retained receipt cannot answer a new question about current values.

    Callers must name the purpose; historical use carries its qualification in
    the returned contract, rather than presenting an old receipt as a fresh read.
    """
    if purpose not in ('EXPLAIN_RECORDED_RESULT','DEFINITION','CURRENT_VALUE'):
        raise ValueError('Unknown evidence reuse purpose')
    if purpose=='CURRENT_VALUE':return None
    receipt=ticket['evidence'].get(evidence_address(context,scope,cell))
    if receipt is None:return None
    return {'receipt':copy.deepcopy(receipt),'purpose':purpose,
            'evidence_use':'RETAINED_EVIDENCE',
            'qualification':'This describes retained evidence, not a new reading of current data.'}
