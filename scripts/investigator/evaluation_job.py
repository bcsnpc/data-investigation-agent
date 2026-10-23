"""Sealed independent evaluation batches; never runtime or graph evidence."""
import copy
import json
from jsonschema import Draft202012Validator
from .shared_state import sha
from .adapters.evaluation_anthropic import task, PROTOCOL, WRITER_SCHEMA, GRADER_SCHEMA

NAMESPACE='independent_evaluation_batches'

class EvaluationJob:
    def __init__(self,state,provider,budget,*,clock):
        if budget.account!='enrichment:round-twenty-one':raise ValueError('EVALUATION_ENRICHMENT_ACCOUNT_REQUIRED')
        self.state,self.provider,self.budget,self.clock=state,provider,budget,clock
    def submit(self,sources,*,batch_key):
        if not isinstance(sources,list)or not 1<=len(sources)<=50:raise ValueError('EVALUATION_BATCH_BOUND')
        sources=[task(s)for s in sources]
        if len({s['case_id']for s in sources})!=len(sources):raise ValueError('EVALUATION_DUPLICATE_CASE')
        try:self.state.get(NAMESPACE,batch_key)
        except KeyError:pass
        else:raise ValueError('EVALUATION_BATCH_ALREADY_RECORDED')
        requests=[self.provider.request_for(s,sha(s))for s in sources];reservations={}
        try:
            for request in requests:
                identity='evaluation:'+sha([batch_key,request['custom_id']]);self.budget.reserve(request,identity);reservations[request['custom_id']]=identity
        except Exception:
            for identity in reservations.values():self.state.settle(self.budget.account,identity,self.budget.owner,0,detail={'not_sent':True})
            raise
        body={'protocol':PROTOCOL,'status':'ADMITTED','tasks':sources,'requests':requests,'reservations':reservations,'submitted_at':self.clock()}
        stored=self.state.put(NAMESPACE,batch_key,body)
        # An uncertain submission is retained and must be reconciled, never resubmitted.
        receipt=self.provider.create(requests);body.update(status='SUBMITTED',receipt=receipt);self.state.put(NAMESPACE,batch_key,body,revision=stored['revision'])
        return {'status':'SUBMITTED','batch_key':batch_key,'receipt':receipt,'requests':len(requests)}
    def resume(self,batch_key):
        stored=self.state.get(NAMESPACE,batch_key);body=stored['body']
        if body['status']=='COMPLETED':return copy.deepcopy(body['result'])
        if body['status']!='SUBMITTED':raise ValueError('EVALUATION_SUBMISSION_UNCERTAIN_RECONCILE')
        self.provider.restore(body['receipt']);receipt=self.provider.status(body['receipt']['id'])
        if receipt['processing_status']!='ended':return {'status':'PENDING','batch_key':batch_key,'receipt':receipt}
        rows=self.provider.results(receipt['id']);by_id={r['custom_id']:r for r in rows}
        if len(rows)!=len(by_id)or set(by_id)!=set(body['reservations']):raise ValueError('EVALUATION_RESULT_IDENTITIES_DIFFER')
        results=[]
        for source,request in zip(body['tasks'],body['requests']):
            row=by_id[request['custom_id']]['result'];message=row.get('message',{});usage=message.get('usage')
            self.budget.settle(body['reservations'][request['custom_id']],usage)
            result={'case_id':source['case_id'],'provider_result':copy.deepcopy(row),'status':'FAILED'}
            if row['type']=='succeeded' and message.get('model')==self.provider.model and message.get('stop_reason')=='end_turn':
                try:
                    output=json.loads(''.join(p['text']for p in message['content']if p['type']=='text'))
                    schema=WRITER_SCHEMA if source['purpose']=='WRITE_TICKETS'else GRADER_SCHEMA
                    Draft202012Validator(schema).validate(output)
                    if source['purpose']=='WRITE_TICKETS'and sorted(x['variation']for x in output['tickets'])!=sorted(source['variations']):raise ValueError('WRITER_VARIATIONS_DIFFER')
                    result.update(status='VALIDATED',output=output)
                except Exception as error:result.update(reason=type(error).__name__+':'+str(error))
            results.append(result)
        result={'status':'COMPLETED','batch_key':batch_key,'results':results,'budget':self.budget.snapshot(),'estate_reads':0,'investigator_model_calls':0,'not_runtime_evidence':True}
        body.update(status='COMPLETED',result=result);self.state.put(NAMESPACE,batch_key,body,revision=stored['revision']);return result
