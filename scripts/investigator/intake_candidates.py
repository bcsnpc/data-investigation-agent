"""Bounded target alternatives, preserving explicit choices and retained scope.

This enumerates catalog addresses only. It never builds a query, guesses a
binding or chooses a target because of a similar name or value elsewhere.
"""
from copy import deepcopy


def enumerate_targets(catalog, *, text, proposal, explicit=None, limit=5):
    if type(limit) is not int or not 1 <= limit <= 5:
        raise ValueError('TARGET_CANDIDATE_LIMIT')
    explicit = deepcopy(explicit or {})
    for field, kind in (('report', 'REPORT'), ('page', 'PAGE'), ('visual', 'VISUAL'),
                        ('measure', 'MEASURE'), ('table', 'TABLE')):
        if field not in explicit:
            continue
        node = catalog.nodes.get(explicit[field], {})
        if node.get('kind') not in (('TABLE', 'VIEW') if field == 'table' else (kind,)):
            raise ValueError('EXPLICIT_TARGET_NOT_IN_CATALOG:' + field)
    # A caller may not smuggle a model-proposed target into the explicit set.
    # The caller supplies only form choices or verbatim-validated named choices.
    base = {k: deepcopy(v) for k, v in proposal.items()
            if k not in ('report', 'page', 'visual', 'measure', 'table', 'status')}
    rows = []
    if 'table' in explicit or 'measure' in explicit and 'report' not in explicit:
        field = 'table' if 'table' in explicit else 'measure'
        rows = [{**base, field: explicit[field]}]
    else:
        reports = ([{'id': explicit['report']}] if explicit.get('report')
                   else catalog.report_matches(text))
        for report in reports:
            report_id = report['id']
            pages = catalog.pages(report_id)
            if explicit.get('page'):
                if explicit['page'] not in {p['id'] for p in pages}:
                    raise ValueError('EXPLICIT_PAGE_OUTSIDE_REPORT')
                pages = [p for p in pages if p['id'] == explicit['page']]
            else:
                named = catalog.named_pages(text, report_id)
                if named:
                    pages = [p for p in pages if p['id'] in {n['id'] for n in named}]
            visuals = [(page, visual) for page in pages
                       for visual in catalog.visuals(report_id, page['id'])]
            if explicit.get('visual'):
                visuals = [(p, v) for p, v in visuals if v['id'] == explicit['visual']]
                if not visuals:
                    raise ValueError('EXPLICIT_VISUAL_OUTSIDE_SELECTED_SCOPE')
            elif explicit.get('measure'):
                visuals = [(p, v) for p, v in visuals
                           if explicit['measure'] in {m['id'] for m in v.get('measures', [])}]
            else:
                ranked = catalog.ranked(text, 'VISUAL', within={v['id'] for _, v in visuals})
                named = {r['id'] for r in ranked if r['confidence'] in ('NAMED', 'NORMALIZED')}
                if named:
                    visuals = [(p, v) for p, v in visuals if v['id'] in named]
            rows.extend({**base, 'report': report_id, 'page': p['id'], 'visual': v['id']}
                        for p, v in visuals)
        if not reports:
            for field, matches in (('table', catalog.table_matches(text)),
                                   ('measure', catalog.measure_matches(text))):
                rows.extend({**base, field: row['id']} for row in matches)
    unique = {}
    for request in rows:
        key = next(request[field] for field in ('visual', 'table', 'measure', 'page', 'report') if request.get(field))
        unique.setdefault(key, request)
    result = []
    for identity, request in list(unique.items())[:limit]:
        node = catalog.nodes[identity]
        result.append({'id': identity, 'name': node['label'], 'intake': request,
                       'retained_scope': deepcopy(node),
                       'scope_nodes': [deepcopy(catalog.nodes[request[f]]) for f in ('report', 'page', 'visual') if request.get(f)],
                       'explicit': deepcopy(explicit)})
    return {'candidates': result, 'total_candidates': len(unique),
            'exhaustive': len(unique) <= limit,
            'qualification': 'Retained catalog scope, including filters, is preserved. Interactive state is not inferred.'}


def select_unique(inventory, observations, figure):
    """A failed/unread candidate or truncated inventory cannot confer uniqueness."""
    from .investigation_read_tools import compare_figure
    expected = {r['id'] for r in inventory['candidates']}
    by_id = {}
    for observation in observations:
        identity = observation['candidate']
        if identity not in expected or identity in by_id:
            raise ValueError('TARGET_OBSERVATION_OUTSIDE_OR_DUPLICATE_CANDIDATE')
        by_id[identity] = observation
    usable = {key: row for key, row in by_id.items()
              if row.get('status') == 'SUCCEEDED' and row.get('evidence_id') and
              'value' in row and not row.get('truncated')}
    matches = [key for key, row in usable.items() if compare_figure(figure, row['value'])['matches']]
    exhaustive = inventory['exhaustive'] and set(usable) == expected and bool(expected)
    return {'selected': matches[0] if exhaustive and len(matches) == 1 else None,
            'matches': matches, 'exhaustive': exhaustive,
            'observations': deepcopy(observations),
            'reason': 'UNIQUE_VALUE_MATCH' if exhaustive and len(matches) == 1 else
                      'CANDIDATES_NOT_EXHAUSTED' if not exhaustive else
                      'MULTIPLE_MATCHES' if len(matches) > 1 else 'NO_MATCH'}
