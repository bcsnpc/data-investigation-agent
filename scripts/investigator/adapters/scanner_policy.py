"""Closed scanner endpoint grammar on top of exact operator URL grants."""
import json
import re
from urllib.parse import urlsplit,parse_qs
from uuid import UUID
from . import scanner_identity as identity

PURPOSES=frozenset({'scanner_metadata','scanner_dax','scanner_auth'})


def declaration(permissions):
    d=permissions.get('scanner')
    if not isinstance(d,dict)or set(d)!={'authentication','workspaces','models'}:
        raise ValueError('SCANNER_POLICY_REQUIRED')
    identity.validate(d['authentication'])
    if not isinstance(d['workspaces'],list)or not 1<=len(d['workspaces'])<=3:
        raise ValueError('SCANNER_WORKSPACE_BOUND')
    if any(str(UUID(w))!=w for w in d['workspaces'])or len(set(d['workspaces']))!=len(d['workspaces']):
        raise ValueError('SCANNER_WORKSPACE_IDS_REQUIRED')
    if not isinstance(d['models'],list)or len(d['models'])>100:
        raise ValueError('SCANNER_MODEL_BOUND')
    for model in d['models']:
        if set(model)!={'workspace','model'}or model['workspace']not in d['workspaces']or str(UUID(model['model']))!=model['model']:
            raise ValueError('SCANNER_MODEL_SCOPE_REQUIRED')
    if permissions.get('sql')or permissions.get('platform_databases')or permissions.get('platform_cas'):
        raise ValueError('SCANNER_NONMETADATA_SCOPE_FORBIDDEN')
    if any(g.get('purpose')not in PURPOSES for g in permissions.get('http',[])):
        raise ValueError('SCANNER_ENDPOINT_PURPOSE_FORBIDDEN')
    if any(g.get('operation')!='XMLA_GRAPH_METADATA'or {'workspace':g.get('workspace'),'model':g.get('model')}not in d['models']
           for g in permissions.get('native_controls',[])):
        raise ValueError('SCANNER_NATIVE_SCOPE_FORBIDDEN')
    return d


def authorize_job(permissions):
    d=declaration(permissions);identity.require_job(d['authentication']);return d


def _body(raw):return json.loads(raw)if isinstance(raw,(str,bytes))else raw


def http(permissions,grant,method,url,body):
    d=authorize_job(permissions);purpose=grant['purpose'];parsed=urlsplit(url)
    if '%' in parsed.path or parsed.fragment:raise ValueError('SCANNER_ENCODED_PATH_REFUSED')
    path=parsed.path;query=parse_qs(parsed.query,strict_parsing=True)
    if purpose=='scanner_auth':
        if grant.get('authentication')!=d['authentication']or not identity.validate_exchange(method,url,body,grant):
            raise ValueError('SCANNER_AUTH_EXCHANGE_REFUSED')
        return
    if purpose=='scanner_dax':
        modern=re.fullmatch(r'/v1.0/myorg/datasets/([0-9a-f-]{36})/executeDaxQueries',path)
        if parsed.netloc=='api.powerbi.com'and modern and method=='POST'and not query:
            models=[m for m in d['models']if m['model']==modern[1]]
            if len(models)!=1:raise ValueError('SCANNER_MODEL_SCOPE_REQUIRED')
            identity.require_job(d['authentication'],[models[0]['workspace']])
            value=_body(body)
            if (not isinstance(value,dict)or set(value)!={'query','queryTimeout','resultSetRowCountLimit'}
                    or type(value['queryTimeout'])is not int or not 1<=value['queryTimeout']<=120
                    or type(value['resultSetRowCountLimit'])is not int or not 1<=value['resultSetRowCountLimit']<=1001):
                raise ValueError('SCANNER_DAX_BODY_REFUSED')
            from .graph_dependencies import validate_query
            validate_query(value['query']);return
        match=re.fullmatch(r'/v1.0/myorg/groups/([0-9a-f-]{36})/datasets/([0-9a-f-]{36})/executeQueries',path)
        if parsed.netloc!='api.powerbi.com'or not match or method!='POST'or query:
            raise ValueError('SCANNER_DAX_ENDPOINT_REFUSED')
        if {'workspace':match[1],'model':match[2]}not in d['models']:raise ValueError('SCANNER_MODEL_SCOPE_REQUIRED')
        identity.require_job(d['authentication'],[match[1]])
        value=_body(body)
        if (not isinstance(value,dict)or set(value)-{'queries','serializerSettings'}or len(value.get('queries',[]))!=1
                or set(value['queries'][0])!={'query'}or value.get('serializerSettings',{'includeNulls':True})!={'includeNulls':True}):
            raise ValueError('SCANNER_DAX_BODY_REFUSED')
        from .graph_dependencies import validate_query
        validate_query(value['queries'][0]['query']);return
    if purpose!='scanner_metadata':raise ValueError('SCANNER_PURPOSE_FORBIDDEN')
    if parsed.netloc=='api.fabric.microsoft.com':
        # Poll URLs are exact operator grants or bound from authorized responses,
        # never a host-wide operation wildcard. Definition POST has no payload or mutation flags.
        poll=re.fullmatch(r'/v1/operations/[0-9a-f-]{36}(?:/result)?',path)
        if poll and method=='GET'and not query and not body:return
        match=re.fullmatch(r'/v1/workspaces/([0-9a-f-]{36})/(items|reports|semanticModels|notebooks|dataPipelines|copyJobs|lakehouses|warehouses|sqlEndpoints)(?:/([0-9a-f-]{36})(?:/(getDefinition|tables))?)?',path)
        if not match or match[1]not in d['workspaces']:raise ValueError('SCANNER_METADATA_ENDPOINT_REFUSED')
        identity.require_job(d['authentication'],[match[1]])
        if match[4]=='getDefinition':
            if method!='POST'or body or set(query)-{'format'}or any(v not in ('PBIR','TMDL','TMSL','ipynb')for v in query.get('format',[])):
                raise ValueError('SCANNER_DEFINITION_REQUEST_REFUSED')
        elif method!='GET'or body or set(query)-{'continuationToken'}:raise ValueError('SCANNER_METADATA_READ_REQUIRED')
        return
    if parsed.netloc=='api.powerbi.com':
        match=re.fullmatch(r'/v1.0/myorg/admin/workspaces/(getInfo|scanStatus/[0-9a-f-]{36}|scanResult/[0-9a-f-]{36})',path)
        if not match:raise ValueError('SCANNER_ADMIN_ENDPOINT_REFUSED')
        if match[1]=='getInfo':
            value=_body(body)
            if (method!='POST'or not isinstance(value,dict)or set(value)!={'workspaces'}or not isinstance(value['workspaces'],list)
                    or not value['workspaces']or not set(value['workspaces'])<=set(d['workspaces'])
                    or set(query)-{'lineage','datasourceDetails','datasetSchema','datasetExpressions'}
                    or any(v!=['true']for v in query.values())):raise ValueError('SCANNER_ADMIN_SCAN_SCOPE_REFUSED')
            identity.require_job(d['authentication'],value['workspaces'])
        elif method!='GET'or body or query:raise ValueError('SCANNER_ADMIN_RESULT_REFUSED')
        return
    raise ValueError('SCANNER_HOST_REFUSED')


