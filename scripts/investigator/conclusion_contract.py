"""Question-shaped delivery contract; native support is checked by the consumer.

This validates structure, references and declared coverage, not the truth of
arbitrary causal prose. Independent grading still evaluates causal correctness.
"""
from copy import deepcopy

CONTEXT_TYPES = ('glossary/synonym', 'metric definition', 'business rule',
                 'schedule/SLA', 'source of truth', 'owner', 'other')
VERDICTS = ('DEVIATION', 'AS DESIGNED', 'UNRESOLVED')


def fields():
    text = {'type': 'string', 'minLength': 1}
    gap = {'type': 'object', 'additionalProperties': False,
           'required': ['type', 'note'], 'properties': {
               'type': {'enum': list(CONTEXT_TYPES)},
               'note': {**text, 'description': 'One fact that would resolve or shorten this case. Record only; never request a context file or invent business intent.'}}}
    gap = {'description': 'Optional record-only metadata: an object with type ('+', '.join(CONTEXT_TYPES)+') and a one-line note about a fact that would shorten the case. Do not invent a gap. This metadata never decides whether a supported finding can be delivered.'}
    return {
        'direct_answer': {**text, 'description': 'One or two sentences answering the exact user question, including why; distinguish incidental observations.'},
        'verdict_class': {'enum': list(VERDICTS), **{'description': ('Question-level disposition, separate from the technical verdict detail. AS DESIGNED describes the observed implemented rule, not approval of business policy; a supported access rule or current record absence can explain the question.' + ' Use the different question technical detail with AS DESIGNED when evidenced selection scopes explain different figures; retain the scope evidence and each measured value.')}},
        'calculation_explanation': {**text, 'description': 'Explain the implemented calculation and filters from cited definitions; for a status-only ask say no quantity calculation was requested.'},
        'undecided': {'type': 'array', 'items': text, 'description': 'Exact unavailable fact or unresolved distinction, with a reason; empty only when nothing remains undecided within the asked scope.'},
        'routing': {'enum': ['ENGINEER', 'BUSINESS_OWNER']},
        'context_gap': gap,
    }


def validate(value, case):
    from jsonschema import Draft202012Validator
    properties = fields()
    Draft202012Validator({'type': 'object', 'properties': properties,
                         'required': [k for k in properties if k!='context_gap']}).validate(value)
    if not value['direct_answer'].strip() or not value['calculation_explanation'].strip():
        raise ValueError('DIRECT_ANSWER_AND_IMPLEMENTED_CALCULATION_REQUIRED')
    if value['verdict_class'] == 'UNRESOLVED' and not value['undecided']:
        raise ValueError('UNRESOLVED_REQUIRES_EXACT_MISSING_EVIDENCE')
    implemented_details = {'as designed', 'definition explained'}
    implemented_details.update({'access difference', 'record missing', 'duplicate record',
                                'blank or error', 'observed value', 'consistent to boundary', 'not found'})
    implemented_details.add('different question')
    if value['verdict_class'] == 'AS DESIGNED' and value.get('verdict') not in implemented_details:
        raise ValueError('AS_DESIGNED_REQUIRES_IMPLEMENTED_RULE_VERDICT')
    if value['verdict_class'] == 'DEVIATION' and value.get('verdict') in ('as designed', 'definition explained', 'not found'):
        raise ValueError('DEVIATION_REQUIRES_EVIDENCED_FLOW_OR_ACCESS_DIFFERENCE')
    if value['verdict_class'] == 'UNRESOLVED' and value.get('verdict') != 'not found':
        raise ValueError('UNRESOLVED_REQUIRES_NOT_FOUND_DETAIL')
    if value['verdict_class']=='DEVIATION':
        from .primary_verification import is_display_verification
        if is_display_verification(case,value):
            raise ValueError('PRIMARY_QUESTION_IS_DISPLAY_VERIFICATION: no comparison or violated intended rule was supplied. Explain the cited implemented calculation and reproduced target value; an incidental upstream difference does not make this question a deviation.')
    # A selected visual is not interchangeable with a similarly valued visual.
    intake = case.get('intake', {})
    explicit = case.get('context', {}).get('explicit_target', {})
    for field in ('report', 'page', 'visual', 'measure', 'table'):
        if field in explicit and intake.get(field) != explicit[field]:
            raise ValueError('EXPLICIT_TARGET_CHANGED:' + field)
    result = {key: deepcopy(value[key]) for key in properties if key in value}
    tag = value.get('context_gap')
    valid_tag = (isinstance(tag,dict) and set(tag)=={'type','note'}
                 and isinstance(tag.get('type'),str) and tag['type'] in CONTEXT_TYPES
                 and isinstance(tag.get('note'),str) and bool(tag['note'].strip()))
    if not valid_tag:
        result['context_gap']={'type':'other','note':'UNRECORDED_CONTEXT_GAP: missing or invalid record-only metadata; no missing business fact is inferred.'}
    return result


def render(value):
    return '\n'.join([
        value['direct_answer'],
        'Verdict class: ' + value['verdict_class'],
        'How it is calculated: ' + value['calculation_explanation'],
        'Could not decide: ' + ('; '.join(value['undecided']) or 'Nothing further within the stated question and cited evidence.'),
        'Routing: ' + value['routing'].replace('_', ' ').lower(),
    ])
