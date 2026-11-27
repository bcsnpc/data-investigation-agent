"""Saved-response investigation replay prototype. Never dispatches HTTP/SQL/model calls."""
import sys,json,copy,os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,os.environ.get('DIA_R27_REPLAY_CODE_ROOT','scripts'))
from investigator.ai_investigation import Investigator
from investigator.investigative_queries import Queries
from investigator.investigation_read_tools import ReadTools
from investigator.run_capture import record_value
from investigator.estate_graph_contract import canonical
class Checkpoint:
 def load(self):return None
 def save(self,state):self.state=copy.deepcopy(state)
def replay(indexfile, *, outcome_override=None, records_override=None, catalog_override=None, observe=None):
 root=Path('.local/round-twenty-seven');index=json.loads(indexfile.read_bytes()) if records_override is None else {};records=[]
 if records_override is None:
  for ref in index['source_batches']:
   records+=record_value((root/'free-models/replay-inputs'/(ref['sha256']+'.json')).read_bytes(),ref.get('encoding'))['records']
  records.sort(key=lambda x:int(x['id'].rsplit(':',1)[1]));records=[x['value']for x in records]
 else:records=copy.deepcopy(records_override)
 outcome=outcome_override or next((v for v in reversed(records)if isinstance(v.get('case'),dict)and 'context'in v['case']),None)
 if not outcome or not isinstance(outcome.get('case'),dict) or 'context'not in outcome['case']:return {'status':'NO_INVESTIGATION_CASE','case':indexfile.name,'before':outcome.get('status') if outcome else None}
 case=outcome['case'];context=copy.deepcopy(case['context']);layers=context['layers'];savedqueries=case['queries']
 evidence=list(case['evidence'].values());restored={b['id']:v['response'] for v in evidence if v.get('kind')=='MODEL_RESPONSE' for b in v['response'].get('content',[])if b.get('type')=='tool_use'}
 raw=[v.get('body',v.get('response',{}))for v in records if v.get('event')=='REASONING_RESPONSE' and isinstance(v.get('body',v.get('response')),dict)];responses=[];investigation_started=False
 for body in raw:
  calls=[b for b in body.get('content',[])if b.get('type')=='tool_use']
  if any(b['id']in restored for b in calls):investigation_started=True
  if not investigation_started:continue
  responses.append(copy.deepcopy(restored.get(calls[0]['id'],body)if calls else body))
 used=[];queries=None;pending_query={};missing=[]
 def execute(layer,bound,**kwargs):
  matches=[q for q in savedqueries if q['layer']==layer and q.get('text')==pending_query.get('text') and q.get('asset_ids',[])==bound.get('asset_ids',[]) and q.get('parameters',[])==bound.get('parameters',[])]
  if not matches:
   missing.append('SAVED_NATIVE_QUERY_NOT_AVAILABLE');raise RuntimeError('SAVED_NATIVE_QUERY_NOT_AVAILABLE')
  q=matches[0];used.append(q['id'])
  if q['status']!='SUCCEEDED':raise RuntimeError(q.get('error','Saved native error'))
  return copy.deepcopy(q['result'])
 def save_query(event):
  if event.get('event')=='QUERY_DISPATCH':pending_query.update(event['query'])
 queries=Queries(layers,execute=execute,reserve=lambda *a:None,save=save_query)
 toolsaved=[v for v in evidence if v.get('tool')]
 def savedtool(name,args):
  def equivalent(value):
   value=copy.deepcopy(value)
   if name=='get_lineage':
    if value.get('operation')=='PATH':value.pop('operation')
    if value.get('words')=='':value.pop('words')
   return value
  matches=[v['result']for v in toolsaved if v['tool']==name and equivalent(v['arguments'])==equivalent(args)]
  if not matches:
   missing.append('SAVED_READ_NOT_AVAILABLE:'+name);raise RuntimeError('SAVED_READ_NOT_AVAILABLE:'+name)
  return copy.deepcopy(matches[0])
 graph=SimpleNamespace(definition_of=lambda node:savedtool('get_definition',{'node':node}),path_to_source=lambda node:savedtool('get_lineage',{'node':node}).get('path'),calculation_path=lambda node:savedtool('get_lineage',{'node':node}).get('path'))
 graph.explore=lambda **args:savedtool('get_lineage',args)
 catalogs=[catalog_override] if catalog_override else [json.loads(p.read_bytes())for p in (root/'free-models/catalogs').glob('*.json')]
 selected=context['intake'].get('report')or context['intake'].get('table')or context['intake'].get('measure')
 candidates=next((g for g in catalogs if any(n['id']==selected for n in g['nodes'])),None)
 reads=ReadTools(candidates=candidates,graph=graph,path=context['path'],queries=queries,intake=context['intake'],job_runs=lambda node:savedtool('get_job_runs',{'node':node}),refresh_history=lambda node:savedtool('get_refresh_history',{'node':node}),security_definitions=lambda node:savedtool('get_security_definitions',{'node':node}))
 if context.get('candidate_inventory'):reads.target_inventory=context['candidate_inventory']
 def registry():
  tools=reads.registry()
  if any(v['tool']=='lookup_screenshot'for v in toolsaved):
   from investigator.ai_investigation import schema
   def screenshot(args):
    result=savedtool('lookup_screenshot',args)
    for read in result.get('reads',[]):
     prior=next((q for q in savedqueries if q['id']==read.get('query_id')),None)
     if prior:
      current=queries.run(prior['layer'],prior['text'],kind='dax'if layers[prior['layer']]['dialect']=='DAX'else'sql',purpose=prior['purpose'])
      current=current.get('record',current);read['query_id']=current.get('id',read.get('query_id'))
    return result
   tools['lookup_screenshot']={'description':'Replay retained private-helper boundary and its saved native reads; opaque model bodies were never recorded.', 'schema':schema({}),'run':screenshot}
  return tools
 position=[0];phases=[];format_boundary=[]
 def complete(**kwargs):
  if observe:observe(kwargs,position[0])
  offered={t['name']for t in kwargs['tools']}
  if position[0]>=len(responses):
   if offered=={'evaluate_delivery'} and format_boundary:
    phases.append({'same_saved_malformed_checker_response_replayed_for_bounded_format_retry':True,'not_an_observed_later_response':True})
    return copy.deepcopy(format_boundary[-1])
   if outcome.get('status')=='BLOCKED' and isinstance(outcome.get('stop'),str):
    from investigator.model_spend import SpendHold
    from investigator.usage_governance import UsageHold
    from investigator.live_gateway import GatewayDenied
    for kind in (SpendHold,UsageHold,GatewayDenied):
     if outcome['stop'].startswith(kind.__name__+':'):raise kind(outcome['stop'].split(':',1)[1].strip())
   missing.append('SAVED_MODEL_RESPONSES_EXHAUSTED');raise RuntimeError('SAVED_MODEL_RESPONSES_EXHAUSTED')
  if len(offered)==1 and (offered <= {'evaluate_delivery','repair_delivery'} or any(b.get('name')=='submit_finding'for b in responses[position[0]].get('content',[])if b.get('type')=='tool_use')):
   probe=position[0]
   while probe<len(responses):
    names={b.get('name')for b in responses[probe].get('content',[])if b.get('type')=='tool_use'}
    if names and names<=offered:
     if probe!=position[0]:phases.append({'superseded_local_drafts_skipped':probe-position[0],'reason':'Current deterministic formatting no longer needs those model-only delivery turns'})
     position[0]=probe;break
    if not names:break
    if not names<={'submit_finding','evaluate_delivery','repair_delivery'}:
     if not names<={'get_definition','get_evidence'}:break
     from investigator.delivery_references import calculation_measure
     draft=json.loads(kwargs['messages'][0]['content']).get('draft',{})
     selected=calculation_measure(context,draft)
     def already_retained(call):
      args=call['input']
      if call['name']=='get_definition':return bool(selected and args.get('node')==selected)
      prior=case['evidence'].get(args.get('id'),{})
      if prior.get('tool')=='get_definition':return bool(selected and prior.get('arguments',{}).get('node')==selected)
      asset=next((n.get('properties',{}).get('asset_id')for n in context['path']['nodes']if n['id']==selected),None)
      return bool(asset and prior.get('kind')=='RETAINED_DEFINITION_REFERENCE'and prior.get('asset_id')==asset)
     if not all(already_retained(b)for b in responses[probe]['content']if b.get('type')=='tool_use'):break
    probe+=1
  value=responses[position[0]];position[0]+=1
  phases.append({'requested_tools':list(offered),'saved_tools':[b.get('name')for b in value.get('content',[])if b.get('type')=='tool_use'],'repair_reason':json.loads(kwargs['messages'][0]['content']).get('reason')if kwargs['system'].startswith('Repair the delivery')else None})
  for b in value.get('content',[]):
   if b.get('type')=='tool_use'and b['name']not in offered:
    missing.append('REPLAY_TOOL_PHASE_DIVERGENCE:'+b['name']);raise RuntimeError('REPLAY_TOOL_PHASE_DIVERGENCE:'+b['name'])
  def remap(item):
   if isinstance(item,str):
    prior=next((q for q in savedqueries if q['id']==item),None)
    if prior:
     matched=next((q for q in queries.records if q['layer']==prior['layer'] and q['text']==prior['text']),None)
     if matched:return matched['id']
   if isinstance(item,str) and item in case['evidence'] and item not in engine.state['evidence']:
    original=case['evidence'][item]
    for key,current in engine.state['evidence'].items():
     if original.get('tool') and current.get('tool')==original['tool'] and current.get('arguments')==original.get('arguments'):return key
     if original.get('kind') and original.get('kind')==current.get('kind') and original==current:return key
     if original.get('tool')=='get_definition' and current.get('kind')=='RETAINED_DEFINITION_REFERENCE':
      from investigator.retained_definition_evidence import resolve
      node=next((n for n in context['path']['nodes']if n['id']==original.get('arguments',{}).get('node')),None)
      if node and node.get('properties',{}).get('asset_id')==current.get('asset_id') and resolve(current,context)['content']==original.get('result',{}).get('content'):return key
     if original.get('kind')=='RETAINED_DEFINITION_REFERENCE' and current.get('kind')==original['kind'] and all(original.get(k)==current.get(k) for k in ('asset_id','content_hash','name')):return key
   if isinstance(item,list):return [remap(v)for v in item]
   if isinstance(item,dict):return {k:remap(v)for k,v in item.items()}
   return item
  mapped=remap(copy.deepcopy(value))
  if offered=={'evaluate_delivery'}:
   from investigator.delivery_evaluator import SCHEMA
   from jsonschema import Draft202012Validator
   calls=[b for b in mapped.get('content',[])if b.get('type')=='tool_use']
   if len(calls)!=1 or list(Draft202012Validator(SCHEMA).iter_errors(calls[0].get('input',{}))):format_boundary.append(copy.deepcopy(mapped))
  if os.environ.get('DIA_R27_REPLAY_DEBUG') and (offered <= {'evaluate_delivery','repair_delivery'} or any(b.get('name')=='submit_finding'for b in responses[position[0]].get('content',[])if b.get('type')=='tool_use')):
   with Path(os.environ['DIA_R27_REPLAY_DEBUG']).open('a',encoding='utf-8')as stream:
    stream.write(json.dumps({'case':indexfile.name,'packet':json.loads(kwargs['messages'][0]['content']),'reply_tools':[b for b in mapped.get('content',[])if b.get('type')=='tool_use']})+'\n')
  return mapped
 checkpoint=Checkpoint()
 try:
  from investigator.regression_features import configured
  flags=next((v['flags']for v in records if v.get('event')=='REGRESSION_FEATURE_CONFIGURATION'),{})
  with configured(flags):
   engine=Investigator(queries=queries,model=SimpleNamespace(complete=complete),read_tools=registry,checkpoint=checkpoint,case_id=case['case_id'],context=context,triage=case['triage'],tool_limit=15,deadline_seconds=900)
   result=engine.run()
  return {'case':indexfile.name,'status':'REPLAY_INCOMPLETE'if missing else'REPLAY_FINISHED','missing_saved_boundaries':list(dict.fromkeys(missing)),'before':outcome.get('status'),'after':result['status'],'saved_responses_used':position[0],'saved_responses_total':len(responses),'bounded_same_saved_format_reply_reuses':sum(bool(p.get('same_saved_malformed_checker_response_replayed_for_bounded_format_retry'))for p in phases),'saved_native_reads':len(used),'stop':result.get('stop'),'query_errors':[q.get('error')for q in queries.records if q['status']=='ERROR']}
 except Exception as e:return {'case':indexfile.name,'status':'REPLAY_FAILURE','error':type(e).__name__,'reason':str(e)[:300],'phases':phases,'saved_responses_used':position[0],'feedback':[b.get('content') for m in getattr(checkpoint,'state',{}).get('messages',[]) if isinstance(m.get('content'),list) for b in m['content'] if b.get('type')=='tool_result' and b.get('is_error')][-3:]}
if __name__=='__main__':
 root=Path('.local/round-twenty-seven/ordered-dev-backtracks');p=next(root.glob('dev03*R17-05*'));print(json.dumps(replay(p),indent=2))
