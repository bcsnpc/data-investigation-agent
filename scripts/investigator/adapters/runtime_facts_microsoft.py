"""Microsoft runtime facts: guarded list APIs and exact declared SQL objects.

No refresh/run/write endpoint is callable here. Every request/response is retained
before its fields can become facts; transport and accounting remain existing
MetadataHttp / managed_sql_worker / SCAN Meter boundaries.
"""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import json
import re
from urllib.parse import quote
from uuid import UUID
from ..facts_collectors import observation, derived_runs
from ..shared_state import encoded, sha
from ..estate_graph_incremental import is_stop_condition
from .metadata_error import MetadataUnavailable, safe_failure

STATUSES={'Completed':'SUCCEEDED','Succeeded':'SUCCEEDED','Failed':'FAILED','InProgress':'RUNNING',
          'NotStarted':'QUEUED','Queued':'QUEUED','Cancelled':'CANCELLED','Canceled':'CANCELLED',
          'Unknown':'UNKNOWN','Disabled':'UNKNOWN','Deduped':'CANCELLED'}


def ident(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}',value):raise ValueError('FACT_SQL_IDENTIFIER')
    return '['+value+']'


def sql_request(route,kind):
    """Compile from exact declared identifiers, never model query text."""
    obj=ident(route['schema'])+'.'+ident(route['table'])
    if kind=='audit':
        fields=route['columns']
        required={'run_id','start','end','status','rows_read','rows_written'}
        if not required<=set(fields)<=required|{'error','high_watermark'}:raise ValueError('FACT_AUDIT_COLUMNS')
        columns=sorted(fields)
        query='SELECT TOP 20 '+','.join(ident(fields[k])+' AS '+ident(k) for k in columns)+' FROM '+obj+' ORDER BY '+ident(fields['start'])+' DESC'
    elif kind=='profile':
        keys=route['key_columns']
        if not isinstance(keys,list) or not 1<=len(keys)<=8 or len(set(keys))!=len(keys):raise ValueError('FACT_PROFILE_KEYS')
        columns=['row_count']+['checksum_'+str(i) for i in range(len(keys))]
        expressions=['COUNT_BIG(*) AS [row_count]']
        for i,key in enumerate(keys):
            column=ident(key)
            material="CASE WHEN "+column+" IS NULL THEN 'NULL' ELSE 'VALUE'+CONVERT(nvarchar(max),"+column+') END'
            expressions.append("SUM(CONVERT(decimal(38,0),CONVERT(bigint,SUBSTRING(HASHBYTES('SHA2_256',"+material+"),1,8)))) AS [checksum_"+str(i)+']')
        query='SELECT '+','.join(expressions)+' FROM '+obj
    else:raise ValueError('FACT_SQL_QUERY_KIND')
    return {'query':query,'parameters':[],'read_only_objects':[obj],'max_rows':21 if kind=='audit' else 2,'result_columns':columns}


def attested_sql(answer,route,request):
    report=answer.get('surface_report') or {}
    if (answer.get('read_only_verified') is not True or answer.get('surface_report_binding')!='VALUE_QUERY'
        or report.get('identity')!=route['principal'] or report.get('object')!=route['database']
        or report.get('engine') not in ('Microsoft Azure SQL Data Warehouse','Microsoft SQL Azure')):
        raise ValueError('FACT_SQL_QUERY_BOUND_ATTESTATION_REQUIRED')
    rows=answer.get('rows')
    if not isinstance(rows,list) or len(rows)>=request['max_rows']:raise ValueError('FACT_SQL_RESULT_BOUND')
    if any(not isinstance(row,dict) or set(row)!=set(request['result_columns']) for row in rows):raise ValueError('FACT_SQL_RESULT_SHAPE')
    return rows


