"""Deny-by-default live I/O authority. Tickets/model output never supply this policy.

The operator supplies DIA_GATEWAY_POLICY (a local JSON file or mounted secret-free
configuration) and explicit identity names per transport. The gateway does not
mint credentials. Existing authenticators still establish the actual principal.
Rejected attempts log hashes, never SQL, ticket text, URLs with secrets or tokens.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import hashlib
import json
from .adapters.platform_credentials import FORBIDDEN_HTTP_SEGMENTS
import logging
import os
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

LOG = logging.getLogger('investigator.live_gateway')
ACTIVE = ContextVar('live_gateway', default=None)
POLICY_ENV = 'DIA_GATEWAY_POLICY'
KILL_ENV = 'DIA_LIVE_ACCESS_DISABLED'


class GatewayDenied(PermissionError):
    """An admission refusal, never an estate finding."""


def _deny(reason, *, identity='', operation='', target=''):
    entry={'event':'LIVE_ACCESS_DENIED', 'reason':reason, 'identity':identity,
        'operation':operation, 'target_sha256':hashlib.sha256(str(target).encode()).hexdigest()}
    LOG.warning(json.dumps(entry,sort_keys=True))
    # Optional deployment-owned durable sink. It is never a request field. A
    # failed audit write still refuses access; it never falls back to allow.
    audit=os.environ.get('DIA_GATEWAY_AUDIT_FILE') or str(Path(__file__).resolve().parents[2]/'.local/gateway-denials.jsonl')
    if audit:
        from datetime import datetime,timezone
        entry['recorded_at']=datetime.now(timezone.utc).isoformat()
        try:
            Path(audit).parent.mkdir(parents=True,exist_ok=True)
            with open(audit,'a',encoding='utf-8') as stream:
                stream.write(json.dumps(entry,sort_keys=True)+'\n')
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            LOG.error('GATEWAY_AUDIT_WRITE_FAILED')
    raise GatewayDenied(reason)


def _network_unlocked():
    """Budget admission commits before an external request starts."""
    from .shared_state import TRANSACTION_ACTIVE
    from .shared_writer_lease import LEASE_ENV
    if TRANSACTION_ACTIVE.get():
        _deny('NETWORK_DURING_SHARED_STATE_TRANSACTION')
    if os.environ.get(LEASE_ENV):
        _deny('NETWORK_DURING_EXCLUSIVE_WRITER_LEASE')


def _url(value):
    if not isinstance(value,str):_deny('INVALID_ENDPOINT')
    try:
        parsed=urlsplit(value)
        port=parsed.port
    except ValueError:_deny('INVALID_ENDPOINT',target=value)
    if (parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.fragment or port not in (None,443) or '\\' in value
            or any(c.isspace() for c in value)):
        _deny('INVALID_ENDPOINT',target=value)
    decoded=unquote(parsed.path)
    if '%' in decoded or any(p in ('.','..') for p in decoded.split('/')):
        _deny('ENCODED_OR_TRAVERSING_ENDPOINT',target=value)
    return value


def _object(value):
    from sqlglot import exp, parse_one
    try:
        tree=parse_one('SELECT 1 FROM '+value,read='tsql')
        table=tree.args['from_'].this
        if (not isinstance(table,exp.Table) or table.catalog or table.args.get('alias')
                or tree.args.get('where') or len(list(tree.find_all(exp.Table)))!=1
                or table.name.startswith(('#','@'))):raise ValueError()
        return (table.db.casefold(),table.name.casefold())
    except Exception:
        _deny('INVALID_OBJECT_ALLOWLIST')


@dataclass(frozen=True)
class Gateway:
    """Policy is trusted operator configuration, never an operation's request."""
    policy: dict

    def graph_objects(self,estate,object_ids,*,identity):
        """Read-only graph authority is an exact caller-independent object slice."""
        scope=self.policy.get('identities',{}).get(identity,{}).get('graph',{})
        if not isinstance(scope,dict):_deny('GRAPH_SCOPE_REQUIRED',identity=identity,operation='graph',target=estate)
        allowed=scope.get(estate)
        if (not isinstance(allowed,list) or not allowed or len(allowed)>1000
                or any(not isinstance(item,str) or not item or item=='*' for item in allowed)):
            _deny('GRAPH_SCOPE_REQUIRED',identity=identity,operation='graph',target=estate)
        if not isinstance(object_ids,(list,set,tuple)) or not object_ids or len(object_ids)>1000:
            _deny('GRAPH_SLICE_BOUND',identity=identity,operation='graph',target=estate)
        if not set(object_ids)<=set(allowed):
            _deny('GRAPH_OBJECT_NOT_ALLOWED',identity=identity,operation='graph',target=estate)
        return tuple(sorted(set(object_ids)))

    def __post_init__(self):
        # Snapshot the source: a caller cannot widen authority after construction.
        object.__setattr__(self,'policy',json.loads(json.dumps(self.policy)))
        if (self.policy.get('version')!=1 or type(self.policy.get('live_enabled')) is not bool
                or not isinstance(self.policy.get('identities'),dict)):
            _deny('INVALID_GATEWAY_POLICY')
        for identity,permissions in self.policy['identities'].items():
            if not isinstance(identity,str) or not identity or not isinstance(permissions,dict):
                _deny('INVALID_GATEWAY_IDENTITY')
            if permissions.get('role')=='scanner':
                from .adapters.scanner_policy import declaration
                try:declaration(permissions)
                except Exception:_deny('INVALID_SCANNER_POLICY',identity=identity)
            if permissions.get('enrichment_batches'):
                from .adapters.enrichment_anthropic import declaration
                if permissions.get('role')!='enrichment':_deny('ENRICHMENT_IDENTITY_REQUIRED')
                try:declaration(permissions['enrichment_batches'])
                except Exception:_deny('INVALID_ENRICHMENT_PROVIDER_POLICY')
            for endpoint in permissions.get('http',[]):
                _url(endpoint['url'])
                if endpoint.get('method') not in ('GET','HEAD','POST','PUT'):
                    _deny('MUTATING_METHOD_IN_POLICY')
                if endpoint.get('purpose') not in ('metadata','dax','model','blob_read','kql','platform_blob','auth_refresh','auth_federation','scanner_metadata','scanner_dax','scanner_auth'):
                    _deny('INVALID_ENDPOINT_PURPOSE')
                if endpoint.get('purpose','').startswith('scanner_')and permissions.get('role')!='scanner':
                    _deny('SCANNER_IDENTITY_REQUIRED',identity=identity)
                if endpoint['method']=='PUT' and endpoint['purpose']!='platform_blob':
                    _deny('ESTATE_WRITE_METHOD_IN_POLICY')
                if endpoint['purpose']=='platform_blob' and permissions.get('role')!='platform':
                    _deny('PLATFORM_IDENTITY_REQUIRED')
            if permissions.get('role')=='platform' and (permissions.get('sql') or
                    any(item['purpose']!='platform_blob' for item in permissions.get('http',[]))):
                _deny('PLATFORM_AND_ESTATE_IDENTITY_MIXED')
            if permissions.get('platform_databases') and permissions.get('role')!='platform':
                _deny('PLATFORM_IDENTITY_REQUIRED')
            if permissions.get('platform_cas'):
                from .adapters.platform_cas import declaration
                if permissions.get('role')!='platform':_deny('PLATFORM_IDENTITY_REQUIRED')
                for item in permissions['platform_cas']:declaration(item)
            if permissions.get('runner_captures'):
                from .adapters.runner_blobs import declaration
                if permissions.get('role')!='platform':_deny('PLATFORM_IDENTITY_REQUIRED')
                for item in permissions['runner_captures']:declaration(item)
            if permissions.get('platform_screenshots'):
                from .adapters.screenshot_blobs import declaration
                if permissions.get('role')!='platform':_deny('PLATFORM_IDENTITY_REQUIRED')
                for item in permissions['platform_screenshots']:declaration(item)
            if permissions.get('platform_archive'):
                from .adapters.platform_archive import declaration
                if permissions.get('role')!='platform':_deny('PLATFORM_IDENTITY_REQUIRED')
                for item in permissions['platform_archive']:declaration(item)
            for target in permissions.get('sql',[]):
                if (target.get('read_only') is not True or not target.get('server') or not target.get('database')
                        or type(target.get('row_cap')) is not int or not 1<=target['row_cap']<=1000
                        or type(target.get('timeout_seconds')) is not int or not 1<=target['timeout_seconds']<=120):
                    _deny('INVALID_SQL_POLICY')
                for name in target.get('objects',[]):_object(name)

    def check_live(self):
        if os.environ.get(KILL_ENV,'').lower() in ('1','true','yes') or not self.policy['live_enabled']:
            _deny('LIVE_ACCESS_DISABLED')

    def identity(self,identity):
        self.check_live()
        permissions=self.policy['identities'].get(identity)
        if permissions is None:_deny('IDENTITY_NOT_ALLOWED',identity=identity)
        if permissions.get('role')=='scanner':
            from .adapters.scanner_policy import authorize_job
            try:authorize_job(permissions)
            except Exception:_deny('SCANNER_JOB_REQUIRED',identity=identity)
        return permissions

    def http(self,identity,method,url,body=None,headers=None):
        _network_unlocked()
        permissions=self.identity(identity);_url(url)
        method=method.upper()
        matches=[item for item in permissions.get('http',[]) if item['method']==method and item['url']==url]
        if not matches and permissions.get('role')=='scanner':
            from .adapters.scanner_policy import followup
            bound=followup(identity,method,url)
            if bound is not None:matches=[bound]
        if permissions.get('role')=='scanner':
            from .adapters.scanner_policy import response_bound_only,followup
            if response_bound_only(url) and followup(identity,method,url) is None:
                _deny('SCANNER_RESPONSE_BINDING_REQUIRED',identity=identity,operation=method,target=url)
        if not matches and permissions.get('role')=='enrichment':
            from .adapters.enrichment_anthropic import permits
            if permits(self,identity,method,url,body,headers):
                return {'method':method,'url':url,'purpose':'ENRICHMENT_ONLY'}
        if len(matches)!=1:
            if not matches and permissions.get('role')=='platform':
                from .adapters.runner_blobs import permits as runner_permits
                if runner_permits(self,identity,method,url,body,headers):
                    return {'method':method,'url':url,'purpose':'runner_capture'}
                from .adapters.platform_cas import permits
                if permits(self,identity,method,url,body,headers):
                    return {'method':method,'url':url,'purpose':'platform_cas'}
                from .adapters.screenshot_blobs import permits as screenshot_permits
                if screenshot_permits(self,identity,method,url,body,headers):
                    return {'method':method,'url':url,'purpose':'platform_screenshot'}
                from .adapters.platform_archive import permits as archive_permits
                if archive_permits(self,identity,method,url,body,headers):
                    return {'method':method,'url':url,'purpose':'platform_archive'}
            _deny('ENDPOINT_METHOD_NOT_ALLOWED',identity=identity,operation=method,target=url)
        path=unquote(urlsplit(url).path).casefold().split('/')
        if (set(path)&FORBIDDEN_HTTP_SEGMENTS
                or method not in ('GET','HEAD') and set(path)&{'refreshes','refresh'}):
            _deny('ESTATE_CONTROL_ENDPOINT_BLOCKED',identity=identity,operation=method,target=url)
        purpose=matches[0]['purpose']
        if purpose.startswith('scanner_'):
            from .adapters.scanner_policy import http
            try:http(permissions,matches[0],method,url,body)
            except Exception:_deny('SCANNER_OPERATION_REFUSED',identity=identity,operation=method,target=url)
        elif purpose=='dax':
            if method!='POST' or path[-1]!='executequeries':_deny('DAX_ENDPOINT_REQUIRED')
            try:
                value=json.loads(body) if isinstance(body,(str,bytes)) else body
                if set(value)-{'queries','serializerSettings'} or len(value['queries'])!=1:
                    raise ValueError()
                query=value['queries'][0]
                if set(query)!={'query'}:raise ValueError()
                validate_dax(query['query'])
            except GatewayDenied:raise
            except Exception:_deny('DAX_REQUEST_SHAPE_REJECTED',identity=identity,target=url)
        elif purpose=='metadata':
            if method not in ('GET','HEAD') and not (method=='POST' and path[-1]=='getdefinition' and not body):
                _deny('METADATA_MUTATION_BLOCKED',identity=identity,operation=method,target=url)
        elif purpose=='auth_federation':
            from .adapters.federated_reader import validate_request
            if not validate_request(method, url, body, matches[0]):
                _deny('AUTH_FEDERATION_REQUEST_REFUSED',identity=identity,target=url)
        elif purpose=='auth_refresh':
            from .adapters.vault_user_cache import validate_refresh_request
            if not validate_refresh_request(method, url, body, matches[0]):
                _deny('AUTH_REFRESH_REQUEST_REFUSED',identity=identity,target=url)
        elif purpose=='blob_read':
            if method not in ('GET','HEAD'):_deny('BLOB_WRITE_BLOCKED',identity=identity,target=url)
        elif purpose=='model':
            if method!='POST' or path[-1] not in ('responses','completions'):
                _deny('MODEL_ENDPOINT_REQUIRED',identity=identity,target=url)
        elif purpose=='platform_blob':
            if method not in ('GET','HEAD','PUT'):
                _deny('PLATFORM_BLOB_OPERATION_BLOCKED',identity=identity,target=url)
        elif purpose=='kql':
            # No general KQL interpreter is exposed in this round. A dot command
            # (including execute_query commands) must not be a metadata bypass.
            _deny('KQL_GATEWAY_NOT_IMPLEMENTED',identity=identity,target=url)
        return matches[0]

    def native_control(self,identity,operation,target,query=None):
        _network_unlocked()
        permissions=self.identity(identity)
        if permissions.get('role')=='scanner'and operation!='XMLA_GRAPH_METADATA':
            _deny('SCANNER_NATIVE_OPERATION_REFUSED',identity=identity,operation=operation)
        if permissions.get('role')=='scanner':
            from .adapters.scanner_identity import require_job
            try:require_job(permissions['scanner']['authentication'],[target['workspace']])
            except Exception:_deny('SCANNER_NATIVE_SCOPE_REFUSED',identity=identity,operation=operation)
        if operation not in ('XMLA_EVALUATE','XMLA_GRAPH_METADATA','SNAPSHOT_SQL_METADATA','SNAPSHOT_XMLA_METADATA'):
            _deny('NATIVE_CONTROL_UNKNOWN',identity=identity)
        grant={'operation':operation,**target}
        if grant not in permissions.get('native_controls',[]):
            _deny('NATIVE_CONTROL_NOT_ALLOWED',identity=identity,operation=operation)
        if operation=='XMLA_EVALUATE':validate_dax(query)
        elif operation=='XMLA_GRAPH_METADATA':
            from .adapters.graph_dependencies import validate_query
            validate_query(query)
        elif query is not None:_deny('FIXED_METADATA_QUERY_REQUIRED',identity=identity)
        return grant

    def platform_database(self,identity,host,database):
        permissions=self.identity(identity)
        if permissions.get('role')!='platform' or {'host':host,'database':database} not in permissions.get('platform_databases',[]):
            _deny('PLATFORM_DATABASE_NOT_ALLOWED',identity=identity,target=host+'/'+database)
        return {'host':host,'database':database}

    def sql_control(self,identity,server,database,control):
        _network_unlocked()
        permissions=self.identity(identity)
        matches=[item for item in permissions.get('sql',[]) if item['server']==server and item['database']==database]
        if len(matches)!=1 or control not in matches[0].get('controls',[]):
            _deny('SQL_CONTROL_NOT_ALLOWED',identity=identity,operation=control)
        if control not in ('PREWARM','SELF_REPORT','CATALOG'):
            _deny('SQL_CONTROL_UNKNOWN',identity=identity,operation=control)
        return matches[0]

    def sql(self,identity,server,database,query,*,objects=None,max_rows=1,timeout=30):
        _network_unlocked()
        permissions=self.identity(identity)
        matches=[item for item in permissions.get('sql',[]) if item['server']==server and item['database']==database]
        if len(matches)!=1:_deny('SQL_CONNECTION_NOT_ALLOWED',identity=identity,target=server+'/'+database)
        target=matches[0]
        if type(max_rows) is not int or not 1<=max_rows<=target['row_cap']:
            _deny('SQL_ROW_CAP_EXCEEDED',identity=identity)
        if type(timeout) is not int or not 1<=timeout<=target['timeout_seconds']:
            _deny('SQL_TIMEOUT_EXCEEDED',identity=identity)
        allowed={_object(name) for name in target.get('objects',[])}
        if objects is not None:
            requested={_object(name) for name in objects}
            if not requested<=allowed:_deny('SQL_OBJECT_SCOPE_NOT_ALLOWED',identity=identity)
            allowed=requested
        references=validate_sql(query,allowed)
        return {'objects':[name for name in target.get('objects',[]) if _object(name) in references],
                'read_only':True,'application_intent':'ReadOnly','timeout_seconds':timeout,'row_cap':max_rows}


