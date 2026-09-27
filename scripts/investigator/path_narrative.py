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
    """Default commentary for offline callers; path facts are rendered separately."""
    if payload.get('deterministic_process_finding',{}).get('classification')=='REFRESH_LATENCY':
        return 'Refresh timing was unavailable to the diagnostic reader; elapsed delay and which state is newer remain unestablished.'
    mechanism=_business_mechanism(payload.get('evidence',[]))
    return ((mechanism+' ' if mechanism else '')+
            'A compatible definition does not prove actual repeated matches, source correctness or business intent.')


def _casefold(term):
    return ''.join('['+c.lower()+c.upper()+']' if c.isalpha() else r'\s+' if c==' ' else c for c in term)


COMMENTARY_FORBIDDEN=(r'\d|\b(?:'+'|'.join(_casefold(w) for w in
    ('upstream','downstream','input','output','feeds','fixed boundary account',
     'fixed account','boundary account','path facts','rendered facts','rendered spine',
     'fixed spine','account states','account shows','account describes','see the table'))+r')\b')


def commentary_schema(bound):
    from . import evidence_prose
    value=evidence_prose.schema(bound)
    value['pattern']='^(?![\\s\\S]*(?:'+COMMENTARY_FORBIDDEN+'))'+value['pattern'][1:]
    return value


def validate_commentary(text):
    import re
    if re.search(COMMENTARY_FORBIDDEN,text):
        raise ValueError('Narrative redeclares path facts or refers to the account instead of explaining the mechanism')


def render(payload):
    rows=facts(payload)
    if not rows:return 'No independently compared boundary ordering was established.'
    measure=payload.get('scope',{}).get('measure_name') or payload.get('scope',{}).get('measure_id') or 'unnamed measure'
    text=[f'Measure: {measure}.'];labels={}
    for i,row in enumerate(rows,1):
        lower,upper=row['input'],row['output']
        for node in (upper,lower):labels[node['term']]=node['layer']
        quantities=(f" Observed input {lower['quantity']}; observed output {upper['quantity']}."
                    if lower['quantity'] is not None and upper['quantity'] is not None else '')
        text.append(f"Boundary B{i} {'agrees' if row['values_equal'] else 'diverges'}: {lower['term']} ({lower['layer']}, upstream input) -> {upper['term']} ({upper['layer']}, downstream output)."+
                    quantities+(' Values agree.' if row['values_equal'] else ' Values differ.'))
    text.extend(term+' = '+identity for term,identity in labels.items())
    return '\n'.join(text)
