"""Bounded target alternatives, preserving explicit choices and retained scope.

This enumerates catalog addresses only. It never builds a query, guesses a
binding or chooses a target because of a similar name or value elsewhere.
"""
from copy import deepcopy
import re


def explicit_names(catalog,text):
    """Verbatim native names constrain scope; model-proposed IDs do not."""
    result={}
    for field,kind in (('report','REPORT'),('page','PAGE'),('visual','VISUAL')):
        within=None
        if field=='page' and result.get('report'):
            within={p['id']for p in catalog.pages(result['report'])}
        if field=='visual' and result.get('report'):
            pages=[p for p in catalog.pages(result['report'])if not result.get('page') or p['id']==result['page']]
            within={v['id']for p in pages for v in catalog.visuals(result['report'],p['id'])}
        # Catalog ranking includes enrichment aliases. Those are search aids,
        # never evidence that the user explicitly selected a native address.
        named=[{'id': n['id'], 'name': n['label'], 'matched_name': n['label']}
               for n in catalog.nodes.values() if n.get('kind') == kind
               and (within is None or n['id'] in within) and n.get('label')
               and re.search(r'(?<!\w)' + re.escape(n['label']) + r'(?!\w)', text, re.I)]
        if named:
            longest=max(len(r.get('matched_name')or r['name'])for r in named)
            named=[r for r in named if len(r.get('matched_name')or r['name'])==longest]
        if len(named)==1:result[field]=named[0]['id']
    # Parent addresses come from containment, not another similar name.
    if result.get('visual') and not result.get('report'):
        reports=catalog.reports_for(result['visual'])
        if len(reports)==1:result['report']=reports[0]['id']
    if result.get('page') and not result.get('report'):
        reports=catalog.reports_for(result['page'])
        if len(reports)==1:result['report']=reports[0]['id']
    if result.get('visual') and result.get('report') and not result.get('page'):
        parents=[p for p in catalog.pages(result['report'])if any(v['id']==result['visual']for v in catalog.visuals(result['report'],p['id']))]
        if len(parents)==1:result['page']=parents[0]['id']
    return result


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
        if not reports and re.search(r'\d',text) and not(catalog.table_matches(text)or catalog.measure_matches(text)):
            # A number without a resolved subject still gets bounded checks,
            # not a bare intake refusal. Truncation forbids target selection.
            reports=catalog.reports()
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
    if len(expected) == 1 and inventory['exhaustive']:
        candidate = inventory['candidates'][0]
        explicit = candidate.get('explicit', {})
        if candidate['id'] in [explicit.get(k) for k in ('visual', 'table', 'measure')]:
            return {'selected': candidate['id'], 'matches': [], 'exhaustive': True,
                    'observations': deepcopy(observations), 'reason': 'EXPLICIT_TARGET'}
    if not figure:
        return {'selected': None, 'matches': [], 'exhaustive': False,
                'observations': deepcopy(observations),
                'reason': 'NO_REPORTED_VALUE_FOR_TARGET_DISAMBIGUATION'}
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
