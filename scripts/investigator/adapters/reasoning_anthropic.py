"""Standard client-side tool calls using the existing workspace Key Vault key.

Separate from the enrichment-only batch adapter and its USD25 account. HTTP
policy must explicitly admit these two model endpoints under existing scope.
No new secret, role, identity or endpoint grant is created by this client.
"""
from copy import deepcopy
import json
import time
from urllib.request import Request,build_opener
from urllib.error import HTTPError
from ..estate_graph_contract import canonical
from ..round23_calendar import require_live_window

BASE='https://api.anthropic.com/v1'
# Preference is operator policy, not ticket or model instructions. Discovery
# records the exact accessible ID before use; pricing is separately pinned.
PREFERENCE=('claude-fable-5-1','claude-opus-5-5','claude-opus-5','claude-opus-4-8',
            'claude-opus-4-7','claude-opus-4-6','claude-sonnet-5-5','claude-sonnet-5','claude-sonnet-4-6')


class ProviderHTTPError(RuntimeError):
    def __init__(self,status):
        self.http_status=status
        super().__init__('ANTHROPIC_HTTP_'+str(status))


def authorize_body(permissions,method,url,raw):
    """An explicit model endpoint, never an extension of enrichment batches."""
    if method!='POST' or url not in (BASE+'/messages',BASE+'/messages/count_tokens'):raise ValueError('REASONING_ENDPOINT')
    body=json.loads(raw) if isinstance(raw,(str,bytes)) else raw
    counted=url.endswith('/count_tokens')
    required={'model','system','messages','tools'}|(set() if counted else {'max_tokens'})
    if not isinstance(body,dict) or set(body)!=required:
        raise ValueError('REASONING_BODY')
    if body['model'] not in permissions.get('reasoning_models',[]):raise ValueError('REASONING_MODEL_NOT_PINNED')
    if not counted and (type(body['max_tokens']) is not int or not 1<=body['max_tokens']<=16000):raise ValueError('REASONING_OUTPUT_BOUND')
    names={'run_sql','run_dax','get_definition','get_lineage','get_job_runs','get_refresh_history',
           'get_security_definitions','record_trace','list_candidates','get_evidence','ask_user_choice','submit_finding',
           'lookup_intake_catalog','resolve_intake','describe_screenshot','plan_screenshot_lookup','lookup_screenshot'}
    if not isinstance(body['tools'],list) or not body['tools']:raise ValueError('CLIENT_TOOLS_REQUIRED')
    for tool in body['tools']:
        if not isinstance(tool,dict) or set(tool)!={'name','description','input_schema'} or tool['name'] not in names:
            raise ValueError('SERVER_OR_UNKNOWN_TOOL_REFUSED')
    system=body['system']
    if (not isinstance(system,list) or len(system)!=1 or set(system[0])!={'type','text','cache_control'}
            or system[0]['type']!='text' or not isinstance(system[0]['text'],str)
            or system[0]['cache_control']!={'type':'ephemeral'} or not isinstance(body['messages'],list)):
        raise ValueError('REASONING_CONTEXT')
    return body


def choose_model(listing,preference=PREFERENCE):
    if listing.get('has_more'):raise ValueError('MODEL_DISCOVERY_REQUIRES_ALL_PAGES')
    available={m['id'] for m in listing['data'] if m.get('lifecycle') not in ('retired','deprecated')}
    for model in preference:
        if model in available:return model
        versions=sorted((m for m in available if m.startswith(model+'-20')),reverse=True)
        if versions:return versions[0]
    raise ValueError('NO_REVIEWED_REASONING_MODEL_AVAILABLE')


