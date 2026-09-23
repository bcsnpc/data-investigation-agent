"""Validate an explicit claim basis, not the semantic truth of LLM interpretations.

Old saved assessments remain readable. The current provider wire contract requires
this support object; it grants no evidence authority or verified classification.
"""
from . import proposal_limits as limits
from .onboarding import fields, text

SCHEMA = {'type':'object','additionalProperties':False,'properties':{
    'mechanism':{'type':'string','minLength':1,'maxLength':limits.ASSESSMENT_DETAIL},
    'mechanism_evidence_ids':{'type':'array','maxItems':8,'items':{'type':'string'}},
    'intent_dependency':{'type':'string','enum':['NOT_REQUIRED','ESTABLISHED','UNKNOWN']},
    'intent_basis':{'type':'string','minLength':1,'maxLength':limits.ASSESSMENT_DETAIL},
    'intent_evidence_ids':{'type':'array','maxItems':8,'items':{'type':'string'}},
    'remaining_test':{'type':'string','minLength':1,'maxLength':limits.ASSESSMENT_DETAIL}},
    'required':['mechanism','mechanism_evidence_ids','intent_dependency','intent_basis',
                'intent_evidence_ids','remaining_test']}


def validate(assessment, observations):
    support=assessment['support'];fields(support,SCHEMA['required'])
    for key in ('mechanism','intent_basis','remaining_test'):text(support[key],limits.ASSESSMENT_DETAIL)
    dependency=support['intent_dependency']
    if dependency not in SCHEMA['properties']['intent_dependency']['enum']:
        raise ValueError('Unknown intent dependency')
    for key in ('mechanism_evidence_ids','intent_evidence_ids'):
        refs=support[key]
        if not isinstance(refs,list) or len(refs)>8 or any(
                not isinstance(r,str) or r not in assessment['evidence_ids'] or
                r not in observations or observations[r].get('status')!='COMPLETED'
                for r in refs):
            raise ValueError('Support must cite completed assessment evidence')
    if dependency=='ESTABLISHED' and not support['intent_evidence_ids']:
        raise ValueError('Established intent needs cited evidence; otherwise mark UNKNOWN or justify NOT_REQUIRED')
    if assessment['classification'] in ('LIKELY_TECHNICAL_DEFECT','EXPECTED_BEHAVIOR','SOURCE_OR_APPLICATION_ISSUE','REFRESH_OR_FRESHNESS_ISSUE'):
        if dependency=='UNKNOWN':
            raise ValueError('Conclusion depends on unknown business intent: qualify as BUSINESS_CONTEXT_REQUIRED or investigate the missing premise')
        if not any(observations[r].get('tool')!='context' and
                   observations[r].get('completeness')=='COMPLETE_RESPONSE'
                   for r in support['mechanism_evidence_ids']):
            raise ValueError('Conclusion needs complete live mechanism evidence, not only a reproduced symptom')
    return support
