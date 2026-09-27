"""Classify retained Fabric job history; successful completion is not freshness."""
from datetime import datetime,timezone


def timestamp(value):
    if not isinstance(value,str):raise ValueError('Missing timestamp')
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    # Fabric fields explicitly declare UTC even when the string omits its suffix.
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def classify(observations):
    def unavailable(state,reason):return {'status':'UNAVAILABLE','run_state':state,'reason':reason}
    if not observations:return unavailable('UNKNOWN','No retained job-history response covers this transformation asset.')
    if any(o.get('status')!='AVAILABLE' or not isinstance(o.get('detail'),list) for o in observations):
        return unavailable('UNKNOWN','Retained job history is unavailable or malformed.')
    runs=[run for o in observations for run in o['detail']]
    if not runs:return unavailable('NOT_RUN','The retained history contains no job run; successful completion is not established.')
    try:
        ordered=sorted([(timestamp(r.get('startTimeUtc')),r) for r in runs],key=lambda x:x[0])
        latest_time,latest=ordered[-1]
        if any(t==latest_time and r!=latest for t,r in ordered[:-1]):
            return unavailable('UNKNOWN','Latest retained job run is ambiguous.')
        status=latest.get('status')
        if status in ('Failed','Cancelled','Canceled'):return unavailable('FAILED','Latest retained job failed or was cancelled.')
        if status in ('InProgress','Running'):return unavailable('IN_PROGRESS','Latest retained job has not completed.')
        if status in ('NotStarted','Queued'):return unavailable('NOT_RUN','Latest retained job has not started.')
        if status!='Completed':return unavailable('UNKNOWN','Latest retained job has an unsupported completion status.')
        if latest.get('failureReason') or timestamp(latest.get('endTimeUtc'))<latest_time:
            return unavailable('UNKNOWN','Retained completion evidence is contradictory.')
    except (ValueError,TypeError,AttributeError):
        return unavailable('UNKNOWN','Retained history lacks valid start/end timestamps.')
    return {'status':'CURRENT','run_state':'SUCCEEDED','reason':'Latest retained job completed successfully; freshness was not assessed.',
            'run_id':latest.get('id'),'started_at':latest_time.isoformat(),
            'completed_at':timestamp(latest['endTimeUtc']).isoformat()}
