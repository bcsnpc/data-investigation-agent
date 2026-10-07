"""Complete bounded key sets, recomputed from original typed probe values."""
from decimal import Decimal
import json,hashlib


def quantities(rows, normalization, completeness):
    if completeness!='COMPLETE_RESPONSE' or not isinstance(rows,list):
        raise ValueError('Complete KEY universe unavailable')
    if (set(normalization)!={'encoding','case_fold','trim'} or normalization['encoding']!='typed-json-utf8'
            or any(type(normalization[k]) is not bool for k in ('case_fold','trim'))):
        raise ValueError('Explicit KEY normalization required')
    values=[]
    for row in rows:
        if set(row)!={'key_value'}:raise ValueError('Original KEY projection differs')
        cell=row['key_value'];value=cell.get('value') if isinstance(cell,dict) else cell
        if isinstance(cell,dict) and cell.get('type')=='decimal':
            number=Decimal(value)
            if not number.is_finite() or number!=number.to_integral_value():raise ValueError('KEY requires exact integral decimal')
            value=int(number)
        if type(value) not in (str,int,bool,type(None)):raise ValueError('Unsupported typed KEY value')
        if isinstance(value,str):
            if normalization['case_fold']:value=value.casefold()
            if normalization['trim']:value=value.rstrip(' ')
        values.append([value])
    def encode(keys):
        distinct=sorted(set(json.dumps(key,ensure_ascii=False,separators=(',',':')).encode('utf8') for key in keys))
        return b''.join(len(v).to_bytes(8,'big')+v for v in distinct)
    from .privacy_identities import digest
    return {'count':len(values),'distinct_count':len(set(json.dumps(v,sort_keys=True) for v in values)),
            'binary_hash':digest(values,encode)}
