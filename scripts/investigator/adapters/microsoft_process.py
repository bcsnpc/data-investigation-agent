"""Microsoft Fabric/Power BI/Azure SQL adapter for the neutral process engine."""
from uuid import uuid4
from .. import context_search
from ..flexible_tools import run as run_query
from ..model_context import assets
from ..process_debugging import Probe


class MicrosoftProcessAdapter:
    def __init__(self,store,config,model,execute_native,execute_source):
        self.store,self.config,self.model=store,config,model
        self.execute_native,self.execute_source=execute_native,execute_source
        self._paths={}

    def capabilities(self):
        return {'resolve_measure_path','evaluate_scoped_quantity'}

    def resolve_path(self,measure_id):
        if measure_id in self._paths:return self._paths[measure_id]
        result=context_search.measure_path(self.store,self.model,measure_id)
        metadata=result;measure=metadata['measure']
        gaps=metadata.get('gaps',[])
        path={'layers':[{'id':measure['parent_id'],'kind':'presentation','measure':measure}],
                'boundary':measure['parent_id'],
                'stopped_by':'NO_LINEAGE' if gaps else 'REACHED',
                'evidence':{'id':'path-'+str(uuid4()),'tool':'context','completeness':'PARTIAL' if gaps else 'COMPLETE_RESPONSE',
                            'metadata':metadata}}
        self._paths[measure_id]=path
        return path

    def presentation_freshness(self,path,scope):
        return {'status':'UNAVAILABLE'}

    def evaluate(self,layer,measure_id,scope):
        measure=next(a for a in assets(self.model['context']) if a['id']==measure_id)
        name=measure['name'].replace(']',']]')
        query=f'EVALUATE ROW("baseline", [{name}])'
        if scope.get('filters'):
            from ..native_diagnostics import build as build_native
            native_plan={'model_id':self.model['id'],'revision':self.model['revision'],
                'context_id':self.model['context_id'],'measure_ids':[measure_id],
                'filters':scope['filters'],'dimension_id':None,'include_dependencies':False}
            query=build_native(self.model,native_plan)['query']
        plan={'model_id':self.model['id'],'revision':self.model['revision'],
              'context_id':self.model['context_id'],'query':query,'max_rows':20}
        result=run_query(self.store,plan,self.config,'bounded_dax',self.execute_native)
        if result['status']!='COMPLETED':
            return Probe('UNAVAILABLE',layer['id'],reason='The presentation reader could not establish a baseline.',query=query)
        rows=result['result']['rows'];value=rows[0] if len(rows)==1 else rows
        return Probe('OBSERVED',layer['id'],evidence={'id':result['id'],'tool':'bounded_dax',
            'completeness':result['result']['completeness'],'values':rows,
            'request_hash':result['request_hash'],'test_purpose':'ESTABLISH_BASELINE',
            'measure_id':measure_id,'dimension_id':None},value=value,query=query)

    def presentation_context(self,boundary,scope):return {'explains':False}
    def transformation_definition(self,boundary):return {'explains':False}
    def job_history(self,boundary):return {'status':'UNAVAILABLE'}
    def ingestion(self,path,scope):return {'status':'UNAVAILABLE'}
