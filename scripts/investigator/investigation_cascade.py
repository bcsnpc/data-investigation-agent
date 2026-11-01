"""Escalate unresolved reasoning without resetting evidence, caps or time."""
from copy import deepcopy
from .estate_graph_contract import canonical


class Cascade:
    def __init__(self, engine, fallback_model):
        self.engine,self.fallback_model=engine,fallback_model

    def __getattr__(self,name):return getattr(self.engine,name)

    def run(self):
        engine=self.engine;limit=engine.tool_limit;deadline=engine.deadline_seconds
        # Divide the existing allowance, rather than grant each model a new one.
        engine.tool_limit=min(7,max(1,limit-1));engine.deadline_seconds=min(deadline,450)
        first=engine.run()
        stages=[{'model':engine.model.model,'status':first['status'],
                 'model_calls':first.get('model_calls',0),'tools_used':first.get('tools_used',0)}]
        outcome=first
        if first['status'] in ('UNRESOLVED','NEEDS_INPUT') and not engine.state.get('pending'):
            # Original model/provider messages remain on the capture and in the
            # evidence store. Opaque model-specific reasoning state is never
            # resent as another model's reasoning input.
            engine.state['outcome']=None;engine.state['turn']=None
            evidence=[{'id':key,'kind':value.get('kind'),'tool':value.get('tool')}
                      for key,value in engine.state['evidence'].items()]
            engine.state['messages']=[{'role':'user','content':canonical({
                'escalation_reason':first.get('stop',first.get('question')),
                'evidence_inventory':evidence,
                'queries':[{'id':q['id'],'layer':q['layer'],'text':q['text'],'status':q['status']}
                           for q in engine.queries.records],
                'instruction':'Continue this same case. Fetch existing evidence by ID; do not repeat reads or infer an unread result.'})}]
            engine.tool_limit=limit;engine.deadline_seconds=deadline
            engine.model=self.fallback_model()
            engine.save()
            outcome=engine.run()
            stages.append({'model':engine.model.model,'status':outcome['status'],
                           'model_calls':outcome.get('model_calls',0)-stages[0]['model_calls'],
                           'tools_used':outcome.get('tools_used',0)-stages[0]['tools_used']})
        engine.tool_limit=limit;engine.deadline_seconds=deadline
        result=deepcopy(outcome)
        result['investigation_cascade']={'stages':stages,'escalated':len(stages)==2,
            'resolved_by_model':stages[-1]['model']if result['status']=='ANSWERED'else None,
            'shared_tool_limit':limit,'shared_deadline_seconds':deadline}
        return result
