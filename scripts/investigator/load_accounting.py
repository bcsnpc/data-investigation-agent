"""Neutral own-run accounting contract and successful completion validation."""
from .source_delivery import instant

# This is the audit writer's interface, not an application/domain schema.
COLUMNS = {'run_id':'nvarchar','pipeline_name':'nvarchar','status':'nvarchar',
           'rows_read':'bigint','rows_written':'bigint','accounting_state':'nvarchar',
           'start_time_utc':'nvarchar','end_time_utc':'nvarchar','high_watermark':'nvarchar'}


def classify(rows, producer_native_id):
    def unavailable(reason): return {'status':'UNAVAILABLE','reason':reason}
    if not isinstance(rows,list) or not rows:
        return unavailable('The declared audit returned no run; successful completion is not established.')
    try:
        if any(set(r)!=set(COLUMNS) for r in rows):
            return unavailable('Audit response does not carry the complete accounting contract.')
        if any(r['pipeline_name']!=producer_native_id for r in rows):
            return unavailable('Audit row names a different producer.')
        ordered=sorted(rows,key=lambda r:instant(r['start_time_utc']))
        latest=ordered[-1]
        if any(instant(r['start_time_utc'])==instant(latest['start_time_utc']) and r!=latest for r in ordered[:-1]):
            return unavailable('Latest audit run is ambiguous.')
        if latest['status']!='Succeeded':
            return unavailable('Latest audited run does not establish successful completion: '+str(latest['status']))
        start,end=instant(latest['start_time_utc']),instant(latest['end_time_utc'])
        if end<start:return unavailable('Audit run timestamps are contradictory.')
        if latest['accounting_state']!='OBSERVED_COPY_OUTPUT':
            return unavailable('Audit accounting is not observed copy-activity output.')
        counts={}
        for key in ('rows_read','rows_written'):
            v=latest[key]
            if isinstance(v,bool) or v is None or str(int(v))!=str(v) or int(v)<0:
                return unavailable('Audit counter missing or not a nonnegative integer.')
            counts[key]=int(v)
        if not isinstance(latest['run_id'],str) or not latest['run_id']:
            return unavailable('Audit run identity is missing.')
    except (ValueError,TypeError,KeyError,AttributeError):
        return unavailable('Audit response has malformed accounting or run timestamps.')
    return {'status':'CURRENT','run_state':'SUCCEEDED','run_id':latest['run_id'],
            'started_at':latest['start_time_utc'],'completed_at':latest['end_time_utc'],
            'accounting':counts,'high_watermark':latest['high_watermark'],
            'reason':'The audited run completed with its own activity counters; source capture currency was not established.'}

