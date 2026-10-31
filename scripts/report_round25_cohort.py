"""Aggregate saved Round25 cohort grades without opening wording on stdout."""
import json,sys,hashlib,statistics,math
from pathlib import Path
from round25_cohort_report import summarize
r=Path('.local/round-twenty-five');cohort=sys.argv[1];assert cohort in ('g2','g3','g4')
source={'g2':Path('acceptance/tickets/guided-v4/held-out.sealed.json'),'g3':r/'g3-records.json','g4':Path('acceptance/tickets/guided-v2/held-out.sealed.json')}[cohort]
rows=json.loads(source.read_bytes())['tickets'];meta={x['id']:x for x in rows};cases={}
for path in sorted((r/'grading').glob('*/'+cohort+'-grader-result.json')):
 label=path.parent.name;p=json.loads(path.read_bytes());sp=r/'grading'/(label+'-second-result.json')
 if p.get('status')!='COMPLETED'or not sp.exists():continue
 second={x['ticket']:x['grade']for x in json.loads(sp.read_bytes())['results']};rp=r/'grading'/(label+'-independent-review-result.json');reviews={x['ticket']:x for x in json.loads(rp.read_bytes())['cases']}if rp.exists()else{}
 for result in p['results']:
  ident=result['case_id'];assert ident in meta and ident in second and ident not in cases,'Duplicate or unbound official grade'
  original=r/(cohort+'-'+ident+'-result.json');raw=original.read_bytes();w=json.loads(raw);a=w.get('result',w);native=w.get('execution',{});start,end=native.get('startTime'),native.get('endTime')
  from datetime import datetime
  duration=(datetime.fromisoformat(end.replace('Z','+00:00'))-datetime.fromisoformat(start.replace('Z','+00:00'))).total_seconds()if start and end else None
  case={'ticket':ident,'class':meta[ident].get('case_id',meta[ident].get('class',meta[ident]['fixture'])),'fixture':meta[ident]['fixture'],'estate':meta[ident].get('estate'),'primary':result['output'],'secondary':second[ident],'grade_wave':label,'outcome_sha256':hashlib.sha256(raw).hexdigest(),'status':a.get('status'),'native_duration_seconds':duration,'worker_wall_seconds':a.get('timing',{}).get('wall_seconds'),'investigation_cost_microdollars':a.get('cost',{}).get('charged_microdollars',0),'physical_requests':a.get('physical_requests',0),'model_calls':a.get('model_calls')}
  if ident in reviews:
   assert reviews[ident]['raw_outcome_sha256']==case['outcome_sha256'];case['raw_review']=reviews[ident]
  cases[ident]=case
value=summarize(list(cases.values()),cohort);value['requested']=len(rows);value['not_yet_graded']=[i for i in meta if i not in cases];value['status']='COMPLETE'if len(cases)==len(rows)and value['raw_review_complete']else'IN_PROGRESS'
for group,select in [('all',list(cases.values())),('full_investigation',[c for c in cases.values()if c['status']=='ANSWERED']),('holds',[c for c in cases.values()if c['status']!='ANSWERED'])]:
 times=sorted(c['native_duration_seconds']for c in select if c['native_duration_seconds']is not None);worker=sorted(c['worker_wall_seconds']for c in select if isinstance(c['worker_wall_seconds'],(float,int)));cost=sum(c['investigation_cost_microdollars']for c in select)
 value.setdefault('timing_cost',{})[group]={'tickets':len(select),'native_observed':len(times),'native_missing':len(select)-len(times),'native_median_seconds':statistics.median(times)if times else None,'native_p90_seconds':times[math.ceil(.9*len(times))-1]if times else None,'worker_median_seconds':statistics.median(worker)if worker else None,'worker_p90_seconds':worker[math.ceil(.9*len(worker))-1]if worker else None,'investigation_cost_microdollars':cost,'cost_per_ticket_usd':cost/len(select)/1e6 if select else None,'physical_requests':sum(c['physical_requests']for c in select)}
Path('docs/runs/round25-'+cohort+'-current-grades.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({'cohort':cohort,'graded':len(cases),'requested':len(rows),'primary':value['official_primary']['all_three'],'strict':value['strict']['all_three'],'raw':value['raw_reviewed']['all_three'],'raw_pending':len(value['raw_review_pending']),'harmful_raw':value['raw_reviewed']['harmful']['correct']}))
