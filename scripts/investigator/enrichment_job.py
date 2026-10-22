"""Separately budgeted asynchronous enrichment, not investigator model routing."""
import copy
import json
from .enrichment import EnrichmentStore, cache_key, task
from .shared_state import encoded, sha, amount, StateConflict

ACCOUNT='enrichment:round-twenty-one'
CEILING=25_000_000


class EnrichmentSpendBudget:
    def __init__(self,state,*,owner,price,account=ACCOUNT):
        if not owner or account!=ACCOUNT:raise ValueError('SEPARATE_ENRICHMENT_ACCOUNT_REQUIRED')
        self.state,self.owner,self.price,self.account=state,owner,price,account
        snapshot=state.snapshot(account)
        if snapshot['unit']!='MICRODOLLARS' or amount(snapshot['ceiling'])!=CEILING or amount(snapshot['protected'])!=0:
            raise ValueError('ENRICHMENT_DOLLAR_POLICY_DIFFERS')

    def reserve(self,request,identity):
        params=request['params'];inputs=len(encoded(request).encode())+4096
        bound=self.price(inputs,params['max_tokens'])
        self.state.reserve(self.account,identity,self.owner,bound,detail={'purpose':'ENRICHMENT_ONLY','request_sha256':sha(request)})
        return identity

    def settle(self,identity,usage=None):
        known=isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens'))
        # No prompt caching/tools are requested; an unexpected charge class is
        # unknown cost, not a convenient zero. Retain the complete reservation.
        if known and any(usage.get(k,0) for k in ('cache_creation_input_tokens','cache_read_input_tokens','server_tool_use')):known=False
        actual=self.price(usage['input_tokens'],usage['output_tokens']) if known else None
        return self.state.settle(self.account,identity,self.owner,actual,detail={'usage':usage,'known':known})

    def snapshot(self):return self.state.snapshot(self.account)


