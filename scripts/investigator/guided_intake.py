"""Versioned, catalog-bound intake. Resolving a target never invents a finding.

The catalog is a projection of admitted graph records, not a hand-maintained
list of fixture names. This module does no network or model calls.
"""
from copy import deepcopy
from urllib.parse import parse_qs, urlsplit
from jsonschema import Draft202012Validator, ValidationError

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
          'required': ['version', 'issue_type', 'compared_with'],
          'anyOf': [{'required': ['report']}, {'required': ['table']}, {'required': ['measure']}],
          'dependentRequired': {'page': ['report'], 'visual': ['report', 'page']}, 'properties': {
    'version': {'const': VERSION}, 'report': ID, 'page': ID, 'visual': ID,
    'table': ID, 'measure': ID,
    'issue_type': {'enum': list(ISSUES)}, 'description': {'type': 'string'},
    'classified_issue_type': {'enum': list(ISSUES[:-1])},
    'compared_with': {'type': 'object', 'additionalProperties': False,
        'properties': {'kind': {'enum': list(COMPARISONS)}, 'target': TARGET,
                       'source': ID, 'figure': FIGURE}, 'required': ['kind']},
    'reported_figure': FIGURE,
    'details': {'type': 'object', 'additionalProperties': False, 'properties': {
        'record': {'type': 'string', 'minLength': 1}, 'approximate_date': {'type': 'string'},
        'users': {'type': 'array', 'maxItems': 20, 'items': ID},
        'roles': {'type': 'array', 'maxItems': 20, 'items': ID},
        'table': ID, 'measure': ID,
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
        if 'report' not in target:
            if 'table' in target:
                if self.nodes.get(target['table'], {}).get('kind') not in ('TABLE', 'VIEW'):
                    raise ValueError('UNKNOWN_TABLE')
                return []
            self.require(target['measure'], 'MEASURE')
            return [row for row in self.rows('MEASURE') if row['id'] == target['measure']]
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
        import re, unicodedata
        from difflib import SequenceMatcher
        def normalized(value):
            return ' '.join(re.findall(r'[^\W_]+', unicodedata.normalize('NFKC', value).casefold()))
        normalized_text = normalized(text)
        text_words = normalized_text.split()
        words=set(re.findall(r'\w+',text.casefold()));rows=[]
        for node in self.nodes.values():
            if node['kind']!=kind or (within is not None and node['id'] not in within):continue
            names=[node['label'],*node.get('enrichment',{}).get('synonyms',[])]
            literal=next((name for name in names if name and re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',text,re.I)),None)
            meaning=node.get('enrichment',{}).get('business_meaning','')
            overlap=len(words & set(re.findall(r'\w+',' '.join([*names,meaning]).casefold())))
            exact_normalized = next((name for name in names if normalized(name) and
                                    re.search(r'(?<!\w)' + re.escape(normalized(name)) + r'(?!\w)', normalized_text)), None)
            fuzzy = 0.0
            for name in names:
                target = normalized(name)
                width = len(target.split())
                if len(target) < 4 or not width:continue
                fuzzy = max(fuzzy, max((SequenceMatcher(None, target, ' '.join(text_words[i:i+width])).ratio()
                                        for i in range(max(0, len(text_words)-width+1))), default=0.0))
            confidence = 'NAMED' if literal else 'NORMALIZED' if exact_normalized else 'FUZZY' if fuzzy >= .86 else 'RELATED_WORDS'
            score = 1.0 if literal else .99 if exact_normalized else fuzzy if fuzzy >= .86 else min(.75, overlap / max(1, len(words)))
            if literal or exact_normalized or fuzzy >= .86 or overlap:
                rows.append({'id':node['id'],'name':node['label'],'confidence':confidence,
                             'matched_name':literal or exact_normalized,'word_matches':overlap,
                             'score':round(score, 6),'basis':'CATALOG_NAME_SYNONYMS_AND_MEANING'})
        return sorted(rows,key=lambda r:(-r['score'],-r['word_matches'],r['name'],r['id']))

    def reports_for(self, identity):
        """Walk actual containment/measure-use edges, never name similarity."""
        seen = {identity}; frontier = [identity]
        while frontier:
            current = frontier.pop()
            for edge in self.edges:
                if edge['target'] != current or edge['kind'] not in ('CONTAINS', 'COMPUTED_FROM'):continue
                parent = edge['source']
                if parent not in seen:
                    seen.add(parent); frontier.append(parent)
        return [row for row in self.reports() if row['id'] in seen]

    def table_matches(self, text):
        """Resolve native container names through retained containment only."""
        direct = [*self.ranked(text, 'TABLE'), *self.ranked(text, 'VIEW')]
        direct.sort(key=lambda r: -r['score'])
        containers = [r for kind in ('MODEL', 'SOURCE') for r in self.ranked(text, kind)
                      if r['confidence'] in ('NAMED', 'NORMALIZED')]
        contained = []
        for parent in containers:
            children = [*self.children(parent['id'], 'TABLE'), *self.children(parent['id'], 'VIEW')]
            if len(children) == 1:
                child = children[0]
                contained.append({**child, 'score':parent['score'], 'confidence':parent['confidence'],
                    'basis':'NATIVE_CONTAINMENT_OF_NAMED_CONTAINER', 'via':parent['id']})
        if direct and direct[0]['confidence'] in ('NAMED', 'NORMALIZED'):
            return [r for r in direct if direct[0]['score']-r['score'] < .08]
        if contained:
            return list({r['id']:r for r in contained}.values())
        return [r for r in direct if r['score'] >= .86 and direct[0]['score']-r['score'] < .08]

    def report_matches(self, text):
        direct = self.ranked(text, 'REPORT')
        if direct and direct[0]['confidence'] in ('NAMED', 'NORMALIZED'):
            return [r for r in direct if direct[0]['score'] - r['score'] < .08]
        pages = self.ranked(text, 'PAGE')
        page_reports = {r['id'] for page in pages if page['score'] >= .86 and pages[0]['score'] - page['score'] < .08
                        for r in self.reports_for(page['id'])}
        matches = []
        for kind in ('VISUAL', 'MEASURE'):
            ranked = self.ranked(text, kind)
            if not ranked or ranked[0]['score'] < .86:continue
            for target in ranked:
                if ranked[0]['score'] - target['score'] >= .08:continue
                for report in self.reports_for(target['id']):
                    matches.append({**report, 'score': target['score'], 'confidence': target['confidence'],
                                    'via': target['id'], 'basis': 'CATALOG_CONTAINMENT_OF_NAMED_' + kind})
        matches = list({r['id']: r for r in matches}.values())
        if page_reports:
            matches = [r for r in matches if r['id'] in page_reports]
            if not matches:
                matches = [{**r, 'score': pages[0]['score'], 'confidence': pages[0]['confidence'],
                            'basis': 'CATALOG_CONTAINMENT_OF_NAMED_PAGE', 'via': pages[0]['id']}
                           for r in self.reports() if r['id'] in page_reports]
        if matches:
            strongest = max(r['score'] for r in matches)
            return [r for r in matches if strongest - r['score'] < .08]
        if direct and direct[0]['score'] >= .86:
            return [r for r in direct if direct[0]['score'] - r['score'] < .08]
        return []


def admit(request, catalog):
    from .planner_recording import _safe
    from .estate_graph_contract import canonical
    _safe(canonical(request).encode())
    Draft202012Validator(SCHEMA).validate(request)
    result = deepcopy(request)
    if sum(bool(request.get(k)) for k in ('report', 'table', 'measure')) > 1:
        raise ValueError('CONFLICTING_TARGET_SELECTION')
    result['measure_candidates'] = catalog.target(request)
    comparison = deepcopy(request['compared_with']); kind = comparison['kind']
    expected = {'ANOTHER_REPORT': 'target', 'SOURCE_SYSTEM': 'source', 'EXPECTED_NUMBER': 'figure'}
    required = {'kind'} | ({expected[kind]} if kind in expected else set())
    if kind != 'ANOTHER_REPORT' and 'target' in comparison:
        catalog.target(comparison['target'])
        if any(request.get(k) != v for k, v in comparison['target'].items()):
            raise ValueError('CONFLICTING_COMPARISON_TARGET')
    if not required <= set(comparison):
        result['comparison_context'] = deepcopy(comparison)
        declared = [n for n in catalog.nodes.values() if n['kind'] == 'SOURCE'
                    and n.get('properties', {}).get('system_of_record') is True]
        comparison = ({'kind': 'SOURCE_SYSTEM', 'source': declared[0]['id']}
                      if len(declared) == 1 else {'kind': 'NOTHING'})
        kind = comparison['kind']
        required = set(comparison)
        result['format_warnings'] = [
            'Comparison details are incomplete; using the declared source of truth.'
            if declared and len(declared) == 1 else
            'Comparison details are incomplete; recreation and freshness proceed without a comparison.']
    extras = set(comparison) - required
    # A copied reference to the selected visual is harmless formatting, but a
    # different target is a real competing referent and must not be discarded.
    if 'target' in extras:
        catalog.target(comparison['target'])
        if any(request.get(k) != v for k,v in comparison['target'].items()):
            raise ValueError('CONFLICTING_COMPARISON_TARGET')
    if extras:
        result.setdefault('comparison_context', {}).update({k:deepcopy(comparison[k]) for k in sorted(extras)})
        result.setdefault('format_warnings', []).append('Supporting comparison details retained separately; selected comparison kind preserved.')
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
        if 'classified_issue_type' not in request:
            result['classification_status'] = 'PENDING_INVESTIGATOR'
    elif 'classified_issue_type' in request and request['classified_issue_type'] != request['issue_type']:
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
    if value.get('report') and value.get('measure'):
        # A measure used by the selected report/visual is contextual detail,
        # not a competing primary target. Preserve it with its native link.
        measure=value['measure'];report=value['report']
        if value.get('visual'):
            linked=any(e['source']==value['visual'] and e['target']==measure
                       and e['kind']=='COMPUTED_FROM' for e in catalog.edges)
        elif value.get('page'):
            linked=any(m['id']==measure for v in catalog.visuals(report,value['page']) for m in v.get('measures',[]))
        else:linked=any(r['id']==report for r in catalog.reports_for(measure))
        if linked:
            value.setdefault('details',{})['measure']=value.pop('measure')
    direct_target = None
    for kind, field in (('TABLE', 'table'), ('MEASURE', 'measure')):
        if value.get(field) and not value.get('report'):
            candidates = catalog.table_matches(text) if field == 'table' else catalog.ranked(text, kind)
            strongest = max((r['score'] for r in candidates), default=0)
            matched = [r for r in candidates if r['score'] >= .86 and strongest - r['score'] < .08]
            if len(matched) == 1 and matched[0]['id'] == value[field]:direct_target = matched[0]
            else:raise ValueError('DIRECT_TARGET_UNRESOLVED_OR_AMBIGUOUS')
    if not value.get('report') and not any(value.get(k) for k in ('table', 'measure')):
        if not any(r['score'] >= .86 for r in catalog.ranked(text, 'REPORT')):
            tables = catalog.table_matches(text)
            if len(tables) == 1:
                value['table'] = tables[0]['id']; direct_target = tables[0]
    reports=catalog.report_matches(text)
    assumption = None
    if len(reports)==1 and not direct_target:
        if value.get('report') and value['report']!=reports[0]['id']:
            raise ValueError('REPORT_REFERENCE_DIFFERS_FROM_TICKET')
        value.setdefault('report',reports[0]['id'])
        if reports[0].get('via') or reports[0]['confidence'] != 'NAMED':
            assumption = {'report': reports[0]['id'], 'name': reports[0]['name'],
                          'basis': reports[0]['basis'], 'matched_node': reports[0].get('via')}
    elif len(reports) > 1 and not direct_target:
        return {'status': 'NEEDS_INPUT', 'prefilled': value, 'question': {
            'text': 'These catalog matches remain close. Which report do you mean?',
            'fields': [{'field': 'report', 'choices': [{'id': r['id'], 'name': r['name']} for r in reports]}]},
            'resolution_candidates': reports}
    if value.get('report'):
        if value.get('visual') and not value.get('page'):
            # A selected visual's unique native parent is an address lookup,
            # not a replacement visual or an inferred filter selection.
            parents=[p for p in catalog.pages(value['report'])
                     if any(v['id']==value['visual']for v in catalog.visuals(value['report'],p['id']))]
            if len(parents)==1:value['page']=parents[0]['id']
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
        exact=any(name and name.casefold() in span['quote'].casefold() for name in names)
        if not exact and value.get('report') and value.get('page'):
            visuals=catalog.visuals(value['report'],value['page'])
            report_visuals={v['id'] for p in catalog.pages(value['report'])
                            for v in catalog.visuals(value['report'],p['id'])}
            named=[r for r in catalog.ranked(text,'VISUAL',within=report_visuals)
                   if r['confidence']=='NAMED']
            measures={e['target']for e in catalog.edges if e['source']==value['visual'] and e['kind']=='COMPUTED_FROM'}
            cited={m for m in measures if catalog.nodes.get(m,{}).get('label','') and
                   catalog.nodes[m]['label'].casefold() in span['quote'].casefold()}
            same_measure=[v for v in visuals if any(m['id']in cited for m in v.get('measures',[]))]
            exact=bool(cited) and len(same_measure)==1 and same_measure[0]['id']==value['visual'] and not named
        if not exact:
            raise ValueError('VISUAL_PROVENANCE_DIFFERS_FROM_TARGET')
        recorded['visual']=span
    missing = [k for k in ('report', 'issue_type') if not value.get(k)
               and not (k == 'report' and (value.get('table') or value.get('measure')))]
    if missing:
        # Check supplied fields even when others are missing.
        partial = deepcopy(SCHEMA); partial['required'] = ['version']
        partial.pop('anyOf', None); partial.pop('dependentRequired', None)
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
    if direct_target:
        result['resolution_assumptions']=[{'name': direct_target['name'], 'basis': 'UNIQUE_NAMED_CATALOG_OBJECT', 'object': direct_target['id']}]
    elif assumption:result['resolution_assumptions']=[assumption]
    selected=direct_target or (reports[0] if len(reports)==1 else None)
    result['resolution_confidence']=selected['confidence'] if selected else 'UNVERIFIED'
    return result


def admit_or_question(request, catalog):
    """Public intake boundary: malformed selections ask once, never crash.

    Secret protection runs outside the recoverable-validation handler. No
    malformed target is replaced with a different report or visual.
    """
    from .planner_recording import _safe
    from .estate_graph_contract import canonical
    _safe(canonical(request).encode())
    value = deepcopy(request)
    warnings = []
    if isinstance(value, dict):
        extra = set(value) - set(SCHEMA['properties'])
        if extra:
            value = {k: v for k, v in value.items() if k in SCHEMA['properties']}
            warnings.append('Unrecognized form fields were ignored; selected target and values are unchanged.')
        value.setdefault('version', VERSION)
        value.setdefault('compared_with', {'kind': 'NOTHING'})
    try:
        result = admit(value, catalog)
        result.setdefault('format_warnings', []).extend(warnings)
        return result
    except (ValidationError, ValueError) as error:
        reason = error.validator if isinstance(error, ValidationError) else str(error)
        selected = value if isinstance(value, dict) else {}
        report = selected.get('report')
        report = report if isinstance(report, str) else None
        fields = []
        physical = selected.get('table') or selected.get('measure')
        physical = physical if isinstance(physical, str) else None
        if report is None and physical and catalog.nodes.get(physical, {}).get('kind') in ('TABLE', 'VIEW', 'MEASURE'):
            pass
        elif catalog.nodes.get(report, {}).get('kind') != 'REPORT':
            fields.append({'field': 'report', 'choices': catalog.reports()})
        else:
            page = selected.get('page')
            valid_pages = catalog.pages(report)
            if page is not None and (not isinstance(page, str) or page not in [p['id'] for p in valid_pages]):
                fields.append({'field': 'page', 'choices': valid_pages})
            elif selected.get('visual') is not None and reason in ('VISUAL_OUTSIDE_PAGE', 'VISUAL_REQUIRES_PAGE', 'UNKNOWN_VISUAL'):
                visuals = catalog.visuals(report, page) if page else [
                    v for p in valid_pages for v in catalog.visuals(report, p['id'])]
                fields.append({'field': 'visual', 'choices': [{'id': v['id'], 'name': v['name']} for v in visuals]})
        if not fields:
            fields.append({'field': 'intake_details', 'choices': [],
                           'needed': 'Confirm the stated figure, issue or comparison; the selected report is retained.'})
        question = {'text': 'Please confirm these details from the catalog choices.', 'fields': fields}
        return {'status': 'NEEDS_INPUT', 'code': 'INTAKE_DETAILS_UNRESOLVED',
                'reason': reason, 'prefilled': value, 'question': question,
                'format_warnings': warnings}
