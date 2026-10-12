"""Install local-only candidate quantities; no native reader fallback."""
from ..onboarding import encoded, digest
from ..process_tape import uuid4
from ..process_debugging import attest
from ..form_candidates import NotMeasurable
from ..declared_reproduction import compose
from .local_process import create

def recorder(store):
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS local_export_evidence(id TEXT PRIMARY KEY,body TEXT NOT NULL,hash TEXT NOT NULL)')
    def save(body):
        identity = 'local-export:' + str(uuid4())
        with store.connect() as db:
            db.execute('INSERT INTO local_export_evidence VALUES(?,?,?)', (identity, encoded(body), digest(body)))
        return identity
    return save

def install(workspace):
    save = recorder(workspace.store)
    def reader(candidate):
        from ..candidate_read_budget import consume
        consume(workspace)
        model = workspace.store.get(candidate['model_id'])
        adapter = create(workspace.store, workspace.agent.config, model, record_evidence=save)
        from .form_candidate_values import plan
        compiled = plan(model, candidate)
        restrictions = compose(candidate['declaration']['restrictions'] + [
            {'field_id': f['column_id'], 'operator': 'IN', 'values': f['values']} for f in candidate['scope']['filters']])
        semantic, _, _ = adapter._semantic(candidate['measure_id'])
        probe = attest(adapter._presentation({'id': semantic, 'kind': 'presentation'},
            candidate['measure_id'], restrictions, compiled['read_address']))
        if probe.status != 'OBSERVED': raise NotMeasurable(probe.reason or 'Local candidate not observed')
        return {'status': 'OBSERVED', 'complete': True, 'value': probe.value['quantity'],
            'receipt_id': probe.evidence['id'], 'query_hash': digest(compiled),
            'execution_surface': probe.execution_surface, 'attestation': probe.evidence['surface_attestation'],
            'execution_mode': 'LOCAL_EXPORTED', 'snapshot_alignment': 'SNAPSHOT_UNVERIFIED'}
    workspace.form_candidate_reader = reader
