"""Deterministic receipt selections for an independent conclusion call.

No model preprocessing, raw record rows, trajectory, or directory. Missing facts
remain missing: selection/formatting does not establish semantic truth.
"""
import copy,json,re
from sqlglot import exp
from sqlglot.lineage import lineage
from sqlglot.errors import SqlglotError
from .onboarding import digest,encoded,Conflict
from .receipt_integrity import verify,TABLES
from .process_debugging import _surface_key
from .process_quantity import quantity
from . import declaration_inventory

DISPLAY_ROWS = 2
EXCERPT_CHARACTERS = 2400


def _context_evidence(observation):
 roles=observation.get('process_roles',[])
 if 'presentation_definition' in roles:
  if not isinstance(observation.get('definitions'),list):
   raise Conflict('Presentation-definition receipt requires retained definitions')
  return {'asked':{'operation':'presentation_context'},'result':copy.deepcopy(observation),
          'provenance':{'hash':digest(observation),'derivation':'RETAINED_REPORT_DEFINITION'}}
 if 'declared_context_definition' in roles:
  if not isinstance(observation.get('metadata'),dict):
   raise Conflict('Declared scope receipt requires retained definition metadata')
  return {'asked':observation.get('lookup'),
          'result':{'declared_restrictions':observation['declared_restrictions'],
                    'declaration_provenance':observation['declaration_provenance'],
                    'declarations':declaration_inventory.neutral(
                        declaration_inventory.validate(
                            observation['declaration_inventory'],observation['declared_restrictions']))},
          'provenance':{'hash':digest(observation),'context_version':observation['metadata'].get('context_version')}}
 if 'transformation_definition' in roles and isinstance(observation.get('quantity_contract'),dict):
  contract=observation['quantity_contract']
  if (observation.get('asset_id')!=contract.get('definition_asset_id')
      or observation.get('content_hash')!=contract.get('definition_hash')
      or not isinstance(observation.get('operations'),list)):
   raise Conflict('Declared quantity definition receipt differs')
  from .business_vocabulary import validate_terms
  vocabulary=validate_terms(observation.get('business_vocabulary',{}),contract)
  return {'asked':{'operation':'transformation_definition','asset_id':observation['asset_id']},
          'result':{'operations':observation['operations'],'quantity_contract':contract,
                    'limitation':observation['limitation'],'judgment':observation['judgment'],
                    **({'business_vocabulary':vocabulary} if vocabulary else {})},
          'provenance':{'hash':digest(observation),'content_hash':observation['content_hash']}}
 if isinstance(roles,list) and 'ingestion' in roles:
  from .adapters.microsoft_context_evidence import ingestion_evidence
  result=ingestion_evidence(observation)
  return {'asked':{'operation':'ingestion','asset_id':result['asset_id']},
          'result':result,
          'provenance':{'hash':digest(observation),'derivation':'PROCESS_ADAPTER_INGESTION_RECEIPT'}}
 if 'freshness' in roles and 'direct_source_proof' in observation:
  return {'asked':{'operation':'declared_source_comparison'},
          'result':{k:observation[k] for k in ('direct_source_proof','comparison_id','reader_timing_unavailable','refresh_timing')},
          'provenance':{'hash':digest(observation),'derivation':'DECLARED_SOURCE_COMPARISON'}}
 if 'job_history' in roles:
  runs=observation.get('runs')
  if not isinstance(runs,list) or not runs or any(not isinstance(r,dict) for r in runs):
   raise Conflict('Job-history receipt requires retained run observations')
  return {'asked':{'operation':'job_history'},'result':{'runs':runs},
          'provenance':{'hash':digest(observation),'derivation':'RETAINED_DISCOVERY_JOB_HISTORY'}}
 if not isinstance(observation.get('metadata'),dict):
  raise Conflict('Context lookup/path receipt requires metadata; unsupported context receipt shape')
 return {'asked':observation.get('lookup'),'result':_definition_evidence(observation),
         'provenance':{'hash':digest(observation),'context_version':observation['metadata'].get('context_version')}}