def bind_response(permissions,channel,grant,method,url,request_body,response):
    """Bind exact follow-ups from an authorized native response, never a ticket."""
    http(permissions,grant,method,url,request_body)
    if grant['purpose']!='scanner_metadata':return
    from urllib.parse import urljoin,quote
    parsed=urlsplit(url);body=response.get('text',{});urls=[]
    if response.get('status_code')==202 and parsed.path.endswith('/getDefinition'):
        headers={k.lower():v for k,v in response.get('headers',{}).items()}
        operation=str(UUID(headers['x-ms-operation-id']))
        urls=[f'https://api.fabric.microsoft.com/v1/operations/{operation}',f'https://api.fabric.microsoft.com/v1/operations/{operation}/result']
    elif parsed.path.endswith('/admin/workspaces/getInfo') and response.get('status_code') in (200,202):
        operation=str(UUID(body['id']))
        urls=[f'https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanStatus/{operation}',
              f'https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanResult/{operation}']
    elif method=='GET' and '/workspaces/'in parsed.path and isinstance(body,dict):
        follow=body.get('continuationUri')or body.get('@odata.nextLink')
        if not follow and body.get('continuationToken'):
            follow=parsed._replace(query='continuationToken='+quote(body['continuationToken'],safe='')).geturl()
        if follow:
            if not isinstance(follow,str)or len(follow)>8192:raise ValueError('SCANNER_CONTINUATION_BOUND')
            follow=urljoin(url,follow);next_url=urlsplit(follow)
            if (next_url.scheme,next_url.netloc,next_url.path)!=(parsed.scheme,parsed.netloc,parsed.path)or next_url.fragment:
                raise ValueError('SCANNER_CONTINUATION_SCOPE_REFUSED')
            if set(parse_qs(next_url.query,strict_parsing=True))!={'continuationToken'}:raise ValueError('SCANNER_CONTINUATION_QUERY_REFUSED')
            urls=[follow]
    active=identity._JOB.get();bound=active[3]
    if len(bound)+len(urls)>1000:raise ValueError('SCANNER_FOLLOWUP_BOUND')
    for follow in urls:
        candidate={'method':'GET','url':follow,'purpose':'scanner_metadata'}
        http(permissions,candidate,'GET',follow,None)
        bound[(channel,'GET',follow)]=candidate


def followup(channel,method,url):
    active=identity._JOB.get()
    return active[3].get((channel,method,url))if active is not None else None
