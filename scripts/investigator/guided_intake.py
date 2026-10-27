"""Versioned, catalog-bound intake. Resolving a target never invents a finding.

The catalog is a projection of admitted graph records, not a hand-maintained
list of fixture names. This module does no network or model calls.
"""
from copy import deepcopy
from urllib.parse import parse_qs, urlsplit
from jsonschema import Draft202012Validator

VERSION = 'IntakeRequest/1'
ISSUES = ('NUMBER_LOOKS_WRONG', 'RECORD_MISSING', 'EXTRA_OR_DUPLICATE_RECORD',
          'DATA_LOOKS_OLD', 'BLANK_ERROR_OR_WONT_LOAD', 'OTHERS_SEE_DIFFERENT_NUMBER',
          'HOW_IS_THIS_CALCULATED', 'SOMETHING_ELSE')
COMPARISONS = ('ANOTHER_REPORT', 'SOURCE_SYSTEM', 'EXPECTED_NUMBER', 'NOTHING')
ID = {'type': 'string', 'minLength': 1}
TARGET = {'type': 'object', 'additionalProperties': False,
          'properties': {k: ID for k in ('report', 'page', 'visual')}, 'required': ['report']}
FIGURE = {'oneOf': [
    {'type': 'object', 'additionalProperties': False, 'properties': {
        'state': {'const': 'EMPTY'}}, 'required': ['state']},
    {'type': 'object', 'additionalProperties': False, 'properties': {
        'state': {'const': 'NUMBER'}, 'value': {'type': 'string', 'pattern': r'^-?\d+(\.\d+)?$'},
        'precision': {'oneOf': [{'const': 'EXACT'}, {'type': 'integer', 'minimum': 0, 'maximum': 100},
                               {'type':'object','properties':{'place':{'type':'integer','minimum':-100,'maximum':100}},
                                'required':['place'],'additionalProperties':False}]}},
     'required': ['state', 'value', 'precision']}]}
SCHEMA = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
          'title': VERSION, 'type': 'object', 'additionalProperties': False,
          'required': ['version', 'report', 'issue_type', 'compared_with'], 'properties': {
    'version': {'const': VERSION}, 'report': ID, 'page': ID, 'visual': ID,
    'issue_type': {'enum': list(ISSUES)}, 'description': {'type': 'string'},
    'classified_issue_type': {'enum': list(ISSUES[:-1])},
    'compared_with': {'type': 'object', 'additionalProperties': False,
        'properties': {'kind': {'enum': list(COMPARISONS)}, 'target': TARGET,
                       'source': ID, 'figure': FIGURE}, 'required': ['kind']},
    'reported_figure': FIGURE,
    'details': {'type': 'object', 'additionalProperties': False, 'properties': {
        'record': {'type': 'string', 'minLength': 1}, 'approximate_date': {'type': 'string'},
        'date_range': {'type': 'object', 'properties': {'from': ID, 'to': ID},
                       'required': ['from', 'to'], 'additionalProperties': False},
        'filters': {'type': 'array', 'items': {'type': 'object', 'properties': {
            'field': ID, 'value': {}}, 'required': ['field', 'value'], 'additionalProperties': False}},
        'report_url': {'type': 'string'}}},
    # Image bytes never enter this request, public logs or catalog. A private
    # case attachment port resolves the hash when vision is actually needed.
    'screenshot': {'type': 'object', 'additionalProperties': False,
        'properties': {'sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
                       'field_names': {'type': 'array', 'items': ID}},
        'required': ['sha256', 'field_names']}}}