class Client:
    def __init__(self,*,model,budget,identity,secret_reference,record,send=None,key_reader=None,sleep=time.sleep,count_tokens=None):
        from .managed_identity import validate_secret_reference
        validate_secret_reference(secret_reference)
        if budget.rate.model!=model:raise ValueError('MODEL_RATE_MISMATCH')
        self.model,self.budget,self.identity=model,budget,identity
        self.reference,self.record=deepcopy(secret_reference),record
        self.send=send;self.key_reader=key_reader
        self.sleep=sleep
        self.count_tokens=(send is None) if count_tokens is None else count_tokens

    def _http(self,method,url,body=None):
        require_live_window()
        from ..live_gateway import current,open_http
        from .managed_identity import secret
        from metadata_auth import NoRedirect
        raw=None if body is None else canonical(body).encode()
        # Authorize before fetching a credential; denied routes see no secret.
        current().http(self.identity,method,url,raw)
        key=(self.key_reader or secret)(self.reference,gateway_identity=self.identity)
        request=Request(url,data=raw,method=method,headers={'x-api-key':key,
            'anthropic-version':'2023-06-01','Content-Type':'application/json'})
        try:
            with open_http(build_opener(NoRedirect()),request,timeout=90,identity=self.identity) as response:
                data=response.read(4*1024*1024+1)
            if len(data)>4*1024*1024:raise ValueError('MODEL_RESPONSE_BOUND')
            if key in data.decode('utf8',errors='replace'):raise ValueError('MODEL_SECRET_ECHO')
            return json.loads(data)
        except HTTPError as error:
            raise ProviderHTTPError(error.code) from None
        finally:key=None;request=None

    def discover(self):
        listing=(self.send or self._http)('GET',BASE+'/models?limit=1000')
        self.record({'event':'REASONING_MODEL_DISCOVERY','listing':listing})
        return listing

    def complete(self,*,system,messages,tools,max_tokens=4000,private_summary=False):
        body={'model':self.model,'max_tokens':max_tokens,'system':[
                  {'type':'text','text':system,'cache_control':{'type':'ephemeral'}}],
              'messages':deepcopy(messages),'tools':deepcopy(tools)}
        from ..planner_recording import _safe
        _safe(canonical(body).encode())
        # The real transport checks the date before making a reservation. The
        # injected transport is only for offline fixture tests, never selected
        # from a ticket or environment variable.
        if self.send is None:require_live_window()
        input_bound=None
        if self.count_tokens:
            count_body={k:v for k,v in body.items() if k!='max_tokens'}
            counted=(self.send or self._http)('POST',BASE+'/messages/count_tokens',count_body)
            count=counted.get('input_tokens')
            if type(count) is not int or count<0:raise ValueError('PROVIDER_TOKEN_COUNT_REQUIRED')
            input_bound=count+4096
            self.record({'event':'REASONING_TOKEN_COUNT','input_tokens':count,'reservation_margin_tokens':4096})
        for attempt in range(3):
            identity=(self.budget.reserve(body) if input_bound is None else
                      self.budget.reserve(body,input_tokens_upper_bound=input_bound))
            try:
                self.record({'event':'REASONING_REQUEST','reservation':identity,
                             **({'private_case_content_omitted':True,'sha256':__import__('hashlib').sha256(canonical(body).encode()).hexdigest()}
                                if private_summary else {'body':body})})
                response=(self.send or self._http)('POST',BASE+'/messages',body)
                self.budget.settle(identity,response.get('usage'))
                _safe(canonical(response).encode())
                self.record({'event':'REASONING_RESPONSE','reservation':identity,
                             **({'private_case_content_omitted':True,'sha256':__import__('hashlib').sha256(canonical(response).encode()).hexdigest(),'usage':response.get('usage')}
                                if private_summary else {'body':response})})
                return response
            except ProviderHTTPError as error:
                if attempt==2 or error.http_status not in (408,429,502,503,504):raise
                wait=30*(attempt+1)
                self.record({'event':'REASONING_TRANSIENT','status':error.http_status,'attempt':attempt+1,'wait_seconds':wait})
            finally:
                # Unknown failures remain charged. Each retry gets a new
                # reservation; 429 is never delivered as an investigation result.
                self.budget.settle(identity)
            self.sleep(wait)
