"""Private, explicit post-replay append control; never rewrites prior evidence."""
import base64,hashlib,json,os
from contextlib import contextmanager
from pathlib import Path
from investigator import process_tape as journal
from investigator.lineage_binding import seal,validate,revalidate_verification

def sha(b):return hashlib.sha256(b).hexdigest()
@contextmanager
def exclusive(f,length):
 f.seek(0)
 if os.name=='nt':
  import msvcrt
  msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,max(1,length))
  try:yield
  finally:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,max(1,length))
 else:
  import fcntl
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:yield
  finally:fcntl.flock(f,fcntl.LOCK_UN)

def current_pins(manifest_path):
 import sqlite3
 from contextlib import closing
 from investigator.runtime import fingerprint
 from investigator.adapters.estate_installation import configuration
 from investigator.onboarding import digest
 m=json.loads(Path(manifest_path).read_text(encoding='utf-8-sig'))
 with closing(sqlite3.connect(Path(m['storage']['catalog']).resolve().as_uri()+'?mode=ro',uri=True)) as db:
  db.row_factory=sqlite3.Row;db.execute('BEGIN')
  row=db.execute("SELECT id,body,hash FROM enterprise_scans WHERE environment=? AND status IN ('COMPLETE','PARTIAL') ORDER BY started DESC LIMIT 1",(m['environment'],)).fetchone()
  if row is None or digest(json.loads(row['body']))!=row['hash']:raise ValueError('PROFILE_CURRENT_ENTERPRISE_CONTEXT_CORRUPT')
  models=dict(db.execute('SELECT id,context_id FROM models WHERE environment=? AND enabled=1',(m['environment'],)).fetchall())
  for model,context in models.items():
   c=db.execute('SELECT body,hash FROM model_contexts WHERE model_id=? AND id=?',(model,context)).fetchone()
   if c is None or digest(json.loads(c['body']))!=c['hash']:raise ValueError('PROFILE_CURRENT_MODEL_CONTEXT_CORRUPT')
 return {'engine_hash':fingerprint(),'context_identity':row['id'],'model_contexts':models,'manifest_hash':seal(m),'config_hash':digest(configuration(m))}

def publish(folder,target,replay_receipt_path,current,receipt_path,*,replay_receipt_sha256):
 # Root must drain every profile writer. This function then holds an exclusive
 # local lock, rechecks the exact prefix immediately before append, and fsyncs.
 folder=Path(folder);target=Path(target);receipt_path=Path(receipt_path)
 if receipt_path.exists():raise ValueError('PROFILE_PUBLICATION_RECEIPT_EXISTS')
 replay_bytes=Path(replay_receipt_path).read_bytes()
 if sha(replay_bytes)!=replay_receipt_sha256:raise ValueError('PROFILE_REPLAY_RECEIPT_CHANGED')
 replay_receipt=json.loads(replay_bytes)
 tape=journal.Tape(folder/'tape.json');b=tape.bootstrap;s=b['state'];i=s['inputs']
 if s.get('capture_contract')!='code-verifier-dependencies-v1':raise ValueError('PROFILE_CAPTURE_CONTRACT')
 if replay_receipt.get('status')!='COMPLETED' or not replay_receipt.get('matched') or replay_receipt.get('replay_engine_revision')!=tape.engine_revision or replay_receipt.get('capture_sha256')!=sha(tape.path.read_bytes()):raise ValueError('PROFILE_EXACT_REPLAY_REQUIRED')
 expected={'engine_hash':i['engine_fingerprint'],'context_identity':i['enterprise_context'],'model_contexts':i['enabled_model_contexts'],'manifest_hash':seal(i['manifest']),'config_hash':seal(b['config'])}
 if current()!=expected:raise ValueError('PROFILE_CURRENT_ENGINE_CONTEXT_CONFIG_DIFFERS')
 name=s['profile_member']
 if name is None or target.resolve()!=Path(s['native_path_identities'][name]).resolve():raise ValueError('PROFILE_NATIVE_TARGET_DIFFERS')
 baseline=(folder/name).read_bytes();clone=(folder/'working'/name).read_bytes()
 if sha(baseline)!=s['members'][name] or not clone.startswith(baseline) or baseline and not baseline.endswith(b'\n'):raise ValueError('PROFILE_BASELINE_OR_EXACT_PREFIX_DIFFERS')
 for member,h in s['members'].items():
  digest=hashlib.sha256()
  with (folder/member).open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
  if digest.hexdigest()!=h:raise ValueError('PROFILE_CAPTURE_DEPENDENCY_CHANGED:'+member)
 final=json.loads(base64.b64decode(tape.events[-1]['body']))
 if final.get('status')!='COMPLETED':raise ValueError('PROFILE_CAPTURE_NOT_COMPLETED')
 if final['working_members'][name]!=sha(clone) or final['profile_identity']!=replay_receipt.get('profile_identity'):raise ValueError('PROFILE_REPLAYED_CLONE_DIFFERS')
 suffix=clone[len(baseline):]
 if not suffix or not suffix.endswith(b'\n'):raise ValueError('PROFILE_NO_COMPLETE_NEW_ENTRIES')
 added=[]
 for line in suffix.splitlines():
  row=json.loads(line);v=row.get('verification')
  if set(row)!={'event','verification','sha256'} or row['event']!='VERIFICATION' or row['sha256']!=seal(v):raise ValueError('PROFILE_NEW_ENTRY_INTEGRITY')
  validate(v['proposal'])
  if v.get('status')!='VERIFIED':raise ValueError('PROFILE_NEW_ENTRY_NOT_VERIFIED')
  if v.get('context') not in set(i['enabled_model_contexts'].values()):raise ValueError('PROFILE_NEW_ENTRY_CONTEXT_DIFFERS')
  revalidate_verification(v);added.append(v)
 with target.open('r+b') as f,exclusive(f,len(clone)+1):
  before=f.read()
  if before!=baseline or sha(before)!=s['members'][name]:raise ValueError('PROFILE_NATIVE_PREFIX_CHANGED')
  if current()!=expected:raise ValueError('PROFILE_CURRENT_PINS_CHANGED_BEFORE_APPEND')
  f.seek(0,2);f.write(suffix);f.flush();os.fsync(f.fileno());f.seek(0)
  after=f.read()
  if after!=clone:raise ValueError('PROFILE_APPEND_RESULT_DIFFERS')
 record={'status':'PROFILE_APPEND_ACCEPTED','control':'DERIVED_PROFILE_PUBLICATION','estate_reads':0,'model_calls':0,'investigation_diagnostics':0,'producer_revision':tape.engine_revision,'capture_sha256':sha(tape.path.read_bytes()),'replay_receipt_sha256':replay_receipt_sha256,'clone_sha256':sha(clone),'suffix_sha256':sha(suffix),'before_sha256':sha(before),'after_sha256':sha(after),'published_profile_path':str(target.resolve()),'added_entries':len(added),'verification_pins':dict(expected,evidence_profile_path=str(target.resolve()),evidence_profile_sha256=sha(after))}
 receipt_path.parent.mkdir(parents=True,exist_ok=True)
 with receipt_path.open('x',encoding='utf8') as f:json.dump(record,f,sort_keys=True,indent=2)
 return record
