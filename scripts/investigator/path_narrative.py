"""Procedure-owned path terms; narrative cannot reverse a checked boundary."""
from decimal import Decimal,InvalidOperation
from .output_contract import _business_mechanism

LIMITATION='These findings apply only to the recorded scope; unchecked conditions remain unestablished.'


def facts(payload):
    entries=payload.get('evidence',[]);by_id={e['id']:e for e in entries};labels={};result=[]
    def label(identity):
        if identity not in labels:labels[identity]='L'+str(len(labels))
        return labels[identity]
    def quantity(identity):
        entry=by_id.get(identity,{})
        if not entry.get('provenance',{}).get('receipt_seal'):return None
        raw=entry.get('verified_quantity',{}).get('quantity')
        try:
            if not isinstance(raw,str) or len(raw)>100:return None
            value=Decimal(raw)
            if value.is_finite() and abs(value.adjusted())<=100:return format(value,',f')
        except InvalidOperation:pass
        return None
    for entry in entries:
        c=entry.get('result',{})
        if entry.get('tool')!='process' or c.get('comparison_status')!='CROSS_SURFACE_VERIFIED':continue
        upper,lower=c.get('upper_layer'),c.get('lower_layer');refs=c.get('referenced_evidence_ids',[])
        if not upper or not lower or len(refs)!=2:continue
        output_label=label(upper);input_label=label(lower)
        result.append({'comparison_id':entry['id'],'input':{'term':input_label,'layer':lower,'quantity':quantity(refs[1])},
                       'output':{'term':output_label,'layer':upper,'quantity':quantity(refs[0])},
                       'values_equal':c['values_equal'],'direction':'UPSTREAM_INPUT_TO_DOWNSTREAM_OUTPUT'})
    return result


def summary(payload):
    if payload.get('deterministic_process_finding',{}).get('classification')=='REFRESH_LATENCY':
        reason=next((e['result']['reader_timing_unavailable'] for e in payload.get('evidence',[])
                     if 'reader_timing_unavailable' in e.get('result',{})),
                    'Refresh timing was unavailable to the diagnostic identity.')
        return ('Independent reads disagree at the presentation and its unchanged declared source. '
                'This establishes a serving-state freshness discrepancy, not a measured delay. '
                +reason+' '+
                'Snapshot alignment is reported separately; elapsed delay and which state is newer are unestablished.')
    count=len(facts(payload))
    mechanism=_business_mechanism(payload.get('evidence',[]))
    return (f'The procedure recorded {count} independently compared boundaries. '
            'The fixed boundary account states input-to-output ordering and observed quantities. '
            +(mechanism+' ' if mechanism else '')+
            'A compatible definition does not prove actual repeated matches, source correctness or business intent.')


def render(payload):
    rows=facts(payload)
    if not rows:return 'No independently compared boundary ordering was established.'
    text=[];labels={}
    for i,row in enumerate(rows,1):
        lower,upper=row['input'],row['output']
        for node in (upper,lower):labels[node['term']]=node['layer']
        quantities=(f" Observed input {lower['quantity']}; observed output {upper['quantity']}."
                    if lower['quantity'] is not None and upper['quantity'] is not None else '')
        text.append(f"Boundary B{i}: {lower['term']} (upstream input) -> {upper['term']} (downstream output)."+
                    quantities+(' Values agree.' if row['values_equal'] else ' Values differ.'))
    text.extend(term+' = '+identity for term,identity in labels.items())
    return '\n'.join(text)
