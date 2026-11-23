"""Trusted installation preparation, synthetic DEV only. No network or grants."""
from copy import deepcopy
from .adapters.reasoning_openrouter import BASE, READ_TOOLS
from .adapters.provider_runtime import validate


def configuration(prior, *, model, discovered_models, secret_reference):
    rows={row['id']:row for row in discovered_models}
    row=rows.get(model)
    if not row or 'tools'not in (row.get('supported_parameters')or[]):raise ValueError('OPENROUTER_DISCOVERED_TOOL_MODEL_REQUIRED')
    free=model.endswith(':free')
    pricing=row.get('pricing')or{}
    if free and any(str(pricing.get(key))not in ('0','0.0')for key in ('prompt','completion')):
        raise ValueError('OPENROUTER_ZERO_PRICED_FREE_MODEL_REQUIRED')
    from decimal import Decimal
    rates={key:float(Decimal(str(pricing[key]))*1000000)for key in ('prompt','completion')}
    value={'gateway_identity':prior['gateway_identity'],'worker_identity':'round27-free-openrouter-'+model.replace('/','-'),
           'provider':'openrouter','endpoint':BASE,'model':model,'secret_reference':deepcopy(secret_reference),
           'synthetic_only':True,'quality_scope':'DEV_ONLY',
           'rate_card':{'input_rate':rates['prompt'],'output_rate':rates['completion'],
                        'source':'https://openrouter.ai/api/v1/models','observed_at':'2026-11-22'}}
    validate(value)
    return value


def gateway(prior,config,*,paid_qualified=False):
    validate(config)
    if config.get('provider')!='openrouter':raise ValueError('OPENROUTER_CONFIG_REQUIRED')
    if not config['model'].endswith(':free') and not paid_qualified:raise ValueError('OPENROUTER_PAID_NOT_QUALIFIED')
    result=deepcopy(prior);actor=result['identities'][config['gateway_identity']]
    if actor.get('role')!='model' or actor.get('sql'):raise ValueError('EXISTING_MODEL_ACTOR_WITHOUT_SQL_REQUIRED')
    secret=config['secret_reference'];actor.clear()
    actor.update(role='model',ai_providers={'openrouter':{'endpoint':BASE,'models':[config['model']],
        'tools':sorted(READ_TOOLS),'synthetic_only':True,'quality_scope':'DEV_ONLY','paid_qualified':paid_qualified}},
        http=[{'method':'GET','url':secret['vault_url']+'/secrets/'+secret['secret_name']+'/'+secret['secret_version']+'?api-version=7.4','purpose':'metadata'},
              *[{'method':'GET','url':BASE+'/'+path,'purpose':'configured_ai'}for path in ('models','key')],
              {'method':'POST','url':BASE+'/chat/completions','purpose':'configured_ai'}])
    return result
