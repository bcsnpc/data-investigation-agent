"""Agent-provided spans through the existing intake admission and preview gates.

No provider is called here. The governing agent records its model call. Picked
form inputs are copied once, remain authority, and are never filled by search.
"""
import copy
from jsonschema import Draft202012Validator
from . import intake_extraction, question_intake, form_scope, question_kind
from .onboarding import Conflict, digest, encoded

SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'extraction': copy.deepcopy(intake_extraction.SCHEMA)}, 'required': ['extraction']}
DESCRIPTION = 'Resolve your verbatim ticket span extraction against retained definitions and immutable picked form facts. Every quote, including comparisons, must occur exactly in the ticket text; fixed comparison enums are not ticket quotes. Code validates referent, scope, figure precision and comparison. An admitted result supplies target_registry and scope_registry: use those IDs for investigation tools, not the original visual ID. Returns an admitted preview or explicit refusal, never starts a read or calls another model.'

class Settlement:
    def __init__(self, workspace, *, text, key_prefix, record_evidence,
                 form_request=None, input_request=None, candidate_binding=None, predecessor=None):
        if not callable(record_evidence) or not isinstance(key_prefix, str) or not 1 <= len(key_prefix) <= 30:
            raise ValueError('Agent settlement requires evidence persistence and bounded request identity')
        if form_request is not None and input_request is not None:
            raise ValueError('One immutable input authority required')
        self.workspace = workspace; self.text = text; self.key_prefix = key_prefix
        self.record_evidence = record_evidence
        self.form = copy.deepcopy(form_request); self.input = copy.deepcopy(input_request)
        self.binding = copy.deepcopy(candidate_binding)
        self.predecessor = predecessor
        self.preview_id = None
        self._admitted_result = None
        self._admitted_request_hash = None
        self._admitted_catalog_hash = None

    def _record(self, body):
        identity = self.record_evidence(copy.deepcopy(body))
        if not isinstance(identity, str) or not identity: raise Conflict('Agent settlement evidence not retained')
        return {**body, 'evidence_ids': [identity], 'facade_evidence_id': identity, 'finding_authority': False}

    def resolve_ticket(self, extraction):
        Draft202012Validator(intake_extraction.SCHEMA).validate(extraction)
        workspace = self.workspace; catalog = question_intake.snapshot(workspace)
        request_hash = digest(extraction)
        if self._admitted_result is not None:
            if request_hash != self._admitted_request_hash or digest(catalog) != self._admitted_catalog_hash:
                raise Conflict('Agent admitted intake cannot be rebound; create an explicit revision')
            workspace.intake.review(self._admitted_result['intake_id'], {
                **{k: self._admitted_result['scope'][k] for k in ('model_id','measure_id','filters','dimension_ids')},
                'symptom': workspace.intake.get(self._admitted_result['intake_id'])['text'], 'predecessor': self.predecessor})
            return copy.deepcopy(self._admitted_result)
        self._current_request_hash = request_hash
        payload = {'text': self.text, 'models': catalog['models']}
        if self.form is not None:
            doc = form_scope.document(self.form, workspace.intake_configuration)
            if self.form['description']:
                part = next(p for p in doc['parts'] if p['pointer'] == '/description')
                payload.update(text=doc['text'][:part['end']], _form_description_input=self.form,
                    _form_configuration=workspace.intake_configuration,
                    _form_description_candidate_binding=self.binding)
            else:
                # A complete, empty-description form needs no invented sentence
                # or span extraction; its actual picked facts still pass form gates.
                return self._form_only(catalog)
        if self.input is not None:
            from .input_reference import preflight, from_input
            preflight(self.input)
            payload['_input_request'] = self.input
            reference = from_input(self.input, payload['text'], catalog['models'])
            if reference is not None: payload['_ticket_reference'] = reference
        try:
            proposal = intake_extraction.resolve(copy.deepcopy(extraction), payload)
            question_intake.validate(proposal, payload); question_kind.intake_route(proposal)
            if proposal.get('action') != 'PROPOSE':
                return self._record({'status': 'UNRESOLVED', 'proposal': proposal,
                    'catalog_hash': digest(catalog), 'target_selected': False})
            if self.form is not None:
                built = form_scope.build(self.form, catalog['models'], workspace.intake_configuration,
                    description_proposal=proposal, candidate_binding=self.binding)
                final = built['proposal']; text = built['document']['text']
                question_intake.validate(final, {'text': text, 'models': catalog['models'],
                    '_form_request': self.form, '_form_configuration': workspace.intake_configuration,
                    '_form_description': proposal, '_form_candidate_binding': self.binding})
            else: final, text = proposal, payload['text']
            return self._admit(catalog, final, text, proposal, extraction, payload)
        except (ValueError, Conflict) as error:
            return self._record({'status': 'UNRESOLVED', 'reason': str(error),
                'error_type': type(error).__name__, 'catalog_hash': digest(catalog), 'target_selected': False})

    def _form_only(self, catalog):
        built = form_scope.build(self.form, catalog['models'], self.workspace.intake_configuration,
            candidate_binding=self.binding)
        question_intake.validate(built['proposal'], {'text': built['document']['text'], 'models': catalog['models'],
            '_form_request': self.form, '_form_configuration': self.workspace.intake_configuration,
            '_form_description': None, '_form_candidate_binding': self.binding})
        return self._admit(catalog, built['proposal'], built['document']['text'], None, None, {})

    def _admit(self, catalog, final, text, description, raw, payload):
        workspace = self.workspace
        if digest(question_intake.snapshot(workspace)) != digest(catalog): raise Conflict('Agent settlement metadata changed')
        key = self.key_prefix + ':' + digest({'raw': raw, 'form': self.form, 'input': self.input})[:64]
        request = {'text': text, 'request_key': key, 'parent_id': None}
        controller = workspace.intake
        with workspace.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            prior = db.execute('SELECT id FROM workspace_intakes WHERE request_key=?', (key,)).fetchone()
            if prior: body = controller.get(prior[0])
            else:
                description_id = None
                if self.form is not None and description is not None:
                    desc_request = {**request, 'text': payload['text'], 'request_key': key + ':d'}
                    desc = controller._new_record(desc_request, payload['text'], catalog)
                    desc.update(status='PROPOSED', proposal=description, provider_calls=0,
                        scope_provenance='AGENT_VALIDATED_EXTRACTION', resolver_extraction=copy.deepcopy(raw),
                        form_description_only=True, form_description_input=copy.deepcopy(self.form))
                    db.execute('INSERT INTO workspace_intakes VALUES(?,?,?,?)', (desc['id'], desc_request['request_key'], encoded(desc), digest(desc)))
                    description_id = desc['id']
                body = controller._new_record(request, text, catalog)
                body.update(status='PROPOSED', proposal=final, provider_calls=0,
                    scope_provenance='AGENT_VALIDATED_EXTRACTION', resolver_extraction=copy.deepcopy(raw),
                    agent_input_authority_hash=digest({'form': self.form, 'input': self.input}))
                if self.predecessor is not None: body['agent_predecessor'] = self.predecessor
                if self.form is not None:
                    body.update(form_request=copy.deepcopy(self.form), form_description_intake=description_id,
                        form_candidate_binding=copy.deepcopy(self.binding))
                if self.input is not None: body['input_request'] = copy.deepcopy(self.input)
                db.execute('INSERT INTO workspace_intakes VALUES(?,?,?,?)', (body['id'], key, encoded(body), digest(body)))
        preview_request = {k: final[k] for k in ('model_id', 'measure_id', 'filters', 'dimension_ids')}
        preview_request.update(symptom=text, predecessor=self.predecessor, intake_id=body['id'])
        preview = workspace.preview(preview_request)
        self.preview_id = preview['id']
        result = self._record({'status': 'INTAKE_ADMITTED', 'intake_id': body['id'], 'preview_id': preview['id'],
            'model_id': final['model_id'], 'measure_id': final['measure_id'], 'scope': copy.deepcopy(final),
            'catalog_hash': digest(catalog), 'config_hash': body['config_hash'], 'engine_hash': body['engine_hash'],
            'data_queries': 0, 'provider_calls': 0})
        self._admitted_result = copy.deepcopy(result)
        self._admitted_request_hash = self._current_request_hash
        self._admitted_catalog_hash = digest(catalog)
        return result

    def start(self, *, controller_owned=False):
        """Controller-only normal start; not a model tool and not a read."""
        if self.preview_id is None: raise Conflict('Agent intake has no admitted preview')
        return self.workspace.start(self.preview_id, controller_owned=controller_owned) if controller_owned else self.workspace.start(self.preview_id)
