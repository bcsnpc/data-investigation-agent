"""Reformat exact saved reference roles; never select a target or add support."""
from copy import deepcopy


def reformat(value, *, queries, evidence, layers):
    result = deepcopy(value)
    by_id = {query['id']: query for query in queries}
    known = set(by_id) | set(evidence)
    changes = []

    def original(identity):
        seen = set()
        while isinstance(identity, str) and identity not in seen:
            seen.add(identity)
            record = evidence.get(identity, {})
            if record.get('tool') != 'get_evidence':
                return identity
            target = record.get('arguments', {}).get('id')
            if not isinstance(target, str) or target not in known:
                return identity
            identity = target
        # A malformed/cyclic wrapper must still reach ordinary validation.
        return None

    if isinstance(result.get('evidence_ids'), list):
        for index, identity in enumerate(result['evidence_ids']):
            if not isinstance(identity, str):
                continue
            target = original(identity)
            if target is not None and target != identity:
                result['evidence_ids'][index] = target
                changes.append({'field': 'evidence_ids', 'before': identity, 'after': target})
    if isinstance(result.get('checked'), list):
        checked = []
        for identity in result['checked']:
            target = identity
            if isinstance(identity, str) and identity not in layers:
                reference = original(identity)
                query = by_id.get(reference)
                record = evidence.get(reference, {})
                if query is None and record.get('tool') in ('run_sql', 'run_dax'):
                    native = record.get('result', {})
                    native = native.get('record', native)
                    query = by_id.get(native.get('id'))
                if query is not None and query.get('layer') in layers:
                    target = query['layer']
                    changes.append({'field': 'checked', 'before': identity, 'after': target})
            if target not in checked:
                checked.append(target)
        result['checked'] = checked
    return result, changes