def _definition_evidence(observation):
 m=observation['metadata'];lookup=observation.get('lookup') or {}
 result={'asset_name':m.get('asset',{}).get('name'),'asset_kind':m.get('asset',{}).get('kind'),
         'matching_assets':m.get('total'),'directory_and_schema_omitted':True}
 operation=lookup.get('operation')
 if operation=='content' and m.get('asset_id')==lookup.get('value') and isinstance(m.get('content_hash'),str) and isinstance(m.get('content'),str):
  content=m['content'];shown=content[:EXCERPT_CHARACTERS]
  result['transformation_excerpt']={'text':shown,'source_offset':m.get('offset',0),
      'total_characters':m.get('total_characters',len(content)),
      'displayed_characters':len(shown),'truncated':len(shown)<len(content) or bool(m.get('truncated'))}
 elif operation=='find' and m.get('asset_id')==lookup.get('value') and m.get('needle')==lookup.get('needle') and isinstance(m.get('matches'),list):
  remaining=EXCERPT_CHARACTERS;matches=[]
  for match in m['matches']:
   excerpt=match.get('excerpt')
   if not isinstance(excerpt,str) or remaining<=0:continue
   shown=excerpt[:remaining];remaining-=len(shown)
   matches.append({'source_offset':match.get('offset'),'text':shown,
                   'displayed_characters':len(shown),'truncated':len(shown)<len(excerpt)})
  result['transformation_matches']={'matches':matches,'displayed_matches':len(matches),
      'returned_matches':len(m['matches']),'truncated':len(matches)<len(m['matches']) or
      any(x['truncated'] for x in matches) or bool(m.get('truncated'))}
 else:result['unstructured_metadata_omitted']=True
 return result


def _query_evidence(tool,query,rows):
 facts={};groups={}
 if tool=='bounded_sql':
  for name in (rows[0] if rows else {}):
   try:
    nodes=list(lineage(name,query,dialect='tsql').walk())
    target=facts if any(n.expression.find(exp.AggFunc) is not None for n in nodes) else groups
    target[name]={'type':rows[0][name]['type'],'values':[r[name].get('value') for r in rows[:DISPLAY_ROWS]]}
   except (ValueError,TypeError,KeyError,AttributeError,SqlglotError):pass
 elif tool=='bounded_dax' and re.match(r'\s*EVALUATE\s+ROW\s*\(',query,re.I) and len(rows)==1:
  facts={k:{'type':v['type'],'values':[v.get('value')]} for k,v in rows[0].items()}
 displayed=rows[:DISPLAY_ROWS]
 return {'returned_rows':len(rows),'displayed_row_count':len(displayed),'displayed_rows':displayed,
         'rows_truncated':len(displayed)<len(rows),'omitted_row_count':max(0,len(rows)-len(displayed)),
         'aggregate_outputs':facts,'group_keys':groups,'group_keys_truncated':False}

def _process_evidence(observation,by_id,quantities=None):
 from .process_receipts import identify
 name,spec=identify(observation)
 if spec.route=='reproduction':
  from .declared_reproduction import validate
  # Preserve the complete validated original, not a reconstructed projection.
  return copy.deepcopy(validate(observation,by_id,quantities))
 if spec.route=='resolution':
  from .report_resolution import validate
  validate(observation,by_id)
  return copy.deepcopy(observation)
 if spec.route=='duplicate':
  prior=by_id.get(observation.get('prior_evidence_id'))
  if prior is None or prior.get('status')!='COMPLETED':
   raise Conflict('Duplicate refusal requires its prior successful receipt')
  return copy.deepcopy(observation)
 if spec.route=='retained':
  return copy.deepcopy(observation)
 status=observation.get('comparison_status')
 if status not in ('CROSS_SURFACE_VERIFIED','NOT_COMPARABLE','WITHIN_LAYER_CHECK'):
  raise Conflict('Unsupported comparison receipt shape: '+name)
 refs=[observation.get('upper_evidence_id'),observation.get('lower_evidence_id')]
 referenced=[by_id.get(ref) for ref in refs if ref]
 if any(item is None or item.get('status')!='COMPLETED' for item in referenced):
  raise Conflict('Process receipt references unavailable evidence')
 upper=observation.get('upper_execution_surface');lower=observation.get('lower_execution_surface')
 for surface in (upper,lower):
  if surface is not None and _surface_key(surface) is None:
   raise Conflict('Process execution surface differs')
 if status=='CROSS_SURFACE_VERIFIED':
  from .surface_difference import validate
  try:validate(observation,by_id)
  except ValueError as exc:raise Conflict('Cross-surface process receipt differs: '+str(exc)) from exc
  if (len(referenced)!=2 or type(observation.get('values_equal')) is not bool):
   raise Conflict('Cross-surface process receipt differs')
  if quantities is not None and any(ref not in quantities for ref in refs):
   raise Conflict('Process comparison requires verified quantity receipts')
  compared=[quantities[ref] for ref in refs] if quantities is not None else [quantity(item.get('values')) for item in referenced]
  if (digest(compared[0])==digest(compared[1])) != observation['values_equal']:
   raise Conflict('Process comparison differs from referenced observations')
 from .snapshot_attestation import checked
 snapshot=checked(observation)
 return {'surface_difference':observation.get('surface_difference'),'snapshot_attestation':snapshot,'comparison_status':status,'upper_layer':observation.get('upper_layer'),
         'lower_layer':observation.get('lower_layer'),'reason':observation.get('reason'),
         'values_equal':observation.get('values_equal'),'upper_execution_surface':upper,
         'lower_execution_surface':lower,'referenced_evidence_ids':[ref for ref in refs if ref],
         'derived_from_referenced_observations':True}

