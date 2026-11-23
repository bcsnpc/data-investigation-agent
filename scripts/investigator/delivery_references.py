"""Reformat exact saved reference roles; never select a target or add support."""
from copy import deepcopy


def reformat(value, *, queries, evidence, layers, nodes=()):
    result = deepcopy(value)
    by_id = {query['id']: query for query in queries}
    known = set(by_id) | set(evidence)
    changes = []
    node_assets={node['id']:(node.get('properties') or {}).get('asset_id') for node in nodes}

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
        cited_ids={original(identity) for identity in result.get('evidence_ids',[]) if isinstance(identity,str)}
        cited_queries=set(cited_ids)&set(by_id)
        for identity in cited_ids:
            record=evidence.get(identity,{})
            if record.get('tool') in ('run_sql','run_dax'):
                native=record.get('result',{});native=native.get('record',native)
                if native.get('id') in by_id:cited_queries.add(native['id'])
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
                elif node_assets.get(identity):
                    matched={by_id[key]['layer'] for key in cited_queries
                             if by_id[key].get('status')=='SUCCEEDED'
                             and node_assets[identity] in by_id[key].get('asset_ids',[])}
                    if len(matched)==1 and next(iter(matched)) in layers:
                        target=next(iter(matched))
                        changes.append({'field':'checked','before':identity,'after':target})
                    elif not matched:
                        # A cited job/definition read belongs in evidence_ids,
                        # not in the enum of measured query layers. Remove the
                        # redundant wrong-role address only with native support.
                        observed=False
                        for key in cited_ids:
                            item=evidence.get(key,{})
                            if item.get('arguments',{}).get('node')!=identity:continue
                            native=item.get('result',{})
                            if item.get('tool') in ('get_job_runs','get_refresh_history','get_security_definitions'):
                                observed=native.get('status')=='OBSERVED' and bool(native.get('source') and native.get('observed_at'))
                            elif item.get('tool')=='get_definition':
                                observed=bool(native.get('content') and native.get('provenance'))
                            if observed:break
                        if observed:
                            changes.append({'field':'checked','before':identity,'after':None,'reason':'ALREADY_CITED_NATIVE_OBJECT_NOT_QUERY_LAYER'})
                            continue
            if target not in checked:
                checked.append(target)
        result['checked'] = checked
    return result, changes