class MicrosoftRuntimeFacts:
    def __init__(self,subjects,*,http,retain,sql=None,now=None):
        if not isinstance(subjects,dict) or not 1<=len(subjects)<=200:raise ValueError('FACT_SUBJECT_DECLARATIONS')
        self.subjects=subjects;self.http=http;self.retain=retain;self.sql=sql
        self.identity='microsoft-runtime:'+sha(subjects)
        self.cache={};self.signals={};self.evidence=[]
        for node,route in subjects.items():
            if not isinstance(node,str) or not node:raise ValueError('FACT_GRAPH_NODE_REQUIRED')
            if route.get('kind') not in ('JOB','MODEL','TABLE'):raise ValueError('FACT_NATIVE_NODE_KIND')
            UUID(route['workspace']);UUID(route['item'])

    def _retain(self,request,response):
        reference=self.retain(encoded({'request':request,'response':response}).encode())
        if not isinstance(reference,dict) or not re.fullmatch('[a-f0-9]{64}',reference.get('sha256','')):
            raise ValueError('FACT_RETAINED_RECEIPT_REQUIRED')
        evidence='sha256:'+reference['sha256'];self.evidence.append(evidence)
        return evidence

    def _get(self,path,audience='fabric'):
        request={'method':'GET','audience':audience,'endpoint':path}
        try:
            response=self.http(path,audience=audience)
        except Exception as error:
            if is_stop_condition(error):raise
            receipt=self._retain(request,{'status':'UNAVAILABLE','failure':safe_failure(error)})
            return None,receipt,'READ_FAILED:'+type(error).__name__+':'+str(getattr(error,'http_status',None))
        receipt=self._retain(request,response)
        if response.get('status_code')!=200:return None,receipt,'HTTP_'+str(response.get('status_code'))
        return response['text'],receipt,None

    def _sql(self,route,kind):
        request=sql_request(route,kind)
        if self.sql is None:
            receipt=self._retain({'kind':kind,'route':{k:route[k] for k in ('database','schema','table')}},{'status':'UNAVAILABLE','reason':'SQL_READ_ROUTE_NOT_CONFIGURED'})
            return None,receipt,'SQL_READ_ROUTE_NOT_CONFIGURED'
        try:
            answer=self.sql(route,request)
            # Retain even rejected responses; successful data are not trusted
            # until the query-bound reader/object attestation checks pass.
            receipt=self._retain({'kind':kind,'database':route['database'],**request},answer)
            return attested_sql(answer,route,request),receipt,None
        except Exception as error:
            if is_stop_condition(error):raise
            receipt=self._retain({'kind':kind,'database':route['database'],**request},{'status':'UNAVAILABLE','failure':safe_failure(error)})
            return None,receipt,'SQL_READ_FAILED:'+type(error).__name__+':'+str(getattr(error,'error_number',None))

    def _gap(self,node,kind,reason,at,evidence):
        return observation(node,kind,None,at,evidence,self.identity,state='UNAVAILABLE',reason=reason)

    def list_changes(self,subjects):
        if not set(subjects)<=set(self.subjects):raise ValueError('FACT_NATIVE_SUBJECT_SCOPE')
        self.evidence=[];items=[]
        # Each route uses the provider's bounded recent-run list, not a GET per
        # run. Caller selects due subjects and applies a shared scan budget.
        for node in subjects:
            route=self.subjects[node];kind=route['kind'];workspace=route['workspace'];item=route['item']
            if kind=='JOB':
                body,proof,error=self._get('workspaces/'+workspace+'/items/'+item+'/jobs/instances')
            elif kind=='MODEL':
                body,proof,error=self._get('groups/'+workspace+'/datasets/'+item+'/refreshes?$top=20','powerbi')
            else:
                # Workspace item modify dates are definition dates, never load
                # markers. Data loads require declared audit/Delta evidence.
                audit=route.get('audit')
                if audit:
                    rows,proof,error=self._sql(audit,'audit');body={'audit_rows':rows} if rows is not None else None
                else:
                    proof=self._retain({'node':node,'operation':'TABLE_LOAD_DECLARATION'},{'status':'UNAVAILABLE','reason':'NO_DECLARED_AUDIT_OR_DELTA_HISTORY_ROUTE'})
                    body=None;error='NO_DECLARED_AUDIT_OR_DELTA_HISTORY_ROUTE'
            self.cache[node]=(body,proof,error)
            marker=sha({'body':body,'error':error})
            load=None
            if kind=='TABLE' and body and body.get('audit_rows'):
                succeeded=[r for r in body['audit_rows'] if str(r['status']).upper() in ('SUCCEEDED','COMPLETED')]
                if succeeded:load=str(succeeded[0]['run_id'])
            items.append({'subject':node,'marker':marker,'load_marker':load})
        return {'items':items,'complete':True,'evidence_ids':list(self.evidence)}

    def fetch(self,node,*,now):
        if node not in self.cache:raise ValueError('FACT_FETCH_NOT_LISTED')
        route=self.subjects[node];body,proof,error=self.cache[node];kind=route['kind']
        fact_kind={'JOB':'JOB_RUN','MODEL':'REFRESH_RUN','TABLE':'TABLE_LOAD'}[kind]
        if error:return [self._gap(node,fact_kind,error,now,[proof])]
        if kind=='TABLE':
            rows=body['audit_rows']
            if not rows:return [observation(node,'TABLE_LOAD',{'runs':[],'latest_successful_end':None},now,[proof],self.identity,state='OBSERVED_NEGATIVE')]
            successes=[row for row in rows if str(row['status']).upper() in ('SUCCEEDED','COMPLETED') and row.get('end')]
            return [observation(node,'TABLE_LOAD',{'audit_runs':rows,'latest_successful_end':successes[0]['end'] if successes else None,
                'accounting_source':'DECLARED_WAREHOUSE_AUDIT','delta_history':'UNAVAILABLE_FROM_SQL_ENDPOINT'},now,[proof],self.identity)]
        native=body.get('value')
        if not isinstance(native,list) or len(native)>100:raise ValueError('FACT_NATIVE_RUN_LIST_BOUND')
        # Continuation means coverage is partial, explicitly named. Never claim
        # absence or overdue from a truncated listing.
        truncated=bool(body.get('continuationUri') or body.get('continuationToken') or body.get('@odata.nextLink'))
        runs=[]
        for row in native[:20]:
            run_id=row.get('id') or row.get('requestId')
            if run_id is None:raise ValueError('FACT_NATIVE_RUN_ID')
            runs.append({'run_id':str(run_id),'start':row.get('startTimeUtc') or row.get('startTime'),
                'end':row.get('endTimeUtc') or row.get('endTime'),'status':STATUSES.get(row.get('status'),'UNKNOWN'),
                'error':row.get('failureReason') or row.get('serviceExceptionJson'),
                'rows_read':None,'rows_written':None})
        result=[observation(node,'RUN_HISTORY',{'runs':runs,'listing_complete':not truncated},now,[proof],self.identity,
            state='OBSERVED_NEGATIVE' if not runs and not truncated else 'OBSERVED')]
        if runs:
            # Keep the full recent window for duration/overdue derivation; the
            # latest run remains the JOB_RUN/REFRESH_RUN tool value.
            result.append(observation(node,fact_kind,{**runs[0],'recent_runs':runs,'accounting':'UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA'},now,[proof],self.identity))
            result.extend(derived_runs(node,runs,now,[proof],self.identity))
        if truncated:result.append(self._gap(node,'COVERAGE','RECENT_RUN_LIST_HAS_CONTINUATION; no absence/overdue established',now,[proof]))
        if kind=='MODEL':
            if runs:result.append(observation(node,'REFRESH_STATE',{'state':runs[0]['status'],'run_id':runs[0]['run_id'],'last_end':runs[0]['end']},now,[proof],self.identity))
            schedule,receipt,failure=self._get('groups/'+route['workspace']+'/datasets/'+route['item']+'/refreshSchedule','powerbi')
            if failure:result.append(self._gap(node,'SCHEDULE',failure,now,[receipt]))
            else:
                try:
                    due=refresh_due(schedule,now)
                    result.append(observation(node,'SCHEDULE',{'native_schedule':schedule,**due},now,[receipt],self.identity))
                    if due['previous_due'] and not truncated:
                        result.extend(v for v in derived_runs(node,runs,now,[proof,receipt],self.identity,schedule={'next_due':due['previous_due']}) if v['kind']=='OVERDUE')
                except ValueError as error:result.append(self._gap(node,'SCHEDULE',str(error),now,[receipt]))
        elif kind=='JOB' and route.get('job_type'):
            schedules,receipt,failure=self._get('workspaces/'+route['workspace']+'/items/'+route['item']+'/jobs/'+quote(route['job_type'],safe='')+'/schedules')
            if failure:result.append(self._gap(node,'SCHEDULE',failure,now,[receipt]))
            else:result.append(observation(node,'SCHEDULE',{'native_schedules':schedules,'next_due':None,'reason':'Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap.'},now,[receipt],self.identity))
        if kind=='JOB' and route.get('audit'):
            rows,receipt,failure=self._sql(route['audit'],'audit')
            if failure:result.append(self._gap(node,'COVERAGE','DECLARED_AUDIT_UNAVAILABLE:'+failure,now,[receipt]))
            else:
                by_id={str(row['run_id']):row for row in rows}
                if runs and runs[0]['run_id'] in by_id:
                    audit=by_id[runs[0]['run_id']]
                    current=next(v for v in result if v['kind']=='JOB_RUN')
                    current['value'].update(rows_read=_count(audit['rows_read']),rows_written=_count(audit['rows_written']),accounting='DECLARED_WAREHOUSE_AUDIT')
                    current['provenance']['evidence_ids'].append(receipt)
                else:result.append(self._gap(node,'COVERAGE','DECLARED_AUDIT_HAS_NO_ROW_FOR_LISTED_RUN',now,[proof,receipt]))
        elif kind=='JOB':
            result.append(self._gap(node,'COVERAGE','LOAD_ACCOUNTING_UNAVAILABLE: no declared audit table or monitoring query route; no counts estimated',now,[proof]))
        coverage=[v for v in result if v['kind']=='COVERAGE']
        result=[v for v in result if v['kind']!='COVERAGE']
        gaps=[v['reason'] for v in coverage if v['state']=='UNAVAILABLE']
        proofs=list(dict.fromkeys([proof,*[e for v in coverage for e in v['provenance']['evidence_ids']]]))
        result.append(self._gap(node,'COVERAGE','; '.join(gaps),now,proofs) if gaps else
            observation(node,'COVERAGE',{'gaps':[],'history_empty':not runs,'listing_complete':not truncated},now,proofs,self.identity,
                state='OBSERVED_NEGATIVE' if not runs else 'OBSERVED'))
        return result

    def profile(self,node,*,load_marker,now):
        route=self.subjects[node].get('profile')
        if route is None:
            proof=self._retain({'node':node,'operation':'PROFILE_DECLARATION'},{'status':'UNAVAILABLE','reason':'NO_DECLARED_PROFILE_SQL_ROUTE'})
            return self._gap(node,'TABLE_PROFILE','NO_DECLARED_PROFILE_SQL_ROUTE',now,[proof])
        rows,proof,error=self._sql(route,'profile')
        if error:return self._gap(node,'TABLE_PROFILE',error,now,[proof])
        if len(rows)!=1:return self._gap(node,'TABLE_PROFILE','PROFILE_AGGREGATE_NOT_SINGLE_ROW',now,[proof])
        row=rows[0]
        return observation(node,'TABLE_PROFILE',{'load_marker':load_marker,'row_count':_count(row['row_count']),
            'checksum':encoded({key:val for key,val in row.items() if key!='row_count'}),
            'checksum_method':'SUM_SHA256_64_PER_DECLARED_COLUMN_SQL_TEXT_REPRESENTATION_NOT_EQUALITY_PROOF',
            'key_columns':route['key_columns']},now,[proof],self.identity)


