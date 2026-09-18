"""Typed action admission independent of metric names and fixed layer order."""
from .onboarding import fields, text, Conflict
from . import native_diagnostics, source_diagnostics, comparisons
from . import record_readback, record_comparison, record_aggregate, record_bindings

TOOLS = {'native': {'cloud':True,'receipt_table':'native_diagnostics'},
         'bounded_dax': {'cloud':True,'receipt_table':'flexible_diagnostics'},
         'bounded_sql': {'cloud':True,'receipt_table':'flexible_diagnostics'},
         'source': {'cloud':True,'receipt_table':'source_diagnostics'},
         'compare': {'cloud':False,'receipt_table':'comparison_assessments'},
         'native_records': {'cloud':True,'receipt_table':'record_readbacks'},
         'source_records': {'cloud':True,'receipt_table':'record_readbacks'},
         'compare_records': {'cloud':False,'receipt_table':'record_comparisons'},
         'reconcile_records': {'cloud':False,'receipt_table':record_aggregate.TABLE}}


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
        if tool in ('bounded_dax','bounded_sql'):
            from .flexible_tools import build
            if not isinstance(payload,dict) or payload.get('model_id')!=model['id']:raise ValueError('Cross-model proposed query')
            compiled.append(build(store,payload,config,tool));cloud+=1
        elif tool in ('native_records','source_records'):
            if not isinstance(payload,dict) or payload.get('model_id')!=model['id']:raise ValueError('Cross-model readback')
            compiled.append(record_readback.build(store,payload,config,tool));cloud+=1
        elif tool=='reconcile_records':
            fields(payload,['native_step','source_step','native_records_step','source_records_step','measure_id','record_mapping_id'])
            for key,expected in [('native_step','native'),('source_step','source'),('native_records_step','native_records'),('source_records_step','source_records')]:
                index=payload[key]
                if type(index) is not int or not 0<=index<ordinal or actions[index]['tool']!=expected:raise ValueError('Reconciliation requires four prior typed reads')
            review=record_bindings.read(store,model['id'],payload['record_mapping_id'])
            record_bindings.validate(store,model['id'],review['body'],config)
            if review['revocation'] is not None:raise Conflict('Record review revoked')
            if review['body']['measure_id']!=payload['measure_id']:raise ValueError('Review measure differs')
            native=compiled[payload['native_step']]
            if payload['measure_id'] not in native['measure_ids'] or native['dimension_id'] is not None:raise ValueError('Reconciliation requires selected scalar')
            for key in ('native_records_step','source_records_step'):
                if actions[payload[key]]['input'].get('record_mapping_id')!=review['id']:raise ValueError('Record reads must pin reconciliation review')
            compiled.append(payload)
        elif tool=='compare_records':
            fields(payload,['native_step','source_step','column_bindings','filter_bindings'])
            for key,expected in [('native_step','native_records'),('source_step','source_records')]:
                index=payload[key]
                if type(index) is not int or not 0<=index<ordinal or actions[index]['tool']!=expected:raise ValueError('Comparison requires prior record reads')
            record_comparison.validate_projection(compiled[payload['native_step']],compiled[payload['source_step']],
                                                 payload['column_bindings'],payload['filter_bindings'])
            compiled.append(payload)
        elif tool in ('native','source'):
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
