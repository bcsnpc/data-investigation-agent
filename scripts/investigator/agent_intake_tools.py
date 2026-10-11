"""Agent intake ports over retained definitions and verified quantity readers.

Search results are evidence, never authority to change a picked form fact.
The enclosing loop owns tape, step, wall-clock and dollar admission. Quantity,
vision and comment ports must be the installation's governed existing ports;
this module has no transport, SQL compiler or estate-write capability.
"""
import copy
from jsonschema import Draft202012Validator
from .onboarding import Conflict, digest
from . import form_candidates, form_intake, reported_figure

ID = {'type': 'string', 'minLength': 1, 'maxLength': 200}
TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 1600}

def schema(properties, optional=()):
    return {'type': 'object', 'additionalProperties': False, 'properties': properties,
            'required': [k for k in properties if k not in optional]}

SCHEMAS = {
    'list_reports': schema({}),
    'list_pages': schema({'report_id': ID}),
    'list_visuals': schema({'report_id': ID, 'page_id': ID}),
    'find_value_on_page': schema({'report_id': ID, 'page_id': ID, 'value': TEXT,
        'cell_mode': {'enum': ['UNGROUPED', 'TOTAL', 'KEYED']}, 'measure_id': ID,
        'cell_keys': form_intake.SCHEMA['properties']['cell_keys']},
        ('cell_mode', 'measure_id', 'cell_keys')),
    'read_screenshot': schema({'image_id': ID}),
    'ask_user': schema({'field':{'enum':['REPORT','PAGE','VISUAL','FIGURE','COMPARISON','SELECTION','BUSINESS_INTENT']},'report_id':{'anyOf':[ID,{'type':'null'}]},'page_id':{'anyOf':[ID,{'type':'null'}]}},('report_id','page_id')),
    'request_screenshot': schema({}),
}
DESCRIPTIONS = {
    'list_reports': 'List retained reports. Definitions are not live screenshots or user selections.',
    'list_pages': 'List retained pages and titles in one report, with definition provenance.',
    'list_visuals': 'List retained visual titles, measures, grouping and declared filter scopes. Incomplete scopes stay explicit.',
    'find_value_on_page': 'Search verified quantities on a page. Returns candidates, not a selected target. Default searches ungrouped cells only; totals or keyed cells require explicit cell_mode and keys. Does not assert a search value came from the user.',
    'read_screenshot': 'Read a supplied attachment through the governed vision port. Transcription is unverified unless user reviewed; positions refer only to supplied pixels.',
    'ask_user': 'Select the missing fact field. Code renders the question and named choices from retained catalog evidence; no free factual assertions or IDs are posted. Supply report_id and page_id only to scope catalog choices. Do not ask for a picked fact. Resume requires a real user comment.',
    'request_screenshot': 'Ask the user for a screenshot in this ticket and pause. Does not capture a browser or select an image.',
}

