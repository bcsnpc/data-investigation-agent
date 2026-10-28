"""Anthropic transport for legacy structured-call interfaces; no Azure fallback."""
import json,os
from contextvars import ContextVar
from .reasoning_anthropic import Client
from ..reasoning_budget import TicketBudget,RateCard
from ..shared_state import configured_state
from ..process_tape import uuid4
from ..planner_recording import _safe, ACTIVE, SESSION

CONFIG_ENV='DIA_RUNTIME_ANTHROPIC_JSON'
CLIENT=ContextVar('runtime_anthropic_client',default=None)


def installed_client():
    supplied=CLIENT.get()
    if supplied is not None:return supplied
    config=json.loads(os.environ[CONFIG_ENV])
    if set(config)!={'model','rate_card','secret_reference','gateway_identity','worker_identity'} or config['model']!='claude-opus-5-5':raise ValueError('ANTHROPIC_RUNTIME_CONFIGURATION')
    state=configured_state()
    if state is None:raise ValueError('ANTHROPIC_SHARED_BUDGET_REQUIRED')
    record=ACTIVE.get()
    metadata=getattr(record,'metadata',{})
    session=SESSION.get() or metadata.get('session_id') or os.environ.get('DIA_RUN_ID')
    if not session:raise ValueError('ANTHROPIC_TICKET_ID_REQUIRED')
    budget=TicketBudget(state,case_id='structured:'+str(session),owner=config['worker_identity'],rate=RateCard(model=config['model'],**config['rate_card']),actual_usage_limit=3000000)
    # The caller's ordinary recording context remains in force; no credential
    # or raw response is copied to shared accounting.
    def record(value):
        from ..process_tape import event
        event('ANTHROPIC_STRUCTURED',value)
    return Client(model=config['model'],budget=budget,identity=config['gateway_identity'],secret_reference=config['secret_reference'],record=record)


def generate(payload,instructions,schema,name,*,max_tokens,image_data_url=None):
    client=installed_client();content=[{'type':'text','text':json.dumps({'purpose':name,'input':payload},sort_keys=True,ensure_ascii=False)}]
    if image_data_url:
        header,data=image_data_url.split(',',1);media=header.removeprefix('data:').split(';')[0]
        content.append({'type':'image','source':{'type':'base64','media_type':media,'data':data}})
    tool={'name':'resolve_intake','description':'Return the requested structured proposal only; no execution or external tool.', 'input_schema':schema}
    response=client.complete(system=instructions,messages=[{'role':'user','content':content}],tools=[tool],max_tokens=max_tokens,private_summary=image_data_url is not None)
    calls=[x for x in response.get('content',[])if x.get('type')=='tool_use'and x.get('name')=='resolve_intake']
    from ..generation_policy import ProviderResponseError
    if response.get('stop_reason')=='max_tokens':raise ProviderResponseError('OUTPUT_TOKEN_LIMIT',response.get('usage'))
    if len(calls)!=1:raise ProviderResponseError('DECISION_CALL_SHAPE',response.get('usage'))
    value=calls[0]['input'];_safe(json.dumps(value).encode())
    return value,{'response_id':response.get('id'),'model':client.model,'usage':response.get('usage')}