def validate_sql(query,allowed_objects):
    """Single SELECT AST and catalog objects; reject unknown syntax/functions."""
    from sqlglot import parse, exp
    from sqlglot.optimizer.scope import traverse_scope
    from .query_sql import NODES
    if not isinstance(query,str) or not 1<=len(query)<=32000:_deny('SQL_TEXT_BOUND')
    try:statements=parse(query,read='tsql')
    except Exception:_deny('SQL_PARSE_REJECTED',target=query)
    if len(statements)!=1 or not isinstance(statements[0],exp.Select):_deny('SINGLE_SELECT_REQUIRED',target=query)
    tree=statements[0]
    if len(list(tree.walk()))>3000:_deny('SQL_AST_BOUND',target=query)
    # Parser allowlist, not a write-keyword denylist. INTO/locking/external
    # table functions are absent. Harmless-looking unknown constructs also stop.
    safe=NODES|{'Collate','Substring','Length','CharacterSet','SHA2','Convert','CurrentUser'}
    for node in tree.walk():
        if node.comments:_deny('SQL_COMMENTS_REJECTED',target=query)
        if isinstance(node,exp.QueryOption):
            if node.sql(dialect='tsql').upper()!='MAXDOP 1':_deny('SQL_QUERY_HINT_REJECTED',target=query)
            continue
        if type(node).__name__ not in safe:
            if isinstance(node,exp.Anonymous) and node.name.upper() in {'DATALENGTH','HASHBYTES','SUSER_SNAME','DB_NAME','ORIGINAL_LOGIN','SERVERPROPERTY'}:
                continue
            _deny('SQL_AST_NOT_ALLOWED:'+type(node).__name__,target=query)
    references=set()
    try:
        for scope in traverse_scope(tree):
            for source in scope.sources.values():
                if isinstance(source,exp.Table):
                    if source.catalog or not isinstance(source.this,exp.Identifier) or source.name.startswith(('#','@')):
                        _deny('SQL_EXTERNAL_OR_TEMP_OBJECT',target=query)
                    item=(source.db.casefold(),source.name.casefold())
                    if item not in allowed_objects:_deny('SQL_OBJECT_NOT_ALLOWED',target=query)
                    references.add(item)
    except GatewayDenied:raise
    except Exception:_deny('SQL_SCOPE_REJECTED',target=query)
    return references


