"""Offline composition scoring against sealed requests, not inferred output prose."""
from jsonschema import Draft202012Validator, ValidationError
from . import evidence_prose, proposal_limits
from .path_narrative import validate_mechanism, validate_declared_layer_tokens,RepeatedHedge

READABILITY_FIELDS=('names_layer_by_role','one_mechanism','no_hedge_twice')


def score_attempt(attempt):
    """The original request carries the vocabulary; current rules are explicit."""
    payload=attempt['payload']; value=attempt['response']
    errors=[]
    try:Draft202012Validator(attempt['schema']).validate(value)
    except ValidationError:errors.append('WIRE_SCHEMA')
    technical=value.get('technical_output',{}) if isinstance(value,dict) else {}
    text=technical.get('text')
    token_valid=False
    if isinstance(text,str):
        try:validate_declared_layer_tokens(text,payload['layer_tokens']);token_valid=True
        except ValueError:errors.append('LAYER_TOKENS')
        try:
            Draft202012Validator(evidence_prose.schema(proposal_limits.ASSESSMENT_CLAIM)).validate(text)
            validate_mechanism(text)
        except RepeatedHedge:errors.append('HEDGE_TWICE')
        except (ValueError,ValidationError):errors.append('MECHANISM_FORM')
    else:errors.append('MISSING_MECHANISM')
    return {'token_valid':token_valid,'rejected_under_current_rules':bool(errors),'errors':sorted(set(errors))}


def score(records,model_version):
    selected=[r for r in records if r['model_version']==model_version]
    attempts=[score_attempt(a) for r in selected for a in r['attempts']]
    missing=[r['case_id'] for r in selected if not r['attempts']]
    return {'step':'synthesis','model_version':model_version,'cases':len(selected),
            'attempts':len(attempts),'no_model_mechanism_cases':missing,
            'score':sum(not a['rejected_under_current_rules'] for a in attempts)/len(attempts) if attempts else None,
            'token_validity':sum(a['token_valid'] for a in attempts)/len(attempts) if attempts else None,
            'rejection_rate':sum(a['rejected_under_current_rules'] for a in attempts)/len(attempts) if attempts else None,
            'basis':'RECORDED_RESPONSES_UNDER_CURRENT_VALIDATION','human_readability':'PENDING',
            'results':attempts}


def review_item(record):
    if not record['attempts']:raise ValueError('No model mechanism to review')
    last=record['attempts'][-1];p=last['payload']
    # A review view, not validation input or a reconstructed receipt.
    return {'case_id':record['case_id'],'model_version':record['model_version'],
            'provider_event_sha256':last['provider_event_sha256'],
            'text':last['response']['technical_output']['text'],
            'allowed_layer_tokens':sorted(p['layer_tokens']), 'boundary_spine':p['boundaries'],
            'human_flags':{f:None for f in READABILITY_FIELDS},'grader':None}


def score_human(items):
    if len(items)!=10 or len({i['case_id'] for i in items})!=10:raise ValueError('Ten distinct human grades required')
    for item in items:
        if not isinstance(item.get('grader'),str) or not item['grader'].strip():raise ValueError('Human grader attribution required')
        flags=item.get('human_flags')
        if not isinstance(flags,dict) or set(flags)!=set(READABILITY_FIELDS) or any(type(v) is not bool for v in flags.values()):
            raise ValueError('Human flags must be explicit booleans; missing is not false')
    return {'items':10,'per_flag':{f:sum(i['human_flags'][f] for i in items)/10 for f in READABILITY_FIELDS},
            'score':sum(all(i['human_flags'].values()) for i in items)/10,'graders':sorted({i['grader'] for i in items})}
