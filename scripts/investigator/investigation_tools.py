"""Read-only agent facade over the existing governed ProcessAdapter contract.

Targets and scopes are registered by trusted intake, never authored by the model.
The required boundary persists/projects/tapes each call before returning it. Native
adapters retain their read admission and receipt/attestation rules. These tools
supply observations, not terminal findings or permission to bypass claim gates.
"""
import copy
from .onboarding import digest
from .process_debugging import Probe, NoValue, attest, applicability
from . import declared_reproduction

TOOLS = {
 'reproduce': ('target_id',),
 'lineage': ('target_id',),
 'probe_layer': ('target_id','layer_id','scope_id'),
 'read_transformation': ('target_id','step'),
 'check_freshness': ('target_id',),
 'compare_reports': ('a','b'),
 'query_source': ('target_id','scope_id'),
}
DESCRIPTIONS = {
 'reproduce':'Evaluate the saved declared report context using target_registry from admitted resolve_ticket, never the raw visual ID. A missing reported figure gives no reproduction verdict, even if within-layer values were read. To measure a quantity without a reported figure, use lineage and probe_layer. Returns named unavailability if context cannot be faithfully evaluated.',
 'lineage':'Read the declared/verified quantity path and its explicit gaps. Metadata reachability does not establish equality or business correctness.',
 'probe_layer':'Evaluate the registered quantity at a resolved path layer under an already admitted scope; no arbitrary SQL or filter expressions.',
 'read_transformation':'Read a retained operation contract for a path step. Returns unavailable rather than manufacturing an operation or causal judgment.',
 'check_freshness':'Read declared load accounting and available timing observations. Does not classify latency or guarantee a shared snapshot.',
 'compare_reports':'Evaluate two registered report targets separately and return their first shared declared path layer. Does not certify equivalent report semantics or causal equality.',
 'query_source':'Read the same registered quantity at the explicitly declared reachable application layer; an undeclared/unreachable source refuses.',
}

def schemas():
 """Provider-independent strict JSON schemas; no free-form native queries."""
 result=[]
 for name,fields in TOOLS.items():
  properties={key:({'type':'integer','minimum':1,'maximum':32} if key=='step' else {'type':'string','minLength':1,'maxLength':300}) for key in fields}
  for key,node in properties.items():
   if key in ('target_id','a','b'):node['description']='Use a key from admitted resolve_ticket.target_registry, not an asset or visual ID.'
   elif key=='scope_id':node['description']='Use the target\'s scope_id from admitted resolve_ticket.scope_registry; scope cannot be changed.'
   elif key=='layer_id':node['description']='Use an exact layer ID from lineage for the registered target.'
  result.append({'name':name,'description':DESCRIPTIONS[name],'parameters':{'type':'object','properties':properties,'required':list(fields),'additionalProperties':False}})
 return result

def unavailable(reason,*,status='UNAVAILABLE',**facts):
 return {'status':status,'reason':reason,'data':facts,'native_evidence_ids':[]}

def evidence_ids(value):
 """Only receipt-bearing structures count, never an asset's bare id."""
 found=[]
 def add(identity):
  if isinstance(identity,str) and identity and identity not in found:found.append(identity)
 def walk(item):
  if isinstance(item,dict):
   for key,child in item.items():
    if key in ('evidence_ids','native_evidence_ids') and isinstance(child,list):
     for identity in child:add(identity)
    elif key=='evidence' and isinstance(child,dict):add(child.get('id'))
    elif key=='observations' and isinstance(child,list):
     for observation in child:
      if isinstance(observation,dict):add(observation.get('id'))
    walk(child)
  elif isinstance(item,list):
   for child in item:walk(child)
 walk(value);return found

