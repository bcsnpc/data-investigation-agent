"""Code-rendered operational particulars from the verdict's ledger witnesses.

No model prose, extra reads, inferred run IDs, or unrelated producer facts.
An expected completion is an estimate, never the scheduled start itself.
"""
from .estate_graph_contract import canonical


def details(support,nodes):
    if support['verdict'] not in ('failed job','waiting on job','latency'):return ''
    fact=support.get('operational_fact')
    if not fact:
        return 'Ledger job details: unavailable; no supporting run was recorded.'
    value=fact['value'];subject=fact['subject'];node=nodes.get(subject,{})
    name=node.get('label') or 'name unavailable (catalog ID '+subject+')'
    status=value.get('status') or ('OVERDUE' if fact['kind']=='OVERDUE' and value.get('overdue')is True else 'unavailable')
    run_id=value.get('run_id') or 'unavailable (no run recorded)'
    start=value.get('start') or 'unavailable'
    end=value.get('end') or ('not finished at observation' if status in ('QUEUED','RUNNING') else 'unavailable')
    lines=['Ledger job details: '+name+'; run ID: '+str(run_id)+'; status: '+status+
           '; start: '+start+'; end: '+end+'; observed: '+fact['observed_at']+'.']
    error=value.get('error')
    message=error if isinstance(error,str) else canonical(error) if error else 'unavailable (not recorded)'
    lines.append('Recorded job error: '+message)
    if support['verdict'] in ('waiting on job','latency'):
        schedule=support.get('operational_schedule');scheduled=schedule.get('value',{}) if schedule else {}
        due=scheduled.get('next_due')
        if scheduled.get('enabled')is False:
            lines.append('Next scheduled run: unavailable (schedule is disabled).')
        else:
            lines.append('Next scheduled run: '+str(due or 'unavailable from the retained ledger facts')+'.')
        if value.get('due_at'):lines.append('Declared due time for the unstarted run: '+value['due_at']+'.')
        if support.get('expected_update_at'):
            lines.append('Estimated update after the scheduled start, using observed median duration: '+support['expected_update_at']+'.')
    return '\n'.join(lines)