class Catalog:
    def __init__(self, graph):
        if graph.get('truncated'):
            raise ValueError('INTAKE_CATALOG_TRUNCATED')
        self.nodes = {n['id']: deepcopy(n) for n in graph.get('nodes', graph.get('candidates', []))}
        self.edges = deepcopy(graph.get('edges', []))

    @classmethod
    def from_graph(cls, graph):
        # Full intake catalog and ticket path have different sizes. Do not use
        # the 200-node investigative slice to silently omit scanned reports.
        return cls(graph.intake_catalog())

    def rows(self, kind):
        return sorted(({'id': n['id'], 'name': n['label']} for n in self.nodes.values()
                       if n['kind'] == kind), key=lambda n: (n['name'].casefold(), n['id']))

    def children(self, parent, kind):
        ids = {e['target'] for e in self.edges if e['source'] == parent and e['kind'] == 'CONTAINS'}
        return [n for n in self.rows(kind) if n['id'] in ids]

    def reports(self): return self.rows('REPORT')
    def sources(self): return self.rows('SOURCE')

    def pages(self, report):
        self.require(report, 'REPORT')
        return self.children(report, 'PAGE')

    def visuals(self, report, page):
        if page not in {p['id'] for p in self.pages(report)}:
            raise ValueError('PAGE_OUTSIDE_REPORT')
        result = self.children(page, 'VISUAL')
        for visual in result:
            ids = {e['target'] for e in self.edges if e['source'] == visual['id']
                   and e['kind'] == 'COMPUTED_FROM'}
            visual['measures'] = [m for m in self.rows('MEASURE') if m['id'] in ids]
        return result

    def require(self, identity, kind):
        if self.nodes.get(identity, {}).get('kind') != kind:
            raise ValueError('UNKNOWN_' + kind)

    def target(self, target):
        self.require(target['report'], 'REPORT')
        if 'page' in target:
            if target['page'] not in {p['id'] for p in self.pages(target['report'])}:
                raise ValueError('PAGE_OUTSIDE_REPORT')
        if 'visual' in target:
            if 'page' not in target:
                raise ValueError('VISUAL_REQUIRES_PAGE')
            visual = next((v for v in self.visuals(target['report'], target['page'])
                           if v['id'] == target['visual']), None)
            if visual is None: raise ValueError('VISUAL_OUTSIDE_PAGE')
            return visual['measures']
        return []

    def view(self):
        return {'version': VERSION, 'reports': self.reports(), 'source_systems': self.sources(),
                'issue_types': list(ISSUES), 'compared_with': list(COMPARISONS),
                'hints': {'description': 'What did you see, and what did you compare it with?',
                          'record': 'A visible record name is enough to start a lookup.'},
                'example': 'On Daily Sales, the Collections card shows 950; my source app shows 900.'}

    def ranked(self,text,kind,*,within=None):
        import re
        words=set(re.findall(r'\w+',text.casefold()));rows=[]
        for node in self.nodes.values():
            if node['kind']!=kind or (within is not None and node['id'] not in within):continue
            names=[node['label'],*node.get('enrichment',{}).get('synonyms',[])]
            literal=next((name for name in names if name and re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',text,re.I)),None)
            meaning=node.get('enrichment',{}).get('business_meaning','')
            overlap=len(words & set(re.findall(r'\w+',' '.join([*names,meaning]).casefold())))
            if literal or overlap:
                rows.append({'id':node['id'],'name':node['label'],'confidence':'NAMED' if literal else 'RELATED_WORDS',
                             'matched_name':literal,'word_matches':overlap})
        return sorted(rows,key=lambda r:(r['confidence']!='NAMED',-r['word_matches'],r['name'],r['id']))


def admit(request, catalog):
    from .planner_recording import _safe
    from .estate_graph_contract import canonical
    _safe(canonical(request).encode())
    Draft202012Validator(SCHEMA).validate(request)
    result = deepcopy(request)
    result['measure_candidates'] = catalog.target(request)
    comparison = deepcopy(request['compared_with']); kind = comparison['kind']
    expected = {'ANOTHER_REPORT': 'target', 'SOURCE_SYSTEM': 'source', 'EXPECTED_NUMBER': 'figure'}
    required = {'kind'} | ({expected[kind]} if kind in expected else set())
    if not required <= set(comparison):
        raise ValueError('COMPARISON_DETAILS_REQUIRED')
    extras = set(comparison) - required
    # A copied reference to the selected visual is harmless formatting, but a
    # different target is a real competing referent and must not be discarded.
    if 'target' in extras:
        catalog.target(comparison['target'])
        if any(request.get(k) != v for k,v in comparison['target'].items()):
            raise ValueError('CONFLICTING_COMPARISON_TARGET')
    permitted = {'target','figure'} if kind == 'SOURCE_SYSTEM' else set()
    if not extras <= permitted:raise ValueError('COMPARISON_DETAILS_REQUIRED')
    if extras:
        result['comparison_context'] = {k:deepcopy(comparison[k]) for k in sorted(extras)}
        result['format_warnings'] = ['Supporting comparison details retained separately; selected comparison kind preserved.']
        comparison = {k:v for k,v in comparison.items() if k in required}
    if kind == 'ANOTHER_REPORT': catalog.target(comparison['target'])
    if kind == 'SOURCE_SYSTEM':
        supplied = comparison['source']
        if catalog.nodes.get(supplied,{}).get('kind') != 'SOURCE':
            matches = [r for r in catalog.sources() if r['name'].casefold() == supplied.casefold()]
            if len(matches) != 1:raise ValueError('SOURCE_NAME_UNRESOLVED_OR_AMBIGUOUS')
            comparison['source'] = matches[0]['id']
            result['source_resolution'] = {'supplied':supplied,'id':matches[0]['id'],'basis':'UNIQUE_EXACT_CATALOG_NAME'}
        catalog.require(comparison['source'], 'SOURCE')
    result['compared_with'] = comparison
    if request['issue_type'] == 'SOMETHING_ELSE':
        if not request.get('description', '').strip(): raise ValueError('OTHER_REQUIRES_DESCRIPTION')
        if 'classified_issue_type' not in request: raise ValueError('OTHER_REQUIRES_CLASSIFICATION')
    elif 'classified_issue_type' in request:
        raise ValueError('CLASSIFICATION_ONLY_FOR_OTHER')
    # URL selections are untrusted user scope, not established report state.
    url = request.get('details', {}).get('report_url')
    if url:
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or parsed.username or parsed.password:
            raise ValueError('REPORT_URL_INVALID')
        result['url_filters'] = parse_qs(parsed.query).get('filter', [])
    result['status'] = 'READY'
    return result


def prefill(text, proposed, catalog, *, provenance=None):
    """Validate model-extracted fields; never manufacture a report or figure.

    Caller supplies a model proposal. No model call is hidden in this function.
    A missing report gets catalog choices; optional page/visual and comparison
    do not block triage. A named target is never replaced by a value match.
    """
    value = deepcopy(proposed)
    value['version'] = VERSION
    value['description']=text
    value.setdefault('compared_with', {'kind': 'NOTHING'})
    reports=[r for r in catalog.ranked(text,'REPORT') if r['confidence']=='NAMED']
    if len(reports)==1:
        if value.get('report') and value['report']!=reports[0]['id']:
            raise ValueError('REPORT_REFERENCE_DIFFERS_FROM_TICKET')
        value.setdefault('report',reports[0]['id'])
    if value.get('report'):
        pages=[p for p in catalog.ranked(text,'PAGE',within={p['id'] for p in catalog.pages(value['report'])})
               if p['confidence']=='NAMED']
        if len(pages)==1:
            if value.get('page') and value['page']!=pages[0]['id']:raise ValueError('PAGE_REFERENCE_DIFFERS_FROM_TICKET')
            value.setdefault('page',pages[0]['id'])
    provenance=deepcopy(provenance or {})
    def source(field):
        from .intake_span_references import tokens
        parts=tokens(text);ref=provenance.get(field)
        if (not isinstance(ref,list) or len(ref)!=2 or any(type(n) is not int for n in ref)
                or not 1<=ref[0]<=ref[1]<=len(parts)):
            raise ValueError('FREE_TEXT_PROVENANCE_REQUIRED:'+field)
        start,end=parts[ref[0]-1]['start'],parts[ref[1]-1]['end']
        return {'start':start,'end':end,'quote':text[start:end]}
    recorded={}
    if 'reported_figure' in value:
        from . import reported_figure
        span=source('reported_figure');figure=value['reported_figure']
        if figure.get('state')=='EMPTY':
            if not reported_figure.empty_result(span['quote']):raise ValueError('EMPTY_PROVENANCE_DIFFERS')
        else:
            number,precision=reported_figure.stated(span['quote'])
            expected='EXACT' if precision['state']=='EXACT' else {'place':precision['place']}
            supplied=figure.get('precision')
            if type(supplied) is int:supplied={'place':-supplied}
            if figure.get('value')!=number or supplied!=expected:raise ValueError('FIGURE_OR_PRECISION_DIFFERS_FROM_TICKET')
        recorded['reported_figure']=span
    if 'visual' in value:
        span=source('visual')
        node=catalog.nodes.get(value['visual'],{})
        names=[node.get('label',''),*node.get('enrichment',{}).get('synonyms',[])]
        if not any(name and name.casefold() in span['quote'].casefold() for name in names):
            raise ValueError('VISUAL_PROVENANCE_DIFFERS_FROM_TARGET')
        recorded['visual']=span
    missing = [k for k in ('report', 'issue_type') if not value.get(k)]
    if missing:
        # Check supplied fields even when others are missing.
        partial = deepcopy(SCHEMA); partial['required'] = ['version']
        Draft202012Validator(partial).validate(value)
        if value.get('report'): catalog.require(value['report'], 'REPORT')
        return {'status': 'NEEDS_INPUT', 'prefilled': value, 'provenance_references':provenance,'question': {
            'text': 'Choose the missing details so I can check the report.',
            'fields': [{'field': k, 'choices': catalog.reports() if k == 'report'
                        else [{'id': i, 'name': i.replace('_', ' ').title()} for i in ISSUES]}
                       for k in missing]}}
    result=admit(value, catalog)
    result['provenance']=recorded
    result['provenance_references']=provenance
    return result
