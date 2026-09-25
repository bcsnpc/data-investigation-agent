"""Validate an explicit claim basis, not the semantic truth of LLM interpretations.

Old saved assessments remain readable. The current provider wire contract requires
this support object; it grants no evidence authority or verified classification.
"""
from . import proposal_limits as limits
from .onboarding import fields, text

SCHEMA = {'type':'object','additionalProperties':False,'properties':{
    'mechanism':{'type':'string','minLength':1,'description':f'Complete concise text, at most {limits.ASSESSMENT_DETAIL} characters. Never cut a sentence or reference to fit.'},
    'mechanism_evidence_ids':{'type':'array','maxItems':8,'items':{'type':'string'}},
    'intent_dependency':{'type':'string','enum':['NOT_REQUIRED','ESTABLISHED','UNKNOWN']},
    'intent_basis':{'type':'string','minLength':1,'description':f'Complete concise text, at most {limits.ASSESSMENT_DETAIL} characters. Never cut a sentence or reference to fit.'},
    'intent_evidence_ids':{'type':'array','maxItems':8,'items':{'type':'string'}},
    'measure_connection':{'type':'string','enum':['ESTABLISHED','NOT_ASSERTED','NOT_ESTABLISHED_SCOPE',
        'NOT_ESTABLISHED_CAPABILITY','NOT_ESTABLISHED_PERMISSION','NOT_ESTABLISHED_BUDGET','NOT_ESTABLISHED_ELIGIBILITY']},
    'measure_connection_basis':{'type':'string','minLength':1,'description':f'Complete concise text, at most {limits.ASSESSMENT_DETAIL} characters. Never cut a sentence or reference to fit.'},
    'measure_connection_evidence_ids':{'type':'array','maxItems':8,'items':{'type':'string'}},
    'remaining_test':{'type':'string','minLength':1,'description':f'Complete concise text, at most {limits.ASSESSMENT_DETAIL} characters. Never cut a sentence or reference to fit.'}},
    'required':['mechanism','mechanism_evidence_ids','intent_dependency','intent_basis',
                'intent_evidence_ids','measure_connection','measure_connection_basis',
                'measure_connection_evidence_ids','remaining_test']}


def validate(assessment, observations):
    support=assessment['support']
    legacy=not any(k in support for k in ('measure_connection','measure_connection_basis','measure_connection_evidence_ids'))
    required=[k for k in SCHEMA['required'] if not legacy or not k.startswith('measure_connection')]
    fields(support,required)
    for key in ('mechanism','intent_basis','remaining_test')+(() if legacy else ('measure_connection_basis',)):
        if isinstance(support[key],str) and len(support[key])>limits.ASSESSMENT_DETAIL:
            raise ValueError(f'Support {key} exceeds {limits.ASSESSMENT_DETAIL} characters; rewrite concisely without dropping the premise or cutting text')
        text(support[key],limits.ASSESSMENT_DETAIL)
    dependency=support['intent_dependency']
    if dependency not in SCHEMA['properties']['intent_dependency']['enum']:
        raise ValueError('Unknown intent dependency')
    for key in ('mechanism_evidence_ids','intent_evidence_ids')+(() if legacy else ('measure_connection_evidence_ids',)):
        refs=support[key]
        if not isinstance(refs,list) or len(refs)>8 or any(
                not isinstance(r,str) or r not in assessment['evidence_ids'] or
                r not in observations or observations[r].get('status')!='COMPLETED'
                for r in refs):
            raise ValueError('Support must cite completed assessment evidence')
    if dependency=='ESTABLISHED' and not support['intent_evidence_ids']:
        raise ValueError('Established intent needs cited evidence; otherwise mark UNKNOWN or justify NOT_REQUIRED')
    cause=assessment['classification'] in ('LIKELY_TECHNICAL_DEFECT','EXPECTED_BEHAVIOR','SOURCE_OR_APPLICATION_ISSUE','REFRESH_OR_FRESHNESS_ISSUE')
    if cause:
        if dependency=='UNKNOWN':
            raise ValueError('Conclusion depends on unknown business intent: qualify as BUSINESS_CONTEXT_REQUIRED or investigate the missing premise')
        if not any(observations[r].get('tool')!='context' and
                   observations[r].get('completeness')=='COMPLETE_RESPONSE'
                   for r in support['mechanism_evidence_ids']):
            raise ValueError('Conclusion needs complete live mechanism evidence, not only a reproduced symptom')
    if legacy:return support
    connection=support['measure_connection']
    if connection not in SCHEMA['properties']['measure_connection']['enum']:raise ValueError('Unknown measure connection status')
    if cause:
        if connection=='NOT_ASSERTED':raise ValueError('Cause conclusion must connect the mechanism to the reported measure or name the exact establishment barrier')
    if connection=='ESTABLISHED':
        refs=support['measure_connection_evidence_ids']
        if not refs:raise ValueError('Established measure connection needs cited evidence')
        if not any(observations[r].get('test_purpose')=='TEST_CONTRIBUTION' or
                   observations[r].get('joint_aggregate') or observations[r].get('reviewed_mapping') or
                   observations[r].get('record_mapping') for r in refs):
            raise ValueError('Measure connection evidence must test contribution or retain an admitted mapping')
    return support