class InvestigationTools:
 """`boundary(name,args,operation)` must return a persisted receipt and result.

Receipt IDs use `agent-tool:` to distinguish facade observations from native
attested reads. The caller still runs existing support and coverage validators.
"""
 def __init__(self,adapter,targets,scopes,boundary):
  if not callable(boundary):raise ValueError('Persisted governed tool boundary required')
  if not isinstance(targets,dict) or not isinstance(scopes,dict):raise ValueError('Trusted target/scope registries required')
  self.adapter=adapter;self._targets=copy.deepcopy(targets);self._scopes=copy.deepcopy(scopes);self.boundary=boundary
  self._probe_ledger={};self._paths={};self._definition_ledger={};self.tool_ledger={}
  for target in self._targets.values():
   if not isinstance(target,dict) or set(target)!={'measure_id','scope_id'} or not isinstance(target['measure_id'],str) or target['scope_id'] not in self._scopes:raise ValueError('Target requires resolved measure and registered scope')
  if any(not isinstance(scope,dict) for scope in self._scopes.values()):raise ValueError('Scope registry requires admitted structured scopes')

 def invoke(self,name,arguments):
  if name not in TOOLS:raise ValueError('Unknown investigation tool')
  if not isinstance(arguments,dict) or set(arguments)!=set(TOOLS[name]):raise ValueError('Investigation tool argument shape differs')
  for key,value in arguments.items():
   if key=='step':
    if type(value) is not int or not 1<=value<=32:raise ValueError('Invalid boundary step')
   elif not isinstance(value,str) or not 1<=len(value)<=300:raise ValueError('Invalid registered identity')
  args=copy.deepcopy(arguments)
  receipt=self.boundary(name,args,lambda:self._execute(name,args))
  if not isinstance(receipt,dict) or set(receipt)!={'receipt_id','result'} or not isinstance(receipt['receipt_id'],str) or not receipt['receipt_id'].startswith('agent-tool:') or not receipt['receipt_id'][11:]:raise ValueError('Tool result requires persisted facade evidence identity')
  result=receipt['result']
  if not isinstance(result,dict) or result.get('status') not in ('AVAILABLE','COMPLETED','UNAVAILABLE','UNDECLARED','NOT_COMPARABLE'):raise ValueError('Invalid persisted tool result')
  result=copy.deepcopy(result);native=evidence_ids(result)
  self.tool_ledger[receipt['receipt_id']]={'tool':name,'arguments':copy.deepcopy(args),'result':copy.deepcopy(result),'receipt_evidence_ids':list(native)}
  attested=[p.evidence['id'] for p in self._probe_ledger.values() if p.evidence and p.evidence['id'] in native and p.evidence.get('surface_attestation',{}).get('status') in ('MATCHED','PARTIAL')]
  return {**result,'tool':name,'facade_evidence_id':receipt['receipt_id'],'native_evidence_ids':native,'attested_read_evidence_ids':list(dict.fromkeys(attested)),'evidence_ids':[receipt['receipt_id'],*native],'finding_authority':False}

 def _execute(self,name,args):
  from .context_search import MeasurePathLimit
  try:return self._dispatch(name,args)
  except MeasurePathLimit as exc:return unavailable('RESOLVER_SIZE_BOUND',characters=exc.characters,limit=exc.limit)

 def terminal_support(self,outcome,target_id,citations):
  from .agent_tool_support import build
  receipt=self.boundary('terminal_support',{'outcome':outcome,'target_id':target_id,'citations':copy.deepcopy(citations)},lambda:build(self,outcome,target_id,citations))
  if not isinstance(receipt,dict) or set(receipt)!={'receipt_id','result'} or not isinstance(receipt['receipt_id'],str) or not receipt['receipt_id'].startswith('agent-tool:'):raise ValueError('Terminal support requires persisted derived evidence')
  return {**receipt['result'],'support_receipt_id':receipt['receipt_id']}

 def _target(self,identity,scope_id=None):
  target=self._targets.get(identity)
  if target is None:return None
  chosen=scope_id or target['scope_id']
  # No scope substitution: the agent cannot alter admitted scope by selecting
  # another target's registered scope, even if it happens to yield a match.
  if chosen!=target['scope_id']:return None
  return target['measure_id'],copy.deepcopy(self._scopes[chosen])

 def _path(self,measure):
  if 'resolve_measure_path' not in applicability(self.adapter)['available']:return None
  path=self.adapter.resolve_path(measure)
  if not isinstance(path,dict) or not isinstance(path.get('layers'),list):raise ValueError('Malformed adapter path')
  path=self._admit_path(copy.deepcopy(path));self._paths[measure]=copy.deepcopy(path)
  return path

 def _admit_path(self,path):
  # Same mandatory estate/verified-inference admission used by vertical().
  estate=getattr(self.adapter,'config',{}).get('_estate',{})
  layers=path['layers'];declared={r['asset_id']:r for r in estate.get('layers',[])}
  terminal=path.get('system_of_record') or {}
  for i,layer in enumerate(layers):
   reason=None;binding=layer.get('binding') or {}
   if estate and layer['id'] not in declared:reason='The layer is not declared in the estate manifest; no read was attempted.'
   elif estate and not declared[layer['id']]['reachable']:reason='The layer is configured unreachable in the estate manifest; no read was attempted.'
   if terminal.get('reachable') is False and terminal.get('asset_id')==layer['id']:reason='The declared system of record is configured unreachable; no application read was attempted.'
   if binding.get('provenance')=='INFERRED_FROM_CODE':
    from .lineage_binding import revalidate_verification
    proof=binding.get('lineage_verification')
    if not estate or proof is None:reason='Inferred code lineage has no authorised original sampled verification evidence.'
    else:
     checked=revalidate_verification(proof);logical={x['asset_id']:x['id'] for x in estate['layers']}
     edge={'from_layer':logical.get(layer['id']),'to_layer':logical.get(layers[i-1]['id']) if i else None}
     locations=[b for b in estate['lineage'].get('code_locations',[]) if b['may_infer_from_code'] and all(b[k]==v for k,v in edge.items())]
     permitted=any(binding.get('code_location') in b['locations'] for b in locations)
     current=[r for r in path.get('evidence',{}).get('code_source_receipts',[]) if all(r.get(k)==v for k,v in (binding.get('code_location') or {}).items())]
     fresh=len(current)==1 and current[0].get('content_hash')==checked['proposal']['location']['content_hash']
     if checked['status']!='VERIFIED' or checked['proposal']['boundary']!=edge or not estate['lineage']['inference']['enabled'] or not permitted or not fresh:reason='Code inference is not authorised and verified at this declared boundary.'
   if reason:
    path.update(stopped_by='NO_ACCESS',missing_comparable_quantity=reason,unresolved_boundary={'upper_layer':layers[i-1]['id'] if i else layer['id'],'lower_layer':layer['id'],'reason':reason})
    layers=layers[:i];path['layers']=layers;break
  ceiling=path.get('max_boundaries',len(layers))
  if type(ceiling) is not int or ceiling<0:raise ValueError('Invalid boundary ceiling')
  if len(layers)>ceiling+1:path.update(layers=layers[:ceiling+1],stopped_by='CAPABILITY_UNAVAILABLE')
  return path

 def _dispatch(self,name,args):
  if name=='compare_reports':return self._compare(args['a'],args['b'])
  resolved=self._target(args['target_id'],args.get('scope_id'))
  if resolved is None:return unavailable('TARGET_OR_SCOPE_UNRESOLVED',status='UNDECLARED')
  measure,scope=resolved;path=self._path(measure)
  if path is None:return unavailable('MEASURE_PATH_CAPABILITY_UNDECLARED',status='UNDECLARED')
  layers=path['layers'];available=set(applicability(self.adapter)['available'])
  if name=='lineage':return {'status':'AVAILABLE','data':{'path':copy.deepcopy(path)},'native_evidence_ids':[]}
  if not layers:return unavailable('NO_DECLARED_QUANTITY_PATH',path=path)
  if name=='reproduce':return self._reproduce(layers[0],measure,scope,available)
  if name=='probe_layer':
   matches=[layer for layer in layers if layer.get('id')==args['layer_id']]
   if len(matches)!=1:return unavailable('LAYER_NOT_ON_RESOLVED_PATH',status='UNDECLARED')
   return self._probe(matches[0],measure,scope,available)
  if name=='query_source':
   declared=path.get('system_of_record')
   if not isinstance(declared,dict) or declared.get('reachable') is False:return unavailable('SYSTEM_OF_RECORD_UNDECLARED_OR_UNREACHABLE',status='UNDECLARED')
   estate=getattr(self.adapter,'config',{}).get('_estate',{})
   roles={entry.get('asset_id'):entry.get('role') for entry in getattr(self.adapter,'config',{}).get('layer_roles',[])}
   roles.update({entry.get('asset_id'):entry.get('role') for entry in estate.get('layers',[])})
   matches=[layer for layer in layers if layer.get('id')==declared.get('asset_id') and roles.get(layer.get('id'))=='APPLICATION']
   if len(matches)!=1:return unavailable('APPLICATION_LAYER_NOT_DECLARED_ON_PATH',status='UNDECLARED')
   return self._probe(matches[0],measure,scope,available)
  if name=='read_transformation':
   step=args['step']
   if step>=len(layers):return unavailable('BOUNDARY_NOT_ON_RESOLVED_PATH',status='UNDECLARED')
   upper=layers[step-1];lower=layers[step];key=digest(scope)
   probes=[self._probe_ledger.get((measure,key,layer['id'])) for layer in (upper,lower)]
   if 'transformation_definition' in available and all(p is not None and p.status=='OBSERVED' for p in probes):
    result=self.adapter.transformation_definition({'upper':copy.deepcopy(upper),'lower':copy.deepcopy(lower),'index':step,'upper_probe':probes[0],'lower_probe':probes[1]})
    if not isinstance(result,dict):raise ValueError('Malformed transformation result')
    self._definition_ledger[(measure,key,step)]=copy.deepcopy(result)
    return {'status':'AVAILABLE' if result.get('evidence') else 'UNAVAILABLE','data':copy.deepcopy(result),'native_evidence_ids':[]}
   contract=lower.get('quantity_contract')
   if not isinstance(contract,dict) or not contract.get('definition_asset_id') or not contract.get('definition_hash'):return unavailable('RETAINED_OPERATION_CONTRACT_UNAVAILABLE',status='UNDECLARED')
   return {'status':'AVAILABLE','data':{'upper_layer':upper['id'],'lower_layer':lower['id'],'quantity_contract':copy.deepcopy(contract),'binding_provenance':lower.get('binding_provenance'),'causal_judgment':None,'judgment_unavailability':'Adjacent attested quantities have not been obtained.'},'native_evidence_ids':[]}
  if name=='check_freshness':
   observations=[];missing=[]
   if 'refresh_timing' in available:observations.append({'kind':'REFRESH_TIMING','result':self.adapter.refresh_timing(path)})
   else:missing.append('refresh_timing')
   if 'source_delivery' in available:
    boundaries=self.adapter.freshness_boundaries(path) if hasattr(self.adapter,'freshness_boundaries') else [{'upper':u,'lower':l,'index':i} for i,(u,l) in enumerate(zip(layers,layers[1:]),1)]
    for boundary in boundaries:observations.append({'kind':'SOURCE_DELIVERY','result':self.adapter.source_delivery(boundary,copy.deepcopy(scope))})
   else:missing.append('source_delivery')
   if not observations:return unavailable('FRESHNESS_CAPABILITIES_UNDECLARED',status='UNDECLARED',missing_capabilities=missing)
   return {'status':'AVAILABLE','data':{'observations':observations,'missing_capabilities':missing,'latency_classification':None,'snapshot_alignment':'NOT_ESTABLISHED'},'native_evidence_ids':[]}
  raise ValueError('Unreachable tool dispatch')

 def _probe(self,layer,measure,scope,available):
  if 'evaluate_scoped_quantity' not in available:return unavailable('SCOPED_QUANTITY_CAPABILITY_UNDECLARED',status='UNDECLARED')
  probe=self.adapter.evaluate(copy.deepcopy(layer),measure,copy.deepcopy(scope))
  if not isinstance(probe,Probe):raise ValueError('Adapter evaluation must return Probe')
  probe=attest(probe)
  self._probe_ledger[(measure,digest(scope),layer['id'])]=copy.deepcopy(probe)
  data={'layer':probe.layer,'value_state':probe.value_state,'value':None if isinstance(probe.value,NoValue) else copy.deepcopy(probe.value),'evidence':copy.deepcopy(probe.evidence),'failure':copy.deepcopy(probe.failure),'execution_surface':copy.deepcopy(probe.execution_surface),'surface_report':copy.deepcopy(probe.surface_report),'surface_reportable':list(probe.surface_reportable),'surface_report_types':copy.deepcopy(probe.surface_report_types),'surface_report_binding':probe.surface_report_binding,'reason':probe.reason}
  return {'status':'AVAILABLE' if probe.status=='OBSERVED' else probe.status,'data':data,'native_evidence_ids':[]}

 def _reproduce(self,layer,measure,scope,available):
  if declared_reproduction.CAPABILITY not in available:return unavailable('DECLARED_CONTEXT_REPRODUCTION_UNDECLARED',status='UNDECLARED')
  result=declared_reproduction.run(self.adapter,copy.deepcopy(layer),measure,copy.deepcopy(scope))
  # Preserve exact consumer refusals, inventory validation and assumption limits.
  return {'status':result['status'],'data':result,'reason':result.get('reason'),'native_evidence_ids':[]}

 def _compare(self,a,b):
  left=self._target(a);right=self._target(b)
  if left is None or right is None:return unavailable('REPORT_TARGET_UNRESOLVED',status='UNDECLARED')
  if not left[1].get('report_binding') or not right[1].get('report_binding'):return unavailable('REPORT_BINDINGS_REQUIRED',status='UNDECLARED')
  lp=self._path(left[0]);rp=self._path(right[0])
  if lp is None or rp is None or not lp['layers'] or not rp['layers']:return unavailable('REPORT_PATH_UNAVAILABLE',status='UNDECLARED')
  available=set(applicability(self.adapter)['available'])
  lresult=self._reproduce(lp['layers'][0],*left,available);rresult=self._reproduce(rp['layers'][0],*right,available)
  shared=next((layer['id'] for layer in lp['layers'] if layer['id'] in {v['id'] for v in rp['layers']}),None)
  return {'status':'AVAILABLE','data':{'a':lresult,'b':rresult,'first_shared_declared_layer':shared,'cross_report_equivalence':'NOT_ESTABLISHED','comparison_verdict':None},'native_evidence_ids':[]}