def validate_dax(query):
    """Lexical query boundary plus an explicit function vocabulary.

    Catalog binding remains the existing query_dax compiler's responsibility;
    this independent transport guard prevents bypasses into native control commands.
    String literals remain data, including SQL/OCR prompt injections.
    """
    from .semantic_graph import tokenize, TOKEN
    from .query_dax import FUNCTIONS, ENUMS
    if not isinstance(query,str) or not 1<=len(query)<=32000:_deny('DAX_TEXT_BOUND')
    if any(m.lastgroup=='comment' for m in TOKEN.finditer(query)):_deny('DAX_COMMENTS_REJECTED',target=query)
    from .adapters.microsoft_self_report import SCALARS
    inspected=query
    for scalar in SCALARS:inspected=inspected.replace(scalar,'1')
    tokens,gaps=tokenize(inspected)
    if gaps or not tokens or tokens[0][0]!='name' or tokens[0][1].upper()!='EVALUATE':
        _deny('SINGLE_EVALUATE_REQUIRED',target=query)
    # Compiler self-description and rendering primitives are read-only scalars.
    functions=FUNCTIONS|{'FORMAT','USERNAME','USEROBJECTID','DISTINCTCOUNTNOBLANK','CONCATENATEX',
                         'INFO','NAMEOF','ISEMPTY','ISINSCOPE','CONTAINSROW','PATH','PATHITEM'}
    depth=0
    for i,(kind,value) in enumerate(tokens[1:],1):
        if kind=='operator' and value==';':_deny('DAX_MULTIPLE_STATEMENTS',target=query)
        if kind=='name' and value.upper() in {'EVALUATE','DEFINE','CREATE','ALTER','DELETE','UPDATE','INSERT','EXEC','EXECUTE','REFRESH'}:
            _deny('DAX_COMMAND_REJECTED',target=query)
        if kind=='name' and i+1<len(tokens) and tokens[i+1][1]=='(' and value.upper() not in functions:
            _deny('DAX_FUNCTION_NOT_ALLOWED',target=query)
        if value=='(':depth+=1
        if value==')':depth-=1
        if depth<0:_deny('DAX_UNBALANCED',target=query)
    if depth:_deny('DAX_UNBALANCED',target=query)
    return query


