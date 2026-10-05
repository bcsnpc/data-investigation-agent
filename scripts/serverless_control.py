"""Explicit connection-only pre-warm; all admission/ledger work is controls."""
import time
from run_source_diagnostic import read_once
from sql_layer_policy import policy
from sql_connect_retry import read_with_retry


def prewarm(config,asset_ids,*,admit_control,record_control,sleep=time.sleep,execute=read_once):
    request={'asset_ids':list(asset_ids),'control_mode':'PREWARM'}
    if not policy(config,request)['serverless']:
        raise ValueError('Pre-warm requires a manifest-declared serverless source')
    expected='sql://'+config['sql']['server']+'/'+config['sql']['database']+'/'
    if not asset_ids or any(not a.startswith(expected) for a in asset_ids):
        raise ValueError('Pre-warm leaves the declared source connection')
    def wait(seconds,call):
        record_control('SERVERLESS_RESUME_WAIT',{'seconds':seconds,'status':'STARTED'})
        call()
        record_control('SERVERLESS_RESUME_WAIT',{'seconds':seconds,'status':'COMPLETED'})
    result=read_with_retry(lambda:admit_control('SERVERLESS_PREWARM',lambda:execute(config,request)),
                           sleep,serverless=True,record_wait=wait)
    record_control('SERVERLESS_PREWARM_RESULT',result)
    return result
