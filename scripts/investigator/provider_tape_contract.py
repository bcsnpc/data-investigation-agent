"""Canonical JSON provider matching; original sealed bytes are never rewritten."""
import base64
import json

KINDS=frozenset(('PROVIDER_REQUEST','PROVIDER_RESPONSE'))

def parse(body):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate provider JSON key')
            result[key]=value
        return result
    def invalid(value):raise ValueError('Non-finite provider JSON number')
    return json.loads(body,object_pairs_hook=pairs,parse_constant=invalid)

def encode(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')

def canonical(kind,body):
    value=parse(body)
    if kind=='PROVIDER_REQUEST' and isinstance(value,dict) and isinstance(value.get('input'),str):
        # This transport serializes its structured planner payload into input.
        # Ordinary prose/query strings inside that payload remain literal content.
        value['input']=encode(parse(value['input'])).decode('utf8')
    elif kind=='PROVIDER_RESPONSE' and isinstance(value,dict) and 'body' in value:
        # Journal envelope: the HTTP response JSON is carried as base64 bytes.
        response=parse(base64.b64decode(value['body'],validate=True))
        if isinstance(response,dict):
            for item in response.get('output',[]):
                if isinstance(item,dict) and item.get('type')=='function_call' and isinstance(item.get('arguments'),str):
                    item['arguments']=encode(parse(item['arguments'])).decode('utf8')
        value['body']=base64.b64encode(encode(response)).decode('ascii')
    return encode(value)

def equal(kind,left,right):return canonical(kind,left)==canonical(kind,right)