@contextmanager
def configured(policy):
    """Dependency injection for deployment/tests; never exposed as an agent tool."""
    token=ACTIVE.set(Gateway(policy))
    try:yield ACTIVE.get()
    finally:ACTIVE.reset(token)


def current():
    gateway=ACTIVE.get()
    if gateway is None:
        path=os.environ.get(POLICY_ENV)
        if not path:_deny('GATEWAY_POLICY_REQUIRED')
        try:gateway=Gateway(json.loads(Path(path).read_text(encoding='utf-8-sig')))
        except GatewayDenied:raise
        except Exception:_deny('GATEWAY_POLICY_UNREADABLE')
    gateway.check_live()
    return gateway


def authorize_http(request,*,identity=None):
    identity=identity or os.environ.get('DIA_GATEWAY_HTTP_IDENTITY','')
    return current().http(identity,request.get_method(),request.full_url,request.data,
                          dict(request.header_items()))


def open_http(opener,request,*,timeout,identity=None):
    if not isinstance(timeout,(int,float)) or not 0<timeout<=120:_deny('HTTP_TIMEOUT_REQUIRED')
    authorize_http(request,identity=identity)
    # All production openers have NoRedirect. The gateway never follows a
    # redirect to an endpoint that did not receive its own admission.
    return opener.open(request,timeout=timeout)


