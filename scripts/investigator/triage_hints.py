"""Path-local triage hints; observations never become automatic causal verdicts."""
from copy import deepcopy

ACTIVE={'failed','running','inprogress','waiting','queued','pending','notstarted'}


def job_hint(triage):
    candidates=[]
    def visit(value,subject=None):
        if isinstance(value,list):
            for row in value:visit(row,subject)
        elif isinstance(value,dict):
            if value.get('kind')=='RUN_HISTORY':return
            subject=value.get('subject',subject)
            status=value.get('status')
            if isinstance(status,str)and status.casefold().replace(' ','')in ACTIVE:
                candidates.append({'subject':subject,'status':status,'run_id':value.get('run_id',value.get('id')),'native':deepcopy(value)})
            else:
                for key,item in value.items():
                    if key not in ('previous','retained','recent_runs'):visit(item,subject)
    for fact in triage.get('facts',[]):
        if fact.get('check') in ('JOB_RUNS','MODEL_REFRESH') and fact.get('state')=='OBSERVED' and fact.get('source'):
            visit(fact.get('value'))
    return candidates


def suggestion(triage):
    hints=job_hint(triage)
    if hints:return 'Read the path job or refresh run first: '+', '.join(str(h['status'])+' '+str(h.get('run_id')or h.get('subject'))for h in hints)+'. Establish its status, times and native error before value comparisons.'
    unavailable=[f['check']for f in triage.get('facts',[])if f.get('state')=='UNAVAILABLE']
    if unavailable:return 'Triage has unavailable checks ('+', '.join(unavailable)+'); this does not establish that those mechanisms are absent.'
    return 'Recreate the selected value, then check its comparison side and retained producing definition; triage alone does not prove a cause.'
