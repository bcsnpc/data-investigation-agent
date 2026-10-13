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
    d=declaration(permissions);identity.require_job(d['authentication'],d['workspaces']);return d


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
        match=re.fullmatch(r'/v1.0/myorg/groups/([0-9a-f-]{36})/datasets/([0-9a-f-]{36})/executeQueries',path)
        if parsed.netloc!='api.powerbi.com'or not match or method!='POST'or query:
            raise ValueError('SCANNER_DAX_ENDPOINT_REFUSED')
        if {'workspace':match[1],'model':match[2]}not in d['models']:raise ValueError('SCANNER_MODEL_SCOPE_REQUIRED')
        value=_body(body)
        if (not isinstance(value,dict)or set(value)-{'queries','serializerSettings'}or len(value.get('queries',[]))!=1
                or set(value['queries'][0])!={'query'}or value.get('serializerSettings',{'includeNulls':True})!={'includeNulls':True}):
            raise ValueError('SCANNER_DAX_BODY_REFUSED')
        from .graph_dependencies import validate_query
        validate_query(value['queries'][0]['query']);return
    if purpose!='scanner_metadata':raise ValueError('SCANNER_PURPOSE_FORBIDDEN')
    if parsed.netloc=='api.fabric.microsoft.com':
        # Poll URLs are exact grants supplied by the operator, never a host-wide
        # operation wildcard. Definition POST has no payload or mutation flags.
        poll=re.fullmatch(r'/v1/operations/[0-9a-f-]{36}(?:/result)?',path)
        if poll and method=='GET'and not query and not body:return
        match=re.fullmatch(r'/v1/workspaces/([0-9a-f-]{36})/(items|reports|semanticModels|notebooks|dataPipelines|copyJobs|lakehouses|warehouses|sqlEndpoints)(?:/([0-9a-f-]{36})(?:/(getDefinition|tables))?)?',path)
        if not match or match[1]not in d['workspaces']:raise ValueError('SCANNER_METADATA_ENDPOINT_REFUSED')
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
        elif method!='GET'or body or query:raise ValueError('SCANNER_ADMIN_RESULT_REFUSED')
        return
    raise ValueError('SCANNER_HOST_REFUSED')
