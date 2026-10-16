"""Estate-owned glossary: evidence-backed links, never model authority.

Storage uses the installation's existing privacy-aware catalog connection. The
mutation methods are server ports: evidence_lookup must read retained evidence,
not echo a client/model payload. Definition seeds are derived here from the
catalog; human confirmations must identify their retained clarification/steward
record and the exact relationship it supports.
"""
import copy
import json
import unicodedata
from contextlib import closing, contextmanager

from .onboarding import digest, Conflict
from .privacy_storage import connect
from .planner_recording import _safe

VERSION = 'estate-glossary-v1'
STATUSES = ('CONFIRMED', 'INFERRED')
KINDS = ('PHRASE', 'CONCEPT', 'REPORT_LABEL', 'MODEL_MEASURE', 'MODEL_COLUMN', 'SOURCE_COLUMN')
PROVENANCE = ('REPORT_DEFINITION', 'MODEL_DEFINITION', 'LINEAGE',
              'CONFIRMED_CLARIFICATION', 'STEWARD_ENTRY', 'MODEL_INFERRED')
HUMAN = {'CONFIRMED_CLARIFICATION': 'USER', 'STEWARD_ENTRY': 'STEWARD'}


def phrase_key(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 1000:
        raise ValueError('GLOSSARY_PHRASE_REQUIRED')
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def models(catalog):
    result = catalog.get('models') if isinstance(catalog, dict) else catalog
    if not isinstance(result, list):
        raise ValueError('GLOSSARY_CATALOG_REQUIRED')
    return result


def node(value, catalog):
    if not isinstance(value, dict) or value.get('kind') not in KINDS:
        raise ValueError('GLOSSARY_NODE_KIND')
    kind = value['kind']
    if kind in ('PHRASE', 'CONCEPT'):
        if set(value) != {'kind', 'label'}:
            raise ValueError('GLOSSARY_LANGUAGE_NODE_SHAPE')
        phrase_key(value['label'])
        # Retain the exact string so installation privacy projection can find
        # it. Case folding belongs to transient lookup, not durable evidence.
        return copy.deepcopy(value)
    if set(value) != {'kind', 'model_id', 'id'}:
        raise ValueError('GLOSSARY_CATALOG_NODE_SHAPE')
    found = [m for m in models(catalog) if m.get('id') == value['model_id']]
    if len(found) != 1:
        raise ValueError('GLOSSARY_UNKNOWN_MODEL')
    model = found[0]
    field, identity = {'REPORT_LABEL': ('visuals', 'target_id'),
                       'MODEL_MEASURE': ('measures', 'id'),
                       'MODEL_COLUMN': ('columns', 'column_id'),
                       'SOURCE_COLUMN': ('source_columns', 'column_id')}[kind]
    items = [x for x in model.get(field, []) if x.get(identity) == value['id']]
    if len(items) != 1:
        raise ValueError('GLOSSARY_UNKNOWN_REFERENCE')
    return copy.deepcopy(value)


def relationship(source, target):
    return digest({'source': source, 'target': target})


def _identity(value):
    return digest({**value, 'label': phrase_key(value['label'])}) if value['kind'] in ('PHRASE', 'CONCEPT') else digest(value)


def _catalog_item(value, catalog):
    if value['kind'] in ('PHRASE', 'CONCEPT'):
        return value
    model = next(m for m in models(catalog) if m['id'] == value['model_id'])
    field, identity = {'REPORT_LABEL': ('visuals', 'target_id'),
                       'MODEL_MEASURE': ('measures', 'id'),
                       'MODEL_COLUMN': ('columns', 'column_id'),
                       'SOURCE_COLUMN': ('source_columns', 'column_id')}[value['kind']]
    return next(x for x in model.get(field, []) if x.get(identity) == value['id'])


def _pins(source, target, catalog):
    pins = {}
    for value in (source, target):
        if value['kind'] in ('PHRASE', 'CONCEPT'):
            continue
        model = next(m for m in models(catalog) if m['id'] == value['model_id'])
        # The compact intake catalog may omit the actual DAX expression. A
        # model-context/revision change must still invalidate old authority.
        pins[digest(value)] = digest({'item': _catalog_item(value, catalog),
                                     'context_id': model.get('context_id'),
                                     'revision': model.get('revision')})
    return pins


def _proof(value, source, target):
    if not isinstance(value, dict) or value.get('kind') not in PROVENANCE:
        raise ValueError('GLOSSARY_PROVENANCE_REQUIRED')
    if not isinstance(value.get('id'), str) or not value['id'] or not isinstance(value.get('sha256'), str):
        raise ValueError('GLOSSARY_EVIDENCE_IDENTITY_REQUIRED')
    if len(value['sha256']) != 64 or any(c not in '0123456789abcdef' for c in value['sha256']):
        raise ValueError('GLOSSARY_EVIDENCE_HASH_REQUIRED')
    if relationship(source, target) not in value.get('supports', []):
        raise ValueError('GLOSSARY_EVIDENCE_DOES_NOT_SUPPORT_LINK')
    if value['kind'] in HUMAN:
        actor = value.get('actor', {})
        if actor.get('kind') != HUMAN[value['kind']] or not actor.get('id'):
            raise ValueError('GLOSSARY_HUMAN_AUTHORITY_REQUIRED')
    return copy.deepcopy(value)


class EstateGlossary:
    def __init__(self, database, estate_id, *, evidence_lookup=None, store=None):
        if not isinstance(estate_id, str) or not estate_id:
            raise ValueError('GLOSSARY_ESTATE_REQUIRED')
        self.database, self.estate_id, self.evidence_lookup = database, estate_id, evidence_lookup
        self.store=store

    @contextmanager
    def connection(self):
        if self.store is not None:
            with self.store.connect()as db:
                db.execute('CREATE TABLE IF NOT EXISTS claim_glossary_events '
                           '(estate_id TEXT NOT NULL, revision INTEGER NOT NULL, body TEXT NOT NULL, '
                           'PRIMARY KEY (estate_id, revision))')
                yield db
        else:
            with closing(self._db())as db:
                with db:yield db

    def _db(self):
        db = connect(self.database)
        db.execute('CREATE TABLE IF NOT EXISTS claim_glossary_events '
                   '(estate_id TEXT NOT NULL, revision INTEGER NOT NULL, body TEXT NOT NULL, '
                   'PRIMARY KEY (estate_id, revision))')
        db.commit()
        return db

    def _read(self, db):
        history = []
        previous = None
        for revision, body in db.execute('SELECT revision,body FROM claim_glossary_events '
                                         'WHERE estate_id=? ORDER BY revision', (self.estate_id,)):
            entry = json.loads(body)
            seal = entry.pop('sha256')
            if (revision != len(history) + 1 or entry.get('version') != VERSION or
                    entry.get('estate_id') != self.estate_id or entry.get('revision') != revision or
                    entry.get('previous') != previous or digest(entry) != seal):
                raise ValueError('GLOSSARY_HISTORY_INVALID')
            entry['sha256'] = seal
            history.append(entry)
            previous = seal
        return history

    def get(self):
        with self.connection() as db:
            history = self._read(db)
        links = {}
        for event in history:
            if event['event'] == 'LINK_ADDED':
                links[event['link']['id']] = copy.deepcopy(event['link'])
            elif event['event'] == 'LINK_CONFIRMED':
                link = links[event['link_id']]
                link['status'] = 'CONFIRMED'
                link.setdefault('confirmations', []).append(copy.deepcopy(event['proof']))
            else:
                raise ValueError('GLOSSARY_EVENT_UNSUPPORTED')
        return {'version': VERSION, 'estate_id': self.estate_id, 'revision': len(history),
                'links': list(links.values()), 'history': history}

    def _append(self, event, expected_revision):
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool):
            raise ValueError('GLOSSARY_EXPECTED_REVISION_REQUIRED')
        with self.connection() as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                history = self._read(db)
                if len(history) != expected_revision:
                    raise Conflict('Glossary changed; reload before editing')
                value = {'version': VERSION, 'estate_id': self.estate_id, 'revision': len(history) + 1,
                         'previous': history[-1]['sha256'] if history else None, **event}
                value['sha256'] = digest(value)
                encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
                _safe(encoded.encode('utf8'))
                db.execute('INSERT INTO claim_glossary_events VALUES (?,?,?)',
                           (self.estate_id, value['revision'], encoded))
                db.commit()
            except BaseException:
                db.rollback()
                raise
        return value

    def _evidence(self, evidence_id, source, target):
        if not isinstance(evidence_id, str) or evidence_id.startswith('catalog:'):
            raise ValueError('GLOSSARY_EVIDENCE_NAMESPACE_RESERVED')
        if self.evidence_lookup is None:
            raise ValueError('GLOSSARY_RETAINED_EVIDENCE_LOOKUP_REQUIRED')
        value = self.evidence_lookup(evidence_id)
        if not isinstance(value, dict) or value.get('id') != evidence_id:
            raise ValueError('GLOSSARY_UNKNOWN_EVIDENCE')
        return _proof(value, source, target)

    def add_link(self, source, target, *, evidence_id, catalog, expected_revision):
        source, target = node(source, catalog), node(target, catalog)
        if source == target:
            raise ValueError('GLOSSARY_SELF_LINK')
        proof = self._evidence(evidence_id, source, target)
        return self._add(source, target, proof, catalog, expected_revision)

    def _add(self, source, target, proof, catalog, expected_revision):
        status = 'INFERRED' if proof['kind'] == 'MODEL_INFERRED' else 'CONFIRMED'
        pins = _pins(source, target, catalog)
        link = {'id': digest({'source': source, 'target': target, 'evidence': proof, 'pins': pins}),
                'source': source, 'target': target, 'status': status, 'proof': proof,
                'catalog_pins': pins}
        if any(x['id'] == link['id'] for x in self.get()['links']):
            raise Conflict('Glossary link already recorded')
        self._append({'event': 'LINK_ADDED', 'link': link}, expected_revision)
        return copy.deepcopy(link)

    def confirm(self, link_id, *, evidence_id, catalog, expected_revision):
        links = [x for x in self.get()['links'] if x['id'] == link_id]
        if len(links) != 1:
            raise ValueError('GLOSSARY_UNKNOWN_LINK')
        link = links[0]
        source, target = node(link['source'], catalog), node(link['target'], catalog)
        if _pins(source, target, catalog) != link['catalog_pins']:
            raise ValueError('GLOSSARY_STALE_REFERENCE')
        proof = self._evidence(evidence_id, source, target)
        if proof['kind'] not in HUMAN:
            raise ValueError('GLOSSARY_INFERENCE_NEEDS_HUMAN_CONFIRMATION')
        self._append({'event': 'LINK_CONFIRMED', 'link_id': link_id, 'proof': proof}, expected_revision)
        return self.get()

    def seed_catalog(self, catalog):
        """Only exact declared labels; no semantic synonym is inferred here."""
        added = []
        for model in models(catalog):
            pairs = []
            for measure in model.get('measures', []):
                if measure.get('name'):
                    pairs.append(({'kind': 'PHRASE', 'label': measure['name']},
                                  {'kind': 'MODEL_MEASURE', 'model_id': model['id'], 'id': measure['id']},
                                  'MODEL_DEFINITION', measure))
            for visual in model.get('visuals', []):
                ref = {'kind': 'REPORT_LABEL', 'model_id': model['id'], 'id': visual['target_id']}
                for label in visual.get('names', []):
                    pairs.append(({'kind': 'PHRASE', 'label': label}, ref, 'REPORT_DEFINITION', visual))
                for measure_id in visual.get('measure_ids', []):
                    pairs.append((ref, {'kind': 'MODEL_MEASURE', 'model_id': model['id'], 'id': measure_id},
                                  'REPORT_DEFINITION', visual))
            for source, target, kind, retained in pairs:
                source, target = node(source, catalog), node(target, catalog)
                proof = {'id': 'catalog:' + digest(retained), 'kind': kind, 'sha256': digest(retained),
                         'supports': [relationship(source, target)]}
                candidate_id = digest({'source': source, 'target': target, 'evidence': proof,
                                       'pins': _pins(source, target, catalog)})
                current = self.get()
                if any(x['id'] == candidate_id for x in current['links']):
                    continue
                added.append(self._add(source, target, proof, catalog, current['revision']))
        return added

    def resolve(self, phrase, catalog):
        phrase_key(phrase)
        start = {'kind': 'PHRASE', 'label': phrase}
        links = []
        for link in self.get()['links']:
            try:
                source, target = node(link['source'], catalog), node(link['target'], catalog)
                if _pins(source, target, catalog) != link['catalog_pins']:
                    continue
                if not link['proof']['id'].startswith('catalog:'):
                    current = self._evidence(link['proof']['id'], source, target)
                    if current != link['proof']:
                        continue
                if link.get('confirmations'):
                    if any(self._evidence(p['id'], source, target) != p for p in link['confirmations']):
                        continue
                links.append(link)
            except (ValueError, KeyError):
                continue
        # The graph is directional and many-to-many. Never choose one path just
        # because it was recorded first; cycles cannot make traversal unbounded.
        pending = [(start, [], {_identity(start)})]
        candidates = {}
        while pending:
            current, path, seen = pending.pop()
            if current['kind'] == 'MODEL_MEASURE':
                measure = _catalog_item(current, catalog)
                label = measure.get('name')
                if not isinstance(label, str) or not label.strip() or label == current['id']:
                    continue
                candidate = {'model_id': current['model_id'], 'measure_id': current['id'], 'label': label,
                             'status': 'CONFIRMED' if all(p['status'] == 'CONFIRMED' for p in path) else 'INFERRED',
                             'evidence_ids': sorted({p['proof']['id'] for p in path} |
                                                    {c['id'] for p in path for c in p.get('confirmations', [])}),
                             'link_ids': [p['id'] for p in path]}
                visual_nodes = [p['target'] for p in path if p['target']['kind'] == 'REPORT_LABEL']
                if visual_nodes:
                    visual = _catalog_item(visual_nodes[-1], catalog)
                    candidate['target_ids'] = [visual_nodes[-1]['id']]
                    for field in ('report_id', 'page_id'):
                        if visual.get(field):
                            candidate[field] = visual[field]
                key = (candidate['model_id'], candidate['measure_id'], tuple(candidate.get('target_ids', [])))
                old = candidates.get(key)
                if old is None or (old['status'] == 'INFERRED' and candidate['status'] == 'CONFIRMED'):
                    candidates[key] = candidate
                continue
            for link in links:
                if _identity(link['source']) != _identity(current) or _identity(link['target']) in seen:
                    continue
                pending.append((link['target'], path + [link], seen | {_identity(link['target'])}))
        return sorted(candidates.values(), key=lambda x: (x['label'], x['model_id'], x['measure_id'], x.get('target_ids', [])))

    resolve_phrase = resolve
