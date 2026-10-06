"""Sampled measure verification through isolated DAX and declared SQL routes.

The native side compiles the actual retained measure at each original address.
The proposed side is a complete, catalog-bound read-only SQL expression. A fixed
SQL expression that ignores a scope-sensitive cell will falsify, never silently
inherit or approximate its filters. Existing filtered lower-walk refusal remains.
"""
import copy
from decimal import Decimal
from .. import flexible_tools
from ..model_context import assets
from ..process_debugging import attest_surface
from ..declared_reproduction import compose as restrictions
from ..process_quantity import quantity
from .report_predicates import quantity_query
from .microsoft_self_report import compose as self_report
from .microsoft_process import SEMANTIC_REPORT, SEMANTIC_TYPES, SEMANTIC_ENGINE, SQL_ENGINE, SQL_TYPES


class MeasureRoute:
    def __init__(self, process, *, measure_id, objects, verification_meter):
        self.process = process; self.measure_id = measure_id
        self.objects = copy.deepcopy(objects); self.verification_meter = verification_meter

    def compile(self, proposal, side, request, address):
        from ..translation_proposer import validate
        validate(proposal, request)
        model = self.process.model
        if request['kind'] != 'MEASURE' or request['target_engine'] != SQL_ENGINE:
            raise NotImplementedError('This route serves native-to-declared-SQL measure witnesses only')
        if request['context'] != model['context_id']:
            raise ValueError('Measure translation differs from pinned context')
        measure = next(a for a in assets(model['context']) if a['id'] == self.measure_id and a['kind'] == 'Measure')
        if request['definition'] != {'measure_id': self.measure_id, 'expression': measure['metadata']['expression']}:
            raise ValueError('Translation definition differs from actual retained native measure')
        cell = address['cell']
        if cell['measure_id'] != self.measure_id: raise ValueError('Sample cell differs from the retained measure')
        plan = {'model_id': model['id'], 'revision': model['revision'], 'context_id': model['context_id'],
                'max_rows': 20, 'read_address': copy.deepcopy(address)}
        if side == 'NATIVE':
            scope = request['scope']
            if set(scope) != {'restrictions'}: raise ValueError('Measure verification requires explicit restrictions')
            applied = restrictions(scope['restrictions'] + cell['key_restrictions'])
            plan.update(query=self_report(quantity_query(model, self.measure_id, applied)),
                        surface_report=copy.deepcopy(SEMANTIC_REPORT))
            compiled = flexible_tools.build(self.process.store, plan, self.process.config, 'bounded_dax')
            if 'quantity' not in compiled['result_columns']: raise ValueError('Native measure quantity projection missing')
            return {'plan': plan, 'tool': 'bounded_dax', 'catalog': None, 'database': None}
        if side != 'PROPOSED': raise ValueError('Unknown translation side')
        if any(o['kind'] != 'TABLE' for o in proposal['objects']):
            raise NotImplementedError('SQL proposal objects must be discovered relational tables')
        names = [o['id'] for o in proposal['objects']]
        try: resolved = [self.objects[name] for name in names]
        except KeyError as exc: raise ValueError('Proposed table lacks an exact declared endpoint') from exc
        endpoints = {(o.get('surface', 'FABRIC_SQL'), o['connection'], o['database']) for o in resolved}
        if len(endpoints) != 1: raise NotImplementedError('No cross-connection measure query')
        surface, connection, database = next(iter(endpoints))
        if surface != 'FABRIC_SQL' or connection != self.process.config['fabric']['sql_reader']['server']:
            raise ValueError('Measure proposal leaves the isolated declared SQL endpoint')
        catalog = [o['catalog'] for o in resolved]
        plan['query'] = proposal['expression']
        compiled = flexible_tools.build(self.process.store, plan, self.process.config, 'bounded_fabric_sql', catalog=catalog)
        if set(compiled['asset_ids']) != {o['id'] for o in catalog}:
            raise ValueError('SQL object declarations differ from compiler-resolved tables')
        if compiled['result_columns'] != ['quantity']:
            raise ValueError('SQL translation must project one quantity')
        return {'plan': plan, 'tool': 'bounded_fabric_sql', 'catalog': catalog, 'database': database}

    def execute(self, side, compiled):
        process = self.process; plan = compiled['plan']; native = compiled['tool'] == 'bounded_dax'
        transport = process.execute_native if native else lambda statement: process.execute_lower(compiled['database'], statement)
        result = self.verification_meter(compiled['tool'], lambda: flexible_tools.run(
            process.store, plan, process.config, compiled['tool'], transport, catalog=compiled['catalog']))
        body = result.get('result') or {}
        observation = {'status': 'FAILED', 'reason': 'Measure probe did not complete',
            'evidence': {'id': result['id'], 'read_status': result['status'], 'error_type': body.get('error_type')}}
        if result['status'] != 'COMPLETED': return observation
        surface = ({'engine': SEMANTIC_ENGINE, 'connection': process.model['workspace'],
            'object': process.model['native_id'], 'identity': process.config['fabric']['native_reader']['account']}
            if native else {'engine': SQL_ENGINE, 'connection': 'sql://' + process.config['fabric']['sql_reader']['server'],
                'object': compiled['database'], 'identity': process.config['fabric']['sql_reader']['account']})
        evidence = {'id': result['id'], 'context_id': plan['context_id'], 'read_address': copy.deepcopy(plan['read_address']),
            'tool': compiled['tool'], 'execution_surface': surface, 'surface_report': body.get('surface_report'),
            'surface_report_types': copy.deepcopy(SEMANTIC_TYPES if native else SQL_TYPES),
            'surface_report_binding': body.get('surface_report_binding'), 'surface_report_receipt_id': result['id'],
            'surface_attestation': attest_surface(surface, body.get('surface_report'), ('identity', 'engine', 'object')),
            'values': copy.deepcopy(body.get('rows')), 'request_hash': result['request_hash'],
            'completeness': body.get('completeness')}
        observation['evidence'] = evidence
        if body.get('completeness') != 'COMPLETE_RESPONSE':
            observation['reason'] = 'Measure response was truncated'; return observation
        try:
            scalar = quantity(body['rows'], SEMANTIC_REPORT if native else None)
            if not isinstance(scalar, dict) or set(scalar) != {'quantity'}:
                raise ValueError('Measure response is not one scalar quantity')
            value = scalar['quantity']
            if value is None: measured = {'state': 'BLANK'}
            else:
                number = Decimal(str(value))
                if not number.is_finite(): raise ValueError('Measure quantity is not finite')
                measured = {'state': 'NUMBER', 'value': str(number)}
        except (ValueError, ArithmeticError) as exc:
            observation['reason'] = str(exc); return observation
        evidence['translation_result'] = {'quantity': copy.deepcopy(measured)}
        return {**observation, 'status': 'COMPLETED', 'reason': None, 'quantity': measured}
