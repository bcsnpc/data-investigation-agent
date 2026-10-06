"""Target-type comparison profiles through the existing guarded SQL surfaces."""
import copy
from .code_verification import VerificationRoute
from ..binding_sample import validate_address, PROFILES
from ..lineage_binding import validate
from ..transformation_sql import compile_quantity
from ..process_debugging import attest


def profile(data_type):
    kind = data_type.casefold()
    if kind in ('bit', 'boolean'):
        return 'BOOLEAN'
    if kind in ('int', 'bigint', 'long', 'smallint', 'tinyint', 'numeric',
                'decimal', 'double', 'float', 'real'):
        return 'NUMERIC'
    if kind in ('date', 'datetime', 'datetime2', 'smalldatetime', 'datetimeoffset'):
        return 'TEMPORAL'
    if kind in ('string', 'nvarchar', 'varchar', 'text', 'char', 'nchar'):
        return 'STRING'
    raise NotImplementedError('TARGET_TYPE_UNSUPPORTED: ' + data_type)


class BindingVerificationRoute(VerificationRoute):
    def __init__(self, process, *, objects, context, normalizations=None, string_semantics=None):
        self.process = process
        self.objects = copy.deepcopy(objects)
        self.context = context
        # A binding profile is not an evaluation of any semantic-model measure.
        self.measure_id = None
        self.normalizations = copy.deepcopy(normalizations or {})
        self.string_semantics = copy.deepcopy(string_semantics or {})

    def target_profile(self, proposal):
        target = self.objects[proposal['target']['table']]['catalog']['metadata']
        matches = [c for c in target['columns'] if c['name'] == proposal['target']['column']]
        if len(matches) != 1:
            raise ValueError('Target column type absent or ambiguous')
        return profile(matches[0]['data_type'])

    def compile(self, proposal, side, context, address):
        proposal = validate(proposal)
        validate_address(address)
        if context != self.context or context != self.process.model['context_id']:
            raise ValueError('Verification retained context differs from actual probe context')
        if address['profile'] != self.target_profile(proposal):
            raise ValueError('Comparison profile differs from discovered target type')
        if side not in ('TARGET', 'SOURCE'):
            raise ValueError('Unknown binding comparison side')
        column = proposal['target']['column']
        table = proposal['target']['table']
        relation = proposal['expression']['relation'] if side == 'SOURCE' else {
            'kind': 'SCAN', 'table': table,
            'columns': list(dict.fromkeys([column, address['sample']['column']]))}
        names = [s['table'] for s in proposal['sources']] if side == 'SOURCE' else [table]
        resolved = [self.objects[name] for name in names]
        endpoints = {(o.get('surface', 'FABRIC_SQL'), o['connection'], o['database']) for o in resolved}
        if len(endpoints) != 1:
            raise NotImplementedError('Expression spans distinct declared connections')
        surface, connection, database = next(iter(endpoints))
        configured = (self.process.config.get('sql', {}).get('server') if surface == 'APPLICATION_SQL'
                      else self.process.config['fabric']['sql_reader']['server'])
        if connection != configured:
            raise ValueError('Declared endpoint differs from isolated reader')
        catalog = {name: obj['catalog'] for name, obj in zip(names, resolved)}
        target_semantics=self.string_semantics.get(table)
        source_declarations={name:self.string_semantics.get(name) for name in
                             dict.fromkeys(s['table'] for s in proposal['sources'])}
        source_semantics=list(source_declarations.values())
        if source_semantics and any(v!=source_semantics[0] for v in source_semantics):
            raise NotImplementedError('Mixed source string semantics require an operation-specific renderer')
        query = compile_quantity(relation, column, catalog, profile=address['profile'],
                                 sample=address['sample'], normalization=self.normalizations.get(table),
                                 string_semantics=target_semantics,
                                 source_string_semantics=source_semantics[0] if source_semantics else None)
        semantics=None
        if target_semantics is not None:
            from ..string_semantics import validate as validate_semantics
            semantics={'target':validate_semantics(target_semantics),
                       'sources':{name:validate_semantics(value) for name,value in source_declarations.items()},
                       'comparison':'TARGET_SEMANTICS_ON_BOTH_SIDES'}
        return {'layer': {'id': resolved[0]['asset_id'], 'binding': {'provenance': 'INFERRED_FROM_CODE'}},
                'compiled': {'catalog': list(catalog.values()), 'query': query, 'database': database,
                             'source_column': column, 'read_address': copy.deepcopy(address)},
                'surface': surface, 'context': context, 'address': copy.deepcopy(address),
                'string_semantics':semantics}

    def execute(self, side, plan):
        probe = attest(self._application(plan) if plan['surface'] == 'APPLICATION_SQL' else
                       self.process._evaluate_lower(plan['layer'], self.measure_id, plan['compiled']))
        result = {'status': 'COMPLETED' if probe.status == 'OBSERVED' else 'FAILED',
                  'context': plan['context'], 'address': copy.deepcopy(plan['address']),
                  'evidence': copy.deepcopy(probe.evidence), 'reason': probe.reason,
                  'failure': copy.deepcopy(probe.failure)}
        if probe.status != 'OBSERVED':
            return result
        evidence = result['evidence']
        evidence['execution_surface'] = copy.deepcopy(probe.execution_surface)
        if evidence.get('context_id') != plan['context'] or evidence.get('read_address') != plan['address']:
            result.update(status='FAILED', reason='Original context or sample address differs')
            return result
        rows = evidence.get('values')
        if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
            result.update(status='FAILED', reason='Complete one-row profile was not obtained')
            return result
        quantities = {}
        for name in PROFILES[plan['address']['profile']]:
            if name not in rows[0]:
                result.update(status='FAILED', reason='Missing profile quantity: ' + name)
                return result
            value = rows[0][name]
            if isinstance(value, dict):
                if 'value' not in value:
                    result.update(status='FAILED', reason='Measured profile field omitted its value')
                    return result
                value = value['value']
            quantities[name] = value
        result['quantities'] = quantities
        # Scope was compiled into the sealed query, not supplied by a narrative.
        evidence['declared_context'] = {'scope': 'BINDING_SAMPLE',
                                        'restriction': copy.deepcopy(plan['address']['sample'])}
        return result
