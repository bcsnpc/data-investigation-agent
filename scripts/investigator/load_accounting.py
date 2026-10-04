"""Neutral own-run accounting contract and successful completion validation."""
from .source_delivery import instant

# This is the audit writer's interface, not an application/domain schema.
COLUMNS = {'run_id':'nvarchar','pipeline_name':'nvarchar','status':'nvarchar',
           'rows_read':'bigint','rows_written':'bigint','accounting_state':'nvarchar',
           'start_time_utc':'nvarchar','end_time_utc':'nvarchar','high_watermark':'nvarchar'}


def classify(rows, producer_native_id):
    excluded=[]
    def unavailable(reason):
        result={'status':'UNAVAILABLE','reason':reason}
        if excluded:result['excluded_rows']=excluded
        return result
    if not isinstance(rows,list) or not rows:
        return unavailable('The declared audit returned no run; successful completion is not established.')
    try:
        valid=[]
        for index,row in enumerate(rows):
            try:_validate_row(row,producer_native_id)
            except (ValueError,TypeError,KeyError,AttributeError) as exc:
                identity=row.get('run_id') if isinstance(row,dict) else None
                excluded.append({'row_index':index,'run_id':identity if isinstance(identity,str) and 1<=len(identity)<=300 else None,
                                 'reason':str(exc)})
            else:valid.append(row)
        if not valid:return unavailable('No valid audit row covers the declared producer.')
        ordered=sorted(valid,key=lambda r:instant(r['start_time_utc']))
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
    result={'status':'CURRENT','run_state':'SUCCEEDED','run_id':latest['run_id'],
            'started_at':latest['start_time_utc'],'completed_at':latest['end_time_utc'],
            'accounting':counts,'high_watermark':latest['high_watermark'],
            'reason':'The audited run completed with its own activity counters; source capture currency was not established.'}

    if excluded:
        result['excluded_rows']=excluded
        result['reason']+=' Malformed audit rows were excluded; this is the latest valid run, not proof that no later run exists.'
    return result


def _validate_row(row,producer_native_id):
    if not isinstance(row,dict) or set(row)!=set(COLUMNS):
        raise ValueError('Audit row does not carry the complete accounting contract.')
    if row['pipeline_name']!=producer_native_id:raise ValueError('Audit row names a different producer.')
    if not isinstance(row['run_id'],str) or not 1<=len(row['run_id'])<=300:
        raise ValueError('Audit run identity is missing or unbounded.')
    start=instant(row['start_time_utc'])
    if row['status'] not in ('Succeeded','Failed','InProgress','Cancelled','NotStarted'):
        raise ValueError('Audit completion status is unsupported.')
    # Unsuccessful runs stay in ordering; no older success can hide them.
    if row['status']!='Succeeded':return
    if instant(row['end_time_utc'])<start:raise ValueError('Audit run timestamps are contradictory.')
    if row['accounting_state']!='OBSERVED_COPY_OUTPUT':
        raise ValueError('Audit accounting is not observed copy-activity output.')
    for key in ('rows_read','rows_written'):
        value=row[key]
        if isinstance(value,bool) or value is None or str(int(value))!=str(value) or int(value)<0:
            raise ValueError('Audit counter missing or not a nonnegative integer.')
