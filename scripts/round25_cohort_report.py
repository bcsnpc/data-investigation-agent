"""Cohort reporting preserves official grades and independent review provenance."""
from copy import deepcopy
from round25_quality import cohort_metrics
from round25_independent_review import differs

def verdict_class(expected):
    """Group authored oracle labels without reading or rewriting ticket prose."""
    record=expected.get('expected',expected)
    value=record.get('verdict') if isinstance(record,dict) else None
    return value if isinstance(value,str) and value else 'ORACLE_VERDICT_UNDECLARED'

def summarize(cases,cohort):
    if cohort not in ('g2','g3','g4'):raise ValueError('INDEPENDENT_REVIEW_COHORT_REQUIRED')
    for case in cases:
        review=case.get('raw_review')
        if review and differs(case['primary'],case['secondary']):
            if review.get('independent_fresh_call')is not True or review.get('operator_judgment_supplied')is not False:
                raise ValueError('OPERATOR_MUST_NOT_ADJUDICATE_G2_G3_G4')
    return {**cohort_metrics(cases),'cohort':cohort,'cases':deepcopy(cases),'raw_review_policy':'FRESH_INDEPENDENT_CLAUDE_CALL; no operator adjudication'}