class EnrichmentJob:
    def __init__(self,state,provider,budget,*,clock):
        self.state,self.provider,self.budget,self.clock=state,provider,budget,clock
        from .privacy_capture import ACTIVE
        if ACTIVE.get() is not None:raise ValueError('ENRICHMENT_PROJECTED_SHARED_STATE_UNIMPLEMENTED')
        self.store=EnrichmentStore(state)
        if provider.recording_class=='RECORDED_STUB' and (state.backend!='sqlite' or state.mode!='offline'):
            raise ValueError('ENRICHMENT_STUB_PRIVATE_OFFLINE_ONLY')

    def submit(self,sources,*,batch_key):
        if not isinstance(sources,list) or not 1<=len(sources)<=50:raise ValueError('ENRICHMENT_BATCH_BOUND')
        sources=[task(s) for s in sources]
        if len({cache_key(s) for s in sources})!=len(sources):raise ValueError('ENRICHMENT_DUPLICATE_TASK')
        if self._prior(batch_key) is not None:raise ValueError('ENRICHMENT_BATCH_ALREADY_ADMITTED')
        selected=[];skipped=[]
        for source in sources:
            old=self.store.cached(source)
            if old and (old['recording_class']!='RECORDED_STUB' or self.provider.recording_class=='RECORDED_STUB'):
                skipped.append(source['subject'])
            else:selected.append(source)
        if not selected:return {'status':'CACHED','skipped':skipped,'batch_key':batch_key}
        requests=[self.provider.request_for(source,cache_key(source)) for source in selected]
        reservations={}
        try:
            for request in requests:
                identity='enrichment:'+sha([batch_key,request['custom_id']])
                reservations[request['custom_id']]=self.budget.reserve(request,identity)
        except Exception:
            # No external submission has happened; release partial admissions.
            for identity in reservations.values():self.budget.state.settle(self.budget.account,identity,self.budget.owner,0,detail={'not_sent':True})
            raise
        body={'batch_key':batch_key,'status':'ADMITTED','tasks':selected,'requests':requests,'reservations':reservations,
              'recording_class':self.provider.recording_class,'provider':self.provider.provider,'submitted_at':self.clock(),'skipped':skipped}
        self.state.put('enrichment_batches',batch_key,body)
        try:receipt=self.provider.create(requests)
        except Exception as error:
            for identity in reservations.values():self.budget.settle(identity)
            self._update(batch_key,{**body,'status':'SUBMISSION_FAILED','error_type':type(error).__name__,'http_status':getattr(error,'http_status',None)})
            raise
        body.update(status='SUBMITTED',receipt=receipt)
        self._update(batch_key,body)
        return {'status':'SUBMITTED','batch_key':batch_key,'receipt':receipt,'submitted':len(selected),'skipped':skipped}

    def _prior(self,key):
        try:return self.state.get('enrichment_batches',key)['body']
        except KeyError:return None

    def _update(self,key,body):
        old=self.state.get('enrichment_batches',key)
        self.state.put('enrichment_batches',key,body,revision=old['revision'])

    def resume(self,batch_key):
        body=self._prior(batch_key)
        if body is None or body['status'] not in ('SUBMITTED','PROCESSING','COMPLETED','PARTIAL'):raise ValueError('ENRICHMENT_BATCH_NOT_SUBMITTED')
        if body['provider']!=self.provider.provider or body['recording_class']!=self.provider.recording_class:raise ValueError('ENRICHMENT_PROVIDER_OR_TAPE_CLASS_DIFFERS')
        if body['status'] in ('COMPLETED','PARTIAL'):return body['result']
        self.provider.restore(body['receipt']);status=self.provider.status(body['receipt']['id'])
        if status.get('processing_status')!='ended':
            body.update(status='PROCESSING',last_status=status);self._update(batch_key,body)
            return {'status':'PROCESSING','batch_key':batch_key,'provider_status':status.get('processing_status')}
        rows=self.provider.results(body['receipt']['id'])
        body.update(completed_receipt=status,result_rows=rows)
        self._update(batch_key,body)
        tasks={cache_key(t):t for t in body['tasks']};seen=set();results=[]
        # Reject the whole response's identity shape before applying any row.
        for row in rows:
            if not isinstance(row,dict) or set(row)!={'custom_id','result'} or row['custom_id'] not in tasks or row['custom_id'] in seen:
                raise ValueError('ENRICHMENT_RESULT_IDENTITY_DIFFERS')
            seen.add(row['custom_id'])
        for row in rows:
            identity=row['custom_id'];result=row['result'];message=result.get('message') if result.get('type')=='succeeded' else None
            usage=message.get('usage') if isinstance(message,dict) and message.get('model')==self.provider.model else None
            self.budget.settle(body['reservations'][identity],usage)
            try:
                if message is None:raise ValueError('ENRICHMENT_PROVIDER_RESULT_'+str(result.get('type')))
                if message.get('model')!=self.provider.model:raise ValueError('ENRICHMENT_MODEL_ID_DIFFERS')
                if message.get('stop_reason') not in ('end_turn','stop_sequence'):raise ValueError('ENRICHMENT_INCOMPLETE_GENERATION')
                content=message.get('content')
                if not isinstance(content,list) or len(content)!=1 or content[0].get('type')!='text':raise ValueError('ENRICHMENT_TEXT_RESULT_REQUIRED')
                output=json.loads(content[0]['text'])
                normalize=getattr(self.provider,'normalize_output',None)
                if normalize is not None:
                    request=next(r for r in body['requests']if r['custom_id']==identity)
                    output=normalize(output,tasks[identity],request)
                evidence='enrichment-batches/'+batch_key+'/results/'+identity+':'+sha(row)
                applied=self.store.apply(tasks[identity],output,at=self.clock(),producer=self.provider.provider,
                    recording_class=self.provider.recording_class,evidence_ids=[evidence])
                results.append({'subject':tasks[identity]['subject'],'status':applied['status'],'recording_class':applied['recording_class']})
            except (ValueError,KeyError,TypeError) as error:
                results.append({'subject':tasks[identity]['subject'],'status':'REJECTED','reason':str(error) if isinstance(error,ValueError) else type(error).__name__})
        for missing in tasks.keys()-seen:
            self.budget.settle(body['reservations'][missing])
            results.append({'subject':tasks[missing]['subject'],'status':'MISSING_RESULT'})
        result={'batch_key':batch_key,'status':'COMPLETED' if all(r['status'] in ('INFERRED','HUMAN_CONFIRMED') for r in results) else 'PARTIAL',
                'recording_class':body['recording_class'],'results':results,'budget':self.budget.snapshot()}
        body.update(status=result['status'],result=result);self._update(batch_key,body)
        return result
