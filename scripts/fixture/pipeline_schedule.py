"""Bounded publisher-only schedule control for genuine future-load cases."""
from datetime import datetime,timezone,timedelta
from uuid import UUID
import copy


def instant(value):
    if not isinstance(value,str):raise ValueError('SCHEDULE_UTC_REQUIRED')
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None or result.utcoffset()!=timedelta(0):raise ValueError('SCHEDULE_UTC_REQUIRED')
    return result


def same_configuration(left,right):
    if set(left)!=set(right):return False
    def native_time(value,config):
        # Fabric examples omit the suffix while declaring the UTC zone.
        parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
        if parsed.tzinfo is None and config.get('localTimeZoneId')=='UTC':parsed=parsed.replace(tzinfo=timezone.utc)
        return instant(parsed.isoformat())
    return all(native_time(left[k],left)==native_time(right[k],right)if k in ('startDateTime','endDateTime')else left[k]==right[k]for k in left)


class PipelineScheduleScenario:
    def __init__(self,control,item_id):
        self.control=control;self.item_id=str(UUID(item_id))
        self.root='workspaces/'+control.workspace+'/items/'+self.item_id+'/jobs/Pipeline/schedules'

    def list(self):
        native=self.control.call(self.root)['text']
        if (not isinstance(native,dict)or set(native)-{'value','continuationToken','continuationUri'}
                or any(native.get(k)not in (None,'')for k in ('continuationToken','continuationUri'))
                or not isinstance(native.get('value'),list)):
            raise ValueError('SCHEDULE_COMPLETE_NATIVE_LIST_REQUIRED')
        return native['value']

    @staticmethod
    def plan(*,start,now):
        now=instant(now);start=instant(start)
        if not 3600<=(start-now).total_seconds()<=172800:
            raise ValueError('SCHEDULE_FUTURE_HEADROOM_REQUIRED')
        return {'enabled':True,'configuration':{'type':'Cron','interval':60,'localTimeZoneId':'UTC',
            'startDateTime':start.isoformat().replace('+00:00','Z'),
            'endDateTime':(start+timedelta(minutes=1)).isoformat().replace('+00:00','Z')}}

    def create(self,*,start,now,key):
        body=self.plan(start=start,now=now)
        before=self.list()
        if before:raise ValueError('SCHEDULE_EXISTING_STATE_NOT_EMPTY_NO_WRITE')
        response=self.control.call(self.root,'POST',body,key=key)
        native=response['text'];identity=str(UUID(native['id']))
        served=self.control.call(self.root+'/'+identity)['text']
        if (served.get('id')!=identity or served.get('enabled')is not True
                or not same_configuration(served.get('configuration',{}),body['configuration'])):
            raise ValueError('SCHEDULE_CREATED_READBACK_DIFFERS_RECONCILE')
        return {'id':identity,'before':before,'expected':copy.deepcopy(body),'served':served}

    def remove(self,owned,*,key):
        identity=str(UUID(owned['id']))
        if owned.get('before')!=[] or owned.get('served',{}).get('id')!=identity:
            raise ValueError('SCHEDULE_OWNED_CREATION_RECEIPT_REQUIRED')
        native=self.list();matches=[x for x in native if x.get('id')==identity]
        if not matches:return {'status':'OWNED_SCHEDULE_ALREADY_ABSENT','other_schedules':native,'mutations':0}
        if (len(matches)!=1 or matches[0].get('enabled')is not owned['expected']['enabled']
                or not same_configuration(matches[0].get('configuration',{}),owned['expected']['configuration'])):
            raise ValueError('SCHEDULE_CONCURRENT_CHANGE_NO_DELETE')
        self.control.call(self.root+'/'+identity,'DELETE',None,key=key)
        after=self.list()
        if any(x.get('id')==identity for x in after):raise ValueError('SCHEDULE_REMOVAL_NOT_CONFIRMED')
        return {'status':'OWNED_SCHEDULE_REMOVED','other_schedules':after,'mutations':1}
