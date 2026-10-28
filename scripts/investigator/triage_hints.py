"""Path-local triage hints; observations never become automatic causal verdicts."""
from copy import deepcopy
from datetime import datetime

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


def current_job_hints(case):
    """Use the latest retained native run read as well as initial triage.

    A current failed run cannot disappear because its evidence was omitted
    from a proposed finding. A newer explicit completed-run read can replace
    an older triage fault; historical failures alone never become current.
    """
    latest={};triage_times={}
    def initial_times(value,inherited=None):
        if isinstance(value,list):
            for item in value:initial_times(item,inherited)
        elif isinstance(value,dict):
            if value.get('kind')=='RUN_HISTORY':return
            at=value.get('observed_at',inherited);subject=value.get('subject')
            if isinstance(subject,str)and isinstance(at,str):
                try:stamp=datetime.fromisoformat(at.replace('Z','+00:00')).timestamp()
                except ValueError:stamp=None
                if stamp is not None:triage_times[subject]=max(stamp,triage_times.get(subject,stamp))
            for key,item in value.items():
                if key not in ('previous','retained','recent_runs'):initial_times(item,at)
    initial_times(case.get('triage',{}))
    for record in case.get('evidence',{}).values():
        if record.get('tool')not in ('get_job_runs','get_refresh_history'):continue
        value=record.get('result',{})
        if not value.get('source')or value.get('status')!='OBSERVED':continue
        try:at=datetime.fromisoformat(value['observed_at'].replace('Z','+00:00')).timestamp()
        except (KeyError,TypeError,ValueError):continue
        facts=[f for f in value.get('facts',[])if isinstance(f,dict)and f.get('kind')in ('JOB_RUN','REFRESH_RUN','REFRESH_STATE')
            and f.get('state')in ('OBSERVED','OBSERVED_NEGATIVE')
            and isinstance(f.get('value'),dict)and isinstance(f['value'].get('status'),str)]
        subjects={f.get('subject')for f in facts if isinstance(f.get('subject'),str)}
        for subject in subjects:
            if at<triage_times.get(subject,float('-inf')):continue
            if subject not in latest or at>latest[subject][0]:latest[subject]=(at,value)
    hints=[h for h in job_hint(case.get('triage',{}))if h.get('subject')not in latest]
    for subject,(_,value)in latest.items():
        wrapper={'facts':[{'check':'JOB_RUNS','source':value['source'],'state':'OBSERVED',
            'value':[f for f in value['facts']if isinstance(f,dict)and f.get('subject')==subject
                and f.get('kind')in ('JOB_RUN','REFRESH_RUN','REFRESH_STATE')
                and f.get('state')in ('OBSERVED','OBSERVED_NEGATIVE')]}]}
        hints.extend(job_hint(wrapper))
    return hints


def suggestion(triage):
    hints=job_hint(triage)
    if hints:return 'Read the path job or refresh run first: '+', '.join(str(h['status'])+' '+str(h.get('run_id')or h.get('subject'))for h in hints)+'. Establish its status, times and native error before value comparisons.'
    unavailable=[f['check']for f in triage.get('facts',[])if f.get('state')=='UNAVAILABLE']
    if unavailable:return 'Triage has unavailable checks ('+', '.join(unavailable)+'); this does not establish that those mechanisms are absent.'
    return 'Recreate the selected value, then check its comparison side and retained producing definition; triage alone does not prove a cause.'
