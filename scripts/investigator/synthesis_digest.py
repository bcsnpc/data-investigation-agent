"""Deterministic receipt selections for an independent conclusion call.

No model preprocessing, raw record rows, trajectory, or directory. Missing facts
remain missing: selection/formatting does not establish semantic truth.
"""
import json,re
from sqlglot import exp
from sqlglot.lineage import lineage
from sqlglot.errors import SqlglotError
from .onboarding import digest,encoded,Conflict
from .receipt_integrity import verify,TABLES

DISPLAY_ROWS = 2
EXCERPT_CHARACTERS = 2400


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

def _process_evidence(observation,by_id):
 status=observation.get('comparison_status')
 if status not in ('CROSS_SURFACE_VERIFIED','NOT_COMPARABLE','WITHIN_LAYER_CHECK'):
  raise Conflict('Unsupported process receipt shape')
 refs=[observation.get('upper_evidence_id'),observation.get('lower_evidence_id')]
 referenced=[by_id.get(ref) for ref in refs if ref]
 if any(item is None or item.get('status')!='COMPLETED' for item in referenced):
  raise Conflict('Process receipt references unavailable evidence')
 upper=observation.get('upper_execution_surface');lower=observation.get('lower_execution_surface')
 for surface in (upper,lower):
  if surface is not None and (not isinstance(surface,dict) or set(surface)!=set(('engine','connection','object'))
      or any(not isinstance(surface[k],str) or not surface[k] for k in surface)):
   raise Conflict('Process execution surface differs')
 if status=='CROSS_SURFACE_VERIFIED':
  if len(referenced)!=2 or upper==lower or type(observation.get('values_equal')) is not bool:
   raise Conflict('Cross-surface process receipt differs')
  if (digest(referenced[0].get('values'))==digest(referenced[1].get('values'))) != observation['values_equal']:
   raise Conflict('Process comparison differs from referenced observations')
 return {'comparison_status':status,'upper_layer':observation.get('upper_layer'),
         'lower_layer':observation.get('lower_layer'),'reason':observation.get('reason'),
         'values_equal':observation.get('values_equal'),'upper_execution_surface':upper,
         'lower_execution_surface':lower,'referenced_evidence_ids':[ref for ref in refs if ref],
         'derived_from_referenced_observations':True}

def build(state,db):
 entries=[];by_id={o['id']:o for o in state['observations'] if isinstance(o,dict) and o.get('id')}
 for o in state['observations']:
  if o['status']!='COMPLETED':continue
  item={'id':o['id'],'tool':o['tool'],'completeness':o['completeness']}
  if o.get('process_roles'):item['process_roles']=o['process_roles']
  if o.get('test_purpose'):item['test_purpose']=o['test_purpose']
  if o['tool']=='context':
   m=o['metadata'];item['asked']=o.get('lookup')
   item['result']=_definition_evidence(o)
   item['provenance']={'hash':digest(o),'context_version':m.get('context_version')}
  elif o['tool']=='process':
   item['result']=_process_evidence(o,by_id)
   item['provenance']={'hash':digest(o),'derivation':'PROCESS_COMPARISON_FROM_REFERENCED_OBSERVATIONS'}
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
   q=request.get('plan',{}).get('query',request.get('query',''))
   rows=o['values']
   item['asked']={'query':q,'query_characters':len(q),'truncated':False}
   item['result']=_query_evidence(o['tool'],q,rows)
   item['provenance']={'request_hash':o['request_hash'],'result_hash':digest(result),'receipt_seal':sealed['hash']}
  entries.append(item)
 result={'version':1,'question':state['envelope']['symptom'],'scope':{k:state['envelope'][k] for k in ('model_id','context_id','measure_id','filters','dimension_ids')},
 'digest_limits':f'Complete validated queries are retained. At most {DISPLAY_ROWS} returned rows and their group keys are displayed per observation, with explicit omitted counts. Explicit definition content/find lookups retain at most {EXCERPT_CHARACTERS} excerpt characters per observation with truncation labels; arbitrary metadata remains omitted. Hypotheses are unverified, not evidence.', 'evidence':entries,'hypotheses':[{'id':h['id'],'claim':h['claim'][:300],'claim_truncated':len(h['claim'])>300,'status':h['status'],'evidence_ids':h['evidence_ids'],'authority':'UNVERIFIED_HYPOTHESIS'} for h in state['hypotheses']]}
 assessment=state.get('assessment') or {}
 process=assessment.get('support',{}).get('process') if isinstance(assessment,dict) else None
 if isinstance(process,dict):
  result['deterministic_process_finding']={'classification':assessment['classification'],
    'terminating_step':assessment.get('terminating_step'),
    'visibility_boundary':process['visibility_boundary'],'baseline_above':process['baseline_above'],
    'recommended_action':process['recommended_action'],'evidence_by_role':process['evidence_by_role'],
    'missing_capability':process['missing_capability']}
 return result
