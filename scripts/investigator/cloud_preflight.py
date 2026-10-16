"""Client prerequisite inventory: declarations never establish permission.

Offline is the default. Optional probe callbacks are installation-owned code,
not model tools; each successful observation names the identity and its receipt.
An unavailable observation is MISSING, never a positive capability finding.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class Observation:
    identity: str
    evidence_id: str
    established: bool
    detail: str


def result(manifest,*,platform=None,probes=None,manifest_validator=None,gateway_validator=None):
    platform=platform or {};probes=probes or {};checks=[]
    def add(identity,status,detail,fix,*,required=True,evidence=None):
        checks.append({'id':identity,'status':status,'detail':detail,'fix':fix,'required':required,'evidence':evidence})
    def observe(identity,principal,detail,fix,*,required=True,identity_valid=True):
        if not identity_valid:
            add(identity,'FAIL','Declared reader identities disagree; no probe is admitted.',fix,required=required)
            return
        probe=probes.get(identity)
        if probe is None:
            add(identity,'MISSING',detail+' No probe evidence was supplied.',fix,required=required)
            return
        try:
            observation=probe()
            if (not isinstance(observation,Observation) or type(observation.established)is not bool
                    or observation.identity!=principal or not observation.evidence_id):
                raise ValueError('PROBE_IDENTITY_OR_RECEIPT_MISSING')
            add(identity,'PASS' if observation.established else 'FAIL',observation.detail,fix,
                required=required,evidence={'identity':observation.identity,'id':observation.evidence_id})
        except Exception as exc:
            # Connector errors can include tokens/connection strings. Preserve
            # exact transport errors in the governed receipt, not this summary.
            add(identity,'FAIL','Probe failed: '+type(exc).__name__+'. Inspect the governed receipt.',fix,required=required)
    if manifest_validator is None:
        from .estate_manifest import validate
        manifest_validator=validate
    try:
        manifest_validator(manifest)
    except Exception as exc:
        add('manifest','FAIL','Manifest validation failed: '+type(exc).__name__,
            'Validate the complete estate manifest with the installed adapter before deployment.')
        return {'status':'NOT_READY','checks':checks,'estate_reads':0,'model_calls':0}
    add('manifest','PASS','Complete manifest passed the installed schema. This is configuration evidence only.',
        'No action required for this configuration check.')
    worker=platform.get('worker_identity',{})
    principal=worker.get('principal_id','UNCONFIGURED')
    identity_ready=worker.get('mode')=='managed_identity' and all(worker.get(k) for k in ('client_id','tenant_id','principal_id'))
    add('worker_identity.configuration','PASS' if identity_ready else 'MISSING',
        'An explicit managed identity is declared.' if identity_ready else 'Cloud worker managed identity is not fully declared.',
        'Set worker_identity mode, client_id, tenant_id and principal_id from the deployed identity; never select a developer credential fallback.')
    observe('worker_identity.authentication',principal,'A declaration does not prove token issuance or identity binding.',
            'Run an identity-bound token probe from the worker; retain audience, tenant and principal binding without retaining the token.')
    policy=platform.get('gateway_policy')
    if not isinstance(policy,dict):
        add('gateway','MISSING','No exact endpoint/object gateway policy is present.',
            'Supply the deployment-owned policy and DIA_GATEWAY_POLICY; enumerate exact methods, URLs, SQL objects and platform database.')
    else:
        try:
            if gateway_validator is None:
                from .live_gateway import Gateway
                gateway_validator=Gateway
            gateway_validator(policy)
            if policy.get('live_enabled')is not True:
                add('gateway','FAIL','The live-access kill switch is set.',
                    'An operator must deliberately enable live access after prerequisites are earned.')
            else:
                add('gateway','PASS','Exact allowlist policy validates. Actual access is checked separately.',
                    'Keep the kill switch available; do not add wildcards or mutation endpoints.')
        except Exception as exc:
            add('gateway','FAIL','Gateway policy refused: '+type(exc).__name__,
                'Install the gateway dependencies and correct the explicit policy; never bypass the gateway.')
    storage=platform.get('postgres',{})
    add('postgres.configuration','PASS' if all(storage.get(k)for k in ('host','database','user'))else'MISSING',
        'PostgreSQL endpoint declaration only; SQLite cannot be the parallel live authority.',
        'Set INVESTIGATOR_STATE_BACKEND=postgresql and INVESTIGATOR_PG_HOST, INVESTIGATOR_PG_DATABASE and INVESTIGATOR_PG_USER.')
    observe('postgres.schema_and_migration',principal,'Shared-state schema and exact migration have not been observed.',
        'Apply versioned migrations, import drained ledgers with hash checks, compare totals/reserve, then run --check-shared-state through the platform gateway.')
    for check,why,fix in [
        ('blob','Content-addressed snapshots, captures and tapes need private Blob access.',
         'Grant the worker Storage Blob Data Contributor on the one tool storage account; verify exact private-container operations through the platform gateway.'),
        ('key_vault','Secret references require scoped Key Vault access; reference validity does not prove access.',
         'Grant Key Vault Secrets User on the one vault; probe a configured versioned reference as the worker without returning or recording the value.'),
        ('model_deployment','A model endpoint in the manifest does not prove deployment availability or caller rights.',
         'Verify the named model deployment, identity and supported request limits through the gateway; a metadata check does not establish successful generation.'),
        ('network','Endpoint names do not establish worker outbound connectivity.',
         'Probe each configured endpoint from the deployed worker; allow only required hosts and ports.')]:
        observe(check+'.access',principal,why,fix)
    ids={row['id']:row for row in manifest['identities']}
    for layer in manifest['layers']:
        layer_id=layer['id'];reader=ids[layer['reach']['reader']]['principal']
        if not layer['reachable']:
            add('layer.'+layer_id+'.read','MISSING','Layer explicitly declared unreachable.',
                'Keep the honest boundary limitation, or obtain a separately approved scoped reader grant.',required=False)
            continue
        observe('layer.'+layer_id+'.read',reader,'Read access and surface attestation are untested for this layer.',
                'Use the configured reader and a bounded attested diagnostic; for SQL retain SELECT permission and absence of write/DDL rights.')
        observe('layer.'+layer_id+'.definitions',reader,'Definition access is independent of value-query access.',
                'Probe the declared definition route; SQL may require object-scoped VIEW DEFINITION. Do not grant write to obtain notebook or pipeline definitions.')
    from .adapters.cloud_prerequisites import observe_platform
    observe_platform(manifest, platform, principal, observe)
    add('budgets.configuration','PASS','Manifest contains explicit diagnostic, daily model, rolling physical, round pot and restoration limits.',
        'Import the current usage exactly; match the sealed PostgreSQL policy. A new worker must not reset counters.')
    recording=manifest.get('recording',{'tape_class':'EXACT'})
    add('recording.configuration','FAIL' if recording['tape_class']=='PRIVACY_PROJECTED' else 'PASS',
        'Projected shared PostgreSQL state is not implemented; admission refuses.' if recording['tape_class']=='PRIVACY_PROJECTED' else 'Exact recording is declared. This does not assert an archive content audit has passed.',
        'Projected installations must remain offline until projection precedes shared-state persistence; never switch silently to EXACT.')
    ready=all(c['status']=='PASS' for c in checks if c['required'])
    return {'status':'READY'if ready else'NOT_READY','manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
            'checks':checks,'estate_reads':0,'model_calls':0,
            'limitation':'Prerequisite checks do not onboard a route or authorize an outcome. Missing optional evidence remains an explicit limit.'}


def shared_state_probe(platform,*,connector=None):
    """Only the tool's own DB; no estate query or model call is made."""
    from .shared_state import configured_state,DDL,USAGE_DDL
    state=connector or configured_state()
    if state is None:raise ValueError('POSTGRES_CONFIGURATION_REQUIRED')
    with state.transaction() as db:
        versions=db.execute('SELECT version,sha256 FROM state_schema_versions ORDER BY version').fetchall()
        migrations=db.execute('SELECT identity,source_hash,verification FROM state_migrations ORDER BY identity').fetchall()
        counts=db.execute("SELECT (SELECT count(*) FROM state_accounts), (SELECT count(*) FROM state_documents WHERE namespace='usage_policy'), (SELECT count(*) FROM state_documents WHERE namespace='catalog_index')").fetchone()
    detail={'versions':[list(r)for r in versions],'migrations':[list(r)for r in migrations]}
    identity=platform['worker_identity']['principal_id']
    fingerprint=hashlib.sha256(json.dumps(detail,sort_keys=True).encode()).hexdigest()
    expected=[(1,hashlib.sha256(DDL.format(number='NUMERIC'if state.backend=='postgresql'else'TEXT').encode()).hexdigest()),
              (2,hashlib.sha256(USAGE_DDL.encode()).hexdigest())]
    proofs=True
    for _,source_hash,raw in migrations:
        proof=json.loads(raw)
        proofs=proofs and proof.get('source_sha256')==source_hash
        if 'totals_before'in proof:proofs=proofs and proof['totals_before']==proof['totals_after']
        proofs=proofs and all(p.get('matched')is True for p in proof.get('tables',[])+proof.get('accounts',[]))
    passed=versions==expected and bool(migrations) and proofs and all(counts)
    return Observation(identity,'preflight-pg:'+fingerprint,passed,
                       'Observed schema versions '+str([v[0]for v in versions])+'; migration records '+str(len(migrations))+
                       '; dollar accounts / usage policies / catalog indexes '+str(list(counts))+
                       '. Schema hashes and retained migration comparisons '+('match.'if passed else'are incomplete or differ.'))
