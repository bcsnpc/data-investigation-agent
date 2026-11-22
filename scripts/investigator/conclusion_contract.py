"""Question-shaped delivery contract; native support is checked by the consumer.

This validates structure, references and declared coverage, not the truth of
arbitrary causal prose. Independent grading still evaluates causal correctness.
"""
from copy import deepcopy
from .regression_features import enabled

CONTEXT_TYPES = ('glossary/synonym', 'metric definition', 'business rule',
                 'schedule/SLA', 'source of truth', 'owner', 'other')
VERDICTS = ('DEVIATION', 'AS DESIGNED', 'UNRESOLVED')


def fields():
    text = {'type': 'string', 'minLength': 1}
    return {
        'direct_answer': {**text, 'description': 'One or two sentences answering the exact user question, including why; distinguish incidental observations.'},
        'verdict_class': {'enum': list(VERDICTS), **({'description': 'Question-level disposition, separate from the technical verdict detail. AS DESIGNED describes the observed implemented rule, not approval of business policy; a supported access rule or current record absence can explain the question.'} if enabled('r27_conclusion_detail_compatibility') else {})},
        'calculation_explanation': {**text, 'description': 'Explain the implemented calculation and filters from cited definitions; for a status-only ask say no quantity calculation was requested.'},
        'undecided': {'type': 'array', 'items': text, 'description': 'Exact unavailable fact or unresolved distinction, with a reason; empty only when nothing remains undecided within the asked scope.'},
        'routing': {'enum': ['ENGINEER', 'BUSINESS_OWNER']},
        'context_gap': {'type': 'object', 'additionalProperties': False,
                        'required': ['type', 'note'], 'properties': {
                            'type': {'enum': list(CONTEXT_TYPES)},
                            'note': {**text, 'description': 'One fact that would resolve or shorten this case. Record only; never request a context file or invent business intent.'}}},
    }


def validate(value, case):
    from jsonschema import Draft202012Validator
    properties = fields()
    Draft202012Validator({'type': 'object', 'properties': properties,
                         'required': list(properties)}).validate(value)
    if not value['direct_answer'].strip() or not value['calculation_explanation'].strip():
        raise ValueError('DIRECT_ANSWER_AND_IMPLEMENTED_CALCULATION_REQUIRED')
    if value['verdict_class'] == 'UNRESOLVED' and not value['undecided']:
        raise ValueError('UNRESOLVED_REQUIRES_EXACT_MISSING_EVIDENCE')
    implemented_details = {'as designed', 'definition explained'}
    if enabled('r27_conclusion_detail_compatibility'):
        implemented_details.update({'access difference', 'record missing', 'duplicate record',
                                    'blank or error', 'observed value', 'consistent to boundary', 'not found'})
    if value['verdict_class'] == 'AS DESIGNED' and value.get('verdict') not in implemented_details:
        raise ValueError('AS_DESIGNED_REQUIRES_IMPLEMENTED_RULE_VERDICT')
    if value['verdict_class'] == 'DEVIATION' and value.get('verdict') in ('as designed', 'definition explained', 'not found'):
        raise ValueError('DEVIATION_REQUIRES_EVIDENCED_FLOW_OR_ACCESS_DIFFERENCE')
    if value['verdict_class'] == 'UNRESOLVED' and value.get('verdict') != 'not found':
        raise ValueError('UNRESOLVED_REQUIRES_NOT_FOUND_DETAIL')
    # A selected visual is not interchangeable with a similarly valued visual.
    intake = case.get('intake', {})
    explicit = case.get('context', {}).get('explicit_target', {})
    for field in ('report', 'page', 'visual', 'measure', 'table'):
        if field in explicit and intake.get(field) != explicit[field]:
            raise ValueError('EXPLICIT_TARGET_CHANGED:' + field)
    return {key: deepcopy(value[key]) for key in properties}


def render(value):
    return '\n'.join([
        value['direct_answer'],
        'Verdict class: ' + value['verdict_class'],
        'How it is calculated: ' + value['calculation_explanation'],
        'Could not decide: ' + ('; '.join(value['undecided']) or 'Nothing further within the stated question and cited evidence.'),
        'Routing: ' + value['routing'].replace('_', ' ').lower(),
    ])
