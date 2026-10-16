"""Build support only from a trusted facade ledger; never run the pipeline.

The model selects an outcome, not evidence roles. Existing outcome/support gates
remain authoritative. Missing producers refuse rather than filling proof gaps.
This produces a support candidate; coverage/narrative validation still precedes
user delivery in the agent runtime.
"""
import copy
from .onboarding import digest
from .process_debugging import _answer,_observation,NoValue
from .process_outcomes import OUTCOMES,REQUIRED_ROLES,BOUNDARY_ATTRIBUTIONS
from .surface_difference import grade,BOUNDARY_GRADES
from .snapshot_attestation import comparison as snapshot,limitation
from .assessment_support import validate


def build(tools,outcome,target_id,citations):
 if outcome not in OUTCOMES:raise ValueError('Unsupported terminal outcome')
 if not isinstance(citations,list) or not citations or len(citations)>200 or any(not isinstance(i,str) for i in citations):raise ValueError('Terminal evidence citations required')
 calls=tools.tool_ledger
 known=set(calls)|{i for call in calls.values() for i in call['receipt_evidence_ids']}
 if set(citations)-known:raise ValueError('Terminal cites unknown or unpersisted evidence')
 selected={key:value for key,value in calls.items() if key in citations or set(value['receipt_evidence_ids'])&set(citations)}
 if any(call['arguments'].get('target_id')!=target_id for call in selected.values()):raise ValueError('Terminal evidence target differs')
 resolved=tools._target(target_id)
 if resolved is None:raise ValueError('Terminal target unresolved')
 measure,scope=resolved;path=tools._paths.get(measure)
 if path is None:raise ValueError('Terminal path was not obtained')
 key=digest(scope);layers=path['layers'];observations=[];probes={}
 cited_reads={i for call in selected.values() for i in call['receipt_evidence_ids']}
 def add(obs,*roles):
  if not isinstance(obs,dict) or not obs.get('id'):return
  if any(existing['id']==obs['id'] for existing in observations):return
  observations.append(_observation(copy.deepcopy(obs),*roles))
 for call in selected.values():
  if call['tool']=='lineage' and call['arguments'].get('target_id')==target_id:
   evidence=path.get('evidence')
   if evidence:
    evidence=copy.deepcopy(evidence)
    if path.get('system_of_record'):evidence.update(resolved_source_path=copy.deepcopy(path),expected_records=scope.get('expected_records',[]))
    add(evidence,'path','established')
  data=call['result'].get('data',{})
  # Existing typed observations keep their producer-owned roles unchanged.
  for observation in data.get('observations',[]):
   if isinstance(observation,dict) and observation.get('id'):add(observation)
 for index,layer in enumerate(layers):
  probe=tools._probe_ledger.get((measure,key,layer['id']))
  if probe is None or not probe.evidence or probe.evidence['id'] not in cited_reads:continue
  probes[layer['id']]=probe
  evidence=copy.deepcopy(probe.evidence);evidence.update(execution_surface=copy.deepcopy(probe.execution_surface),surface_report=copy.deepcopy(probe.surface_report),test_purpose='ESTABLISH_BASELINE' if index==0 else 'REPRODUCE_MEASURE')
  add(evidence,*(['baseline','established'] if probe.status=='OBSERVED' else ['established']))
 comparisons=[];connected=True;deepest=layers[0]['id'] if layers else 'unresolved path';step=0
 baseline={'status':'NOT_ESTABLISHED','layer':None,'reason':'No cited attested presentation probe was obtained.','evidence_ids':[]}
 top=probes.get(layers[0]['id']) if layers else None
 if top is not None and top.status=='OBSERVED':baseline={'status':'ESTABLISHED','layer':top.layer,'reason':None,'evidence_ids':[top.evidence['id']]}
 for index,(upper_layer,lower_layer) in enumerate(zip(layers,layers[1:]),1):
  upper=probes.get(upper_layer['id']);lower=probes.get(lower_layer['id'])
  if upper is None or lower is None or upper.status!='OBSERVED' or lower.status!='OBSERVED':connected=False;continue
  difference=grade(upper.evidence,lower.evidence)
  if difference['grade'] not in BOUNDARY_GRADES:connected=False;continue
  # Faithful scope evidence must come from each actual query receipt, not a
  # model-selected scope label or equal values. Missing context stays unknown.
  contexts=[p.evidence.get('declared_context') for p in (upper,lower)]
  if not isinstance(contexts[0],dict) or contexts[0]!=contexts[1]:connected=False;continue
  obs={'id':'agent-boundary:'+digest({'upper':upper.evidence['id'],'lower':lower.evidence['id']}),'tool':'process','upper_layer':upper.layer,'lower_layer':lower.layer,'comparison_status':'CROSS_SURFACE_VERIFIED','surface_difference':difference,'values_equal':upper.value==lower.value,'upper_evidence_id':upper.evidence['id'],'lower_evidence_id':lower.evidence['id'],'upper_execution_surface':upper.execution_surface,'lower_execution_surface':lower.execution_surface,'upper_surface_attestation':upper.evidence['surface_attestation'],'lower_surface_attestation':lower.evidence['surface_attestation'],'lower_binding_provenance':lower.evidence.get('binding_provenance'),'upper_declared_context':contexts[0],'lower_declared_context':contexts[1]}
  obs['snapshot_attestation']=snapshot(obs,upper.evidence.get('snapshot_identity'),lower.evidence.get('snapshot_identity'))
  add(obs,'comparison',*(['flow_consistency'] if connected and obs['values_equal'] else []));comparisons.append(obs);deepest=lower.layer;step=index
  definition=tools._definition_ledger.get((measure,key,index))
  definition_refs=evidence_ids_for_selected(selected,'read_transformation',target_id,index)
  if definition and definition.get('evidence',{}).get('id') in definition_refs:
   result=definition;ev=copy.deepcopy(result['evidence'])
   if result.get('explains') is True and obs['values_equal'] is False:
    ev.setdefault('judgment',{k:copy.deepcopy(result[k]) for k in ('status','explains','explanation','limitation') if k in result});ev['comparison_id']=obs['id'];add(ev,'transformation_definition','mechanism','established')
  if outcome in BOUNDARY_ATTRIBUTIONS and not obs['values_equal']:
   baseline={'status':'ESTABLISHED','layer':upper.layer,'reason':None,'evidence_ids':[upper.evidence['id']]}
 if outcome in ('CONSISTENT_TO_BOUNDARY','CONSISTENT_TO_SOURCE') and any(c['values_equal'] is not True for c in comparisons):
  raise ValueError('Consistency cannot suppress an observed divergent boundary')
 if outcome=='TRANSFORMATION_LOGIC':
  explained=[c for c in comparisons if not c['values_equal'] and any('transformation_definition' in o.get('process_roles',[]) and o.get('comparison_id')==c['id'] for o in observations)]
  if len(explained)!=1:raise ValueError('Transformation requires one unambiguous producer-supported divergence')
  chosen=explained[0];step=next(i for i,l in enumerate(layers) if l['id']==chosen['lower_layer']);deepest=chosen['lower_layer']
  baseline={'status':'ESTABLISHED','layer':chosen['upper_layer'],'reason':None,'evidence_ids':[chosen['upper_evidence_id']]}
 # No producer grants a role from a requested outcome. For example, timestamps
 # alone do not become freshness, and a retained definition is not absence.
 reason=path.get('missing_comparable_quantity')
 if outcome in ('NO_COMPARABLE_PATH','NO_KNOWN_PATTERN') and not reason:
  barriers=[call['result'].get('reason') for call in selected.values() if call['result'].get('status') in ('UNAVAILABLE','UNDECLARED','NOT_COMPARABLE') and call['result'].get('reason')]
  if not barriers:raise ValueError('Capability-gap outcome requires an actual recorded named barrier')
  reason='Recorded tool barrier: '+str(barriers[0])
 # A resolved path's terminal barrier belongs to its last layer. An agent
 # stopping sooner has not established that barrier at its checked depth.
 stopped=path.get('stopped_by','REACHED') if layers and deepest==layers[-1]['id'] else 'REACHED'
 assessment=_answer(outcome,step,observations,deepest,stopped,baseline,roles=REQUIRED_ROLES[outcome],missing_capability=reason if outcome in ('NO_COMPARABLE_PATH','NO_KNOWN_PATTERN') else None,capabilities=tools.adapter.capabilities())
 compared={(o['upper_layer'],o['lower_layer']) for o in comparisons}
 unchecked=[{'upper_layer':a['id'],'lower_layer':b['id'],
             'reason':'Investigation terminated before this boundary'}
            for a,b in zip(layers,layers[1:]) if (a['id'],b['id']) not in compared]
 if path.get('unresolved_boundary'):unchecked.append(copy.deepcopy(path['unresolved_boundary']))
 assessment['technical_output']['layer_labels']=copy.deepcopy(path.get('layer_labels',{}))
 for row in unchecked:
  from .lineage_limits import technical as lineage_limit
  assessment['limits'].append(lineage_limit(row) or f"Unchecked {row['upper_layer']} -> {row['lower_layer']}: {row['reason']}.")
 for ordinal,obs in enumerate(comparisons,1):
  limit=limitation(obs,ordinal)
  if limit:assessment['limits'].append(limit)
 for output in ('business_output','technical_output'):
  assessment[output]['unverified_boundaries']=copy.deepcopy(unchecked)
  assessment[output]['depth_ceiling']=path.get('max_boundaries',len(layers))
  assessment[output]['checked_depth']=deepest
  assessment[output]['mandatory_limits']=list(assessment['limits'])
 mapping={o['id']:o for o in observations};validate(assessment,mapping)
 return {'assessment':assessment,'observations':mapping,'target_id':target_id,'scope':scope,'requires_coverage_validation':True,'requires_narrative_validation':True,'delivery_validated':False}


def evidence_ids_for_selected(selected,tool,target_id,step):
 return {identity for call in selected.values() if call['tool']==tool and call['arguments'].get('target_id')==target_id and call['arguments'].get('step')==step for identity in call['receipt_evidence_ids']}
