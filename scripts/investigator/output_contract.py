"""Closed business composition with evidence-backed labels and outcome actions."""
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
    'ASK_UPSTREAM_OWNER': 'Ask the owner of the unchecked part of the process to investigate the remaining gap.',
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
    """Five sentences from sealed quantities and definition-backed business labels."""
    from decimal import Decimal, InvalidOperation
    outcome=canonical(outcome)
    entries=(payload or {}).get('evidence',[])
    baseline=next((e for e in entries if e.get('test_purpose')=='ESTABLISH_BASELINE'
                   and e.get('provenance',{}).get('receipt_seal')),None)
    def number_from(entry):
        if not (entry or {}).get('provenance',{}).get('receipt_seal'):return None
        raw=entry.get('verified_quantity',{}).get('quantity')
        if isinstance(raw,str) and len(raw)<=100:
            try:
                value=Decimal(raw)
                if value.is_finite() and abs(value.adjusted())<=100:return format(value,',f')
            except InvalidOperation:pass
        return None
    number=number_from(baseline)
    first=('The checked report value was '+number+'.' if number is not None else
           'A single report value could not be established from the available verified evidence.')
    comparisons=[e['result'] for e in entries if e.get('tool')=='process'
                 and e.get('result',{}).get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    immediate=next((c for c in comparisons if baseline and
                    c.get('referenced_evidence_ids',[None])[0]==baseline['id']),None)
    agrees=immediate is not None and immediate['values_equal'] is True
    differs=any(c['values_equal'] is False for c in comparisons)
    divergence=next((c for c in comparisons if c['values_equal'] is False),None)
    by_id={e['id']:e for e in entries}
    lower=(number_from(by_id.get(divergence['referenced_evidence_ids'][1]))
           if divergence and len(divergence.get('referenced_evidence_ids',[]))==2 else None)
    if outcome=='REFRESH_LATENCY' and immediate is not None and number is not None and lower is not None:
        return ' '.join((f'The report showed {number}, while its direct input totaled {lower}.',
            'No processing changes the compared quantity between them, so the report is serving a different data state.',
            'The refresh time was unavailable to the diagnostic account because its read access does not permit refresh history.',
            'The checks do not establish how long the difference has existed, which state is newer, or whether the original entries are correct.',
            'Recommended action: '+action(outcome)['text']))
    if immediate is not None and number is not None and lower is not None:
        terms=_business_terms(entries)
        subject=terms.get('subject',{}).get('text');matched=terms.get('matched',{}).get('text')
        first=(f'The report showed {number}'+(f' for {subject}' if subject else '')+
               (', matching the total used to prepare it.' if agrees else '.'))
        compared=(f'An earlier check of {subject} returned {lower}; the difference appears in the step that matches {subject} with {matched}.'
                  if agrees and subject and matched else
                  f'An earlier check returned {lower}; the difference appears during preparation of the report.' if agrees else
                  f'The total used to prepare the report was {lower}; the difference appears between that total and the displayed number.')
        mechanism=_business_mechanism(entries) if outcome=='TRANSFORMATION_LOGIC' else None
        mechanism=mechanism or 'The checks locate the difference but do not establish a specific explanation for it.'
        remaining=(f'We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how {subject} were first entered.'
                   if subject and mechanism else
                   'The retrieved definition supplies no usable business names for the compared entries; their origin, update timing and intended treatment remain unconfirmed.')
        return ' '.join((first,compared,mechanism,remaining,'Recommended action: '+action(outcome)['text']))
    if agrees:
        compared=('A separate check of the total used to prepare the report agreed'+
                  (', but a comparison further back found a different total.' if differs else '.'))
        ruled_out='This rules out a report-to-input difference within these checks, but does not prove the original records are correct.'
    elif immediate is not None:
        compared='A separate check of the total used to prepare the report found a different total.'
        ruled_out='These checks establish a difference, but do not by themselves establish which total is correct.'
    else:
        compared='The available evidence did not establish a boundary comparison with the total used to prepare the report.'
        ruled_out='A difference between the report and its input therefore remains possible.'
    remaining=('A documented processing rule can explain the difference, but its intended meaning, the original entries and update timing remain unverified.'
               if outcome=='TRANSFORMATION_LOGIC' else
               'The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish.')
    return ' '.join((first,compared,ruled_out,remaining,'Recommended action: '+action(outcome)['text']))


def _business_mechanism(entries):
    """Translate unambiguous declared operations, never names or model prose."""
    for e in entries:
        if 'transformation_definition' not in e.get('process_roles',[]):continue
        result=e.get('result',{});contract=result.get('quantity_contract',{})
        judgment=result.get('judgment',{})
        if judgment.get('judgment')!='EXPLAINS' or contract.get('kind')!='UNCHANGED_ADDITIVE_COLUMN':continue
        operations=contract.get('operations',[])
        kinds={o.get('operation') for o in operations}-{'DERIVED_COLUMN'}
        if kinds=={'JOIN'} and all(o.get('how') in ('left','right','inner','outer','full','cross')
                                  for o in operations if o.get('operation')=='JOIN'):
            terms=_business_terms([e])
            if terms:
                return f"Several matching {terms['matched']['text']} can cause an entry to contribute more than once."
            return 'A matching step can count an entry more than once when it has several matches.'
        # Ambiguous/mixed or unsupported mechanisms are not guessed from prose.
    return None


def _business_terms(entries):
    from .business_vocabulary import validate_terms
    candidates=[]
    for e in entries:
        if 'transformation_definition' not in e.get('process_roles',[]):continue
        result=e.get('result',{});contract=result.get('quantity_contract',{})
        if result.get('judgment',{}).get('judgment')!='EXPLAINS':continue
        operations=contract.get('operations',[])
        if (contract.get('kind')!='UNCHANGED_ADDITIVE_COLUMN' or
            len([o for o in operations if o.get('operation')=='JOIN'])!=1 or
            {o.get('operation') for o in operations}-{'DERIVED_COLUMN'}!={'JOIN'}):continue
        terms=validate_terms(result.get('business_vocabulary',{}),contract)
        if terms:candidates.append(terms)
    return candidates[0] if len(candidates)==1 else {}
