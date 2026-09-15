"""Typed action admission independent of metric names and fixed layer order."""
from .onboarding import fields, text, Conflict
from . import native_diagnostics, source_diagnostics, comparisons

TOOLS = {'native': {'cloud':True,'receipt_table':'native_diagnostics'},
         'source': {'cloud':True,'receipt_table':'source_diagnostics'},
         'compare': {'cloud':False,'receipt_table':'comparison_assessments'}}


def normalize(request):
    if isinstance(request,dict) and 'actions' in request:
        fields(request,['model_id','actions','call_budget'])
        return request
    fields(request,['native_plan','source_plan','measure_id','mapping_id','call_budget'])
    return {'model_id':request['native_plan']['model_id'],'call_budget':request['call_budget'],
            'actions':[{'tool':'native','input':request['native_plan']},
                       {'tool':'source','input':request['source_plan']},
                       {'tool':'compare','input':{'native_step':0,'source_step':1,'measure_id':request['measure_id'],
                                                 'mapping_id':request['mapping_id']}}]}


def compile_actions(store,config,request):
    fields(request,['model_id','actions','call_budget'])
    model=store.get(request['model_id']); actions=request['actions']
    if not isinstance(actions,list) or not 1<=len(actions)<=20:raise ValueError('Action budget exceeded')
    if type(request['call_budget']) is not int or not 1<=request['call_budget']<=10:raise ValueError('Invalid call budget')
    compiled=[]; cloud=0
    for ordinal,action in enumerate(actions):
        fields(action,['tool','input']);tool=action['tool'];payload=action['input']
        if not isinstance(tool,str) or tool not in TOOLS:raise ValueError('Unknown registered tool')
        if tool in ('native','source'):
            if not isinstance(payload,dict) or payload.get('model_id')!=model['id']:raise ValueError('Cross-model action')
            compiled.append(native_diagnostics.build(model,payload) if tool=='native' else source_diagnostics.build(store,payload,config))
            cloud+=1
        else:
            fields(payload,['native_step','source_step','measure_id','mapping_id'])
            for key,expected in [('native_step','native'),('source_step','source')]:
                index=payload[key]
                if type(index) is not int or not 0<=index<ordinal or actions[index]['tool']!=expected:
                    raise ValueError('Comparison needs prior typed observations')
            native=compiled[payload['native_step']]
            if actions[payload['source_step']]['input']['operation']=='watermark_age_microseconds':
                raise ValueError('Watermark age is not a native metric comparison')
            if payload['measure_id'] not in native['measure_ids'] or native['dimension_id'] is not None:
                raise ValueError('Comparison needs selected scalar native measure')
            if payload['mapping_id'] is not None:
                review=comparisons.mapping(store,model['id'],text(payload['mapping_id'],500))
                if review['revocation'] is not None:raise Conflict('Mapping review revoked')
                contract=review['body']
                if contract['context_id']!=model['context_id'] or contract['revision']!=model['revision']:
                    raise Conflict('Mapping review is stale')
            compiled.append(payload)
    if cloud>request['call_budget']:raise ValueError('Plan exceeds reserved cloud-call budget')
    return compiled