def build(state,db):
 entries=[];quantities={};pending=[];by_id={o['id']:o for o in state['observations'] if isinstance(o,dict) and o.get('id')}
 for o in state['observations']:
  from .process_receipts import validate_for_synthesis
  name,spec=validate_for_synthesis(o)
  if o['status']!='COMPLETED':continue
  item={'id':o['id'],'tool':o['tool'],'completeness':o['completeness']}
  if o.get('process_roles'):item['process_roles']=o['process_roles']
  if o.get('test_purpose'):item['test_purpose']=o['test_purpose']
  if spec.route=='context':
   item.update(_context_evidence(o))
  elif spec.route!='query':
   pending.append((item,o))
   item['provenance']={'hash':digest(o),'derivation':
       'PROCESS_COMPARISON_FROM_REFERENCED_OBSERVATIONS' if spec.route=='comparison' else 'PROCESS_'+name+'_RECEIPT'}
  else:
   if o['tool'] not in TABLES:raise Conflict('Unsupported receipt integrity adapter')
   sealed=verify(db,o['tool'],o['id'])
   if sealed['state']!='SEALED':raise Conflict('Synthesis requires sealed query receipts')
   r=db.execute('SELECT model_id,status,request,result FROM '+TABLES[o['tool']]+' WHERE id=?',(o['id'],)).fetchone()
   if not r or r[0]!=state['model_id'] or r[1]!='COMPLETED':raise Conflict('Synthesis receipt scope/status differs')
   request,result=map(json.loads,r[2:])
   expected=result.get('rows',[]) if o['tool']!='source' else [result.get('value')]
   compiled={k:v for k,v in request.items() if k!='plan'}
   if digest(expected)!=digest(o['values']) or digest(compiled)!=o['request_hash']:
    raise Conflict('Synthesis observation differs from sealed receipt')
   if o.get('surface_report_binding')=='VALUE_QUERY':
    if (o.get('surface_report')!=result.get('surface_report')
        or result.get('surface_report_binding')!='VALUE_QUERY'):
     raise Conflict('Quantity-bound surface report differs from sealed value receipt')
   q=request.get('plan',{}).get('query',request.get('query',''))
   rows=o['values']
   quantities[o['id']]=quantity(rows,request.get('surface_report_columns'))
   if isinstance(quantities[o['id']],dict):
    item['verified_quantity']=quantities[o['id']]
   item['asked']={'query':q,'query_characters':len(q),'truncated':False}
   item['result']=_query_evidence(o['tool'],q,rows)
   item['provenance']={'request_hash':o['request_hash'],'result_hash':digest(result),'receipt_seal':sealed['hash']}
  entries.append(item)
 for item,o in pending:item['result']=_process_evidence(o,by_id,quantities)
 result={'version':1,'question':state['envelope']['symptom'],'scope':{k:state['envelope'][k] for k in ('model_id','context_id','measure_id','filters','dimension_ids')},
 'digest_limits':f'Complete validated queries are retained. At most {DISPLAY_ROWS} returned rows and their group keys are displayed per observation, with explicit omitted counts. Explicit definition content/find lookups retain at most {EXCERPT_CHARACTERS} excerpt characters per observation with truncation labels; arbitrary metadata remains omitted. Hypotheses are unverified, not evidence.', 'evidence':entries,'hypotheses':[{'id':h['id'],'claim':h['claim'],'claim_truncated':False,'status':h['status'],'evidence_ids':h['evidence_ids'],'authority':'UNVERIFIED_HYPOTHESIS'} for h in state['hypotheses']]}
 if state.get('measure_display_name'):result['scope']['measure_name']=state['measure_display_name']
 assessment=state.get('assessment') or {}
 process=assessment.get('support',{}).get('process') if isinstance(assessment,dict) else None
 if isinstance(process,dict):
  result['deterministic_process_finding']={'classification':assessment['classification'],
    'terminating_step':assessment.get('terminating_step'),
    'visibility_boundary':process['visibility_boundary'],'baseline_above':process['baseline_above'],
    'recommended_action':process['recommended_action'],'evidence_by_role':process['evidence_by_role'],
    'conclusion_blocker':process['missing_capability'],
    'capability_limitations':{'visibility_boundary':process['visibility_boundary'],
                              'skipped_checks':process['skipped_steps']},
    'mandatory_limits':assessment['limits']}
 return result
