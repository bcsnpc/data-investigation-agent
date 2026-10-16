"""Bounded local fixture export. Callbacks own guarded, metered read controls.
No cloud or secret access lives here. Values are projected before any write.
"""
from contextlib import closing
import base64, datetime, decimal, hashlib, json, math, sqlite3
from pathlib import Path

VERSION='local-fixture-export-v1'
TYPES={'INTEGER':'INTEGER','REAL':'REAL','TEXT':'TEXT','DECIMAL':'TEXT','DATE':'TEXT','DATETIME':'TEXT','BOOLEAN':'INTEGER','BINARY':'BLOB'}
RECEIPT_FIELDS={'request_id','identity','surface','query','started_at','ended_at','attestation','snapshot','physical_requests','status'}

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def quoted(v):return '"'+v.replace('"','""')+'"'
def encode(value,kind):
 if value is None:return None
 if kind=='INTEGER' and type(value) is int:return value
 if kind=='REAL' and type(value) in (int,float) and math.isfinite(value):return float(value)
 if kind=='BOOLEAN' and type(value) is bool:return int(value)
 if kind=='TEXT' and isinstance(value,str):return value
 if kind=='DECIMAL' and isinstance(value,(decimal.Decimal,str)):
  v=decimal.Decimal(value)
  if v.is_finite():return str(v)
 if kind=='DATE' and isinstance(value,str):
  datetime.date.fromisoformat(value);return value
 if kind=='DATETIME' and isinstance(value,str):
  datetime.datetime.fromisoformat(value);return value
 if kind=='DATE' and isinstance(value,datetime.date) and not isinstance(value,datetime.datetime):return value.isoformat()
 if kind=='DATETIME' and isinstance(value,datetime.datetime):return value.isoformat()
 if kind=='BINARY' and isinstance(value,bytes):return value
 raise ValueError('EXPORT_NATIVE_TYPE_MISMATCH:'+kind)
def jsonvalue(v):return {'base64':base64.b64encode(v).decode()} if isinstance(v,bytes) else v

