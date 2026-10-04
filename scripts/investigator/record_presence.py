"""Expected-record presence is a separate receipt-backed fact, never a quantity."""
from decimal import Decimal,InvalidOperation


def address(layer,requested):return {'kind':'RECORD_PRESENCE','layer':layer,'records':requested}


def validate_address(value):
    from .reported_figure import span
    from .numeral_roles import LIMIT
    if (not isinstance(value,dict) or set(value)!={'kind','layer','records'}
            or value['kind']!='RECORD_PRESENCE' or not isinstance(value['layer'],str) or not value['layer']
            or not isinstance(value['records'],list) or not 1<=len(value['records'])<=LIMIT):
        raise ValueError('Expected-record read address is incomplete')
    for record in value['records']:
        if not isinstance(record,dict) or set(record)!={'value','source'} or not isinstance(record['value'],str):
            raise ValueError('Expected-record read address lacks quoted identity')
        span(record['source'])
    return value


def counts(rows,requested):
    if not isinstance(rows,list) or len(rows)!=1:raise ValueError('Presence requires one complete count row')
    row=rows[0];result={}
    for i,record in enumerate(requested):
        name='presence_'+str(i)
        matches=[row[k] for k in (name,'['+name+']') if k in row]
        if len(matches)!=1:raise ValueError('Presence count is absent or ambiguous')
        cell=matches[0]
        try:
            if not isinstance(cell,dict) or cell.get('value') is None:raise ValueError('Presence count unavailable')
            value=Decimal(str(cell['value']))
            if not value.is_finite() or value<0 or value!=value.to_integral_value():raise ValueError('Presence count is not a nonnegative integer')
        except InvalidOperation as exc:raise ValueError('Presence count invalid') from exc
        result[record['value']]=value>0
    return result


def validate(observation):
    fact=observation['record_presence'];attestation=observation.get('surface_attestation',{})
    expected_address=address(fact['layer'],fact['requested'])
    validate_address(expected_address)
    if (observation.get('status')!='COMPLETED' or observation.get('completeness')!='COMPLETE_RESPONSE'
            or attestation.get('consistency')!='MATCHED' or attestation.get('missing_required_fields')
            or observation.get('surface_report_binding')!='VALUE_QUERY'
            or observation.get('read_address')!=expected_address
            or fact['presence']!=counts(observation.get('values'),fact['requested'])):
        raise ValueError('Expected-record presence lacks its original completed attested counts')
    return fact


def proof(requested,layers,observations):
    if not requested:return True
    facts=[]
    for layer in layers:
        matches=[o for o in observations if o.get('record_presence',{}).get('layer')==layer['id']]
        if len(matches)!=1:return False
        try:fact=validate(matches[0])
        except (ValueError,KeyError,TypeError):return False
        if fact['requested']!=requested:return False
        facts.append(fact['presence'])
    return bool(facts) and all(fact==facts[-1] for fact in facts)


def render(observations,labels,business=False,layers=()):
    facts=[validate(o) for o in observations if o.get('record_presence')]
    if not facts:return None
    if business:
        states=[list(f['presence'].values()) for f in facts]
        if all(len(s)==1 for s in states) and all(s==states[0] for s in states):
            status='present' if states[0][0] else 'absent'
            names=[labels.get(f['layer'],{}).get('business_name','declared layer') for f in facts]
            joined=', '.join(names[:-1])+' and '+names[-1] if len(names)>1 else names[0]
            return 'The record you named was '+status+' at every checked layer: '+joined+'.'
    lines=[]
    for fact in facts:
        role=labels.get(fact['layer'],{})
        label=role.get('business_name','declared layer')
        if not business:
            index=next((i for i,l in enumerate(layers) if l['id']==fact['layer']),None)
            label=('L'+str(index) if index is not None else 'unlabelled layer')+' ('+role.get('role','UNDECLARED')+', '+label+')'
        states=list(fact['presence'].values())
        text=('present' if all(states) else 'absent' if not any(states) else 'partly present')
        lines.append(('the record you named' if len(states)==1 else 'the records you named')+' '+
                     ('was ' if len(states)==1 else 'were ')+text+' in '+label)
    return 'Presence checks: '+ '; '.join(lines)+'.'
