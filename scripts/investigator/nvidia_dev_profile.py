"""Trusted synthetic-dev configuration preparation; never launches a run."""
from copy import deepcopy
from .adapters.reasoning_nvidia import BASE, READ_TOOLS
from .adapters.provider_runtime import validate


def configuration(prior, *, model, discovered_models, secret_reference):
    if model not in discovered_models:
        raise ValueError('NVIDIA_MODEL_NOT_DISCOVERED')
    value={key:deepcopy(prior[key]) for key in ('gateway_identity',)}
    value.update(provider='nvidia', endpoint=BASE, model=model,
        worker_identity='round27-free-'+model.replace('/','-'),
        secret_reference=deepcopy(secret_reference), synthetic_only=True, quality_scope='DEV_ONLY',
        rate_card={'input_rate':0,'output_rate':0,'source':'https://build.nvidia.com',
                   'observed_at':'2026-11-22'})
    validate(value)
    return value


def gateway(prior, config):
    """Replace only the existing model actor's provider/key HTTP surface.

    Estate SQL, investigator/scanner scopes and platform grants are untouched.
    This is local policy preparation, not an identity/permission grant.
    """
    validate(config)
    if config.get('provider')!='nvidia':raise ValueError('NVIDIA_CONFIG_REQUIRED')
    result=deepcopy(prior);actor=result['identities'][config['gateway_identity']]
    if actor.get('role')!='model':raise ValueError('EXISTING_MODEL_ACTOR_REQUIRED')
    if actor.get('sql'):raise ValueError('MODEL_ACTOR_CANNOT_HAVE_SQL')
    secret=config['secret_reference']
    actor.clear()
    actor.update(role='model', ai_providers={'nvidia':{'endpoint':BASE,'models':[config['model']],
        'tools':sorted(READ_TOOLS),'synthetic_only':True,'quality_scope':'DEV_ONLY'}},
        http=[{'method':'GET','url':secret['vault_url']+'/secrets/'+secret['secret_name']+'/'+secret['secret_version']+'?api-version=7.4','purpose':'metadata'},
              {'method':'GET','url':BASE+'/models','purpose':'configured_ai'},
              {'method':'POST','url':BASE+'/chat/completions','purpose':'configured_ai'}])
    return result
