"""Compile each neutral candidate under its complete retained scope.

Offline scoring uses sealed, exact-statement receipts; it never uses a golden
value or a reported figure as a result. Missing receipts are not measurable.
"""
from ..onboarding import digest
from ..form_candidates import NotMeasurable
from ..declared_reproduction import compose
from ..process_quantity import quantity
from ..process_debugging import attest_surface
from .microsoft_process import SEMANTIC_REPORT,SEMANTIC_ENGINE,semantic_self_report


def plan(model,candidate):
    from .report_predicates import quantity_query
    from ..read_address import baseline
    restrictions=compose(candidate['declaration']['restrictions']+[
        {'field_id':f['column_id'],'operator':'IN','values':f['values']} for f in candidate['scope']['filters']])
    query=semantic_self_report(quantity_query(model,candidate['measure_id'],restrictions))
    return {'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],
            'query':query,'max_rows':20,'surface_report':SEMANTIC_REPORT,'read_address':baseline(restrictions)}


def observation(model,config,compiled,result):
    if result.get('status')!='COMPLETED' or result.get('result',{}).get('completeness')!='COMPLETE_RESPONSE':
        raise NotMeasurable('Candidate quantity query did not return a complete response')
    surface={'engine':SEMANTIC_ENGINE,'connection':model['workspace'],'object':model['native_id'],
             'identity':config['fabric']['native_reader']['account']}
    attestation=attest_surface(surface,result['result'].get('surface_report'),('identity','engine','object'))
    value=quantity(result['result']['rows'],SEMANTIC_REPORT)
    if isinstance(value,dict) and set(value)=={'quantity'}:value=value['quantity']
    if value is not None and not isinstance(value,str):raise NotMeasurable('Candidate result is not a scalar')
    return {'status':'OBSERVED','complete':True,'value':value,'receipt_id':result['id'],
            'query_hash':digest(compiled),'execution_surface':surface,'attestation':attestation}


def install(workspace):
    def reader(candidate):
        from ..flexible_tools import run
        model=workspace.store.get(candidate['model_id']);request=plan(model,candidate)
        counter=getattr(workspace,'_form_candidate_count',0)
        if counter>=workspace.dynamic_read_limit:raise NotMeasurable('Per-form diagnostic cap reached')
        workspace._form_candidate_count=counter+1
        session=workspace._form_candidate_session
        result=workspace.agent.governor.metered_read(session,'candidate:'+str(counter),
            lambda:run(workspace.store,request,workspace.agent.config,'bounded_dax',workspace.agent.runtime.native_transport))
        return observation(model,workspace.agent.config,request,result)
    workspace.form_candidate_reader=reader


def retained_reader(workspace):
    """Read-only offline port; exact compiled statement/context and sealed receipt."""
    def reader(candidate):
        import json
        from ..receipt_integrity import verify
        model=workspace.store.get(candidate['model_id']);request=plan(model,candidate)
        matches=[]
        with workspace.store.connect() as db:
            for row in db.execute("SELECT id,request,result FROM flexible_diagnostics WHERE status='COMPLETED' AND model_id=?",(model['id'],)):
                saved=json.loads(row['request']);p=saved['plan']
                if p.get('query')!=request['query'] or p.get('context_id')!=request['context_id']:continue
                if saved.get('workspace')!=model['workspace'] or saved.get('native_model_id')!=model['native_id']:continue
                if verify(db,'bounded_dax',row['id'])['state']!='SEALED':continue
                body=json.loads(row['result'])
                if body.get('completeness')!='COMPLETE_RESPONSE':continue
                matches.append({'id':row['id'],'status':'COMPLETED','result':body})
        if not matches:raise NotMeasurable('No sealed receipt for the exact compiled candidate/context')
        probes=[observation(model,workspace.agent.config,request,r) for r in matches]
        if len({digest(p['value']) for p in probes})!=1:
            raise NotMeasurable('Retained exact-statement receipts disagree; fixture snapshot not established')
        chosen=probes[0];chosen['offline_provenance']='SEALED_EXACT_STATEMENT_RECEIPT'
        return chosen
    return reader
