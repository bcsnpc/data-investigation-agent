"""Build an investigation from one validated manifest; no configuration fallback."""
import copy
from pathlib import Path
from .estate_manifest import load, policy


def build(path, *, execution_enabled=True,secret_store=None):
    manifest=load(path)
    from .adapters.estate_installation import configuration,transports,provider
    config=configuration(manifest)
    from metadata_config import ROOT
    if manifest.get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':
        from .privacy_capture import Capture
        from .privacy_projection import Projection
        from .privacy_installation import Installation
        from .adapters.windows_privacy_secrets import resolver
        projection=Projection(manifest['recording'],secret_store or resolver(ROOT))
        capture=Capture(projection,[ROOT/manifest['storage']['catalog'],config['storage']['database']])
        try:
            with capture.active():workspace=_build_workspace(manifest,path,config,execution_enabled)
            workspace.store.privacy_capture=capture
            return manifest,Installation(workspace,capture,ROOT/'.local/privacy-process-tapes')
        except BaseException:
            capture.close();raise
    return manifest,_build_workspace(manifest,path,config,execution_enabled)


def _build_workspace(manifest,path,config,execution_enabled):
    from .adapters.estate_installation import transports,provider
    from .onboarding import ModelStore
    from .runtime import Runtime
    from .adaptive_runtime import AdaptiveRuntime
    from .workspace import Workspace
    from metadata_config import ROOT
    model=manifest['model'];budget=manifest['budgets']
    planner,resolver=provider(model['provider'],model['credential']) if execution_enabled else (None,None)
    store=ModelStore(ROOT/manifest['storage']['catalog'],config['storage']['database'],manifest['environment'])
    native,source=transports(config) if execution_enabled else (None,None)
    profile={'adapter':model['provider'],'deployment':model['deployment'],'endpoint':model['endpoint'],
        'process_max_boundaries':budget['max_boundaries'],'generation_options':model['generation_options'],
        'max_planner_recoveries':model['max_planner_recoveries']}
    lineage=None
    if any(b['may_infer_from_code'] for b in manifest['lineage'].get('code_locations',[])):
        from .adapters.code_lineage import Installation
        lineage=Installation(manifest,path,ROOT)
        if execution_enabled:lineage.approval()
    agent=AdaptiveRuntime(Runtime(store,config,native,source),planner,
        planner_profile=profile,usage_policy=policy(manifest),process_lineage=lineage)
    ownership=copy.deepcopy(manifest.get('ownership',{'business':[],'technical':[]}))
    addresses={layer['id']:layer['asset_id'] for layer in manifest['layers']}
    addresses.update({pipeline['id']:pipeline['producer_asset_id'] for pipeline in manifest['pipelines']})
    for row in ownership['technical']:row['layer_or_pipeline']=addresses[row['layer_or_pipeline']]
    workspace=Workspace(agent,execution_enabled=execution_enabled,
        question_resolver=resolver,
        intake_configuration=manifest.get('intake'),
        ownership_configuration=ownership,
        dynamic_read_limit=budget['diagnostic_reads_per_run'],dynamic_input_limit=budget['input_characters_per_run'])
    from .adapters.report_list_installation import install as install_report_lists
    workspace.report_lists=install_report_lists(workspace,config)
    if execution_enabled:
        from .adapters.form_candidate_values import install as install_form_candidates
        install_form_candidates(workspace)
    return workspace