def model_request(request):
    current().http(os.environ.get('DIA_GATEWAY_MODEL_IDENTITY',''),request.method,str(request.url),request.read())


def authorize_sql_payload(payload):
    identity=os.environ.get('DIA_GATEWAY_SQL_IDENTITY','')
    from .adapters.binding_catalog import compiled_control_objects
    catalog_objects=compiled_control_objects(payload)
    if catalog_objects is None:
        from .adapters.graph_sql_changes import compiled_control_objects as graph_catalog_objects
        catalog_objects=graph_catalog_objects(payload)
    if catalog_objects is not None:
        gateway=current()
        gateway.sql_control(identity,payload['server'],payload['database'],'CATALOG')
        # Reuse normal connection/object/row/time admission; SELECT 1 has no
        # additional object authority. Only the exact compiler shape above can
        # use catalog views, and all user-object permission guards remain.
        gateway.sql(identity,payload['server'],payload['database'],'SELECT 1',
            objects=catalog_objects,max_rows=payload['max_rows'],timeout=30)
        return {**payload,'require_read_only':True,'read_only_objects':catalog_objects}
    admission=current().sql(identity,payload['server'],payload['database'],payload['query'],
        objects=payload.get('read_only_objects'),max_rows=payload.get('max_rows',1),timeout=30)
    return {**payload,'require_read_only':True,'read_only_objects':admission['objects']}


def authorize_sql_control(server,database,control,*,identity=None):
    return current().sql_control(identity or os.environ.get('DIA_GATEWAY_SQL_IDENTITY',''),server,database,control)


def authorize_platform_database(identity,host,database):
    """Internal persistence only; no agent/model tool exposes this operation."""
    return current().platform_database(identity,host,database)


def authorize_native_control(operation,target,query=None,*,identity=None):
    return current().native_control(identity or os.environ.get('DIA_GATEWAY_HTTP_IDENTITY',''),operation,target,query)
