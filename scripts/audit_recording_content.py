"""Offline structural inventory of recordings; never a semantic privacy verdict."""
import argparse,base64,collections,hashlib,json,os,sqlite3,zipfile
from datetime import datetime,timezone
from pathlib import Path
from contextlib import closing
SKIP={'.git','node_modules','__pycache__','Lib','azure-fabric-sql','azure-reader-sql','azure-reader-powerbi'}


def shapes(value):
 result={'row_arrays':0,'max_rows':0,'candidates':[],'nested_json_failures':0}
 stack=[(value,'',0)]
 while stack:
  item,path,depth=stack.pop()
  if depth>80:continue
  if isinstance(item,dict):
   for key,child in item.items():
    next_path=path+'/'+str(key)
    if key=='rows' and isinstance(child,list):
     result['row_arrays']+=1;result['max_rows']=max(result['max_rows'],len(child))
     if len(child)>249:
      result['candidates'].append({'path':next_path,'rows':len(child),'first_row_keys':sorted(child[0]) if child and isinstance(child[0],dict) else [],'classification':'REVIEW_REQUIRED_NOT_AUTOMATICALLY_BULK'})
    stack.append((child,next_path,depth+1))
  elif isinstance(item,list):
   stack.extend((v,path+'/'+str(i),depth+1)for i,v in enumerate(item))
  elif isinstance(item,str) and item[:1] in ('{','[') and len(item)<=64*1024*1024:
   try:parsed=json.loads(item)
   except (ValueError,RecursionError):result['nested_json_failures']+=1
   else:stack.append((parsed,path+'/@json',depth+1))
 return result


def row_array_class(kind,path):
 if kind=='BUDGET_INPUT' and path in {'/tables/adaptive_usage/rows','/tables/read_allocations/rows'}:
  return 'CONTROL_ACCOUNTING_ROWS'
 return 'UNCLASSIFIED_ROW_ARRAY'


def tape(path):
 before=path.stat();raw=path.read_bytes();out={'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 try:
  data=json.loads(raw);out.update(version=data.get('version'),events=len(data.get('events',[])),row_arrays=0,max_rows=0,candidates=[],decode_failures=[])
  for index,event in enumerate(data.get('events',[])):
   try:body=json.loads(base64.b64decode(event['body'],validate=True))
   except (ValueError,TypeError,KeyError,UnicodeDecodeError):out['decode_failures'].append({'event':index,'kind':event.get('kind')});continue
   found=shapes(body);out['row_arrays']+=found['row_arrays'];out['max_rows']=max(out['max_rows'],found['max_rows'])
   out['candidates'] +=[{'event':index,'kind':event.get('kind'),'row_class':row_array_class(event.get('kind'),c['path']),**c}for c in found['candidates']]
  out['status']='SHAPE_AUDITED' if not out['decode_failures'] else 'PARTIAL_DECODING'
  out['sealed_final_present']=bool(data.get('events')) and data['events'][-1].get('kind')=='FINAL'
 except Exception as exc:out.update(status='UNREADABLE',error_type=type(exc).__name__)
 after=path.stat()
 if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):out['status']='CHANGED_DURING_AUDIT'
 return out


def inventory(path):
 out={'path':str(path),'bytes':path.stat().st_size}
 try:
  with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True))as db:
   db.execute('BEGIN');names=[r[0]for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
   out['tables']=names;out['counts']={n:db.execute('SELECT count(*) FROM '+chr(34)+n.replace(chr(34),chr(34)*2)+chr(34)).fetchone()[0]for n in names}
  out['unexpected_tables']=[n for n in names if n not in {'assets','scans','observations','sqlite_sequence'}]
  out['status']='METADATA_TABLES_ONLY' if not out['unexpected_tables'] else 'REVIEW_REQUIRED'
 except Exception as exc:out.update(status='UNREADABLE',error_type=type(exc).__name__)
 return out


def catalog_schema(path):
 out={'path':str(path),'bytes':path.stat().st_size}
 try:
  with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True))as db:
   out['tables']=[r[0]for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
  out['status']='SCHEMA_ONLY_NO_PAYLOAD_AUDIT'
 except Exception as exc:out.update(status='UNREADABLE',error_type=type(exc).__name__)
 return out


def run(root,output):
 root=Path(root).resolve();output=Path(output);output.mkdir(parents=True,exist_ok=False)
 paths=[];inventories=[];catalogs=[];archives=[]
 for directory,dirs,files in os.walk(root):
  dirs[:]=[d for d in dirs if d not in SKIP]
  for name in files:
   p=Path(directory)/name
   if name=='tape.json':paths.append(p)
   elif name=='inventory.sqlite':inventories.append(p)
   elif name=='catalog.sqlite':catalogs.append(p)
   elif p.suffix.lower()in {'.zip','.gz'}:archives.append(p)
 aggregate=collections.Counter();maximum=0
 with (output/'tapes.jsonl').open('x',encoding='utf8')as stream:
  for i,p in enumerate(sorted(paths)):
   result=tape(p);maximum=max(maximum,result.get('max_rows',0));aggregate[result['status']]+=1
   aggregate['row_arrays']+=result.get('row_arrays',0);aggregate['candidate_arrays']+=len(result.get('candidates',[]));aggregate['bytes']+=result['bytes']
   stream.write(json.dumps(result,sort_keys=True)+'\n');stream.flush()
   if i%50==0:print(json.dumps({'tapes_done':i+1,'tapes_total':len(paths),'candidate_arrays':aggregate['candidate_arrays']}),flush=True)
 with (output/'inventories.jsonl').open('x',encoding='utf8')as stream:
  for p in inventories:stream.write(json.dumps(inventory(p),sort_keys=True)+'\n');stream.flush()
 with (output/'catalog-schemas.jsonl').open('x',encoding='utf8')as stream:
  for p in catalogs:stream.write(json.dumps(catalog_schema(p),sort_keys=True)+'\n');stream.flush()
 archive_results=[]
 for p in archives:
  row={'path':str(p),'bytes':p.stat().st_size,'content_inspected':False}
  if p.suffix.lower()=='.zip':
   try:
    with zipfile.ZipFile(p)as z:row.update(members=len(z.infolist()),expanded_bytes=sum(i.file_size for i in z.infolist()),data_file_candidates=[i.filename for i in z.infolist()if Path(i.filename).suffix.lower()in {'.parquet','.duckdb','.csv'}])
   except Exception as exc:row['error_type']=type(exc).__name__
  archive_results.append(row)
 (output/'archives.json').write_text(json.dumps(archive_results,indent=2),encoding='utf8')
 summary={'root':str(root),'loose_tapes':len(paths),'inventory_snapshots':len(inventories),'catalog_schemas':len(catalogs),'archives':len(archives),'tape_results':dict(aggregate),'max_rows_array_including_controls':maximum,'estate_reads':0,'model_calls':0,'archive_extractions':0,'finished_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'JSON rows arrays after event and nested JSON decoding; SQLite table schema/counts. Not seal validation, all opaque/raw-text formats, credential review, or universal proof of no bulk data.'}
 (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary))
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.root,a.output)
