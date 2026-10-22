"""Observed, timestamped node facts on the existing graph/shared-state authority.

Unavailable and successful negative observations are different records. Nothing
in this module promotes inferred descriptions to observed runtime evidence.
"""
import copy
from datetime import datetime, timedelta, timezone
import json
from .estate_graph_contract import timestamp
from .shared_state import encoded, sha, StateConflict

KINDS = frozenset({'JOB_RUN', 'REFRESH_RUN', 'REFRESH_STATE', 'SCHEDULE', 'TABLE_LOAD',
                   'OVERDUE', 'TYPICAL_DURATION', 'TABLE_PROFILE', 'COVERAGE'})
STATES = frozenset({'OBSERVED', 'OBSERVED_NEGATIVE', 'UNAVAILABLE'})
SOURCES = frozenset({'RUNTIME_OBSERVATION', 'DECLARED_CONFIG', 'DERIVED_OBSERVATIONS'})


def fact(value):
    required = {'subject', 'kind', 'value', 'observed_at', 'collected_at', 'source',
                'provenance', 'state', 'reason'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError('FACT_SHAPE')
    value = copy.deepcopy(value)
    if not isinstance(value['subject'], str) or not value['subject'] or value['kind'] not in KINDS:
        raise ValueError('FACT_SUBJECT_OR_KIND')
    if value['state'] not in STATES or value['source'] not in SOURCES:
        raise ValueError('FACT_STATE_OR_SOURCE_NOT_OBSERVED')
    for key in ('observed_at', 'collected_at'):
        value[key] = timestamp(value[key])
    if value['observed_at'] > value['collected_at']:
        raise ValueError('FACT_OBSERVED_AFTER_COLLECTION')
    proof = value['provenance']
    if not isinstance(proof, dict) or set(proof) != {'evidence_ids', 'collector', 'locator'}:
        raise ValueError('FACT_PROVENANCE')
    if not isinstance(proof['evidence_ids'], list) or not proof['evidence_ids'] or any(not isinstance(v, str) or not v for v in proof['evidence_ids']):
        raise ValueError('FACT_EVIDENCE_REQUIRED')
    if any(not isinstance(proof[k], str) or not proof[k] for k in ('collector', 'locator')):
        raise ValueError('FACT_PROVENANCE')
    if value['state'] == 'UNAVAILABLE':
        if value['value'] is not None or not isinstance(value['reason'], str) or not value['reason']:
            raise ValueError('FACT_UNAVAILABLE_REASON_REQUIRED')
    elif value['reason'] is not None or value['value'] is None:
        raise ValueError('FACT_OBSERVED_VALUE_REQUIRED')
    if value['state'] != 'UNAVAILABLE':
        payload=value['value']
        if not isinstance(payload,dict):raise ValueError('FACT_VALUE_OBJECT_REQUIRED')
        if value['kind'] in ('JOB_RUN','REFRESH_RUN'):
            if payload.get('status') not in ('SUCCEEDED','FAILED','RUNNING','QUEUED','CANCELLED','UNKNOWN') or not payload.get('run_id'):
                raise ValueError('FACT_RUN_STATUS_OR_ID')
            for field in ('start','end'):
                if payload.get(field) is not None:timestamp(payload[field])
            for field in ('rows_read','rows_written'):
                count=payload.get(field)
                if count is not None and (type(count) is not int or count<0):raise ValueError('FACT_EXACT_COUNT_REQUIRED')
        if value['kind']=='TABLE_PROFILE':
            if not payload.get('load_marker'):raise ValueError('FACT_PROFILE_LOAD_MARKER')
            if type(payload.get('row_count')) is not int or payload['row_count']<0 or not isinstance(payload.get('checksum'),str) or not payload['checksum'] or not payload.get('checksum_method'):
                raise ValueError('FACT_PROFILE_COUNTS_CHECKSUM_REQUIRED')
        if value['kind']=='OVERDUE' and type(payload.get('overdue')) is not bool:raise ValueError('FACT_OVERDUE_BOOLEAN')
        if value['kind']=='TYPICAL_DURATION' and (type(payload.get('sample_count')) is not int or payload['sample_count']<1 or type(payload.get('median_seconds')) not in (int,float) or payload['median_seconds']<0):
            raise ValueError('FACT_DURATION_SAMPLE_REQUIRED')
    if len(encoded(value).encode('utf8')) > 128000:
        raise ValueError('FACT_BYTE_BOUND')
    return value


class FactLedger:
    def __init__(self, state):
        self.state = state

    def append(self, estate, values):
        if not isinstance(values, list) or len(values) > 1000:
            raise ValueError('FACT_WRITE_BOUND')
        values = [fact(v) for v in values]
        with self.state.transaction() as db:
            for value in values:
                # Current graph nodes are replaced transactionally by the existing
                # scanner. Validate membership here; do not FK durable history to
                # a current projection that is legitimately deleted/reinserted.
                subject = self.state.sql(db, 'SELECT identity FROM estate_graph_nodes WHERE estate=? AND identity=?', (estate,value['subject'])).fetchone()
                if subject is None:raise ValueError('FACT_SUBJECT_NOT_IN_GRAPH')
                identity = sha(value)
                old = self.state.sql(db, 'SELECT body_hash FROM estate_node_facts WHERE estate=? AND identity=?', (estate, identity)).fetchone()
                if old:
                    if old[0] != identity: raise StateConflict('FACT_HASH_DIFFERS')
                    continue
                self.state.sql(db, 'INSERT INTO estate_node_facts VALUES(?,?,?,?,?,?,?,?)',
                    (estate, identity, value['subject'], value['kind'], value['observed_at'],
                     value['collected_at'], encoded(value), identity))
        return [sha(v) for v in values]

    def read(self, estate, subjects, *, as_of=None, now=None, max_age_seconds=3600):
        if not subjects or len(subjects) > 200 or len(set(subjects)) != len(subjects):
            raise ValueError('FACT_PATH_BOUND')
        if type(max_age_seconds) is not int or max_age_seconds < 0:
            raise ValueError('FACT_AGE_BOUND')
        cutoff = timestamp(as_of) if as_of else None
        current = timestamp(now) if now else cutoff
        where = 'estate=? AND subject IN (' + ','.join('?' for _ in subjects) + ')'
        args = [estate, *subjects]
        if cutoff:
            # Historical answers exclude observations not yet collected then.
            where += ' AND observed_at<=? AND collected_at<=?'
            args += [cutoff, cutoff]
        with self.state.transaction() as db:
            rows = self.state.sql(db, 'SELECT identity,body,body_hash FROM estate_node_facts WHERE ' + where + ' ORDER BY observed_at DESC,collected_at DESC,identity LIMIT 10001', args).fetchall()
        if len(rows) > 10000: raise ValueError('FACT_READ_BOUND')
        latest = {}
        for identity, raw, digest in rows:
            value = json.loads(raw)
            if sha(value) != digest or identity != digest: raise StateConflict('FACT_HASH_DIFFERS')
            key = (value['subject'], value['kind'])
            if key in latest: continue
            age = (datetime.fromisoformat(current.replace('Z', '+00:00')) - datetime.fromisoformat(value['collected_at'].replace('Z', '+00:00'))).total_seconds() if current else None
            latest[key] = {'id': identity, **value, 'freshness': 'STALE' if age is not None and age > max_age_seconds else 'CURRENT' if age is not None else 'AGE_NOT_EVALUATED'}
        return {'facts': list(latest.values()), 'missing_subjects': sorted(set(subjects) - {v['subject'] for v in latest.values()}), 'as_of': cutoff}

    def cursor(self, estate, collector, subject):
        with self.state.transaction() as db:
            row = self.state.sql(db, 'SELECT marker FROM estate_fact_cursors WHERE estate=? AND collector=? AND subject=?', (estate, collector, subject)).fetchone()
        return row[0] if row else None

    def advance(self, estate, collector, subject, marker, at):
        at = timestamp(at)
        with self.state.transaction() as db:
            self.state.sql(db, 'INSERT INTO estate_fact_cursors VALUES(?,?,?,?,?) ON CONFLICT(estate,collector,subject) DO UPDATE SET marker=excluded.marker,collected_at=excluded.collected_at', (estate, collector, subject, marker, at))

    def coverage(self, estate, nodes, expected, *, now):
        result = self.read(estate, list(nodes), now=now)
        found = {(v['subject'], v['kind']): v for v in result['facts']}
        return [{'subject': node, 'node_kind': node_kind, 'fact_kind': kind,
                 'status': found[(node, kind)]['state'] if (node, kind) in found else 'MISSING',
                 'freshness': found[(node, kind)]['freshness'] if (node, kind) in found else None,
                 'reason': found[(node, kind)]['reason'] if (node, kind) in found else 'No retained observation.'}
                for node, node_kind in sorted(nodes.items()) for kind in expected.get(node_kind, ())]
