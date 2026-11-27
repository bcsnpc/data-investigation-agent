import sys,runpy,json,socket,copy,collections,os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,os.environ.get('DIA_R28_CODE_ROOT','scripts'))
from investigator.run_capture import record_value
from investigator.estate_graph_contract import canonical
from investigator.guided_intake import Catalog,admit_or_question
try:
 from investigator.form_candidate_admission import check as check_form
except ModuleNotFoundError:
 check_form=lambda request,catalog:(request,[],[])
from investigator.guided_text_resolver import Resolver
import tiktoken
encoding=tiktoken.get_encoding('o200k_base')
r=Path('.local/round-twenty-eight-fixes');functions=runpy.run_path(str(r/'replay_engine.py'));replay=functions['replay']
output={'generation_calls':0,'estate_reads':0,'tokenizer':'tiktoken0.12.0/o200k_base, offline comparative counts, not provider billing tokens','rows':[],'calls':[]}
practice=Path('.local/round-twenty-seven');indices=[]
for p in sorted((practice/'ordered-dev-backtracks').glob('dev*.json')):
 v=json.loads(p.read_bytes())
 if v.get('cohort')in ('dev01','dev01-plumbing','dev01-completion-advisory','dev02-advisory','dev03-slim'):indices.append(('practice',p,v))
for item in json.loads((r/'healthnet-saved-index.json').read_bytes()):indices.append(('healthnet',Path(item['result_path']),item))

def packet(value):return canonical({k:value.get(k)for k in ('system','messages','tools')})
for cohort,indexfile,index in indices:
 records=[]
 for ref in index['source_batches']:
  path=Path(ref['local_path'])if 'local_path'in ref else practice/'free-models/replay-inputs'/(ref['sha256']+'.json')
  records.extend(record_value(path.read_bytes(),ref.get('encoding'))['records'])
 records.sort(key=lambda x:int(x['id'].rsplit(':',1)[1]));values=[x['value']for x in records]
 native=json.loads(indexfile.read_bytes()).get('result')if cohort=='healthnet'else None
 outcome=native or next((v for v in reversed(values)if isinstance(v.get('case'),dict)and 'context'in v['case']),None)
 case=outcome.get('case',{})if outcome else {};evidence=case.get('evidence',{})
 call_ids={b['id']for v in evidence.values()if v.get('kind')=='MODEL_RESPONSE'for b in v['response'].get('content',[])if b.get('type')=='tool_use'}
 before=[];pending=None;started=False
 for v in values:
  if v.get('event')=='REASONING_REQUEST':pending=v.get('body',{})
  if v.get('event')=='REASONING_RESPONSE':
   body=v.get('body',v.get('response',{}));calls=[b for b in body.get('content',[])if b.get('type')=='tool_use']
   if any(b.get('id')in call_ids for b in calls):started=True
   if started:before.append(pending or {})
 metrics=[]
 def observe(kwargs,position):
  after=packet(kwargs);prior=packet(before[position])if position<len(before)else None
  metrics.append(dict(case=indexfile.name,cohort=cohort,call=len(metrics)+1,saved_response_position=position,before_characters=len(prior)if prior else None,after_characters=len(after),before_tokens=len(encoding.encode(prior,disallowed_special=()))if prior else None,after_tokens=len(encoding.encode(after,disallowed_special=()))))
 catalog=next((v['catalog']for v in values if v.get('event')=='GUIDED_INTAKE_CATALOG'),None)
 try:
  with patch.object(socket.socket,'connect',side_effect=RuntimeError('OFFLINE_REPLAY_NETWORK_FORBIDDEN')):
   row=replay(indexfile,outcome_override=outcome,records_override=values,catalog_override=catalog,observe=observe)
   if catalog and outcome and outcome.get('ticket',{}).get('version')=='IntakeRequest/1':
    form=outcome['ticket'];resolved,checks,_=check_form(form,Catalog(catalog));admitted=admit_or_question(resolved,Catalog(catalog))
    row['form_intake_replay']={'status':admitted['status'],'reason':admitted.get('reason'),'candidate_checks':len(checks),'model_calls':0,'estate_reads':0}
 except Exception as error:row={'case':indexfile.name,'status':'REPLAY_FAILURE','reason':type(error).__name__+': '+str(error)[:200]}
 row.update(cohort=cohort);output['rows'].append(row);output['calls'].extend(metrics)
 (r/os.environ.get('DIA_R28_PROGRESS','replay-progress.json')).write_text(json.dumps(output,indent=2)+'\n')
 print(cohort,indexfile.name,row['status'],row.get('before'),row.get('after'),flush=True)
output['counts']=dict(collections.Counter(x['status']for x in output['rows']));output['classification_changes']=[x for x in output['rows']if x.get('before')and x.get('after')and x['before']!=x['after']];output['complete']=True
(r/os.environ.get('DIA_R28_REPORT','replay-results.private.json')).write_text(json.dumps(output,indent=2)+'\n');print('REPLAY_DONE',output['counts'])
