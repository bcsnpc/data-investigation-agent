"""Cohort reporting preserves official grades and independent review provenance."""
from copy import deepcopy
from round25_quality import cohort_metrics
from round25_independent_review import differs
import json
from pathlib import Path

def established_intake_exception(failure,exit_record):
    return (failure.get('error_type')=='ValueError'
            and failure.get('message')in ('COMPARISON_DETAILS_REQUIRED','CONFLICTING_COMPARISON_TARGET')
            and exit_record.get('exit_code')==1
            and exit_record.get('reason')=='UNDELIVERED_EXCEPTION'
            and exit_record.get('last_step')=='guided-investigation')

def load_saved_outcome(root,cohort,ident):
    """Report a real native exception without inventing an engine answer/usage."""
    root=Path(root);p=root/(cohort+'-'+ident+'-result.json')
    if p.exists():
        raw=p.read_bytes();return p,raw,json.loads(raw)
    p=root/(cohort+'-'+ident+'-terminal-error.json');raw=p.read_bytes();error=json.loads(raw)
    return p,raw,{'execution':error.get('execution',{}),'reporting_only_native_exception':True,
        'result':{'status':'UNDELIVERED_NATIVE_EXCEPTION','stop':error.get('error'),
                  'native_error':error,'outputs':{},'cost':{},'physical_requests':None,'model_calls':None}}

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
