"""Governed native filter probes with complete-key extraction and self-report.

Native compilation is supplied by the retained-definition adapter, independently
of the proposed query. No expression is sent directly to the transport. An empty
key set still returns one marked attestation row; that row is never a key.
"""
import copy
from decimal import Decimal
from .. import flexible_tools, query_dax, proposal_limits
from ..raw_surface_report import MAX_ROWS
from ..model_context import assets
from ..process_debugging import attest_surface
from .microsoft_process import SEMANTIC_REPORT, SEMANTIC_TYPES, SEMANTIC_ENGINE
from .microsoft_self_report import compose


class FilterRoute:
    def __init__(self, process, *, verification_meter, native_compiler=None):
        from .translation_filter_definition import compile_native
        self.process = process
        self.native_compiler = native_compiler or (lambda request, address: compile_native(process.model, request, address))
        # Explicit verification-class caller; never the process diagnostic meter.
        self.verification_meter = verification_meter

    def compile(self, proposal, side, request, address):
        from ..translation_proposer import validate
        validate(proposal, request)
        if request['context'] != self.process.model['context_id']:
            raise ValueError('Translation differs from pinned native context')
        if request['kind'] != 'FILTER' or request['target_engine'] != SEMANTIC_ENGINE:
            raise NotImplementedError('This route serves native filter key sets only')
        if side not in ('NATIVE', 'PROPOSED'): raise ValueError('Unknown translation side')
        columns = request['metadata']['native_key_columns']
        catalog = assets(self.process.model['context'])
        if not columns or len(columns) > 8 or len(columns) != len(set(columns)):
            raise ValueError('Native filter requires ordered discovered key columns')
        if any(not any(a['id'] == column and a['kind'] == 'SemanticColumn' for a in catalog) for column in columns):
            raise ValueError('Key column absent from pinned model')
        query = (self.native_compiler(copy.deepcopy(request), copy.deepcopy(address))
                 if side == 'NATIVE' else proposal['expression'])
        if side == 'PROPOSED' and not query.lstrip().upper().startswith('EVALUATE '):
            # The proposer supplies a predicate. The adapter owns the rowset,
            # discovered grouping and output labels on both sides.
            by_id = {a['id']: a for a in catalog}
            parents = {by_id[column]['parent_id'] for column in columns}
            if len(parents) != 1:
                raise NotImplementedError('Predicate keys span different tables')
            table = "'" + by_id[next(iter(parents))]['name'].replace("'", "''") + "'"
            fields = ','.join('"translation_key_' + str(i) + '",' + table + '[' +
                by_id[column]['name'].replace(']', ']]') + ']' for i,column in enumerate(columns))
            query = 'EVALUATE DISTINCT(SELECTCOLUMNS(FILTER(' + table + ',' + query + '),' + fields + '))'
        compiled = query_dax.compile_query(query, catalog)
        labels = ['translation_key_' + str(i) for i in range(len(columns))]
        if set(compiled['result_columns']) != set(labels):
            raise ValueError('Filter query must project exactly the declared key tuple')
        if side == 'PROPOSED' and set(compiled['asset_ids']) != {o['id'] for o in proposal['objects']}:
            raise ValueError('Proposed object list differs from compiler-resolved references')
        norm = request['metadata']['normalization']
        if (set(norm) != {'encoding', 'case_fold', 'trim'} or norm['encoding'] != 'typed-json-utf8'
                or type(norm['case_fold']) is not bool or type(norm['trim']) is not bool):
            raise NotImplementedError('Native key normalization declaration is unsupported')
        if not query.startswith('EVALUATE '): raise ValueError('Native query must have one EVALUATE')
        sentinel = ','.join('"' + label + '",BLANK()' for label in labels)
        query = 'EVALUATE UNION(ADDCOLUMNS(' + query.removeprefix('EVALUATE ') + \
            ',"translation_marker",FALSE()),ROW(' + sentinel + ',"translation_marker",TRUE()))'
        plan = {'model_id': self.process.model['id'], 'revision': self.process.model['revision'],
            'context_id': request['context'], 'query': compose(query),
            'max_rows': min(proposal_limits.QUERY_ROWS, MAX_ROWS) - 1,
            'surface_report': copy.deepcopy(SEMANTIC_REPORT), 'read_address': copy.deepcopy(address)}
        flexible_tools.build(self.process.store, plan, self.process.config, 'bounded_dax')
        definition = request['definition'].get('pbir_filter', {})
        top = next((source.get('Expression', {}).get('Subquery', {}).get('Query', {}).get('Top')
                    for source in definition.get('From', []) if source.get('Type') == 2), None)
        return {'plan': plan, 'labels': labels, 'normalization': copy.deepcopy(norm), 'top_n': top}

    def execute(self, side, compiled):
        process = self.process; plan = compiled['plan']
        result = self.verification_meter('bounded_dax', lambda: flexible_tools.run(
            process.store, plan, process.config, 'bounded_dax', process.execute_native))
        body = result.get('result') or {}
        observation = {'status': 'FAILED', 'reason': 'Native key probe did not complete',
                       'evidence': {'id': result['id'], 'read_status': result['status']}}
        if result['status'] != 'COMPLETED': return observation
        surface = {'engine': SEMANTIC_ENGINE, 'connection': process.model['workspace'],
            'object': process.model['native_id'], 'identity': process.config['fabric']['native_reader']['account']}
        report = body.get('surface_report')
        evidence = {'id': result['id'], 'tool': 'bounded_dax', 'context_id': plan['context_id'],
            'read_address': copy.deepcopy(plan['read_address']), 'execution_surface': surface,
            'surface_report': report, 'surface_report_types': copy.deepcopy(SEMANTIC_TYPES),
            'surface_attestation': attest_surface(surface, report, tuple(SEMANTIC_REPORT)),
            'surface_report_binding': body.get('surface_report_binding'),
            'surface_report_receipt_id': result['id'], 'values': copy.deepcopy(body.get('rows')),
            'request_hash': result['request_hash'], 'completeness': body.get('completeness')}
        observation['evidence'] = evidence
        if body.get('completeness') != 'COMPLETE_RESPONSE':
            observation['reason'] = 'Selected key set was truncated; complete comparison refused'
            return observation
        def scalar(cell):
            if not isinstance(cell, dict) or set(cell) != {'type', 'value'}:
                raise ValueError('Key result lacks original typed cell')
            value = cell['value']
            if cell['type'] == 'decimal':
                if not isinstance(value, str) or len(value) > 128:
                    raise ValueError('Native decimal key representation differs')
                number = Decimal(value)
                if not number.is_finite() or number != number.to_integral_value():
                    raise ValueError('Native key requires exact integral decimal')
                value = int(number)
            elif cell['type'] not in ('blank', 'string', 'boolean'):
                raise ValueError('Native key type unavailable')
            elif ((cell['type'] == 'blank' and value is not None)
                    or (cell['type'] == 'string' and not isinstance(value, str))
                    or (cell['type'] == 'boolean' and type(value) is not bool)):
                raise ValueError('Native key type differs from its value')
            if isinstance(value, str):
                if compiled['normalization']['case_fold']: value = value.casefold()
                if compiled['normalization']['trim']: value = value.rstrip(' ')
            return value
        keys = []; markers = 0
        try:
            for row in body['rows']:
                # Execute Queries wraps projected labels in square brackets.
                decoded = {}; seen = set()
                for label in [*compiled['labels'], 'translation_marker']:
                    present = [key for key in (label, '[' + label + ']') if key in row]
                    if len(present) != 1: raise ValueError('Native key result label absent or repeated')
                    seen.add(present[0]); decoded[label] = scalar(row[present[0]])
                if set(row) != seen:
                    raise ValueError('Native key result shape differs')
                marker = decoded['translation_marker']
                if type(marker) is not bool: raise ValueError('Native key marker is not boolean')
                if marker:
                    if any(decoded[label] is not None for label in compiled['labels']):
                        raise ValueError('Attestation sentinel carries a key')
                    markers += 1
                else: keys.append([decoded[label] for label in compiled['labels']])
            if markers != 1: raise ValueError('Native key attestation sentinel is missing or repeated')
        except (ValueError, KeyError, ArithmeticError) as exc:
            observation['reason'] = str(exc); return observation
        payload = {'keys': keys, 'complete': True, 'normalization': compiled['normalization']}
        evidence['translation_result'] = copy.deepcopy(payload)
        result = {**observation, 'status': 'COMPLETED', 'reason': None, **payload}
        if compiled.get('top_n') is not None and len(keys) > compiled['top_n']:
            failure = {'reason': 'TIE_AT_BOUNDARY', 'row_count': len(keys) - compiled['top_n']}
            evidence['verification_failure'] = copy.deepcopy(failure)
            result['verification_failure'] = failure
        return result
