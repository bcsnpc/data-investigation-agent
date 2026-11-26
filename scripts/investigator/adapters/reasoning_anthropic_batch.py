"""Owned static-ticket Message Batches; unknown submissions are never repeated."""
from contextvars import ContextVar
from copy import deepcopy
import json,re,time
from .reasoning_anthropic import BASE,authorize_body
SESSION=ContextVar('reasoning_static_batch',default=None)
ENDPOINT=BASE+'/messages/batches'
class BatchPending(RuntimeError):
    """The taped submission must be resumed by ID, never submitted again."""
def permits(permissions,identity,method,url,raw):
    session=SESSION.get()
    if session is None or session.identity!=identity:return False
    # An existing reasoning grant remains necessary; no enrichment identity.
    provider=permissions.get('ai_providers',{}).get('anthropic')
    allowed=permissions.get('reasoning_models',[]) if provider is None else provider.get('models',[])
    if permissions.get('role')!='model' or session.model not in allowed:return False
    if not any(p.get('method')=='POST'and p.get('url')==BASE+'/messages'and p.get('purpose')in('reasoning_model','configured_ai')for p in permissions.get('http',[])):return False
    if method=='POST'and url==ENDPOINT:
        try:
            body=json.loads(raw)if isinstance(raw,(str,bytes))else raw
            if not isinstance(body,dict)or set(body)!={'requests'}or not 1<=len(body['requests'])<=50:return False
            ids=set()
            for row in body['requests']:
                if set(row)!={'custom_id','params'}or not re.fullmatch('[A-Za-z0-9_-]{1,64}',row['custom_id'])or row['custom_id']in ids:return False
                ids.add(row['custom_id'])
                params=authorize_body({'reasoning_models':[session.model]},'POST',BASE+'/messages',row['params'])
                if provider is not None and any(t['name']not in provider.get('tools',[])for t in params['tools']):return False
            return body==session.submitting
        except (ValueError,KeyError,TypeError):return False
    return method=='GET'and not raw and any(url==ENDPOINT+'/'+batch or batch in session.ended and url==ENDPOINT+'/'+batch+'/results'for batch in session.owned)
class StaticBatch:
    def __init__(self,client,*,static_ticket,clock=time.monotonic):
        if static_ticket is not True:raise ValueError('BATCH_STATIC_TICKET_REQUIRED')
        self.client=client;self.identity=client.identity;self.model=client.model
        self.clock=clock;self.owned=set();self.ended=set();self.submitting=None
    def request(self,method,url,body=None):
        marker=SESSION.set(self)
        try:return (self.client.send or self.client._http)(method,url,body)
        finally:SESSION.reset(marker)
    def submit(self,requests):
        from ..planner_recording import _safe
        from ..estate_graph_contract import canonical
        from ..process_tape import uuid4
        if not isinstance(requests,list)or not 1<=len(requests)<=50:raise ValueError('STATIC_BATCH_BOUND')
        for body in requests:authorize_body({'reasoning_models':[self.model]},'POST',BASE+'/messages',body)
        rows=[];reservations={}
        # Reserve all requests before the only POST. Unknown failures stay charged.
        for body in requests:
            authorize_body({'reasoning_models':[self.model]},'POST',BASE+'/messages',body)
            _safe(canonical(body).encode())
            key=uuid4().hex;reservation=self.client.budget.reserve(body)
            self.client.record({'event':'STATIC_BATCH_RESERVED','custom_id':key,'reservation':reservation})
            rows.append({'custom_id':key,'params':deepcopy(body)});reservations[key]=reservation
        if not 1<=len(rows)<=50:raise ValueError('STATIC_BATCH_BOUND')
        self.submitting={'requests':rows}
        self.client.record({'event':'STATIC_BATCH_REQUEST','body':self.submitting,'reservations':reservations})
        try:
            result=self.request('POST',ENDPOINT,self.submitting)
            batch=result.get('id')
            if not isinstance(batch,str)or not re.fullmatch('msgbatch_[A-Za-z0-9]+',batch):raise ValueError('STATIC_BATCH_ID')
            self.owned.add(batch)
            receipt={'id':batch,'reservations':reservations,'processing_status':result.get('processing_status')}
            if receipt['processing_status']=='ended':self.ended.add(batch)
            self.client.record({'event':'STATIC_BATCH_SUBMITTED','receipt':receipt,'body':result})
            return receipt
        except Exception:
            for reservation in reservations.values():self.client.budget.settle(reservation)
            raise
        finally:self.submitting=None
    def restore(self,receipt):
        if not re.fullmatch('msgbatch_[A-Za-z0-9]+',receipt['id']):raise ValueError('STATIC_BATCH_ID')
        self.owned.add(receipt['id'])
        if receipt.get('processing_status')=='ended':self.ended.add(receipt['id'])
    def collect(self,receipt,*,wait_seconds=0):
        batch=receipt['id']
        if batch not in self.owned:raise ValueError('STATIC_BATCH_NOT_OWNED')
        deadline=self.clock()+wait_seconds
        while batch not in self.ended:
            response=self.request('GET',ENDPOINT+'/'+batch)
            if response.get('id')!=batch:raise ValueError('STATIC_BATCH_ID_MISMATCH')
            self.client.record({'event':'STATIC_BATCH_STATUS','body':response})
            if response.get('processing_status')=='ended':self.ended.add(batch);break
            if self.clock()>=deadline:raise BatchPending('STATIC_BATCH_PENDING_USE_SAVED_ID:'+batch)
            self.client.sleep(min(30,max(0,deadline-self.clock())))
        rows=self.request('GET',ENDPOINT+'/'+batch+'/results')
        if not isinstance(rows,list)or len(rows)!=len(receipt['reservations']):raise ValueError('STATIC_BATCH_RESULT_COUNT')
        results={}
        for row in rows:
            key=row.get('custom_id')
            if key not in receipt['reservations']or key in results:raise ValueError('STATIC_BATCH_RESULT_ID')
            result=row['result'];results[key]=result
        self.client.record({'event':'STATIC_BATCH_RESULTS','id':batch,'rows':rows})
        for key,result in results.items():
            reservation=receipt['reservations'][key]
            if result.get('type')=='succeeded':self.client.budget.settle(reservation,result['message'].get('usage'))
            else:self.client.budget.settle(reservation)
        return results

def batch_rate(rate):
    """The documented 50% batch rate stacks with cache prices; round only at usage."""
    from ..reasoning_budget import RateCard
    return RateCard(model=rate.model,input_rate=rate.input_rate/2,output_rate=rate.output_rate/2,
        base_input_rate=rate.base_input_rate/2,cache_read_rate=rate.cache_read_rate/2,
        cache_write_rate=rate.cache_write_rate/2,source=rate.source,observed_at=rate.observed_at)
