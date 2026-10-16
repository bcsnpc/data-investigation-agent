"""Private proposal: per-operation scratch hydration; native sources never removed."""
import hashlib,json,shutil,tempfile
import ctypes
from pathlib import Path
FLOOR=3*1024**3
RESERVE=512*1024**2

def memory():
 class Status(ctypes.Structure):
  _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),('page_total',ctypes.c_ulonglong),('page_available',ctypes.c_ulonglong),('virtual_total',ctypes.c_ulonglong),('virtual_available',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
 if hasattr(ctypes,'windll'):
  value=Status();value.length=ctypes.sizeof(Status)
  if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):raise ValueError('MEMORY_ADMISSION_STATE_UNAVAILABLE')
  return value.available
 import os
 return os.sysconf('SC_AVPHYS_PAGES')*os.sysconf('SC_PAGE_SIZE')

def refs(op):
 out=[]
 for key in ('tape','catalog','inventory','estate_manifest'):
  if op.get(key):out.append(op[key])
 for key in ('dependencies','capture_support','after_artifacts'):
  out.extend(r for r in op.get(key,{}).values() if r)
 return out

def peak(suite,op):
 assets={r['asset'] for r in refs(op)}
 selected=[a for a in suite['assets'] if a['id'] in assets]
 for a in selected:
  for k in ('ciphertext_bytes','uncompressed_bytes'):
   if type(a.get(k)) is not int or not 0<=a[k]<=(256*1024**2+128 if k=='ciphertext_bytes' else 4_000_000_000):raise ValueError('BOUNDED_ASSET_SIZE_PIN_REQUIRED:'+k)
 # Fresh full shards plus conservative full-shard clone allowance; gzip disk is absent.
 return selected,sum(a['ciphertext_bytes']+2*a['uncompressed_bytes'] for a in selected)+RESERVE

def retain(source,destination):
 destination.mkdir(exist_ok=False)
 rows=[]
 for p in sorted(source.rglob('*')):
  if p.is_symlink() or getattr(p,'is_junction',lambda:False)():raise ValueError('REPLAY_OUTPUT_SYMLINK_OR_JUNCTION')
  if not p.is_file():continue
  # Only scratch mutable databases/sidecars are disposable; logs/receipts preserved.
  if p.name.endswith(('.sqlite','.sqlite-wal','.sqlite-shm','.sqlite-journal')):continue
  rel=p.relative_to(source);target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  with target.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
  rows.append({'member':rel.as_posix(),'sha256':h,'bytes':target.stat().st_size})
 return rows

def run_bounded(suite,output,scratch_parent,repo,*,validate,consumers,hydrate,run,free=lambda p:shutil.disk_usage(p).free,available_memory=memory):
 validate(suite);consumers(repo,suite)
 output=Path(output);scratch_parent=Path(scratch_parent)
 if output.exists():raise ValueError('BOUNDED_OUTPUT_ALREADY_EXISTS')
 if not scratch_parent.is_dir() or scratch_parent.is_symlink():raise ValueError('BOUNDED_SCRATCH_PARENT_REQUIRED')
 output.mkdir();rows=[]
 for op in suite['operations']:
  assets,estimate=peak(suite,op);available=free(scratch_parent)
  required_memory=max(2*1024**3+512*1024**2,sum(6*a['ciphertext_bytes']+a['uncompressed_bytes'] for a in assets)+RESERVE)
  available_ram=available_memory()
  admission={'required_memory':required_memory,'available_memory_before':available_ram,'id':op['id'],'peak_disk_estimate':estimate,'floor':FLOOR,'available_before':available,'estate_reads':0,'model_calls':0}
  if available<FLOOR+estimate or available_ram<required_memory:
   admission['status']='RESOURCE_ADMISSION_REFUSED';rows.append(admission);break
  # TemporaryDirectory owns only the unpredictable, newly created child. It never removes the caller's parent or existing artifacts.
  scratch=Path(tempfile.mkdtemp(prefix='dia-suite-scratch-',dir=scratch_parent))
  owned=scratch.resolve();parent=scratch_parent.resolve();members=scratch/'members';work=scratch/'replay';retained=False
  try:
   hydrate(repo,{**suite,'assets':assets},members)
   result=run(suite,members,work,repo,operation_ids={op['id']})
   admission.update(status='REPLAY_FINISHED',result=result)
  except Exception as exc:
   admission.update(status='REPLAY_TRANSPORT_BLOCKED',error_type=type(exc).__name__,error_message=str(exc))
  finally:
   try:
    admission['retained_outputs']=retain(work,output/op['id']) if work.is_dir() else [];retained=True
   except Exception as exc:
    admission.update(status='OUTPUT_RETENTION_BLOCKED',retention_error_type=type(exc).__name__,retention_error_message=str(exc),preserved_scratch=str(scratch))
   if retained:
    if scratch.is_symlink() or getattr(scratch,'is_junction',lambda:False)() or scratch.resolve()!=owned or owned.parent!=parent or not owned.name.startswith('dia-suite-scratch-'):
     admission.update(status='SCRATCH_CLEANUP_REFUSED',preserved_scratch=str(scratch))
    else:
     shutil.rmtree(scratch);admission['cleanup_scope']='NEW_EXCLUSIVE_SCRATCH_CHILD_ONLY'
  admission['available_after']=free(scratch_parent);rows.append(admission)
  (output/'partial-map.json').write_text(json.dumps(rows,sort_keys=True,indent=2))
 native=[r for row in rows for r in row.get('result',{}).get('operations',[])]
 counts={kind:sum(r['status']==kind for r in native) for kind in ('MATCHED_CAPTURED_OPERATION','REPLAY_BLOCKED','MISSING_CAPTURE','REPLAY_DIFFERED','CAPTURE_CHANGED_DURING_REPLAY')}
 attempted={row['id'] for row in rows};remaining=[o['id'] for o in suite['operations'] if o['id'] not in attempted]
 complete=len(native)==len(suite['operations']) and not remaining
 matched=complete and all(row['status']=='REPLAY_FINISHED' and row['result'].get('roster_matched') for row in rows)
 result={'operations':rows,'native_operations':native,'counts':counts,'remaining_not_admitted':remaining,'roster_matched':bool(matched),'estate_reads':0,'model_calls':0,'scratch_peak_bound_recorded':True,'scope':'Captured replay roster, not live accuracy.'}
 (output/'final-map.json').write_text(json.dumps(result,sort_keys=True,indent=2));return result
