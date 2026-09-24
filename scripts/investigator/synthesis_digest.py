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

def build(state,db):
 entries=[]
 for o in state['observations']:
  if o['status']!='COMPLETED':continue
  item={'id':o['id'],'tool':o['tool'],'completeness':o['completeness']}
  if o['tool']=='context':
   m=o['metadata'];item['asked']=o.get('lookup');a=m.get('asset',{})
   snippets=m.get('content') or '\n'.join(x.get('excerpt','') for x in m.get('matches',[]))
   definition=a.get('metadata',{}).get('expression')
   item['result']={'asset_name':a.get('name'),'asset_kind':a.get('kind'),'matching_assets':m.get('total'),
    'excerpt':(snippets or definition or '')[:400],'excerpt_truncated':len(snippets or definition or '')>400,
    'directory_and_schema_omitted':True}
   item['provenance']={'hash':digest(o),'context_version':m.get('context_version')}
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
   rows=o['values'];facts={}
   if o['tool']=='bounded_sql':
    for name in (rows[0] if rows else {}):
     try:
      nodes=lineage(name,q,dialect='tsql').walk()
      if any(n.expression.find(exp.AggFunc) is not None for n in nodes):facts[name]={'type':rows[0][name]['type'],'values':[r[name].get('value') for r in rows[:4]]}
     except (ValueError,TypeError,KeyError,AttributeError,SqlglotError):pass
   elif o['tool']=='bounded_dax' and re.match(r'\s*EVALUATE\s+ROW\s*\(',q,re.I) and len(rows)==1:
    facts={k:{'type':v['type'],'values':[v.get('value')]} for k,v in rows[0].items()}
   item['asked']={'query':q[:400],'truncated':len(q)>400}
   item['result']={'returned_rows':len(rows),'record_rows_omitted':True,
    'aggregate_outputs':facts,'outputs_truncated':len(rows)>4,
    'group_keys_omitted':len(rows)>1}
   item['provenance']={'request_hash':o['request_hash'],'result_hash':digest(result),'receipt_seal':sealed['hash']}
  entries.append(item)
 return {'version':1,'question':state['envelope']['symptom'],'scope':{k:state['envelope'][k] for k in ('model_id','context_id','measure_id','filters','dimension_ids')},
 'digest_limits':'Only exact aggregate outputs are copied; at most four returned groups per output. Group keys and raw record rows are omitted and cannot support claims. Metadata excerpts and queries can be truncated. Hypotheses are unverified, not evidence.', 'evidence':entries,'hypotheses':[{'id':h['id'],'claim':h['claim'][:300],'claim_truncated':len(h['claim'])>300,'status':h['status'],'evidence_ids':h['evidence_ids'],'authority':'UNVERIFIED_HYPOTHESIS'} for h in state['hypotheses']]}
