"""Answer native run questions without requiring a report or an AI call."""
from copy import deepcopy
from .operational_delivery import details


def run(admission, history, *, record, history_for_selector=None):
    node = admission['target']
    subject = node['id']
    kinds = {'JOB_RUN', 'REFRESH_RUN', 'RUN_HISTORY', 'SCHEDULE'}
    selector = admission['ticket']['request'].get('run_selector')
    first = history_for_selector(subject,kinds,selector,admission['ticket']['text'])if selector and history_for_selector else history(subject, kinds)
    record({'event': 'OPERATIONAL_FASTPATH_READ', 'result': first})
    facts = first.get('facts', [])
    selector = admission['ticket']['request'].get('run_selector')
    if selector:
        from .operational_run_selection import select
        try:
            chosen=select(selector, facts, admission['ticket']['text'])
            if chosen['kind']=='RUN_HISTORY':chosen['kind']='REFRESH_RUN'if node['kind']=='MODEL'else'JOB_RUN'
            facts=[chosen]
        except ValueError as error:
            return {'status': 'NEEDS_INPUT', 'business': 'The requested run was not resolved in the retained native history.',
                    'stop': str(error), 'history': first, 'model_calls': 0}
    jobs = [f for f in facts if f.get('kind') in ('JOB_RUN', 'REFRESH_RUN') and f.get('state') == 'OBSERVED']
    if not jobs:
        return {'status': 'UNRESOLVED', 'business': 'I checked ' + node['label'] + ', but its native run status was unavailable.',
                'history': first, 'model_calls': 0}
    chosen = jobs[0]
    initial_status = chosen['value'].get('status')
    if initial_status in ('RUNNING', 'QUEUED'):
        final = history_for_selector(subject,kinds,selector,admission['ticket']['text'])if selector and history_for_selector else history(subject, kinds)
        record({'event': 'OPERATIONAL_FASTPATH_ANSWER_RECHECK', 'result': final})
        if selector:
            try:
                fresh=select(selector,final.get('facts',[]),admission['ticket']['text'])
                if fresh['kind']=='RUN_HISTORY':fresh['kind']=chosen['kind']
                newer=[fresh]if fresh['value'].get('run_id')==chosen['value'].get('run_id')else[]
            except ValueError:newer=[]
        else:
            newer = [f for f in final.get('facts', []) if f.get('kind') == chosen['kind']
                     and f.get('state') == 'OBSERVED' and f['value'].get('run_id') == chosen['value'].get('run_id')]
        if not newer:
            return {'status': 'UNRESOLVED', 'business': 'The run was active at the first read; its status could not be confirmed again at answer time.',
                    'history': final, 'model_calls': 0}
        chosen = newer[0]
    state = chosen['value'].get('status')
    verdict = ('failed job' if state == 'FAILED' else 'waiting on job' if state in ('QUEUED', 'RUNNING')
               else 'as designed' if state in ('COMPLETED', 'SUCCEEDED') else 'not found')
    schedule = next((f for f in facts if f.get('kind') == 'SCHEDULE' and f.get('state') == 'OBSERVED'), None)
    rendered = details({'verdict': verdict, 'operational_fact': chosen, 'operational_schedule': schedule}, {subject: node})
    return {'status': 'ANSWERED', 'business': rendered, 'model_calls': 0,
            'technical': {'verdict': verdict, 'operational_fact': deepcopy(chosen),
                          'initial_status': initial_status, 'answer_status': state,
                          'waiting_fixture_still_active': state in ('RUNNING', 'QUEUED'),
                          'scope': 'Native job status only; no data-correctness claim.'}}
