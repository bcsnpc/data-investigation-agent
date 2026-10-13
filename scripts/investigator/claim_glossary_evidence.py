"""Build glossary authority only from a retained, accepted claim interpretation."""
import json
from contextlib import closing

from .onboarding import digest
from .privacy_storage import connect
from .claim_glossary import node, relationship, _pins

PREFIX = 'claim-confirmation/'


def _accepted(store, identity, catalog):
    with store.connect() as db:
        row = db.execute('SELECT revision,body,body_hash FROM claim_intakes WHERE id=?', (identity,)).fetchone()
    if row is None:
        return None
    body = json.loads(row[1])
    if digest(body) != row[2] or body.get('id') != identity or body.get('revision') != row[0]:
        raise ValueError('GLOSSARY_CLAIM_INTEGRITY')
    if body.get('status') != 'CONFIRMED':
        return None
    confirmation = body.get('confirmation') or {}
    if (confirmation.get('authority') != 'USER_CONFIRMED' or
            confirmation.get('actor', {}).get('kind') != 'USER' or
            not confirmation.get('actor', {}).get('id') or
            confirmation.get('catalog_hash') != digest(catalog) or
            body.get('catalog_hash') != digest(catalog)):
        return None
    # The accepted boolean must exist in the original retained request, not
    # merely in a model/candidate status or a copied request hash.
    requests = [d['request'] for d in body.get('documents', [])
                if d.get('hash') == confirmation.get('request_hash') and
                isinstance(d.get('request'), dict) and digest(d['request']) == d['hash']]
    if len(requests) != 1:
        return None
    request = requests[0]
    if (request.get('accepted') is not True or request.get('id') != identity or
            request.get('revision') != body['revision'] - 1 or
            not any(h.get('kind') == 'CONFIRMATION' and h.get('accepted') is True and
                    h.get('request_hash') == digest(request) for h in body.get('history', []))):
        return None
    from .claim_facts import settled
    actual, conflicts = settled(body['claim']['facts'])
    from . import claim_clarification as policy
    scope=policy.merge_location_scope(actual)
    scope=policy.candidate_location(scope,catalog,policy.candidates(actual,catalog))
    if scope:actual['scope']=scope
    if conflicts or actual != body['claim'].get('settled'):
        return None
    from .claim_clarification import interpretation
    rendered = interpretation(body['claim'], catalog)
    if (rendered != body.get('interpretation') or
            digest(rendered) != confirmation.get('interpretation_hash') or
            rendered['fact_ids'] != confirmation.get('fact_ids')):
        return None
    return body


def confirmed_relationships(store, identity, catalog):
    body = _accepted(store, identity, catalog)
    if body is None:
        return []
    metrics = body['claim']['settled'].get('metric') or []
    binding = body['claim'].get('selected_binding') or {}
    # One selected metric cannot establish synonyms for several distinct asks.
    # Such claims remain usable, but require individual stewardship for links.
    if len(metrics) != 1 or not binding.get('model_id') or not binding.get('measure_id'):
        return []
    source = node({'kind': 'PHRASE', 'label': metrics[0]['phrase']}, catalog)
    target = node({'kind': 'MODEL_MEASURE', 'model_id': binding['model_id'],
                   'id': binding['measure_id']}, catalog)
    model = next(m for m in catalog['models'] if m['id'] == target['model_id'])
    measure = next(m for m in model['measures'] if m['id'] == target['id'])
    if binding.get('label') != measure.get('name'):
        return []
    pair = relationship(source, target)
    evidence_id = PREFIX + identity + '/' + str(body['revision']) + '/' + pair
    proof = {'id': evidence_id, 'kind': 'CONFIRMED_CLARIFICATION', 'sha256': digest(body),
             'actor': body['confirmation']['actor'], 'supports': [pair]}
    return [{'source': source, 'target': target, 'proof': proof}]


class RetainedClaimEvidence:
    def __init__(self, store, catalog_provider, *, fallback=None):
        self.store, self.catalog_provider, self.fallback = store, catalog_provider, fallback

    def __call__(self, identity):
        if not isinstance(identity, str) or not identity.startswith(PREFIX):
            return self.fallback(identity) if self.fallback else None
        parts = identity[len(PREFIX):].split('/')
        if len(parts) != 3 or not parts[1].isdigit():
            return None
        for item in confirmed_relationships(self.store, parts[0], self.catalog_provider()):
            if item['proof']['id'] == identity:
                return item['proof']
        return None


def record_confirmation(glossary, store, identity, catalog):
    """Call after the controller has committed the user's accepted request."""
    recorded = []
    for item in confirmed_relationships(store, identity, catalog):
        source, target, proof = item['source'], item['target'], item['proof']
        current = glossary.get()
        matching = [x for x in current['links'] if x['source'] == source and x['target'] == target]
        if any(x['proof']['id'] == proof['id'] or
               any(p['id'] == proof['id'] for p in x.get('confirmations', [])) for x in matching):
            continue
        inferred = [x for x in matching if x['status'] == 'INFERRED' and
                    x['catalog_pins'] == _pins(source, target, catalog)]
        if inferred:
            glossary.confirm(inferred[-1]['id'], evidence_id=proof['id'], catalog=catalog,
                             expected_revision=current['revision'])
            recorded.append({'event': 'LINK_CONFIRMED', 'link_id': inferred[-1]['id'], 'evidence_id': proof['id']})
        else:
            link = glossary.add_link(source, target, evidence_id=proof['id'], catalog=catalog,
                                     expected_revision=current['revision'])
            recorded.append({'event': 'LINK_ADDED', 'link_id': link['id'], 'evidence_id': proof['id']})
    return recorded