def _count(value):
    if value is None:return None
    if isinstance(value,bool) or not re.fullmatch('[0-9]+',str(value)):raise ValueError('FACT_NONNEGATIVE_EXACT_INTEGER')
    return int(value)


WINDOWS_ZONES={'UTC':'UTC','Central Standard Time':'America/Chicago','Eastern Standard Time':'America/New_York',
               'Pacific Standard Time':'America/Los_Angeles','India Standard Time':'Asia/Kolkata','GMT Standard Time':'Europe/London'}
DAYS=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']


def refresh_due(schedule,now):
    """Compute declared daily/weekly refresh slots, with timezone/DST explicit."""
    if not isinstance(schedule,dict) or type(schedule.get('enabled')) is not bool:raise ValueError('REFRESH_SCHEDULE_SHAPE_UNAVAILABLE')
    if not schedule['enabled']:return {'previous_due':None,'next_due':None,'enabled':False}
    zone_name=schedule.get('localTimeZoneId')
    if zone_name not in WINDOWS_ZONES:raise ValueError('REFRESH_SCHEDULE_TIMEZONE_UNSUPPORTED:'+str(zone_name))
    try:zone=ZoneInfo(WINDOWS_ZONES[zone_name])
    except Exception:raise ValueError('REFRESH_SCHEDULE_TIMEZONE_DATABASE_UNAVAILABLE') from None
    days=schedule.get('days');times=schedule.get('times')
    if not isinstance(days,list) or not days or not set(days)<=set(DAYS) or not isinstance(times,list) or not times:raise ValueError('REFRESH_SCHEDULE_SLOTS_UNAVAILABLE')
    if any(not isinstance(t,str) or not re.fullmatch(r'(?:[01][0-9]|2[0-3]):[0-5][0-9]',t) for t in times):raise ValueError('REFRESH_SCHEDULE_TIME_UNSUPPORTED')
    instant=datetime.fromisoformat(now.replace('Z','+00:00')).astimezone(timezone.utc)
    local=instant.astimezone(zone);slots=[]
    for offset in range(-8,9):
        day=local.date()+timedelta(days=offset)
        if DAYS[day.weekday()] not in days:continue
        for clock in times:
            hour,minute=map(int,clock.split(':'));candidate=datetime(day.year,day.month,day.day,hour,minute,tzinfo=zone)
            # Ambiguous/nonexistent DST slot cannot establish an overdue fact.
            if candidate.replace(fold=0).utcoffset()!=candidate.replace(fold=1).utcoffset():raise ValueError('REFRESH_SCHEDULE_DST_SLOT_AMBIGUOUS')
            slots.append(candidate.astimezone(timezone.utc))
    past=[s for s in slots if s<=instant];future=[s for s in slots if s>instant]
    render=lambda value:value.isoformat().replace('+00:00','Z') if value else None
    return {'previous_due':render(max(past) if past else None),'next_due':render(min(future) if future else None),'enabled':True}
