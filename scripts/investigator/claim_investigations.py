"""Once-only execution of retained, explicitly confirmed business claims.

The request selects a saved claim, never a query, route, field or scope. Each
admitted check uses the ordinary AdaptiveRuntime session and read governor.
"""
import copy
import json
import re
from .onboarding import Conflict, digest, encoded
from .process_tape import event
from .run_recording import operation


class ClaimInvestigations:
    def __init__(self, workspace):
        self.workspace = workspace
        self.store = workspace.store
        with self.store.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS claim_investigations(
                claim_id TEXT PRIMARY KEY, request_key TEXT UNIQUE,
                request_hash TEXT, confirmed_hash TEXT, body TEXT, body_hash TEXT)''')
            db.execute('''CREATE TABLE IF NOT EXISTS claim_execution_failures(
                claim_id TEXT, phase TEXT, body TEXT, body_hash TEXT,
                PRIMARY KEY(claim_id,phase))''')

    def _failure(self, identity, phase, exc):
        from .process_failure import capture
        detail = capture(exc)
        reference = 'claim-failure:' + digest({'claim_id': identity, 'phase': phase, 'failure': detail})
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT INTO claim_execution_failures VALUES(?,?,?,?)',
                       (identity, phase, encoded(detail), digest(detail)))
        event('CONFIGURATION', {'claim_execution_failure': phase, 'claim_id': identity,
                                'evidence_id': reference, 'failure': detail})
        return {'type': detail['error_type'], 'evidence_id': reference}

    def _load(self, db, identity):
        row = db.execute('SELECT body,body_hash FROM claim_investigations WHERE claim_id=?',
                         (identity,)).fetchone()
        if row is None:
            return None
        body = json.loads(row[0])
        if digest(body) != row[1] or body['claim_id'] != identity:
            raise Conflict('Claim investigation integrity differs')
        return body

    def _save(self, db, body):
        event('CONFIGURATION', {'claim_investigation': 'STATE', 'body': body})
        db.execute('UPDATE claim_investigations SET body=?,body_hash=? WHERE claim_id=?',
                   (encoded(body), digest(body), body['claim_id']))

    def get(self, identity):
        with self.store.connect() as db:
            body = self._load(db, identity)
        if body is None:
            raise KeyError('Claim investigation not found')
        return copy.deepcopy(body)

    def _confirmed(self, request):
        intake = self.workspace.claims
        intake._guard()
        with self.store.connect() as db:
            revision, body = intake._load(db, request['id'])
        if revision != request['revision']:
            raise Conflict('Claim revision changed')
        confirmation = body.get('confirmation')
        plan = body.get('engine_admission') or {}
        if (body['status'] != 'CONFIRMED' or not confirmation
                or confirmation.get('authority') != 'USER_CONFIRMED'
                or plan.get('claim_hash') != digest(body['claim'])
                or plan.get('confirmation_hash') != digest(confirmation)
                or confirmation.get('interpretation_hash') != digest(body.get('interpretation'))):
            raise Conflict('A retained user-confirmed interpretation is required')
        accepted = [d for d in body.get('documents', [])
                    if d.get('hash') == confirmation.get('request_hash')
                    and digest(d.get('request')) == d.get('hash')
                    and d['request'].get('accepted') is True]
        if len(accepted) != 1:
            raise Conflict('Retained confirmation request is missing or ambiguous')
        return body

    def _current(self, body):
        """Re-resolve the same referent, keeping the original pin untouched."""
        from . import claim_clarification as policy
        catalog = self.workspace.claims._catalog()
        claim = copy.deepcopy(body['claim'])
        binding = claim.get('selected_binding') or {}
        bindings = binding.get('bindings', []) if binding.get('kind') == 'MULTIPLE' else [binding]
        for target in bindings:
            if not target:
                continue
            models = [m for m in catalog['models'] if m['id'] == target.get('model_id')]
            if len(models) != 1:
                return None, 'CONFIRMED_TARGET_UNAVAILABLE'
            model = models[0]
            if target.get('measure_id') and target['measure_id'] not in {m['id'] for m in model.get('measures', [])}:
                return None, 'CONFIRMED_TARGET_UNAVAILABLE'
            if target.get('measure_id'):
                target['label'] = next(m['name'] for m in model['measures'] if m['id'] == target['measure_id'])
            if any(t not in {v['target_id'] for v in model.get('visuals', [])}
                   for t in target.get('target_ids', [])):
                return None, 'CONFIRMED_TARGET_UNAVAILABLE'
        if binding.get('kind') == 'MULTIPLE':
            binding['label'] = ', '.join(t['label'] for t in bindings)
        try:
            rendered = policy.interpretation(claim, catalog)
        except (ValueError, KeyError):
            return None, 'CONFIRMED_SCOPE_UNAVAILABLE'
        if digest(rendered) != body['confirmation']['interpretation_hash']:
            return None, 'INTERPRETATION_RECONFIRMATION_REQUIRED'
        return catalog, None

    def _prepare(self, body):
        settled = body['claim']['settled']
        scope = settled.get('scope') or {}
        direction = settled.get('direction')
        captured = body.get('captured_context')
        if captured and (captured.get('visible_filter_scope') or {}).get('status') != 'COMPILED':
            return {'status': 'HELD', 'reason': 'SCREENSHOT_SCOPE_NOT_COMPILED',
                    'limitations': ['The screenshot establishes visible context, not an admitted unfiltered or security scope.']}, None
        if direction == 'DEFINITION':
            return {'status': 'HELD', 'reason': 'LEGACY_ROUTE_ADMISSION_UNAVAILABLE',
                    'limitations': ['A definition or business-rule question requires its existing faithful definition/handoff route, not a page-value comparison.']}, None
        if direction not in ('LESS', 'MORE', 'DIFFERENT', 'STALE', 'FIELD_WRONG', 'WRONG_BREAKDOWN'):
            return {'status': 'HELD', 'reason': 'UNIMPLEMENTED_CLAIM_ROUTE',
                    'limitations': ['This question kind has no admitted claim check; a different question was not substituted.']}, None
        if (direction == 'STALE' or direction not in ('FIELD_WRONG', 'WRONG_BREAKDOWN')
                and (scope.get('kind') in ('PAGE', 'REPORT') or len(scope.get('visual_ids', [])) > 1)):
            from .page_investigations import PageInvestigations
            service = PageInvestigations(self.workspace)
            kind = 'PAGE_FRESHNESS' if direction == 'STALE' else 'PAGE_CONSISTENCY'
            prepared = service.prepare(body, kind=kind)
            return prepared, lambda adapter: (service.freshness(body, adapter)
                                              if kind == 'PAGE_FRESHNESS' else service.consistency(body, adapter))
        if direction == 'FIELD_WRONG':
            kind = 'RECORD_VALUE'
        elif direction == 'WRONG_BREAKDOWN':
            kind = 'DECOMPOSITION'
        elif scope.get('kind') == 'RECORDS' and direction in ('LESS', 'DIFFERENT', 'MORE'):
            kind = 'MULTIPLICITY' if direction == 'MORE' else 'SET_RECONCILIATION'
        else:
            from .claim_reference import compile as compile_claim_reference
            try:
                compiled=compile_claim_reference(body,self.workspace.claims._catalog())
            except Conflict:
                return {'status': 'HELD', 'reason': 'LEGACY_ROUTE_ADMISSION_UNAVAILABLE',
                        'limitations': ['This claim cannot be faithfully admitted as one ungrouped visual without changing its confirmed scope.']}, None
            binding=body['claim']['selected_binding']
            return {'status':'PLANNED','kind':'CONFIRMED_LEGACY_VISUAL',
                'model_id':binding['model_id'],'measure_ids':[binding['measure_id']],
                'compiled_reference':compiled,'limitations':[]}, None
        from .claim_projection import validate_request
        if scope.get('kind') != 'RECORDS' or scope.get('visual_ids'):
            return {'status': 'HELD', 'reason': 'VISUAL_PROJECTION_SCOPE_UNSUPPORTED',
                    'limitations': ['The selected visual or page restrictions have not been compiled into an equivalent record projection.']}, None
        if settled.get('time') or settled.get('filters'):
            return {'status': 'HELD', 'reason': 'CLAIM_SCOPE_NOT_COMPILED',
                    'limitations': ['The supplied time or filter scope cannot be silently removed.']}, None
        binding = body['claim'].get('selected_binding') or {}
        if binding.get('kind') == 'MULTIPLE' or not binding.get('model_id') or not binding.get('measure_id'):
            return {'status': 'HELD', 'reason': 'CLAIM_MULTI_MODEL_OR_METRIC_UNSUPPORTED', 'limitations': []}, None
        keys = []
        for example in settled.get('examples', []):
            values = example if isinstance(example, list) else [example]
            for value in values:
                # A submitted integral key is exactly representable; prose,
                # decimals, booleans and nested structures are never guessed.
                keys.append(str(value) if type(value) is int else copy.deepcopy(value))
        # Example prose is not a key compiler. Only the explicit exact key form
        # is admitted; the adapter independently verifies its native key mapping.
        request = {'kind': kind, 'keys': copy.deepcopy(keys)}
        if kind == 'RECORD_VALUE':
            request['field_id'] = scope.get('field_id')
        if kind == 'DECOMPOSITION':
            request['dimension_id'] = scope.get('dimension_id')
            request['measure_id'] = binding['measure_id']
        try:
            validate_request(request)
        except (ValueError, KeyError, TypeError) as exc:
            failure = self._failure(body['id'], 'PREPARATION', exc)
            return {'status': 'HELD', 'reason': 'CLAIM_PROJECTION_REQUEST_UNRESOLVED',
                    'failure': failure,
                    'limitations': ['The confirmed claim lacks an exact supported key or field/dimension binding.']}, None
        prepared = {'status': 'PLANNED', 'model_id': binding['model_id'],
                    'measure_ids': [binding['measure_id']], 'scope': {}, 'request': request,
                    'limitations': []}
        return prepared, lambda adapter: self._projection(adapter, request, binding['measure_id'])

    def _projection(self, adapter, request, measure_id):
        from .claim_projection import reduce
        path = adapter.resolve_path(measure_id)
        observations, unavailable, expected_requests = [], [], {}
        for layer in path.get('layers', []):
            contract = adapter.claim_probe_contract(path, layer, request, {})
            if contract.get('status') != 'COMPILED':
                unavailable.append({'layer': layer['id'], 'reason': contract.get('reason') or 'Projection mapping unavailable'})
                continue
            expected_requests[layer['id']] = contract
            try:
                answer = adapter.claim_probe(path, layer, request, {})
            except Exception as exc:
                from .usage_governance import UsageHold
                if not isinstance(exc, UsageHold):
                    raise
                remaining = path['layers'][path['layers'].index(layer):]
                unavailable.extend({'layer': rest['id'], 'reason': 'Diagnostic budget or deadline exhausted'} for rest in remaining)
                break
            if answer.get('status') == 'OBSERVED':
                observations.append(answer['evidence'])
            else:
                unavailable.append({'layer': layer['id'], 'reason': answer.get('reason') or 'Projection unavailable'})
        result = reduce(self.store, adapter.model['id'], path, request, observations, unavailable,
                        expected_requests=expected_requests)
        declared = {row['asset_id']: row for row in adapter.config.get('_estate', {}).get('layers', [])}
        role_defaults = {'presentation': 'report calculation',
                         'declared_source': 'declared source',
                         'application_quantity': 'declared application'}
        display = {}
        for layer in path['layers']:
            default_name = role_defaults.get(layer.get('kind'), 'the next declared layer')
            declaration = declared.get(layer['id'], {})
            role = declaration.get('role', 'UNDECLARED')
            proof_source = (layer.get('copy_mapping_proof') or {}).get('source', {})
            if proof_source.get('id') == layer['id']:
                default_name = 'declared application'
            display[layer['id']] = {'role': role, 'name': declaration.get('business_name', default_name)}
        result['display_layers'] = display
        from .model_context import assets
        semantic_columns = {column['id']: column.get('name') for column in assets(adapter.model['context'])
                            if column.get('kind') == 'SemanticColumn'}
        field_name = semantic_columns.get(request.get('field_id'), 'field')
        dimension_name = semantic_columns.get(request.get('dimension_id'), 'group')
        business, technical = [], []
        for observed in result.get('observations', []):
            label = display[observed['layer']]
            actual = observed['facts']
            counts = actual.get('global_counts')
            if counts:
                sentence = (label['name'] + ' has ' + str(counts['row_count']) + ' rows and '
                            + str(counts['distinct_nonnull_keys']) + ' distinct nonblank declared keys; '
                            + str(counts['duplicate_nonnull_rows']) + ' rows repeat those keys and '
                            + str(counts['null_key_rows']) + ' rows have blank keys.')
                business.append(sentence)
                technical.append(label['role'] + ': ' + sentence)
            for record in actual.get('records', []):
                sentence = ('Record ' + record['key'] + ' has ' + str(record['count']) + ' rows in ' + label['name'] + '.')
                if record.get('value_state') == 'OBSERVED':
                    value = record['value']
                    rendered = 'blank' if value['type'] == 'blank' else str(value['value'])
                    sentence += ' The checked ' + field_name + ' is ' + rendered + '.'
                elif record.get('value_state') == 'AMBIGUOUS_DUPLICATE_KEY':
                    sentence += ' A single field value cannot be selected because the key is repeated.'
                business.append(sentence)
                technical.append(label['role'] + ': ' + sentence)
            for group in actual.get('groups', []):
                # Groups are typed integral/blank by the reducer; no raw JSON.
                value = group.get('group_value', group.get('group'))
                if isinstance(value, dict):
                    group_name = 'blank' if value['type'] == 'blank' else str(value['value'])
                else:
                    group_name = str(value)
                quantity = group.get('quantity', {})
                total = 'blank' if quantity.get('type') == 'blank' else str(quantity.get('value'))
                sentence = dimension_name + ' ' + group_name + ' totals ' + total + ' in ' + label['name'] + '.'
                business.append(sentence); technical.append(label['role'] + ': ' + sentence)
        for transition in result.get('key_transitions', []):
            lower, upper = display[transition['input']], display[transition['output']]
            key = transition['key']
            kind = transition['kind']
            if kind == 'NOT_COMPARABLE':
                sentence = 'The field comparison for record ' + key + ' between ' + lower['name'] + ' and ' + upper['name'] + ' is not comparable.'
            elif kind == 'UNCHANGED':
                sentence = 'The checked record ' + key + ' result agrees between ' + lower['name'] + ' and ' + upper['name'] + '.'
            else:
                change = {'APPEARED': 'appearance', 'DISAPPEARED': 'disappearance',
                          'COUNT_CHANGED': 'row-count change', 'VALUE_CHANGED': 'field-value change'}[kind]
                sentence = ('The ' + ('first observed ' if transition['first_change_established'] else 'observed ')
                            + change + ' for record ' + key + ' is between ' + lower['name'] + ' and ' + upper['name'] + '.')
            business.append(sentence)
            technical.append(lower['role'] + ' to ' + upper['role'] + ': ' + sentence)
        for boundary in ([] if result.get('key_transitions') else result.get('boundaries', [])):
            lower, upper = display[boundary['input']], display[boundary['output']]
            if boundary['agrees'] is None:
                sentence = 'The field comparison between ' + lower['name'] + ' and ' + upper['name'] + ' is not comparable.'
                business.append(sentence)
            elif boundary['first_change_established']:
                sentence = 'The first observed change is between ' + lower['name'] + ' and ' + upper['name'] + '.'
                business.append(sentence)
            else:
                sentence = ('The checked results ' + ('agree' if boundary['agrees'] else 'differ')
                            + ' between ' + lower['name'] + ' and ' + upper['name'] + '.')
                business.append(sentence)
            technical.append(lower['role'] + ' to ' + upper['role'] + ': ' + sentence)
        if result.get('missing_layers'):
            names = [display[row['layer']]['name'] for row in result['missing_layers']]
            business.append('No completed comparable check was obtained for ' + ', '.join(names) + '.')
        for gap in result.get('comparison_gaps', []):
            if gap.get('reason') and gap['reason'] not in business:
                business.append(gap['reason'])
        result['business_summary'] = ' '.join(business) or 'No completed comparable data check was obtained.'
        result['technical_summary'] = ' '.join(technical) or result['business_summary']
        return result

    def _envelope(self, prepared, body):
        from .process_debugging import VERSION
        model = self.store.get(prepared['model_id'])
        measures = prepared.get('measure_ids') or []
        if not measures:
            raise ValueError('An actual admitted measure is required')
        configured = self.workspace.agent.config.get('_estate', {}).get('budgets', {})
        cap = min(12, configured.get('diagnostic_reads_per_run', 12),
                  getattr(self.workspace, 'dynamic_read_limit', 12))
        wall = min(900, self.workspace.agent.config.get('_estate', {}).get('investigation', {}).get('wall_seconds', 900))
        return {'model_id': model['id'], 'revision': model['revision'], 'context_id': model['context_id'],
                'measure_id': measures[0], 'filters': [], 'dimension_ids': [], 'source_tests': [],
                'source_selection': 'reviewed_mappings', 'strategy': VERSION,
                'symptom': 'Owner-confirmed business claim; the full interpretation and fact hashes are retained.',
                'limits': {'cloud_calls': cap, 'planner_calls': 1, 'wall_seconds': wall,
                           'input_characters': 32000, 'max_depth': 0}}

    @staticmethod
    def _limits(checks, limits):
        """Carry each receipt's actual attestation gaps across every route."""
        retained = copy.deepcopy(limits)
        for entry in checks.get('evidence', []) + checks.get('observations', []):
            identity = entry.get('id', entry.get('evidence_id'))
            attestation = entry.get('attestation', entry.get('surface_attestation')) or {}
            fields = attestation.get('unattested_fields', [])
            if fields and isinstance(identity, str):
                sentence = ('Surface fields not self-reported for receipt ' + identity + ': '
                            + ', '.join(sorted(set(fields))) + '.')
                if sentence not in retained:
                    retained.append(sentence)
        return retained

    @staticmethod
    def _held_reason(checks):
        if checks.get('reason'):
            return checks['reason']
        reasons = {row['reason'] for row in checks.get('comparisons', [])
                   if row.get('outcome') == 'NOT_COMPARABLE' and row.get('reason')}
        if len(reasons) == 1:
            return next(iter(reasons))
        if len(reasons) > 1:
            return 'MULTIPLE_COMPARISON_GAPS'
        if checks.get('missing_layers'):
            return 'LAYER_EVIDENCE_UNAVAILABLE'
        if checks.get('comparison_gaps'):
            return 'COMPARISON_EVIDENCE_UNAVAILABLE'
        return checks.get('outcome') or checks.get('status') or 'REQUIRED_EVIDENCE_UNAVAILABLE'

    @staticmethod
    def _action(checks, status, reason):
        """Consumer-owned next step; no action confers a cause or a grant."""
        if reason == 'DIFFERENT_DECLARED_RESTRICTIONS':
            return ('Ask the report owner whether these visuals should use the same restrictions; '
                    'compare matching declared scope before diagnosing a pipeline defect.')
        if reason in ('CONFIRMED_TARGET_UNAVAILABLE', 'CONFIRMED_SCOPE_UNAVAILABLE',
                      'INTERPRETATION_RECONFIRMATION_REQUIRED'):
            return 'Confirm the current target and interpretation before another investigation.'
        if reason in ('SCREENSHOT_SCOPE_NOT_COMPILED', 'SCREENSHOT_FILTER_SCOPE_NOT_COMPILED',
                      'CLAIM_SCOPE_NOT_COMPILED', 'VISUAL_PROJECTION_SCOPE_UNSUPPORTED'):
            return 'Ask the report owner to establish the missing filter and security scope before comparing the data.'
        if checks.get('kind') == 'PAGE_FRESHNESS':
            return ('Ask the report and pipeline owners to review the retained refresh and load times '
                    'and supply any missing timing evidence; current freshness has not been established.')
        if checks.get('missing_layers') or status == 'HELD':
            return 'Ask the relevant owner for the missing scope or evidence, then reassess the confirmed request.'
        if checks.get('status') == 'OBSERVED_DIFFERENCE':
            return ('Ask the owner of the observed boundary to review its declared operation; '
                    'the observed change does not establish its cause or whether it is wrong.')
        return ('Review the bounded findings and their limits with the report or application owner; '
                'agreement alone does not establish business correctness.')

    @staticmethod
    def _prose(checks, status, reason, limits):
        limits = ClaimInvestigations._limits(checks, limits)
        summary = checks.get('business_summary', checks.get('summary'))
        if not isinstance(summary, str) or not summary:
            summary = ('The requested check could not be completed under the confirmed scope.'
                       if status == 'HELD' else
                       'The bounded checks are retained. Observed differences alone do not establish a data defect.')
        evidence = checks.get('evidence', [])
        ids = [e['id'] for e in evidence if isinstance(e, dict) and e.get('id')]
        ids += [o['evidence_id'] for o in checks.get('observations', []) if o.get('evidence_id')]
        ids = list(dict.fromkeys(ids))
        technical_summary = checks.get('technical_summary', summary)
        if not isinstance(technical_summary, str):
            raise ValueError('Claim technical narrative requires plain text')
        technical = technical_summary + (' Evidence receipts: ' + ', '.join(ids) + '.' if ids else
                               ' No usable data evidence was established by this check.')
        if any(re.search(r'\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b', value, re.I)
               for value in (summary, technical_summary)):
            raise ValueError('Claim explanation cannot use internal asset identifiers')
        if any(value.lstrip().startswith(('{', '[')) for value in (summary, technical_summary)):
            raise ValueError('Claim explanation cannot substitute a serialized structure')
        limit_text, technical_limits = [], []
        for limit in limits:
            if isinstance(limit, str):
                if limit.startswith('SNAPSHOT_UNVERIFIED'):
                    limit_text.append('The checks may describe different moments; timing has not been ruled out.')
                    technical_limits.append('SNAPSHOT_UNVERIFIED: query-bound served versions were not aligned; timing was not excluded.')
                elif limit.startswith('Surface fields not self-reported for receipt '):
                    limit_text.append('The reader did not self-report all connection properties; the exact attestation limits are retained.')
                    technical_limits.append(limit.rstrip('.') + '.')
                elif re.fullmatch(r'[A-Z_]+', limit):
                    limit_text.append('Some requested comparisons were not established.')
                else:
                    limit_text.append(limit.rstrip('.') + '.')
                    technical_limits.append(limit.rstrip('.') + '.')
        if checks.get('snapshot_status') == 'SNAPSHOT_UNVERIFIED' and not any('timing' in t.lower() for t in limit_text):
            limit_text.append('The checks may describe different moments; timing has not been ruled out.')
        if limit_text:
            suffix = ' Limits: ' + ' '.join(dict.fromkeys(limit_text))
            summary += suffix
            technical += ' Limits: ' + ' '.join(dict.fromkeys(technical_limits or limit_text))
        action = ' Recommended action: ' + ClaimInvestigations._action(checks, status, reason)
        summary += action
        technical += action
        return {'business_explanation': summary, 'technical_narrative': technical}

    @operation('claim_run')
    def run(self, request):
        if not isinstance(request, dict) or set(request) != {'id', 'revision', 'request_key'}:
            raise ValueError('Claim execution accepts only a retained claim reference')
        if (not isinstance(request['id'], str) or type(request['revision']) is not int
                or not isinstance(request['request_key'], str) or not 1 <= len(request['request_key']) <= 100):
            raise ValueError('Claim execution reference is invalid')
        if not getattr(self.workspace, 'execution_enabled', False):
            raise Conflict('Investigation execution is disabled')
        claim = self._confirmed(request)
        identity = request['id']
        claim_hash = digest(claim['claim'])
        confirmation_hash = digest(claim['confirmation'])
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current_revision, current_claim = self.workspace.claims._load(db, identity)
            if current_revision != request['revision'] or digest(current_claim) != digest(claim):
                raise Conflict('Claim changed before execution admission')
            prior = self._load(db, identity)
            if prior:
                row = db.execute('SELECT request_hash FROM claim_investigations WHERE claim_id=?', (identity,)).fetchone()
                if row[0] != digest(request):
                    raise Conflict('This confirmed claim already has an execution admission')
                return copy.deepcopy(prior)
            result = {'claim_id': identity, 'status': 'RUNNING', 'reason': None, 'outputs': None,
                      'session_id': None, 'checks': {}, 'limits': [], 'reads': {},
                      'confirmed_claim_hash': claim_hash, 'confirmation_hash': confirmation_hash}
            db.execute('INSERT INTO claim_investigations VALUES(?,?,?,?,?,?)',
                       (identity, request['request_key'], digest(request), claim_hash, encoded(result), digest(result)))
            self._save(db, result)
        session = None
        stop_error = None
        try:
            catalog, reason = self._current(claim)
            if reason:
                prepared, execute = {'status': 'HELD', 'reason': reason, 'limitations': []}, None
            else:
                prepared, execute = self._prepare(claim)
                result['catalog_revalidation'] = {'recorded_catalog_hash': claim['catalog_hash'],
                                                   'current_catalog_hash': digest(catalog)}
            if prepared['status'] != 'PLANNED':
                checks = prepared
            else:
                envelope = self._envelope(prepared, claim)
                legacy=prepared.get('kind')=='CONFIRMED_LEGACY_VISUAL'
                if legacy:
                    compiled=prepared['compiled_reference']
                    envelope.update({k:copy.deepcopy(compiled[k]) for k in ('target_visual','report_binding','reported_figure')})
                    envelope.update(ticket_shape='MISMATCH_COMPLAINT',comparison_mode='VERTICAL')
                    session=self.workspace.agent.create(envelope,'confirmed-visual:'+identity)
                else:
                    session = self.workspace.agent.begin_claim_process(envelope, 'claim:' + identity,
                        claim_hash=claim_hash, confirmation_hash=confirmation_hash)
                result['session_id'] = session['id']
                with self.store.connect() as db:
                    db.execute('BEGIN IMMEDIATE'); self._save(db, result)
                if legacy:
                    self.workspace.agent.run_process(session['id'])
                    self.workspace.agent.synthesize(session['id'])
                    from .ticket_findings import from_state
                    finding=from_state(self.workspace.agent.get(session['id']))
                    checks={'status':'HELD'if finding['classification']=='HELD'else'COMPLETED','validated_findings':finding,
                        'observations':finding['observations'],'limits':finding['assessment'].get('limits',[]) if finding['assessment'] else []}
                    result['classification']=finding['classification']
                else:
                    adapter = self.workspace.agent.process_adapter(session['id'])
                    checks = execute(adapter)
            result['checks'] = checks
            if checks.get('cause_verified') is True or checks.get('defect_established') is True:
                raise ValueError('CLAIM_CAUSAL_PROOF_NOT_ESTABLISHED')
            if checks.get('status') not in ('HELD', 'UNAVAILABLE', 'NOT_COMPARABLE', 'PARTIAL',
                                          'COMPLETED', 'OBSERVED', 'OBSERVED_EQUAL', 'OBSERVED_DIFFERENCE'):
                raise ValueError('CLAIM_CHECK_STATUS_UNRECOGNIZED')
            result['status'] = ('HELD' if checks['status'] in ('HELD', 'UNAVAILABLE', 'NOT_COMPARABLE')
                                else 'PARTIAL' if checks['status'] == 'PARTIAL' else 'COMPLETED')
            result['reason'] = self._held_reason(checks) if result['status'] == 'HELD' else checks.get('reason')
            result['limits'] = self._limits(checks, checks.get('limitations', checks.get('limits', [])))
        except Exception as exc:
            result.update(status='HELD', reason='CLAIM_EXECUTION_FAILED',
                          failure=self._failure(identity, 'EXECUTION', exc))
            result['limits'] = ['The check stopped; any earlier metered read receipts remain retained.']
            from .model_spend import SpendHold
            provider_error = type(exc).__module__.startswith('openai')
            if isinstance(exc, SpendHold) or provider_error and (
                    getattr(exc, 'status_code', None) in (401, 402, 403)
                    or getattr(exc, 'code', None) == 'insufficient_quota'):
                stop_error = exc
        finally:
            try:
                finding=result['checks'].get('validated_findings')
                if finding:
                    result['outputs']={'business_explanation':finding['outputs']['business_output']['explanation']['text'],
                        'technical_narrative':finding['outputs']['technical_output']['explanation']['text']}
                else:
                    result['outputs'] = self._prose(result['checks'], result['status'], result['reason'], result['limits'])
            except (ValueError, TypeError, KeyError) as exc:
                result.update(status='HELD', reason='CLAIM_OUTPUT_VALIDATION_FAILED')
                result['output_failure'] = self._failure(identity, 'OUTPUT', exc)
                result['outputs'] = self._prose({}, 'HELD', result['reason'], result['limits'])
            context = claim['interpretation']['text'].removesuffix('Is this interpretation correct?').strip()
            ending = {'HELD':'The request remains unresolved.',
                      'PARTIAL':'Only part of the request was checked.',
                      'COMPLETED':'The bounded checks completed.'}[result['status']]
            for key in result['outputs']:
                result['outputs'][key] = 'Confirmed request: ' + context + ' ' + ending + ' ' + result['outputs'][key]
            if session:
                try:
                    if prepared.get('kind')=='CONFIRMED_LEGACY_VISUAL':
                        final=self.workspace.agent.get(session['id'])
                    else:
                        final = self.workspace.agent.finalize_claim_process(session['id'], result,
                            claim_hash=claim_hash, confirmation_hash=confirmation_hash)
                except Exception as exc:
                    result.update(status='HELD', reason='CLAIM_FINALIZATION_FAILED',
                                  finalization_failure=self._failure(identity, 'FINALIZATION', exc))
                    final = self.workspace.agent.get(session['id'])
                    result['outputs'] = self._prose({}, 'HELD', result['reason'],
                        ['The original read receipts were retained, but final result persistence failed.'])
                    for key in result['outputs']:
                        result['outputs'][key] = 'Confirmed request: ' + context + ' The request remains unresolved. ' + result['outputs'][key]
                result['reads'] = {'diagnostic': final['cloud_calls'], 'physical': final.get('physical_calls', 0),
                                   'receipts': copy.deepcopy(final.get('process_read_receipts', []))}
            with self.store.connect() as db:
                db.execute('BEGIN IMMEDIATE'); self._save(db, result)
        if stop_error:
            raise stop_error
        # Optional handoff is a separate, once-only phase. It cannot replace
        # these retained receipts, checked outcome or original outputs.
        from .claim_handoff import maybe
        handoff = maybe(self.workspace, claim, result)
        if handoff is not None:
            result['automatic_handoff'] = handoff
            with self.store.connect() as db:
                db.execute('BEGIN IMMEDIATE'); self._save(db, result)
        return copy.deepcopy(result)
