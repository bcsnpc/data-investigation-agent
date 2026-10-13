"""Offline admission against a retained, fresh control-plane job observation.

No job is read, started, or updated here. The operator supplies the unmodified
GET result and its observation time immediately before constructing a launch.
"""
import hashlib
import json
import math
import re
import time


def admit(stage, observation, *, now=None):
    now=time.time() if now is None else now
    if (not isinstance(observation,dict) or set(observation)!={'observed_at','job'}
            or type(now)not in (int,float) or not math.isfinite(now)):
        raise ValueError('CLOUD_JOB_TIMEOUT_OBSERVATION_REQUIRED')
    observed=observation['observed_at'];job=observation['job']
    if type(observed)not in (int,float) or not math.isfinite(observed) or not 0<=now-observed<=300:
        raise ValueError('CLOUD_JOB_TIMEOUT_OBSERVATION_STALE')
    if not isinstance(job,dict) or not re.fullmatch(
            r'/subscriptions/[0-9a-f-]{36}/resourceGroups/[A-Za-z0-9_.()-]+/providers/Microsoft.App/jobs/[a-z0-9-]+',job.get('id','')):
        raise ValueError('CLOUD_JOB_RESOURCE_OBSERVATION_REQUIRED')
    timeout=job.get('properties',{}).get('configuration',{}).get('replicaTimeout')
    if type(timeout)is not int or timeout<=0:raise ValueError('CLOUD_JOB_TIMEOUT_NOT_ESTABLISHED')
    required=stage.get('required_runtime_seconds')
    if type(required)is not int or required<1800 or timeout!=required:
        raise ValueError('CLOUD_JOB_RUNTIME_MUST_MATCH_APPROVED_1800_OR_GREATER')
    deadline=stage.get('deadline')
    if type(deadline)not in (int,float) or not math.isfinite(deadline) or deadline<=now:
        raise ValueError('CLOUD_JOB_DEADLINE_REQUIRED')
    requested=deadline-now
    if requested>timeout:raise ValueError('CLOUD_STAGE_DEADLINE_EXCEEDS_JOB_TIMEOUT')
    reserve=stage.get('finalization_reserve_seconds')
    if type(reserve)is not int or reserve<600 or requested>min(1200,timeout-reserve):
        raise ValueError('CLOUD_STAGE_FINALIZATION_RESERVE_REQUIRED')
    return {'version':'cloud-job-deadline-admission-v1','job_id':job['id'],
            'observed_at':observed,'admitted_at':now,'deadline':deadline,
            'replica_timeout_seconds':timeout,'remaining_deadline_seconds':requested,
            'finalization_reserve_seconds':reserve,'work_limit_seconds':1200,
            'observation_sha256':hashlib.sha256(json.dumps(observation,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'platform_settings_changed':False}


def isolation(stage, observation, *, now):
    """Validate bounded operator readbacks; worker rechecks the actual PG lease."""
    if not isinstance(observation,dict)or set(observation)!={'observed_at','executions','scheduled_job','advisory_lock_holders','lease'}:
        raise ValueError('CLOUD_ISOLATION_OBSERVATION_REQUIRED')
    at=observation['observed_at']
    if type(at)not in (float,int)or not math.isfinite(at)or not 0<=now-at<=300:
        raise ValueError('CLOUD_ISOLATION_OBSERVATION_STALE')
    executions=observation['executions']
    if not isinstance(executions,list)or len(executions)>1000:raise ValueError('CLOUD_EXECUTION_OBSERVATION_BOUND')
    if any(not isinstance(v,dict)or v.get('properties',{}).get('status')not in ('Succeeded','Failed','Stopped')for v in executions):
        raise ValueError('CLOUD_OTHER_EXECUTION_NOT_DRAINED')
    scheduled=observation['scheduled_job']
    if not isinstance(scheduled,dict)or scheduled.get('properties',{}).get('configuration',{}).get('triggerType')!='Manual':
        raise ValueError('CLOUD_OLD_SCHEDULE_NOT_PAUSED')
    if type(observation['advisory_lock_holders'])is not int or observation['advisory_lock_holders']!=0:
        raise ValueError('CLOUD_SHARED_LOCK_NOT_IDLE')
    declared=stage.get('exclusive_writer');lease=observation['lease']
    if (not isinstance(declared,dict)or set(declared)!={'owner','lease_id','expires_at'}
            or not isinstance(lease,dict)or any(lease.get(k)!=v for k,v in declared.items())
            or lease.get('status')!='ACTIVE' or type(lease.get('expires_at'))not in (int,float)
            or lease['expires_at']<now+stage['required_runtime_seconds']):
        raise ValueError('CLOUD_EXCLUSIVE_LEASE_NOT_ESTABLISHED_FOR_FULL_RUNTIME')
    return {'observation_sha256':hashlib.sha256(json.dumps(observation,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'owner':declared['owner'],'lease_id':declared['lease_id'],'expires_at':declared['expires_at'],
            'operational_boundary':'Old images and raw administrative SQL must remain drained; this is not a database ACL.'}
