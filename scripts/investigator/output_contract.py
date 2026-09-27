"""Closed business language and outcome-owned actions; no free-text interpolation."""
from .process_outcomes import ACTIONS, OLD_TO_CURRENT

def canonical(outcome):
    return OLD_TO_CURRENT.get(outcome, outcome)

BUSINESS = {
    'REFRESH_LATENCY': 'The reported number has not yet caught up with the latest available information.',
    'LOAD_LATENCY': 'A scheduled update has not yet delivered the information needed by the reported number.',
    'PRESENTATION_LOGIC': 'The way the report presents the information explains the difference. This does not establish whether that behavior is intended.',
    'TRANSFORMATION_LOGIC': 'A documented processing rule explains the difference. This does not establish whether that rule is intended.',
    'INGESTION_GAP': 'Some expected information has not arrived in the checked process.',
    'DEFECT': 'The checked process changes the number in a way that the inspected rules do not explain.',
    'CONSISTENT_TO_BOUNDARY': 'The reported number agrees with the information checked so far. This does not establish whether the original entries or business rules are correct.',
    'NO_COMPARABLE_PATH': 'The reported number was checked, but the available information does not allow a reliable comparison further back.',
    'DEFINITION_DIFFERENCE': 'The two numbers use different calculation rules. Whether that difference is intended remains a business decision.',
    'SCOPE_DIFFERENCE': 'The two numbers cover different selections. Whether those selections are intended remains a business decision.',
    'DIFFERENT_SUBJECT': 'The two numbers describe different subjects and should not be treated as the same quantity.',
    'BUSINESS_QUESTION': 'The checked information agrees. The remaining question requires business knowledge that this investigation cannot establish.',
    'NO_KNOWN_PATTERN': 'The available checks do not establish an explanation for the reported problem.',
}
ACTION_TEXT = {
    'RECHECK_AFTER_REFRESH': 'Check the number again after the report updates.',
    'RECHECK_AFTER_JOB': 'Check the number again after the scheduled update finishes.',
    'CONFIRM_INTENT_OR_REQUEST_ENHANCEMENT': 'Ask the responsible business owner whether this behavior is intended; request a change if it is not.',
    'ROUTE_OPERATIONAL_FIX': 'Ask the operations owner to investigate the missing delivery using the recorded evidence.',
    'RAISE_BUG_WITH_EVIDENCE': 'Raise a defect with the recorded evidence for the responsible engineering team.',
    'ASK_UPSTREAM_OWNER': 'Ask the owner of the information before the checked stage to investigate the remaining gap.',
    'NAME_MISSING_BINDING_OR_ACCESS': 'Ask the system owner to provide the missing connection information or read access identified in the limits.',
    'DECIDE_BUG_OR_ENHANCEMENT': 'Ask the business owner whether the difference requires a defect fix or a requested change.',
    'CONFIRM_SCOPE_INTENT': 'Confirm with the requester which selections the comparison should use.',
    'INFORMATIONAL': 'Confirm which subject the requester wants to investigate before comparing the numbers.',
    'ASK_DOMAIN_SPECIALIST': 'Ask a business specialist to explain the intended rule.',
    'FOLLOW_NAMED_NEXT_STEP': 'Ask the responsible owner to review the recorded missing evidence and next step.',
}

def action(outcome):
    code = ACTIONS[canonical(outcome)]
    return {'code': code, 'text': ACTION_TEXT[code]}

def business_text(outcome, payload=None):
    """Five sentences from sealed quantity/comparison facts, never asset prose."""
    from decimal import Decimal, InvalidOperation
    outcome=canonical(outcome)
    entries=(payload or {}).get('evidence',[])
    baseline=next((e for e in entries if e.get('test_purpose')=='ESTABLISH_BASELINE'
                   and e.get('provenance',{}).get('receipt_seal')),None)
    number=None
    raw=(baseline or {}).get('verified_quantity',{}).get('quantity')
    if isinstance(raw,str) and len(raw)<=100:
        try:
            value=Decimal(raw)
            if value.is_finite() and abs(value.adjusted())<=100:
                number=format(value,',f')
        except InvalidOperation:pass
    first=('The checked report value was '+number+'.' if number is not None else
           'A single report value could not be established from the available verified evidence.')
    comparisons=[e['result'] for e in entries if e.get('tool')=='process'
                 and e.get('result',{}).get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    immediate=next((c for c in comparisons if baseline and
                    c.get('referenced_evidence_ids',[None])[0]==baseline['id']),None)
    agrees=immediate is not None and immediate['values_equal'] is True
    differs=any(c['values_equal'] is False for c in comparisons)
    if agrees:
        compared=('An independent check of the information feeding the report agreed'+
                  (', but a comparison further back found a different total.' if differs else '.'))
        ruled_out='This rules out a report-to-input difference within these checks, but does not prove the original records are correct.'
    elif immediate is not None:
        compared='An independent check of the information feeding the report found a different total.'
        ruled_out='These checks establish a difference, but do not by themselves establish which information is correct.'
    else:
        compared='The available evidence did not establish an independent comparison with the information feeding the report.'
        ruled_out='A difference between the report and its input therefore remains possible.'
    remaining=('A documented processing rule can explain the difference, but its intended meaning, earlier information and update timing remain unverified.'
               if outcome=='TRANSFORMATION_LOGIC' else
               'Earlier information, unchecked selections, update timing and intended business rules remain outside what these comparisons establish.')
    return ' '.join((first,compared,ruled_out,remaining,'Recommended action: '+action(outcome)['text']))
