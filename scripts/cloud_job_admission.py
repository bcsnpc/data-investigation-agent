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
    deadline=stage.get('deadline')
    if type(deadline)not in (int,float) or not math.isfinite(deadline) or deadline<=now:
        raise ValueError('CLOUD_JOB_DEADLINE_REQUIRED')
    requested=deadline-now
    if requested>timeout:raise ValueError('CLOUD_STAGE_DEADLINE_EXCEEDS_JOB_TIMEOUT')
    return {'version':'cloud-job-deadline-admission-v1','job_id':job['id'],
            'observed_at':observed,'admitted_at':now,'deadline':deadline,
            'replica_timeout_seconds':timeout,'remaining_deadline_seconds':requested,
            'observation_sha256':hashlib.sha256(json.dumps(observation,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'platform_settings_changed':False}
