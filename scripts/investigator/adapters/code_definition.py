"""Thin definition transport: code identity only, no investigation transport."""
import base64
import json
import time
import re
from urllib.parse import urlsplit
from ..code_sources import MAX_BYTES, relative_path, validate_source
from ..process_tape import bounded_call

def fetch(source,path,meter,request,*,wait=time.sleep):
    validate_source(source)
    if source['kind']!='PLATFORM_ITEM_API':raise ValueError('Definition API source kind differs')
    parts=relative_path(path).split('/',1)
    if len(parts)!=2 or parts[0] not in source['item_ids']:
        raise ValueError('Code item/path is outside declared source')
    item,filename=parts
    endpoint=f"workspaces/{source['workspace']}/items/{item}/getDefinition"
    def call(method,endpoint):
        descriptor={'method':method,'endpoint':endpoint,'identity':source['identity']}
        value=meter(lambda:bounded_call('code_definition_http',descriptor,lambda:request(method,endpoint)))
        if not isinstance(value,dict) or set(value)!={'status','headers','body'}:
            raise ValueError('Definition HTTP response shape differs')
        if value['status'] not in (200,202):
            raise RuntimeError('Definition HTTP '+str(value['status'])+': '+json.dumps(value['body'],sort_keys=True))
        return value
    response=call('POST',endpoint)
    for _ in range(4):
        if response['status']==200:break
        headers={k.lower():v for k,v in response['headers'].items()}
        location=urlsplit(headers.get('location',''))
        operation=headers.get('x-ms-operation-id')
        if operation is None and location.scheme=='https' and location.netloc.endswith('.analysis.windows.net'):
            operation=location.path.removeprefix('/v1/operations/')
        if operation is not None:
            if not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}',operation):
                raise ValueError('Definition operation identity is invalid')
            # Follow the operation ID on the documented public API; never send
            # the credential to a response-supplied regional host.
            location=urlsplit('https://api.fabric.microsoft.com/v1/operations/'+operation)
        if location.scheme!='https' or location.netloc!='api.fabric.microsoft.com' or not location.path.startswith('/v1/operations/') or location.query or location.fragment:
            raise ValueError('Definition polling location outside declared API')
        delay=float(headers.get('retry-after',1))
        if not 0<=delay<=60:raise ValueError('Definition polling wait exceeds bound')
        # Wait is a control, never another diagnostic read or deadline extension.
        from ..process_tape import ACTIVE
        if not (ACTIVE.get() and ACTIVE.get().replaying):wait(delay)
        status=call('GET',location.path.removeprefix('/v1/'))
        if status['status']==202:response=status;continue
        if 'definition' in status['body']:response=status;break
        state=status['body'].get('status')
        if state=='Succeeded':
            response=call('GET',location.path.removeprefix('/v1/')+'/result');break
        if state in ('Failed','Cancelled'):raise RuntimeError('Definition operation '+state+': '+json.dumps(status['body'],sort_keys=True))
    if response['status']!=200 or 'definition' not in response['body']:
        raise RuntimeError('Definition operation did not complete within bounded polling')
    return decode(source,path,response['body'])

def decode(source,path,body):
    """Decode a served definition, including a retained operation's result."""
    validate_source(source)
    parts=relative_path(path).split('/',1)
    if source['kind']!='PLATFORM_ITEM_API' or len(parts)!=2 or parts[0] not in source['item_ids']:
        raise ValueError('Code item/path is outside declared source')
    item,filename=parts
    declared=body['definition']['parts']
    if not isinstance(declared,list) or len(declared)>512:raise ValueError('Definition part count exceeds bound')
    decoded={}
    for part in declared:
        name=relative_path(part['path'])
        if name in decoded or part['payloadType']!='InlineBase64':raise ValueError('Duplicate or unsupported definition part')
        raw=base64.b64decode(part['payload'],validate=True)
        if len(raw)>MAX_BYTES:raise ValueError('Definition part exceeds bound')
        decoded[name]=raw
    if sum(map(len,decoded.values()))>MAX_BYTES:raise ValueError('Definition exceeds code bound')
    if filename not in decoded:raise ValueError('Declared code part absent: '+filename)
    logical=None
    if '.platform' in decoded:
        platform=json.loads(decoded['.platform'])
        logical=platform.get('config',{}).get('logicalId')
    return {'content':decoded[filename].hex(),'item_identity':{'item_id':item,'logical_id':logical},
            'locator':f"{source['workspace']}/{item}/{filename}"}
