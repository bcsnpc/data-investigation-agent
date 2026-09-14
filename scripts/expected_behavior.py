"""A narrow business contract, not a general no-defect classifier."""
from decimal import Decimal,localcontext
from investigation_checks import number


def money(value):
    result=number(str(value) if isinstance(value,Decimal) else value)
    if result<0 or result>=Decimal('1e28') or result.as_tuple().exponent < -4:raise ValueError('Invalid business amount')
    return result


def verify_refunds(payload,context,result):
    if context.get('question')!='why_net_cash_below_captures' or context.get('contract')!='captured-minus-refunds-v1':
        return {'verified':False,'reason':'Unsupported business question or contract'}
    if result['comparison_status']!='MATCH':return {'verified':False,'reason':'Record differences remain'}
    records=context.get('records')
    if not isinstance(records,list):raise ValueError('Business records required')
    observed={(r['order_id'],r['currency']):r for r in payload['rows']};seen=set();totals={}
    with localcontext() as arithmetic:
        arithmetic.prec=100
        for i,row in enumerate(records):
            if set(row)!={'order_id','currency','captured_amount','refunded_amount'}:raise ValueError('Invalid business record')
            key=(row['order_id'],row['currency'])
            if key in seen:raise ValueError('Duplicate business key')
            seen.add(key)
            if key not in observed:return {'verified':False,'reason':'Business evidence scope differs'}
            captured=money(row['captured_amount']);refunded=money(row['refunded_amount'])
            if refunded>captured:return {'verified':False,'reason':'Refund exceeds recorded capture'}
            if captured-refunded!=money(observed[key]['silver_net_cash']):
                return {'verified':False,'reason':'Capture/refund arithmetic does not explain observations'}
            group=totals.setdefault(key[1],{'captured':Decimal(0),'refunded':Decimal(0),'net_cash':Decimal(0),'references':[]})
            group['captured']+=captured;group['refunded']+=refunded;group['net_cash']+=captured-refunded
            group['references'].append('/request/business_context/records/'+str(i))
        if seen!=set(observed):return {'verified':False,'reason':'Business evidence is incomplete'}
        if not any(v['refunded']>0 for v in totals.values()):return {'verified':False,'reason':'No refunds support the proposed explanation'}
        return {'verified':True,'contract':'captured-minus-refunds-v1',
            'scope':'Recorded local Silver/Gold net cash after refunds only; not full-estate health or a period-over-period trend',
            'by_currency':{currency:{k:format(v,'.4f') if isinstance(v,Decimal) else v for k,v in group.items()} for currency,group in totals.items()}}
