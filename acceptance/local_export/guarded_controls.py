"""Existing guarded SQL transport hook; no CLI/cloud side effects on import.
Caller supplies current approved governor/config. Local cap counts each physical
admission, controls remain ordinary-pot requests but no diagnostic run exists.
"""
import datetime,hashlib,json
from pathlib import Path
class ControlReader:
 def __init__(self,governor,config,session,*,physical_cap,should_stop=None):
  self.governor=governor;self.config=config;self.session=session;self.cap=physical_cap;self.logical=0;self.requests=[];self.should_stop=should_stop
 def read_sql(self,asset):
  if self.should_stop is not None and self.should_stop():raise RuntimeError('EXPORT_OWNER_STOP')
  self.logical+=1;key='export-control-'+str(self.logical)
  request={k:asset[k] for k in ('query','parameters','read_only_objects','max_rows','result_columns','asset_ids') if k in asset}
  request.update(require_read_only=True,response_mode='records')
  if self.config.get('_estate',{}).get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':raise ValueError('EXPORT_PROJECTED_TRANSPORT_NOT_WIRED')
  start=datetime.datetime.now(datetime.timezone.utc).isoformat()
  if asset.get('export_full') is True:
   call=lambda:full_export_transport(self.config,asset,request)
  elif asset['surface']=='AZURE_SQL':
   from run_source_diagnostic import transport
   call=lambda:transport(self.config,request)
  elif asset['surface']=='FABRIC_SQL':
   from fabric_sql_surface import read
   call=lambda:read(self.config,asset['database'],request)
  else:raise ValueError('EXPORT_SQL_SURFACE_UNSUPPORTED')
  # CappedGovernor below intercepts reserve for every physical child admission.
  value=self.governor.metered_read(self.session,key,call)
  row={'control_class':'LOCAL_EXPORT','request_key':key,'query_sha256':hashlib.sha256(asset['query'].encode()).hexdigest(),'started_at':start,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'surface':asset['surface'],'status':'AVAILABLE'}
  self.requests.append(row);return value

def capped_governor_type():
 from investigator.usage_governance import UsageGovernor
 class ExportGovernor(UsageGovernor):
  def __init__(self,*args,physical_cap,should_stop=None,**kwargs):
   self.export_admissions=0;self.export_cap=physical_cap;self.export_should_stop=should_stop
   super().__init__(*args,**kwargs)
  def reserve(self,db,session_id,key,kind,*args,**kwargs):
   if kind=='cloud' and self.export_should_stop is not None and self.export_should_stop():raise RuntimeError('EXPORT_OWNER_STOP')
   if kind=='cloud' and self.export_admissions>=self.export_cap:raise RuntimeError('EXPORT_CONTROL_PHYSICAL_CAP')
   result=super().reserve(db,session_id,key,kind,*args,**kwargs)
   if kind=='cloud':self.export_admissions+=1
   return result
 return ExportGovernor

def full_export_transport(config,asset,request):
 """Dedicated control response cap, same identity and read-only guards."""
 from investigator.physical_reads import run
 from sql_layer_policy import policy
 if not 2<=request['max_rows']<=10000:raise ValueError('EXPORT_CONTROL_ROW_BOUND')
 if asset['surface']=='AZURE_SQL':
  options=config['sql'];payload={'server':options['server'],'database':options['database'],'credential_file':options['auth']['credential_file'],**request};worker='Read-ExportSource.ps1'
 elif asset['surface']=='FABRIC_SQL':
  from fabric_sql_auth import get_sql_token
  options=config['fabric']['sql_reader'];access=get_sql_token(config['fabric']['auth']['tenant_id'],options['account'],options['profile'])
  payload={'server':options['server'],'database':asset['database'],'access_token':access,**{k:request[k] for k in ('query','parameters','read_only_objects','max_rows','result_columns')}};worker='Read-ExportFabric.ps1'
 else:raise ValueError('EXPORT_CONTROL_SURFACE')
 p=run(['powershell','-NoProfile','-NonInteractive','-File',str(Path(__file__).parent/worker)],input=json.dumps(payload),capture_output=True,text=True,encoding='utf8',timeout=policy(config,request)['worker_timeout_seconds'])
 payload=None
 if len(p.stdout.encode('utf8'))>16*1024*1024:raise ValueError('EXPORT_CONTROL_RESPONSE_BYTES')
 value=json.loads(p.stdout)
 if p.returncode or value.get('error'):
  failure=RuntimeError('EXPORT_CONTROL_SQL_FAILED');failure.worker_failure=value;raise failure
 return value
