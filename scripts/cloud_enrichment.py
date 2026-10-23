"""Typed enrichment-only batch submit/resume through the existing cloud worker."""
import json
import re
from pathlib import Path

from cloud_investigator import reference


def validate_options(options):
    if not isinstance(options,dict):raise ValueError('ENRICHMENT_RUNNER_OPTIONS')
    operation=options.get('operation')
    expected={'operation','config','batch_key'}|({'tasks'} if operation=='submit' else set())
    if operation not in ('submit','resume') or set(options)!=expected:raise ValueError('ENRICHMENT_RUNNER_OPTIONS')
    if not isinstance(options['batch_key'],str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,160}',options['batch_key']):raise ValueError('ENRICHMENT_BATCH_KEY')
    config=json.loads(reference(options['config'],maximum=64000).read_bytes())
    if not isinstance(config,dict) or set(config)!={'secret_reference','gateway_identity','worker_identity'}:raise ValueError('ENRICHMENT_RUNNER_CONFIG')
    from investigator.adapters.managed_identity import validate_secret_reference
    validate_secret_reference(config['secret_reference'])
    for key in ('gateway_identity','worker_identity'):
        if not isinstance(config[key],str) or not config[key]:raise ValueError('ENRICHMENT_RUNNER_IDENTITY')
    sources=None
    if operation=='submit':
        from investigator.enrichment import task
        sources=json.loads(reference(options['tasks'],maximum=4*1024*1024).read_bytes())
        if not isinstance(sources,list) or not 1<=len(sources)<=50:raise ValueError('ENRICHMENT_BATCH_BOUND')
        sources=[task(source) for source in sources]
    return operation,config,sources


def execute(plan,context):
    operation,config,sources=validate_options(plan['options']);batch_key=plan['options']['batch_key']
    from enrich_estate import live_job
    from investigator.shared_state import configured_state
    from investigator.enrichment_job import ACCOUNT
    from investigator import process_tape as journal
    from investigator.runtime import fingerprint
    from investigator.source_revision import committed_revision
    from investigator.slim_recording import stores,validate,CONFIG_ENV
    from investigator.planner_recording import _safe
    import os
    state=configured_state()
    if state is None or state.backend!='postgresql':raise ValueError('ENRICHMENT_CLOUD_SHARED_POSTGRES_REQUIRED')
    root=Path(context.root);root.mkdir(parents=True,exist_ok=True)
    tape=journal.Tape(root/'enrichment-tape.json',bootstrap={'entry_point':'enrichment_batch',
        'context_identity':batch_key,'config':{'_estate':{'operating_mode':'BUILD_PHASE'},'enrichment':config},
        'profile':{},'usage_policy':None,'engine_hash':fingerprint(),
        'state':{'engine_revision':committed_revision(),'operation':operation,'batch_key':batch_key,
                 'tasks':sources,'account':ACCOUNT}})
    def record(kind,body):
        from investigator.shared_state import encoded
        _safe(encoded(body).encode())
        # API request/response bodies only. Key Vault values and HTTP headers
        # are never passed to this callback by the installed BatchClient.
        context.record('enrichment-provider',{'kind':kind,'body':body})
    try:
        with journal.active(tape):
            job=live_job(config,record=record);before=job.budget.snapshot()
            result=job.submit(sources,batch_key=batch_key) if operation=='submit' else job.resume(batch_key)
            output={'operation':operation,'batch_key':batch_key,'result':result,
                    'enrichment_budget_before':before,'enrichment_budget_after':job.budget.snapshot(),
                    'investigator_model_calls':0,'estate_reads':0,'account':ACCOUNT}
            context.record('enrichment-result',output);tape.finish(output)
            return output
    finally:
        # A failed submission retains its incomplete tape and original durable
        # batch/reservation state; the runner records the failure, never retries
        # it under a replacement batch key silently.
        _,files=stores(validate(json.loads(Path(os.environ[CONFIG_ENV]).read_bytes())))
        artifacts={name:files.capture(path) for name,path in [('tape',tape.path),('events',tape.journal_path)] if path.exists()}
        context.record('enrichment-tape',{'batch_key':batch_key,'operation':operation,'artifacts':artifacts,
                       'complete':tape.finished,'account':ACCOUNT,'credential_or_scope_change':False})
