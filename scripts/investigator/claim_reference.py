"""Confirmed-claim authority for a faithful single, ungrouped visual route.

This is a new provenance variant, never a fabricated text span or form ticket.
Admission revalidates the exact immutable claim revision and user confirmation.
"""
import copy, json
from .onboarding import digest, Conflict

FIELDS = ('version','claim_id','revision','claim_hash','confirmation_hash','model_id',
          'measure_id','report_id','target_id','mode')
SCHEMA = {'type':'object','additionalProperties':False,'properties': {
    **{k:{'type':'string','minLength':1} for k in FIELDS if k!='revision'},
    'revision':{'type':'integer','minimum':0}},'required':list(FIELDS)}


def compile(body, catalog):
    from .claim_clarification import interpretation
    claim=body['claim']; confirmation=body.get('confirmation') or {}
    try:current_interpretation=interpretation(claim,catalog)
    except (ValueError,KeyError) as exc:
        raise Conflict('Confirmed claim interpretation cannot be revalidated') from exc
    if (body.get('status')!='CONFIRMED' or confirmation.get('authority')!='USER_CONFIRMED'
        or confirmation.get('interpretation_hash')!=digest(body.get('interpretation'))
        or confirmation.get('interpretation_hash')!=digest(current_interpretation)
        or confirmation.get('fact_ids')!=[f['id'] for f in claim['facts']]):
        raise Conflict('Confirmed claim reference requires unchanged user interpretation')
    accepted=[d for d in body.get('documents',[]) if d.get('hash')==confirmation.get('request_hash')
              and digest(d.get('request'))==d.get('hash') and d['request'].get('accepted') is True]
    if len(accepted)!=1:raise Conflict('Confirmed claim reference lacks retained user decision')
    binding=claim.get('selected_binding') or {}; settled=claim['settled']; scope=settled.get('scope') or {}
    if (settled.get('direction') not in ('LESS','MORE','DIFFERENT')
        or binding.get('kind')=='MULTIPLE' or settled.get('time') or settled.get('filters')
        or any(item not in ([],None) for item in settled.get('examples',[])) or scope.get('kind')!='VISUALS'
        or set(scope)-{'kind','model_id','report_id','page_id','visual_ids','phrase','report_phrase','page_phrase'}
        or len(scope.get('visual_ids',[]))!=1 or len(binding.get('target_ids',[]))!=1
        or scope['visual_ids']!=binding['target_ids']):
        raise Conflict('Confirmed claim route requires one exact visual and no added scope')
    model=next((m for m in catalog['models'] if m['id']==binding.get('model_id')),None)
    if model is None:raise Conflict('Confirmed claim model is unavailable')
    visual=next((v for v in model.get('visuals',[]) if v['target_id']==scope['visual_ids'][0]),None)
    if (visual is None or visual.get('grouping_columns')!=[] or visual.get('unsupported')
        or binding.get('measure_id') not in visual['measure_ids']
        or scope.get('report_id')!=visual['report_id'] or scope.get('page_id')!=visual.get('page_id')):
        raise Conflict('Confirmed claim visual is not faithfully ungrouped')
    declared=visual.get('declared_scopes',{}).get(binding['measure_id'])
    if not declared or declared.get('state')!='COMPLETE' or declared.get('restrictions')!=[]:
        raise Conflict('Confirmed claim visual lacks a complete empty declared context')
    proof={'version':'confirmed-claim-reference-v1','claim_id':body['id'],'revision':body['revision'],
        'claim_hash':digest(claim),'confirmation_hash':digest(confirmation),'model_id':model['id'],
        'measure_id':binding['measure_id'],'report_id':visual['report_id'],'target_id':visual['target_id'],'mode':'UNGROUPED'}
    observed=[o['figure'] for o in settled.get('observation',[]) if o.get('role')=='OBSERVED']
    if len(observed)>1:raise Conflict('Confirmed claim has more than one reported figure')
    return {'proof':proof,'reported_figure':copy.deepcopy(observed[0] if observed else {'state':'UNSPECIFIED'}),
        'target_visual':{'target_id':visual['target_id'],'report_id':visual['report_id'],
            'measure_id':binding['measure_id'],'mode':'UNGROUPED','source':None,'mode_source':None,
            'resolution':'RESOLVED','match_basis':{'confirmed_claim':proof}},
        'report_binding':{'resolution_kind':'USER_CONFIRMED_CLAIM','report_id':visual['report_id'],
                          'source':None,'claim_reference':proof}}


def validate_proof(proof):
    from jsonschema import Draft202012Validator
    Draft202012Validator(SCHEMA).validate(proof)
    if proof['version']!='confirmed-claim-reference-v1' or proof['mode']!='UNGROUPED':
        raise Conflict('Unknown confirmed claim reference')
    for key in ('claim_hash','confirmation_hash'):
        if len(proof[key])!=64 or any(c not in '0123456789abcdef' for c in proof[key]):
            raise Conflict('Confirmed claim reference hash is invalid')
    return proof


def validate_envelope(envelope, store, catalog):
    target=envelope.get('target_visual') or {}; proof=target.get('match_basis',{}).get('confirmed_claim')
    validate_proof(proof)
    with store.connect() as db:
        row=db.execute('SELECT body,body_hash FROM claim_revisions WHERE id=? AND revision=?',
                       (proof['claim_id'],proof['revision'])).fetchone()
    if row is None:raise Conflict('Confirmed claim reference is not retained')
    body=json.loads(row[0])
    if digest(body)!=row[1]:raise Conflict('Confirmed claim revision is corrupt')
    expected=compile(body,catalog)
    if any(envelope.get(k)!=expected[k] for k in ('target_visual','report_binding','reported_figure')):
        raise Conflict('Confirmed claim envelope differs from retained user scope')
    if envelope['model_id']!=proof['model_id'] or envelope['measure_id']!=proof['measure_id'] or proof!=expected['proof']:
        raise Conflict('Confirmed claim envelope changed its model or measure')
    return expected
