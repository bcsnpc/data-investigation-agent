"""Local exported execution over unchanged, retained Microsoft definitions.

The Microsoft adapter is used for metadata-only path resolution. All execution
is overridden here; there is no native transport or authentication fallback.
"""
import copy
import re
from ..model_context import assets
from ..onboarding import Conflict, digest
from ..process_debugging import Probe
from ..local_bundle import LocalBundle, UnsupportedLocalQuantity
from .microsoft_process import MicrosoftProcessAdapter

class LocalProcessAdapter:
    def __init__(self, store, config, model, bundle, *, record_evidence,
                 meter_read=None, judge_definition=None, max_boundaries=1):
        if not isinstance(bundle, LocalBundle) or not callable(record_evidence):
            raise ValueError('Pinned local bundle and evidence recorder required')
        contexts = bundle.manifest.get('contexts', [])
        expected = {'model_id': model.get('id'), 'context_id': model.get('context_id'),
                    'context_hash': digest(model.get('context')), 'revision': model.get('revision')}
        if [c for c in contexts if c.get('model_id') == model.get('id')] != [expected]:
            raise Conflict('LOCAL_MODEL_CONTEXT_PIN_MISMATCH')
        from ..context_search import latest
        enterprise = latest(store)
        pinned = bundle.manifest.get('enterprise_context')
        if not enterprise or not isinstance(pinned, dict) or set(pinned) != {'id', 'hash'}:
            raise Conflict('LOCAL_ENTERPRISE_CONTEXT_PIN_REQUIRED')
        body = dict(enterprise); identity = body.pop('version')
        if identity != pinned['id'] or digest(body) != pinned['hash']:
            raise Conflict('LOCAL_ENTERPRISE_CONTEXT_PIN_MISMATCH')
        if bundle.manifest.get('estate_manifest_hash') != config.get('_estate', {}).get('execution', {}).get('source_manifest_hash'):
            raise Conflict('LOCAL_ESTATE_MANIFEST_PIN_MISMATCH')
        self.store, self.config, self.model = store, config, model
        self.bundle, self.record_evidence, self.meter_read = bundle, record_evidence, meter_read
        self.metadata = MicrosoftProcessAdapter(store, config, model, self._deny, self._deny,
            judge_definition=judge_definition, max_boundaries=max_boundaries)
        self._declared_checks = {}
    @staticmethod
    def _deny(*args, **kwargs):
        raise Conflict('LOCAL_NATIVE_TRANSPORT_FORBIDDEN')
    def capabilities(self):
        result = {'resolve_measure_path', 'evaluate_scoped_quantity', 'declared_context_reproduction'}
        if self.metadata.judge_definition is not None: result.add('transformation_definition')
        return result
    def capability_gaps(self):
        return {'native_execution': 'LOCAL_EXPORTED; native engine semantics and source snapshot alignment are not established',
            'freshness': 'An immutable local copy is not live load history',
            'relationship_filters': 'Cross-table filters require a supported verified relationship plan; no local join inferred'}
    def resolve_path(self, measure_id):
        path = copy.deepcopy(self.metadata.resolve_path(measure_id))
        path['execution_mode'] = 'LOCAL_EXPORTED'; path['local_export_hash'] = self.bundle.manifest_sha256
        return path
    def report_catalog(self): return self.metadata.report_catalog()
    def transformation_definition(self, boundary): return self.metadata.transformation_definition(boundary)
    def declared_probe_cost(self, *args, **kwargs): return 1
    def declared_context(self, layer, measure_id, scope):
        from .report_predicates import extract, Refusal
        if layer.get('kind') != 'presentation': return {'status': 'UNDECLARED', 'reason': 'Presentation layer required'}
        try: declaration = extract(self.model, measure_id, scope)
        except Refusal as error: return {'status': 'UNDECLARED', 'reason': str(error), 'unsupported_form': error.form}
        self._declared_checks[measure_id] = declaration
        return declaration
    def declared_cells(self, layer, measure_id, scope):
        from .report_predicates import cells, Refusal
        if layer.get('kind') != 'presentation': return {'status': 'UNDECLARED', 'reason': 'Presentation layer required'}
        try: batch = cells(self.model, measure_id, scope)
        except Refusal as error: return {'status': 'UNDECLARED', 'reason': str(error), 'unsupported_form': error.form}
        for declaration in batch['cells']:
            self._declared_checks[(measure_id, declaration['cell']['id'])] = declaration
        return batch
    def evaluate_declared_context(self, layer, measure_id, scope):
        from ..declared_reproduction import compose
        from ..read_address import baseline, cell
        declaration = self._declared_checks.get((measure_id, scope['cell_id']) if 'cell_id' in scope else measure_id)
        if not declaration: raise Conflict('No pinned local declaration admitted')
        expected = {'restrictions', 'dimension_ids'} | ({'cell_id', 'probe_purpose'} if 'cell' in declaration else set())
        keys = declaration.get('cell', {}).get('key_restrictions', [])
        allowed = ([], compose(declaration['restrictions'] + keys))
        if (set(scope) != expected or scope['dimension_ids'] != [] or scope['restrictions'] not in allowed
            or ('cell' in declaration and scope['probe_purpose'] not in ('DECLARED_CONTEXT', 'UNDECLARED_CONTEXT'))):
            raise Conflict('Local reproduction scope differs from admitted declaration')
        address = cell(declaration['cell']) if scope.get('probe_purpose') == 'DECLARED_CONTEXT' else baseline(scope['restrictions'])
        return self._presentation(layer, measure_id, scope['restrictions'], address,
            {'definition_evidence_id': declaration['evidence']['id'], 'applied_restrictions': copy.deepcopy(scope['restrictions'])})
    def _semantic(self, measure_id):
        catalog = {a['id']: a for a in assets(self.model['context'])}
        measure = catalog.get(measure_id)
        if not measure or measure.get('kind') != 'Measure': raise UnsupportedLocalQuantity('Measure absent from retained definitions')
        expression = measure.get('metadata', {}).get('expression', '')
        if isinstance(expression, list): expression = '\n'.join(expression)
        match = re.fullmatch(r"\s*SUM\s*\(\s*(?:'((?:''|[^'])+)'|([A-Za-z_][\w]*))\s*\[((?:\]\]|[^\]])+)\]\s*\)\s*", expression, re.I)
        if not match: raise UnsupportedLocalQuantity('Unsupported local DAX: only direct additive SUM')
        table_name = (match.group(1) or match.group(2)).replace("''", "'"); column = match.group(3).replace(']]', ']')
        tables = [a for a in catalog.values() if a.get('kind') == 'SemanticTable' and a.get('name') == table_name and a['id'] == measure['parent_id']]
        if len(tables) != 1: raise UnsupportedLocalQuantity('Semantic table is not exactly bound')
        return tables[0]['id'], column, catalog
    def _presentation(self, layer, measure_id, restrictions, address, extra=None):
        try:
            table, column, catalog = self._semantic(measure_id)
            if layer['id'] != table: raise UnsupportedLocalQuantity('Presentation layer does not match measure table')
            translated = []
            for r in restrictions:
                c = catalog.get(r['field_id'])
                if not c or c.get('kind') != 'SemanticColumn' or c.get('parent_id') != table:
                    raise UnsupportedLocalQuantity('Cross-table or unresolved filter unsupported locally')
                translated.append({'column': c['name'], 'operator': r['operator'], 'values': r['values']})
            return self._read(layer, measure_id, table, column, translated, address, extra)
        except UnsupportedLocalQuantity as error:
            return Probe('NOT_COMPARABLE', layer['id'], reason=str(error))
    def evaluate(self, layer, measure_id, scope):
        from ..read_address import baseline
        if scope.get('dimension_ids'): return Probe('NOT_COMPARABLE', layer['id'], reason='Grouped local quantities not implemented')
        if layer['kind'] == 'presentation':
            restrictions = [{'field_id': f['column_id'], 'operator': 'IN', 'values': f['values']} for f in scope.get('filters', [])]
            return self._presentation(layer, measure_id, restrictions, baseline(restrictions))
        if scope.get('filters'): return Probe('NOT_COMPARABLE', layer['id'], reason='Lower filtered scope translation not implemented')
        if layer['kind'] == 'declared_source':
            compiled, reason = self.metadata._lower_quantity(layer, scope)
            if compiled is None: return Probe('NOT_COMPARABLE', layer['id'], reason=reason)
        elif layer['kind'] in ('declared_quantity', 'application_quantity'):
            compiled = layer.get('compiled')
            if not compiled or not layer.get('quantity_contract'): return Probe('NOT_COMPARABLE', layer['id'], reason='No verified additive column contract')
        else: return Probe('NOT_COMPARABLE', layer['id'], reason='Unsupported local layer kind')
        return self._read(layer, measure_id, layer['id'], compiled['source_column'], [], baseline([]), {
            'binding_provenance': 'DECLARED_BY_DEFINITION', 'quantity_contract': layer.get('quantity_contract'),
            'direct_source_proof': layer.get('direct_source_proof')})
    def _read(self, layer, measure_id, asset, column, restrictions, address, extra=None):
        from ..refresh_comparison import whole_entity_context
        def execute(): return self.bundle.quantity(asset, column, restrictions)
        try: result = self.meter_read('local_exported_quantity', execute) if self.meter_read else execute()
        except UnsupportedLocalQuantity as error: return Probe('NOT_COMPARABLE', layer['id'], reason=str(error))
        evidence = {**result, 'tool': 'local_exported_quantity', 'completeness': 'COMPLETE_RESPONSE',
            'request_hash': digest(result['plan']), 'measure_id': measure_id, 'dimension_id': None,
            'read_address': copy.deepcopy(address), 'values': [{'quantity': result['value']}],
            'declared_context': whole_entity_context() if not restrictions else None, **(extra or {})}
        identity = self.record_evidence(copy.deepcopy(evidence))
        if not isinstance(identity, str) or not identity: raise Conflict('Local quantity receipt not retained')
        evidence['id'] = identity
        surface = {'engine': 'SQLITE_LOCAL_COPY', 'connection': 'local-export:' + self.bundle.manifest_sha256,
            'object': asset, 'identity': 'LOCAL_IMMUTABLE_EXPORT_READER'}
        return Probe('OBSERVED', layer['id'], value={'quantity': result['value']}, evidence=evidence,
            execution_surface=surface, surface_report=dict(surface), surface_reportable=tuple(surface),
            surface_report_binding='VALUE_QUERY', surface_report_types={k: 'LOCAL_EXPORT_IDENTITY' for k in surface})


def create(store, config, model, *, record_evidence, meter_local_read=None, judge_definition=None, max_boundaries=1):
    execution = config.get('_estate', {}).get('execution', {})
    if execution.get('mode') != 'LOCAL_EXPORTED' or set(execution) != {'mode', 'bundle', 'manifest_sha256', 'source_manifest_hash'}:
        raise Conflict('Explicit pinned LOCAL_EXPORTED execution required')
    bundle = LocalBundle(execution['bundle'], execution['manifest_sha256'])
    return LocalProcessAdapter(store, config, model, bundle, record_evidence=record_evidence,
        meter_read=meter_local_read, judge_definition=judge_definition, max_boundaries=max_boundaries)
