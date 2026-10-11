"""Recorded dollar-guard authority for new agent tapes; historical captures stay unchanged."""
import json,os
CONTROL='AGENT_DOLLAR_GUARD_DECLARATION'
VERSION='agent-dollar-guard-v1'
NEW_VERSION='bounded-worker-tape-v10'
def schema(value):
 if not isinstance(value,dict) or set(value)!={'control','version','configured','ceiling_microdollars','admission'}:raise ValueError('AGENT_DOLLAR_GUARD_SCHEMA')
 if value['control']!=CONTROL or value['version']!=VERSION or value['configured'] is not True or value['admission']!='MODEL_SPEND_V1' or type(value['ceiling_microdollars']) is not int or value['ceiling_microdollars']<=0:raise ValueError('AGENT_DOLLAR_GUARD_SCHEMA')
 return value

def declare(*,tape=None,environment=None,policy_factory=None,emit=None):
 if tape is not None and tape.replaying:
  projected=tape.version=='privacy-projected-tape-v2' and tape.bootstrap.get('state',{}).get('agent_dollar_guard')==VERSION
  if tape.version!=NEW_VERSION and not projected:raise ValueError('AGENT_DOLLAR_GUARD_NOT_RECORDED')
  # Take owning validated tape bytes. No SpendBudget constructor/DB/env needed.
  return schema(json.loads(tape.take('CONFIGURATION')))
 env=os.environ if environment is None else environment
 path=env.get('INVESTIGATOR_MODEL_SPEND_DB');raw=env.get('INVESTIGATOR_MODEL_SPEND_MICRODOLLARS')
 if not path or not raw:raise ValueError('AGENT_DOLLAR_GUARD_REQUIRED')
 try:ceiling=int(raw)
 except (ValueError,TypeError):raise ValueError('AGENT_DOLLAR_GUARD_REQUIRED') from None
 if ceiling<=0:raise ValueError('AGENT_DOLLAR_GUARD_REQUIRED')
 if policy_factory is None:
  from investigator.model_spend import SpendBudget
  policy_factory=SpendBudget
 policy_factory(path,ceiling) # validates actual persisted configured policy first
 value=schema({'control':CONTROL,'version':VERSION,'configured':True,'ceiling_microdollars':ceiling,'admission':'MODEL_SPEND_V1'})
 if tape is not None:
  projected=tape.version=='privacy-projected-tape-v2' and tape.bootstrap.get('state',{}).get('agent_dollar_guard')==VERSION
  if tape.version!=NEW_VERSION and not projected:raise ValueError('NEW_AGENT_DOLLAR_GUARD_VERSION_REQUIRED')
 if emit is not None:emit('CONFIGURATION',value)
 return value
