"""Fixed INFO metadata over the newer ExecuteDaxQueries Arrow API.

This is deliberately not ExecuteQueries, not an arbitrary DAX endpoint, and
not an automatic XMLA fallback. The caller owns each physical reservation.
"""
import base64
import hashlib
import io
import json
from uuid import UUID
from urllib.error import HTTPError
from urllib.request import Request, build_opener

from metadata_auth import NoRedirect
from .graph_dependencies import query, validate_query

MAX_BODY = 8 * 1024 * 1024
SCOPE = 'https://analysis.windows.net/powerbi/api/.default'


def arrow_rows(raw, *, row_limit):
    """Decode all IPC streams, including HTTP-200 error streams; never truncate."""
    import pyarrow as pa
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BODY:
        raise ValueError('GRAPH_ARROW_BODY_BOUND')
    if type(row_limit) is not int or not 1 <= row_limit <= 1001:
        raise ValueError('GRAPH_ARROW_ROW_BOUND')
    stream = io.BytesIO(raw); results = []; errors = []; decoded_bytes = 0
    while stream.tell() < len(raw):
        before = stream.tell()
        reader = pa.ipc.open_stream(stream)
        metadata = {k.decode('utf8'): v.decode('utf8') for k,v in (reader.schema.metadata or {}).items()}
        rows = []
        for batch in reader:
            decoded_bytes += batch.nbytes
            if len(rows) + batch.num_rows > row_limit or decoded_bytes > MAX_BODY:
                raise ValueError('GRAPH_ARROW_DECODED_BOUND')
            rows.extend(batch.to_pylist())
        if stream.tell() <= before: raise ValueError('GRAPH_ARROW_NO_PROGRESS')
        if metadata.get('IsError','').lower() == 'true':
            errors.append({'metadata': metadata, 'rows': rows})
        else: results.append(rows)
        if len(results) + len(errors) > 4: raise ValueError('GRAPH_ARROW_STREAM_BOUND')
    if errors: return {'status': 'FAILED', 'rows': [], 'error': {'arrow_errors': errors}}
    # Our fixed compiler emits exactly one EVALUATE. Extra rowsets cannot be
    # silently discarded or combined into a purported complete dependency set.
    if len(results) != 1: raise ValueError('GRAPH_ARROW_SINGLE_RESULT_REQUIRED')
    normalized=[]
    for row in results[0]:
        value={}
        for key,item in row.items():
            name=key[1:-1] if key.startswith('[') and key.endswith(']') else key
            if name in value:raise ValueError('GRAPH_ARROW_DUPLICATE_FIELD')
            value[name]=item
        normalized.append(value)
    return {'status': 'SUCCEEDED', 'rows': normalized, 'error': None}


class DaxMetadataHttp:
    def __init__(self, tokens, identity, retain, *, opener=None):
        self.tokens, self.identity, self.retain = tokens, identity, retain
        self.opener = opener or build_opener(NoRedirect())

    def __call__(self, descriptor):
        from .scanner_identity import Tokens, require_job
        if not isinstance(self.tokens,Tokens): raise PermissionError('GRAPH_SCANNER_CREDENTIAL_REQUIRED')
        if descriptor['route'] != 'EXECUTE_DAX_QUERIES': raise ValueError('GRAPH_DAX_ROUTE_REQUIRED')
        target = descriptor['target']
        if set(target) != {'workspace','model'}: raise ValueError('GRAPH_DAX_TARGET')
        UUID(target['workspace']); model = str(UUID(target['model']))
        require_job(self.tokens.declaration,[target['workspace']])
        statement = descriptor['query']; validate_query(statement)
        if statement != query(descriptor['kind'], descriptor['row_cap']): raise ValueError('GRAPH_DAX_QUERY_DIFFERS')
        timeout = descriptor['timeout']
        if type(timeout) is not int or not 1 <= timeout <= 120: raise ValueError('GRAPH_DAX_TIMEOUT')
        body = {'query':statement, 'queryTimeout':timeout, 'resultSetRowCountLimit':descriptor['row_cap']+1}
        url = 'https://api.powerbi.com/v1.0/myorg/datasets/'+model+'/executeDaxQueries'
        request = Request(url, data=json.dumps(body,sort_keys=True,separators=(',',':')).encode(), method='POST',
            headers={'Content-Type':'application/json',
                     'Accept':'application/vnd.apache.arrow.stream'})
        from investigator.live_gateway import authorize_http, open_http
        authorize_http(request,identity=self.identity)
        request.add_header('Authorization','Bearer '+self.tokens.get_token(SCOPE))
        try:
            with open_http(self.opener,request,timeout=timeout,identity=self.identity) as response:
                status, headers, raw = response.status, dict(response.headers), response.read(MAX_BODY+1)
        except HTTPError as exc:
            status, headers, raw = exc.code, dict(exc.headers), exc.read(MAX_BODY+1)
        if len(raw)>MAX_BODY: raise ValueError('GRAPH_DAX_RESPONSE_BOUND')
        envelope={'request':{'url':url,'method':'POST','body':body,'target':target},
                  'status':status,'content_type':next((v for k,v in headers.items() if k.lower()=='content-type'),''),
                  'body_base64':base64.b64encode(raw).decode(),'body_sha256':hashlib.sha256(raw).hexdigest()}
        receipt = self.retain(envelope)
        if not isinstance(receipt,str) or not receipt: raise ValueError('GRAPH_DAX_RECEIPT_REQUIRED')
        if status != 200:
            result={'status':'PERMISSION_DENIED' if status in (401,403) else 'FAILED','rows':[],
                    'error':{'http_status':status,'body_sha256':envelope['body_sha256']}}
        elif not envelope['content_type'].split(';')[0].strip().lower() == 'application/vnd.apache.arrow.stream':
            result={'status':'FAILED','rows':[],'error':{'code':'GRAPH_DAX_CONTENT_TYPE','body_sha256':envelope['body_sha256']}}
        else:
            try: result=arrow_rows(raw,row_limit=descriptor['row_cap']+1)
            except Exception as exc:
                result={'status':'FAILED','rows':[],'error':{'code':'GRAPH_DAX_ARROW_INVALID','type':type(exc).__name__,
                        'body_sha256':envelope['body_sha256']}}
        return {**result,'receipt_id':receipt}
