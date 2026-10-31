"""Owner-required fresh Claude adjudication of G2/G3/G4 disagreements only."""
import json,sys,runpy,subprocess,hashlib
from pathlib import Path
sys.path.insert(0,'scripts')
from round25_independent_review import packet,exact_deduplicate,differs,schema,SYSTEM,metric_winner
from round25_quality import raw_answer
from investigator.adapters.reasoning_anthropic import Client
from investigator.reasoning_budget import TicketBudget,RateCard
from investigator.live_gateway import configured
from investigator.process_tape import bytes_of
from investigator.planner_recording import _safe
from jsonschema import Draft202012Validator
r=Path('.local/round-twenty-five');cohort,label=sys.argv[1:];assert cohort in ('g2','g3','g4')
primary=json.loads((r/'grading'/label/(cohort+'-grader-result.json')).read_bytes());assert primary['status']=='COMPLETED'
secondary={x['ticket']:x['grade']for x in json.loads((r/'grading'/(label+'-second-result.json')).read_bytes())['results']}
selected=[x for x in primary['results']if differs(x['output'],secondary[x['case_id']])]
paths={'g2':(Path('acceptance/tickets/guided-v4/held-out.sealed.json'),Path('acceptance/tickets/guided-v4/expectations.sealed.json')),'g3':(r/'g3-records.json',r/'g3-original-expectations.json'),'g4':(Path('acceptance/tickets/guided-v2/held-out.sealed.json'),Path('acceptance/tickets/guided-v2/expectations.sealed.json'))}
tp,ep=paths[cohort];tickets={x['id']:x for x in json.loads(tp.read_bytes())['tickets']};e=json.loads(ep.read_bytes())['expectations'];expected={x['id']:x for x in e}if isinstance(e,list)else e
folder=r/'grading'/(label+'-independent-review');folder.mkdir(exist_ok=True)
state=runpy.run_path('.local/round-twenty-two/owner-budget-state.py')['state'];cfg=json.loads((r/'early-smoke-runner-10.json').read_bytes());policy=json.loads(cfg['environment']['DIA_PLATFORM_GATEWAY_POLICY']);reason=json.loads((r/'early-smoke-inputs/round25-smoke-spec.json').read_bytes())['reasoning'];reference=reason['secret_reference'];key=None
cli=[str(Path('.local/azure-cli-env/Scripts/python.exe').resolve()),'-m','azure.cli']
def read_key(*args,**kwargs):
 global key
 if key is None:
  p=subprocess.run(cli+['keyvault','secret','show','--vault-name','kv-dia-d5dd7d65','--name','anthropic-api-key','--version',reference['secret_version'],'--query','value','-o','tsv','--only-show-errors'],capture_output=True,text=True,timeout=45)
  if p.returncode:raise RuntimeError('EXISTING_KEY_VAULT_READ_FAILED_NO_SECRET_OUTPUT')
  key=p.stdout.strip();p=None
 return key
rate=RateCard(model='claude-opus-5-5',**reason['rate_card']);results=[]
with configured(policy):
 for row in selected:
  ident=row['case_id'];raw=(r/(cohort+'-'+ident+'-result.json')).read_bytes();w=json.loads(raw);case=w.get('result',w).get('case',{})
  inputs=packet(ticket=tickets[ident],answer=raw_answer(w),evidence={k:case.get(k)for k in ('intake','queries','triage','evidence')},expectation=expected[ident],primary=row['output'],secondary=secondary[ident]);packed=exact_deduplicate(inputs);payload=bytes_of(packed);_safe(payload);source_hash=hashlib.sha256(payload).hexdigest()
  source=folder/(ident+'-input.json');out=folder/(ident+'-review.json');provider=folder/(ident+'-provider.jsonl');started=folder/(ident+'-started.json')
  if source.exists():assert source.read_bytes()==payload
  else:source.write_bytes(payload)
  if out.exists():result=json.loads(out.read_bytes());assert result['source_sha256']==source_hash;results.append(result);continue
  response=None
  if started.exists():
   events=[json.loads(x)for x in provider.read_bytes().splitlines()]if provider.exists()else[];responses=[x['body']for x in events if x.get('event')=='REASONING_RESPONSE']
   if len(responses)!=1:raise RuntimeError('INDEPENDENT_REVIEW_UNCERTAIN_DO_NOT_DUPLICATE '+ident)
   response=responses[0]
  budget=TicketBudget(state,case_id='round25-independent-review:'+cohort+':'+ident,owner='round25-independent-reviewer',rate=rate,purpose='GRADING')
  if response is None:
   def record(event):
    raw=bytes_of(event);_safe(raw)
    with provider.open('ab')as f:f.write(raw+b'\n');f.flush()
   client=Client(model='claude-opus-5-5',budget=budget,identity='reasoning',secret_reference=reference,record=record,key_reader=read_key)
   started.write_bytes(bytes_of({'source_sha256':source_hash,'model':'claude-opus-5-5','independent_fresh_call':True,'operator_judgment_supplied':False,'estate_reads':0}))
   response=client.complete(system=SYSTEM,messages=[{'role':'user','content':payload.decode()}],tools=[{'name':'resolve_intake','description':'Return independent saved-evidence adjudication only; no reads or investigations.','input_schema':schema()}],max_tokens=4000)
  calls=[x for x in response.get('content',[])if x.get('type')=='tool_use'and x.get('name')=='resolve_intake'];assert len(calls)==1 and response.get('stop_reason')=='tool_use'
  decision=calls[0]['input'];Draft202012Validator(schema()).validate(decision);model_winner=decision['winner'];winner=metric_winner(decision,row['output'],secondary[ident]);decision={k:v for k,v in decision.items()if k!='winner'}
  result={'ticket':ident,'winner':winner,'independent_model_winner':model_winner,'grade':decision,'reason':decision['reason'],'model':'claude-opus-5-5','independent_fresh_call':True,'operator_judgment_supplied':False,'source_sha256':source_hash,'raw_outcome_sha256':hashlib.sha256(raw).hexdigest(),'usage':response['usage'],'cost_microdollars':budget.status()['charged_microdollars']};out.write_bytes(bytes_of(result));results.append(result);print(json.dumps({'ticket':ident,'independent_review_complete':True,'winner':winner,'harmful':decision['harmful']}),flush=True)
key=None
summary={'cohort':cohort,'label':label,'disagreements':len(selected),'cases':results,'estate_reads':0,'operator_adjudication':False};(r/'grading'/(label+'-independent-review-result.json')).write_bytes(bytes_of(summary))
Path('docs/runs/'+label+'-independent-review.json').write_bytes(bytes_of(summary)+b'\n')
print(json.dumps({'independent_reviews_completed':len(results),'cohort':cohort,'label':label}))
