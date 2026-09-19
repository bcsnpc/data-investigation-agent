"""Operator-owned bounded provider settings; never inferred from ticket content."""


def validate(value=None):
    value={} if value is None else value
    if not isinstance(value,dict) or set(value)-{'timeout_seconds','max_output_tokens','reasoning_effort','max_payload_characters'}:
        raise ValueError('Unknown generation settings')
    result={'timeout_seconds':45,'max_output_tokens':1500,'max_payload_characters':32000,**value}
    for name,lower,upper in [('timeout_seconds',10,120),('max_output_tokens',500,8000),('max_payload_characters',8000,64000)]:
        if type(result[name]) is not int or not lower<=result[name]<=upper:
            raise ValueError('Invalid generation limit: '+name)
    if 'reasoning_effort' in result and result['reasoning_effort'] not in ('none','low','medium','high'):
        raise ValueError('Invalid reasoning effort')
    return result


def error_summary(error):
    """Exception classes only: provider messages can contain credentials or payloads."""
    import re
    classes=[];seen=set();current=error
    while current is not None and id(current) not in seen and len(classes)<4:
        seen.add(id(current));name=type(current).__name__
        classes.append(name if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]{0,63}',name) else 'UnknownError')
        current=current.__cause__
    return {'error_type':classes[0],'cause_types':classes[1:]}
