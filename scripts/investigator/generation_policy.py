"""Operator-owned bounded provider settings; never inferred from ticket content."""

MAX_OUTPUT_TOKENS=16000


def validate(value=None):
    value={} if value is None else value
    if not isinstance(value,dict) or set(value)-{'timeout_seconds','max_output_tokens','reasoning_effort','max_payload_characters'}:
        raise ValueError('Unknown generation settings')
    result={'timeout_seconds':45,'max_output_tokens':1500,'max_payload_characters':32000,**value}
    for name,lower,upper in [('timeout_seconds',10,120),('max_output_tokens',500,MAX_OUTPUT_TOKENS),('max_payload_characters',8000,128000)]:
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
    result={'error_type':classes[0],'cause_types':classes[1:]}
    if isinstance(error,ProviderResponseError):result['response_failure']=error.code
    return result


class ProviderResponseError(ValueError):
    """Allowlisted failure category and numeric usage, never response content."""
    CODES={'OUTPUT_TOKEN_LIMIT','CONTENT_FILTER','INCOMPLETE','REFUSAL',
           'RESPONSE_NOT_COMPLETED','DECISION_CALL_SHAPE','INVALID_JSON','DECISION_DECODE'}

    def __init__(self,code,usage=None):
        if code not in self.CODES:raise ValueError('Unknown response failure category')
        super().__init__(code)
        self.code=code
        self.usage={k:v for k,v in (usage if isinstance(usage,dict) else {}).items()
                    if k in ('input_tokens','output_tokens','total_tokens') and type(v) is int and v>=0} or None


def failure_usage(error):
    return error.usage if isinstance(error,ProviderResponseError) else None