class IntakeTools:
    def __init__(self, snapshot_reader, record_evidence, *, candidate_reader=None,
                 screenshot_reader=None, comment_port=None, fixed_facts=None):
        self.snapshot_reader = snapshot_reader
        self.record_evidence = record_evidence
        self.candidate_reader = candidate_reader
        self.screenshot_reader = screenshot_reader
        self.comment_port = comment_port
        self._fixed = copy.deepcopy(fixed_facts or {})
        if set(self._fixed) - {'report_id', 'page_id', 'target_id', 'comparison', 'measure_id', 'cell_mode', 'cell_keys'}:
            raise ValueError('Unknown picked form fact')

    @property
    def fixed_facts(self):
        return copy.deepcopy(self._fixed)

    def definitions(self):
        from .intake_span_references import enabled
        descriptions=copy.deepcopy(DESCRIPTIONS)
        if not enabled():descriptions['ask_user']='Post one question to this ticket and pause. No answer is fabricated; resume requires a real user comment.'
        definitions=[{'name':name,'description':descriptions[name],'parameters':copy.deepcopy(parameters)} for name,parameters in self.schemas().items()]
        if enabled():
            for d in definitions:
                if d['name']=='ask_user':d['parameters']['required']=list(d['parameters']['properties'])
        return definitions

    def schemas(self):
        from .intake_span_references import enabled
        value=copy.deepcopy(SCHEMAS)
        if not enabled():
            value['ask_user']=schema({'question':TEXT,'choices':{'type':'array','minItems':2,'maxItems':8,'uniqueItems':True,'items':TEXT}},('choices',))
            value['request_screenshot']=schema({'what':TEXT})
        return value

    def handlers(self):
        return {name: (lambda name=name, **arguments: self.call(name, arguments)) for name in SCHEMAS}

    def invoke(self, name, arguments):
        return self.call(name, arguments)

    def call(self, name, arguments):
        if name not in SCHEMAS:
            raise ValueError('Unknown agent intake tool')
        Draft202012Validator(self.schemas()[name]).validate(arguments)
        for key, value in self._fixed.items():
            if key in arguments and value is not None and arguments[key] is not None and arguments[key] != value:
                raise Conflict('Picked form fact is immutable: ' + key)
        return getattr(self, name)(**copy.deepcopy(arguments))

    def _catalog(self):
        catalog = copy.deepcopy(self.snapshot_reader())
        if not isinstance(catalog, dict) or not isinstance(catalog.get('models'), list) or not isinstance(catalog.get('versions'), dict):
            raise Conflict('Retained definition snapshot unavailable')
        if any(not m.get('context_id') or not catalog['versions'].get(m['id']) for m in catalog['models']):
            raise Conflict('Definition context/version is unbound')
        return catalog

    def _record(self, name, body, catalog=None):
        result = {'tool': name, **body, 'picked_form_facts': self.fixed_facts}
        if catalog is not None:
            result['provenance'] = {'kind': 'RETAINED_DEFINITIONS',
                'catalog_hash': digest(catalog['models']), 'versions': catalog['versions'],
                'context_ids': {m['id']: m['context_id'] for m in catalog['models']}}
        # Recorder owns privacy projection and sealed evidence storage. Refuse an
        # unrecorded result instead of inventing a citation from a content hash.
        identity = self.record_evidence(copy.deepcopy(result))
        if not isinstance(identity, str) or not identity:
            raise Conflict('Tool result was not recorded as evidence')
        native = [o['receipt_id'] for o in body.get('observations', [])]
        if body.get('receipt_id'): native.append(body['receipt_id'])
        return {**result, 'evidence_id': identity, 'facade_evidence_id': identity,
                'native_evidence_ids': list(dict.fromkeys(native)),
                'evidence_ids': list(dict.fromkeys([identity, *native])), 'finding_authority': False}

    def _report(self, catalog, report_id):
        if self._fixed.get('report_id') is not None and self._fixed['report_id'] != report_id:
            raise Conflict('Picked form fact is immutable: report_id')
        matches = [(m, r) for m in catalog['models'] for r in m.get('reports', []) if r['id'] == report_id]
        if len(matches) != 1:
            raise Conflict('Report is absent or ambiguously bound')
        return matches[0]

    def _page(self, catalog, report_id, page_id):
        if self._fixed.get('page_id') is not None and self._fixed['page_id'] != page_id:
            raise Conflict('Picked form fact is immutable: page_id')
        model, report = self._report(catalog, report_id)
        visuals = [v for v in model.get('visuals', []) if v['report_id'] == report_id and v.get('page_id') == page_id]
        if not visuals:
            raise Conflict('Page has no retained visuals')
        if len({v['target_id'] for v in visuals}) != len(visuals):
            raise Conflict('Visual identity is ambiguous on page')
        return model, report, visuals

    def list_reports(self):
        catalog = self._catalog()
        reports = [{'report_id': r['id'], 'title': r['name'], 'model_id': m['id']}
                   for m in catalog['models'] for r in m.get('reports', [])]
        if len({r['report_id'] for r in reports}) != len(reports):
            raise Conflict('Report identity is ambiguous')
        return self._record('list_reports', {'status': 'AVAILABLE', 'reports': reports}, catalog)

    def list_pages(self, report_id):
        catalog = self._catalog(); model, _ = self._report(catalog, report_id)
        pages = {}
        for visual in model.get('visuals', []):
            if visual['report_id'] != report_id: continue
            page = visual.get('page_id')
            if page is None: continue
            pages.setdefault(page, set()).update(visual.get('page_names', []))
        return self._record('list_pages', {'status': 'AVAILABLE', 'report_id': report_id,
            'pages': [{'page_id': p, 'titles': sorted(t)} for p, t in sorted(pages.items())]}, catalog)

    def list_visuals(self, report_id, page_id):
        catalog = self._catalog(); model, _, visuals = self._page(catalog, report_id, page_id)
        names = {m['id']: m['name'] for m in model['measures']}
        results = [{'target_id': v['target_id'], 'titles': copy.deepcopy(v.get('names', [])),
            'form': v.get('form'), 'measures': [{'measure_id': mid, 'title': names.get(mid),
                'declared_scope': {k: copy.deepcopy(value) for k, value in v.get('declared_scopes', {}).get(mid, {'state': 'UNAVAILABLE'}).items()
                    if k in ('state', 'restrictions', 'context_id', 'context_hash', 'reason', 'assumed_slicer_defaults')}}
                for mid in v['measure_ids']], 'grouping_columns': copy.deepcopy(v['grouping_columns']),
            'unsupported': copy.deepcopy(v.get('unsupported', []))} for v in visuals]
        return self._record('list_visuals', {'status': 'AVAILABLE', 'report_id': report_id,
            'page_id': page_id, 'visuals': results, 'scope_limit': 'SAVED_DECLARATIONS_ONLY; user selection and RLS not inferred'}, catalog)

    def find_value_on_page(self, report_id, page_id, value, cell_mode='UNGROUPED', measure_id=None, cell_keys=None):
        for key, value_arg in (('measure_id', measure_id), ('cell_mode', cell_mode), ('cell_keys', cell_keys or [])):
            if self._fixed.get(key) is not None and self._fixed[key] != value_arg:
                raise Conflict('Picked form fact is immutable: ' + key)
        catalog = self._catalog(); self._page(catalog, report_id, page_id)
        # Existing candidate machinery compiles complete declarations through the
        # verified compiler and quantity reader. No SQL/DAX is constructed here.
        request = {'version': form_intake.VERSION, 'request_key': 'agent-value-search',
            'report_id': report_id, 'page_id': page_id, 'target_id': None,
            'cell_mode': cell_mode, 'value_seen': value, 'comparison': 'DECLARED_SUBJECT',
            'description': '', 'cell_keys': cell_keys or []}
        if measure_id is not None: request['measure_id'] = measure_id
        candidates = form_candidates.candidates(request, catalog['models'])
        if self._fixed.get('target_id') is not None:
            candidates = [c for c in candidates if c['target_id'] == self._fixed['target_id']]
            if not candidates: raise Conflict('Picked visual has no candidate for requested cell')
        if self.candidate_reader is None:
            return self._record('find_value_on_page', {'status': 'UNAVAILABLE', 'reason': 'VERIFIED_QUANTITY_READER_UNAVAILABLE'}, catalog)
        observed = []
        try:
            for candidate in candidates:
                probe = self.candidate_reader(copy.deepcopy(candidate))
                if (not isinstance(probe, dict) or probe.get('status') != 'OBSERVED' or probe.get('complete') is not True
                    or not all(probe.get(k) for k in ('receipt_id', 'query_hash', 'execution_surface', 'attestation'))
                    or probe['attestation'].get('consistency') != 'MATCHED'):
                    raise form_candidates.NotMeasurable('Candidate observation is incomplete or unattested')
                label = reported_figure.label(candidate['scope']['reported_figure'], probe['value'])
                observed.append({'model_id': candidate['model_id'], 'target_id': candidate['target_id'],
                    'measure_id': candidate['measure_id'], 'cell_mode': candidate['mode'],
                    'cell_keys': copy.deepcopy(candidate['scope']['filters']), 'scope_hash': candidate['scope_hash'],
                    'match': label == 'REPRODUCED', 'value': probe['value'],
                    'receipt_id': probe['receipt_id'], 'query_hash': probe['query_hash'],
                    'execution_surface': copy.deepcopy(probe['execution_surface']), 'attestation': copy.deepcopy(probe['attestation'])})
            if digest(self._catalog()) != digest(catalog):
                raise Conflict('Definitions changed during candidate observations')
        except Exception as error:
            self._record('find_value_on_page', {'status': 'INCOMPLETE', 'observations': observed,
                'expected_candidates': len(candidates), 'error_type': type(error).__name__}, catalog)
            raise
        return self._record('find_value_on_page', {'status': 'AVAILABLE', 'observations': observed,
            'matches': [o for o in observed if o['match']], 'coverage': {'cell_mode': cell_mode,
                'exhaustive_for_requested_cell_mode': True, 'all_page_cells': False},
            'search_authority': 'AGENT_SEARCH_ARGUMENT; not a user-reported-figure assertion',
            'target_selected': False}, catalog)

    def read_screenshot(self, image_id):
        if self.screenshot_reader is None:
            return self._record('read_screenshot', {'status': 'UNAVAILABLE', 'reason': 'VISION_PORT_UNAVAILABLE'})
        read = self.screenshot_reader(image_id)
        if not isinstance(read, dict) or not read.get('image_sha256') or not read.get('receipt_id'):
            raise Conflict('Screenshot read lacks attachment hash or governed receipt')
        if not isinstance(read.get('visible_text', ''), str) or len(read.get('visible_text', '')) > 1600:
            raise Conflict('Screenshot transcription exceeds the visible-text bound')
        positioned = read.get('items')
        if positioned is not None:
            item_schema = schema({'text': TEXT, 'box': {'type': 'array', 'minItems': 4, 'maxItems': 4,
                'items': {'type': 'number', 'minimum': 0, 'maximum': 1}}})
            Draft202012Validator({'type': 'array', 'maxItems': 100, 'items': item_schema}).validate(positioned)
            if any(i['box'][0] > i['box'][2] or i['box'][1] > i['box'][3] for i in positioned):
                raise Conflict('Screenshot position box is reversed')
        return self._record('read_screenshot', {'status': 'AVAILABLE', 'image_id': image_id,
            'image_sha256': read['image_sha256'], 'receipt_id': read['receipt_id'],
            'visible_text': read.get('visible_text', ''), 'items': copy.deepcopy(positioned),
            'positions_status': 'AVAILABLE' if positioned is not None else 'UNAVAILABLE_FROM_TRANSCRIPTION',
            'interpretation_verified': False, 'scope_authority': 'VISIBLE_PIXELS_ONLY; hidden filters, RLS and cause not established'})

    def _question(self, kind, text, choices=None, grounding=None, catalog=None):
        if self.comment_port is None:
            return self._record(kind, {'status': 'UNAVAILABLE', 'reason': 'TICKET_COMMENT_PORT_UNAVAILABLE'})
        posted = self.comment_port({'actor': 'AGENT', 'kind': kind, 'question': text, 'choices': choices or []})
        if not isinstance(posted, dict) or not posted.get('comment_id'):
            raise Conflict('Question was not retained in the ticket thread')
        return self._record(kind, {'status': 'WAITING_FOR_USER', 'comment_id': posted['comment_id'],
            'question': text, 'choices': choices or [], 'answer': None, **({'grounding':grounding} if grounding else {})}, catalog)

    def ask_user(self, field=None, report_id=None, page_id=None, question=None, choices=None):
        from .intake_span_references import enabled
        if not enabled():return self._question('ask_user',question,choices)
        if question is not None or choices is not None:raise Conflict('Ungrounded model-written question refused')
        from .clarification_grounding import render
        catalog=self._catalog();rendered=render(field,catalog,self._fixed,report_id,page_id)
        return self._question('ask_user',rendered['question'],rendered['choices'],rendered['grounding'],catalog)

    def request_screenshot(self, what=None):
        from .intake_span_references import enabled
        if not enabled():return self._question('request_screenshot',what)
        if what is not None:raise Conflict('Ungrounded screenshot request refused')
        return self._question('request_screenshot','Please share a screenshot of the visual and its visible selections.')
