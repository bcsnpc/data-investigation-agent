"""Installed transport registry and adapter-owned manifest projections."""
import copy


def configuration(manifest):
    implementations={a['implementation'] for a in manifest['adapters']}
    if implementations!={'microsoft'}:
        raise ValueError('Estate adapter is not installed: '+', '.join(sorted(implementations)))
    if len(manifest['adapters'])!=1:
        raise ValueError('This installed adapter requires one connection bundle')
    from metadata_config import validate_config
    options=copy.deepcopy(manifest['adapters'][0]['options'])
    # Scattered roles/audits/source declarations are forbidden in adapter
    # options: these are derived solely from the neutral manifest inventory.
    if set(options)!={'sql','fabric'}:
        raise ValueError('manifest.adapters.options: expected sql and fabric only')
    identities={i['id']:i for i in manifest['identities']}
    for row in manifest['layers']+manifest['resources']:
        if row['reach']['address']!=row['asset_id']:
            raise ValueError('manifest.reach.address: this adapter requires the exact discovered asset address')
        declared=identities[row['reach']['reader']]['principal']
        options_reader=(options['sql']['auth'].get('account') if row['role']=='APPLICATION'
            else options['fabric'].get('native_reader',{}).get('account')) if 'role' in row else options['fabric'].get('sql_reader',{}).get('account')
        if declared!=options_reader:
            raise ValueError('manifest.identities.'+row['reach']['reader']+': adapter account differs')
        reference=identities[row['reach']['reader']]['credential_reference']
        if row.get('role')=='APPLICATION':
            auth=options['sql']['auth']
            if auth.get('mode')=='federated_reader':
                from .vault_user_cache import credential
                from .federated_reader import reference as identity_reference
                actual=identity_reference(credential(auth))
            elif auth.get('mode')=='managed_identity':
                from .managed_identity import reference as identity_reference
                actual=identity_reference({k:auth[k] for k in ('mode','tenant_id','client_id','principal_id')})
            else:actual=auth['credential_file']
        else:
            reader=options['fabric']['sql_reader']
            if reader.get('mode')=='federated_reader':
                from .vault_user_cache import credential
                from .federated_reader import reference as identity_reference
                actual=identity_reference(credential(reader))
            elif reader.get('mode')=='key_vault_user_cache':
                from .vault_user_cache import credential, reference as identity_reference
                actual=identity_reference(credential(reader))
            elif reader.get('mode')=='managed_identity':
                from .managed_identity import reference as identity_reference
                actual=identity_reference({k:reader[k] for k in ('mode','tenant_id','client_id','principal_id')})
            else:actual=reader['profile']
        if reference!=actual:
            raise ValueError('manifest.identities.'+row['reach']['reader']+': adapter credential reference differs')
    config={'version':1,**options,'storage':{'database':manifest['storage']['inventory']},
        'layer_roles':[{k:layer[k] for k in ('asset_id','role','business_name')} for layer in manifest['layers']]}
    terminal=manifest['system_of_record']
    if terminal is not None:
        layer=next(l for l in manifest['layers'] if l['id']==terminal)
        config['system_of_record']={'asset_id':layer['asset_id'],'reachable':layer['reachable']}
    resources={r['id']:r for r in manifest['resources']}
    audits=[{'delivery_asset_id':p['delivery_asset_id'],'producer_asset_id':p['producer_asset_id'],
        'audit_asset_id':resources[p['audit']['resource']]['asset_id']}
        for p in manifest['pipelines'] if p['audit']['status']=='PRESENT']
    if audits:config['load_audits']=audits
    if manifest['lineage']['source_delivery'] is not None:
        config['source_delivery']=copy.deepcopy(manifest['lineage']['source_delivery'])
    config=validate_config(config)
    # The manifest hash, not the adapter subset, is pinned by discovery.
    from ..onboarding import digest
    from ..provider_terms import declaration
    config['_estate']={'manifest_hash':digest(manifest),'round':manifest['budgets']['round'],
        'capability_ceiling':manifest['capability_ceiling'],'layers':manifest['layers'],'resources':manifest['resources'],
        # Code-source credentials/declarations never reach investigation workers.
        'lineage':{k:v for k,v in manifest['lineage'].items() if k!='code_sources'},
        'accepted_limits':manifest['accepted_limits'],
        # Recorder configuration only, never a worker option or model prompt.
        'provider_terms':declaration(manifest['model']), 'trace_footer':True}
    if 'execution' in manifest:config['_estate']['execution']=copy.deepcopy(manifest['execution'])
    if 'investigation' in manifest:config['_estate']['investigation']=copy.deepcopy(manifest['investigation'])
    if 'recording' in manifest:
        config['_estate']['recording']=copy.deepcopy(manifest['recording'])
    return config


def transports(config):
    if config.get('_estate',{}).get('execution',{}).get('mode')=='LOCAL_EXPORTED':
        def forbidden(*args,**kwargs):
            raise ValueError('LOCAL_NATIVE_TRANSPORT_FORBIDDEN')
        return forbidden,forbidden
    from run_native_diagnostic import transport as native
    from run_source_diagnostic import transport as source
    return lambda r:native(config,r),lambda r:source(config,r)


def validate_provider_credential(credential):
    from .managed_identity import validate,validate_secret_reference
    if credential.get('mode')=='managed_identity':
        validate(credential);return
    if credential.get('mode')=='key_vault':
        if set(credential)!={'mode','reference'}:raise ValueError('manifest.model.credential: invalid vault reference')
        validate_secret_reference(credential['reference']);return
    if set(credential)!={'subscription_id','resource_group','account'} or any(not isinstance(v,str) or not v for v in credential.values()):
        raise ValueError('manifest.model.credential: invalid installed provider options')


def validate_registered_options(manifest):
    # Uninstalled adapters/providers can pass neutral schema validation, but
    # cannot execute. Every installed native options object is closed here.
    if {a['implementation'] for a in manifest['adapters']}=={'microsoft'}:configuration(manifest)
    if manifest['model']['provider']=='azure':validate_provider_credential(manifest['model']['credential'])


def provider(name,credential):
    from ..adaptive_planner import azure_plan
    from ..question_intake import azure_resolve
    if name!='azure':raise ValueError('Model provider is not installed: '+name)
    validate_provider_credential(credential)
    return azure_plan,azure_resolve