def export(plan,read,output,*,projection=None,definitions=()):
 output=Path(output)
 if output.exists():raise ValueError('EXPORT_EXCLUSIVE_NEW_OUTPUT_REQUIRED')
 if plan.get('version')!=VERSION or plan.get('tape_class') not in ('EXACT','PRIVACY_PROJECTED'):raise ValueError('EXPORT_POLICY_REQUIRED')
 if (projection is None)!=(plan['tape_class']=='EXACT'):raise ValueError('EXPORT_PROJECTION_POLICY_REQUIRED')
 if not isinstance(plan.get('estate_manifest_hash'),str) or len(plan['estate_manifest_hash'])!=64 or set(plan.get('enterprise_context',{}))!={'id','hash'}:raise ValueError('EXPORT_APPROVED_ESTATE_BINDING_REQUIRED')
 contexts=plan.get('contexts')
 if not isinstance(contexts,list) or not contexts or any(set(c)!={'model_id','context_id','context_hash','revision'} for c in contexts):raise ValueError('EXPORT_APPROVED_CONTEXT_BINDING_REQUIRED')
 assets=plan.get('assets')
 if not isinstance(assets,list) or not assets:raise ValueError('EXPORT_ASSETS_REQUIRED')
 if len({a['asset_id'] for a in assets})!=len(assets):raise ValueError('EXPORT_DUPLICATE_ASSET')
 output.mkdir(parents=True);db=output/'data.sqlite';records=[]
 manifest={'version':VERSION,'estate_id':plan['estate_id'],'tape_class':plan['tape_class'],'engine':'SQLITE_LOCAL_COPY','comparison_limit':'Native engine semantics and cross-layer snapshot alignment are not established by this export. Unsupported native expressions must refuse, not approximate.','estate_manifest_hash':plan['estate_manifest_hash'],'enterprise_context':plan['enterprise_context'],'contexts':contexts,'assets':records,'definitions':[],'missing_layers':plan.get('missing_layers',[])}
 if projection:manifest['privacy']=projection.descriptor()
 try:
  with closing(sqlite3.connect(db)) as con, con:
   for index,a in enumerate(assets):
    cap=a['max_rows'];bytecap=a['max_bytes']
    if type(cap)is not int or not 1<=cap<=10000 or type(bytecap)is not int or not 1<=bytecap<=16*1024*1024:raise ValueError('EXPORT_BOUND_REQUIRED')
    cols=a['columns'];names=[c['name'] for c in cols]
    if not cols or len(set(names))!=len(names) or any(c['logical_type'] not in TYPES for c in cols):raise ValueError('EXPORT_SCHEMA_INVALID')
    result=read(a)
    if result.get('status')!='AVAILABLE':raise ValueError('EXPORT_READ_UNAVAILABLE')
    if result.get('truncated') is not False:raise ValueError('EXPORT_COMPLETENESS_UNESTABLISHED')
    rows=result['rows'];receipt=result['receipt']
    if not isinstance(rows,list) or len(rows)>cap:raise ValueError('EXPORT_ROW_CAP_EXCEEDED')
    if set(receipt)-RECEIPT_FIELDS:raise ValueError('EXPORT_RECEIPT_FIELDS_UNSAFE')
    if any(k not in receipt for k in ('identity','surface','query','status','physical_requests')):raise ValueError('EXPORT_RECEIPT_REQUIRED')
    if receipt['query']!=a['query'] or receipt['status']!='AVAILABLE':raise ValueError('EXPORT_RECEIPT_REQUEST_DIFFERS')
    projected=[];size=0;digest=hashlib.sha256()
    for row in rows:
     if not isinstance(row,(list,tuple)) or len(row)!=len(cols):raise ValueError('EXPORT_ROW_WIDTH')
     encoded=[]
     for c,value in zip(cols,row):
      value=projection.bind(c['identity'],value) if projection else value
      encoded.append(encode(value,c['logical_type']))
     raw=canonical([jsonvalue(v) for v in encoded]);size+=len(raw)+1
     if size>bytecap:raise ValueError('EXPORT_BYTE_CAP_EXCEEDED')
     digest.update(raw+b'\n');projected.append(encoded)
    table='t%04d'%index
    con.execute('CREATE TABLE '+quoted(table)+' ('+','.join(quoted(c['name'])+' '+TYPES[c['logical_type']] for c in cols)+')')
    con.executemany('INSERT INTO '+quoted(table)+' VALUES ('+','.join('?' for c in cols)+')',projected)
    # Every fully validated asset is independently committed. A later refusal
    # preserves those rows as partial evidence; it never implies COMPLETE.
    con.commit()
    safe_receipt=projection.project(receipt) if projection else receipt
    records.append({'asset_id':a['asset_id'],'role':a['role'],'table':table,'columns':cols,'rows':len(rows),'encoded_bytes':size,'content_sha256':digest.hexdigest(),'receipt':safe_receipt})
  for index,d in enumerate(definitions):
   if set(d)!={'asset_id','kind','content','source_sha256'}:raise ValueError('EXPORT_DEFINITION_FIELDS_UNSAFE')
   if hashlib.sha256(d['content'].encode('utf8')).hexdigest()!=d['source_sha256']:raise ValueError('EXPORT_DEFINITION_SOURCE_DIFFERS')
   content=projection.project(d['content']) if projection else d['content']
   path=output/('definition-%04d.txt'%index);path.write_bytes(content.encode('utf8'))
   manifest['definitions'].append({'asset_id':d['asset_id'],'kind':d['kind'],'source_sha256':d['source_sha256'],'file':path.name,'sha256':sha(path)})
  manifest['database']={'file':db.name,'sha256':sha(db)};manifest['status']='COMPLETE'
 except BaseException as e:
  manifest['status']='BLOCKED';manifest['failure']={'type':type(e).__name__,'code':str(e).split(':')[0]}
  (output/'manifest.json').write_bytes(canonical(manifest));raise
 (output/'manifest.json').write_bytes(canonical(manifest));return manifest
