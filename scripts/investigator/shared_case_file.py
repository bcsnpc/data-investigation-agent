"""Production case-file sections written with the source-row transaction.

Sections retain source rows and hashes. They do not infer a finding, promote
provenance, or merge a claim with another ticket's runtime by a guessed name.
"""
import json
from .shared_state import encoded, sha, StateConflict

SOURCE_KEYS = {'claim_intakes': 'id', 'claim_investigations': 'claim_id',
               'claim_execution_failures': 'claim_id', 'claim_handoffs': 'claim_id',
               'adaptive_sessions': 'id', 'adaptive_syntheses': 'session_id',
               'v2_runs': 'id', 'v2_steps': 'run_id', 'v2_run_events': 'run_id',
               'adaptive_events': 'session_id', 'agent_progress': 'ticket_id'}


def publish_changed(state, db, environment, tables):
    for table, payload in tables.items():
        identity_column = SOURCE_KEYS.get(table)
        if identity_column is None or payload is None:continue
        columns = payload['columns']
        if identity_column not in columns:raise StateConflict('CASE_SOURCE_IDENTITY_MISSING')
        groups = {}
        for row in payload['rows']:
            record = dict(zip(columns, row[1:])); identity = record[identity_column]
            if not isinstance(identity, str) or not identity:raise StateConflict('CASE_SOURCE_IDENTITY_MISSING')
            groups.setdefault(identity, []).append({'rowid': row[0], 'record': record})
        for identity, records in groups.items():
            kind = 'claim' if table.startswith('claim_') else 'runtime'
            key = encoded([environment, kind, identity])
            try:prior = state._get(db, 'case_file', key)
            except KeyError:prior = None
            body = prior['body'] if prior else {'version': 'shared-case-file-v1',
                'environment': environment, 'kind': kind, 'identity': identity, 'sections': {}}
            section = {'source_table': table, 'rows': records, 'sha256': sha(records)}
            if body['sections'].get(table) == section:continue
            body['sections'][table] = section
            # Explicit runtime relation, never an identity/name join.
            if table == 'claim_investigations':
                retained = json.loads(records[0]['record']['body'])
                body['runtime_ids'] = sorted({retained[k] for k in ('session_id', 'candidate_session_id')
                                              if isinstance(retained.get(k), str)})
            if prior is None:
                state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)', ('case_file', key, 0, encoded(body), sha(body)))
            else:state.sql(db, 'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                           (prior['revision']+1, encoded(body), sha(body), 'case_file', key))


def read(state, environment, kind, identity):
    if kind not in ('claim', 'runtime'):raise ValueError('CASE_KIND_REQUIRED')
    result = state.get('case_file', encoded([environment, kind, identity]))
    for section in result['body']['sections'].values():
        if sha(section['rows']) != section['sha256']:raise StateConflict('CASE_SECTION_HASH_DIFFERS')
    return result
