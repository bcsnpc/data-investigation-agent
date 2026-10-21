"""Native-first practical value checks over a conserved declared report scope.

This compiler accepts catalog coordinates, never caller SQL. Transports are the
runner's existing guarded readers. A failed visual read is retained and stops
the path; it cannot be replaced with a storage value or earn VALUE_VERIFIED.
"""
import copy
import hashlib
import re
from decimal import Decimal, InvalidOperation

from investigator.declared_reproduction import compose
from investigator.model_context import assets
from investigator.onboarding import digest
from investigator import report_scope
from investigator.adapters import report_predicates

VERSION = 'declared-layer-value-plan-v1'


class Refused(ValueError):
    pass


def _one(items, reason):
    if len(items) != 1: raise Refused(reason)
    return items[0]


def _column(model, table, name):
    catalog = assets(model['context'])
    parent = _one([a for a in catalog if a['kind'] == 'SemanticTable' and a['name'].casefold() == table.casefold()], 'SEMANTIC_TABLE_AMBIGUOUS')
    return _one([a for a in catalog if a['kind'] == 'SemanticColumn' and a['parent_id'] == parent['id'] and a['name'].casefold() == name.casefold()], 'SEMANTIC_COLUMN_AMBIGUOUS')


def measure_program(model, measure_id):
    """Small explicitly supported DAX subset; every other expression refuses."""
    measure = _one([a for a in assets(model['context']) if a['id'] == measure_id and a['kind'] == 'Measure'], 'MEASURE_UNRESOLVED')
    expression = measure['metadata'].get('expression')
    if isinstance(expression, list): expression = '\n'.join(expression)
    if not isinstance(expression, str): raise Refused('MEASURE_EXPRESSION_MISSING')
    table = r"(?:'((?:[^']|'')+)'|([A-Za-z_][A-Za-z_0-9 ]*))"
    ref = table + r'\[([^\]]+)\]'
    simple = re.fullmatch(r'\s*SUM\s*\(\s*' + ref + r'\s*\)\s*', expression, re.I)
    if simple:
        name = (simple[1] or simple[2]).replace("''", "'")
        return {'kind': 'SUM', 'column': _column(model, name, simple[3])['id'], 'expression_hash': digest(expression)}
    # SUMX/FILTER/RELATED is deliberately closed. No inferred coercion,
    # arbitrary CALCULATE, nested measures or inferred REMOVEFILTERS semantics.
    pattern = (r'\s*CALCULATE\s*\(\s*SUMX\s*\(\s*FILTER\s*\(\s*' + table +
        r'\s*,\s*' + ref + r'\s*=\s*"((?:[^"]|"")*)"\s*\)\s*,\s*RELATED\s*\(\s*' + ref +
        r'\s*\)\s*\)\s*,\s*REMOVEFILTERS\s*\(\s*' + table + r'\s*\)\s*\)\s*')
    match = re.fullmatch(pattern, expression, re.I)
    if not match: raise Refused('UNSUPPORTED_MEASURE_SEMANTICS')
    groups = match.groups()
    fact = (groups[0] or groups[1]).strip().replace("''", "'")
    filtered = (groups[2] or groups[3]).strip().replace("''", "'")
    lookup = (groups[6] or groups[7]).strip().replace("''", "'")
    removed = (groups[9] or groups[10]).strip().replace("''", "'")
    if fact.casefold() != filtered.casefold() or lookup.casefold() != removed.casefold(): raise Refused('UNSUPPORTED_CALCULATE_SCOPE')
    filter_column = _column(model, fact, groups[4])
    related = _column(model, lookup, groups[8])
    fact_table = next(a for a in assets(model['context']) if a['id'] == filter_column['parent_id'])
    lookup_table = next(a for a in assets(model['context']) if a['id'] == related['parent_id'])
    rel = _one([a for a in assets(model['context']) if a['kind'] == 'SemanticRelationship'
        and a['metadata'].get('fromTable') == fact_table['name'] and a['metadata'].get('toTable') == lookup_table['name']
        and a['metadata'].get('isActive', True) is True], 'RELATED_RELATIONSHIP_AMBIGUOUS')
    meta = rel['metadata']
    if meta.get('toCardinality', 'one').casefold() != 'one' or meta.get('crossFilteringBehavior', 'oneDirection') != 'oneDirection':
        raise Refused('RELATED_RELATIONSHIP_UNSUPPORTED')
    return {'kind': 'SUMX_RELATED', 'column': related['id'], 'filter_column': filter_column['id'],
        'filter_value': groups[5].replace('""', '"'), 'fact_key': _column(model, fact, meta['fromColumn'])['id'],
        'lookup_key': _column(model, lookup, meta['toColumn'])['id'], 'remove_table': lookup_table['id'],
        'relationship_id': rel['id'], 'expression_hash': digest(expression)}


def _ident(text):
    if not isinstance(text, str) or not text or len(text) > 256 or '\x00' in text: raise Refused('PHYSICAL_IDENTIFIER_INVALID')
    return '[' + text.replace(']', ']]') + ']'


def _literal(value):
    if value is None: return 'NULL'
    if type(value) is bool: return '1' if value else '0'
    if type(value) is str:
        if not value.isascii(): raise Refused('UNICODE_FILTER_REQUIRES_PARAMETER_PORT')
        return "'" + value.replace("'", "''") + "'"
    if type(value) in (int, float):
        number = Decimal(str(value))
        if not number.is_finite(): raise Refused('NONFINITE_FILTER')
        return format(number, 'f')
    raise Refused('FILTER_LITERAL_UNSUPPORTED')


def compile_layer(model, program, restrictions, mapping):
    """Compile only mapped catalog columns, preserving dimension semijoin scope.

    mapping = {layer_id, endpoint, objects:{id:{schema,table,columns}},
      columns:{semantic_id:{object_id,column}}, relationships:[semantic rel id]}
    Coordinates must have been resolved by the graph/DirectLake/producer bridge.
    This function does not infer a physical binding from a matching label.
    """
    objects, columns = mapping['objects'], mapping['columns']
    if not objects or len(objects) > 32 or len(columns) > 256: raise Refused('MAPPING_BOUND')
    catalog = {a['id']: a for a in assets(model['context'])}
    def mapped(identity):
        if identity not in catalog or catalog[identity]['kind'] != 'SemanticColumn': raise Refused('MAPPING_SEMANTIC_COLUMN_UNKNOWN')
        entry = columns.get(identity)
        if not isinstance(entry, dict) or set(entry) != {'object_id', 'column'}: raise Refused('UNMAPPED_SCOPE_COLUMN:' + identity)
        obj = objects.get(entry['object_id'])
        if not obj or entry['column'] not in obj['columns']: raise Refused('MAPPING_PHYSICAL_COLUMN_UNKNOWN')
        return entry
    def table(identity):
        obj = objects[identity]
        return _ident(obj['schema']) + '.' + _ident(obj['table'])
    main = mapped(program.get('filter_column', program['column']))['object_id']
    aliases = {main: 'f'}
    def ref(identity):
        entry = mapped(identity)
        if entry['object_id'] not in aliases: raise Refused('COLUMN_OUTSIDE_RELATION')
        return aliases[entry['object_id']] + '.' + _ident(entry['column'])
    where, guards, translations = [], [], []
    related_from = ''
    if program['kind'] == 'SUMX_RELATED':
        lookup = mapped(program['column'])['object_id']
        if lookup == main: raise Refused('RELATED_PHYSICAL_TABLE_ALIAS_COLLISION')
        aliases[lookup] = 'p'
        fk, lk = ref(program['fact_key']), ref(program['lookup_key'])
        related_from = ' LEFT JOIN ' + table(lookup) + ' p ON ' + fk + '=' + lk
        key = _ident(mapped(program['lookup_key'])['column'])
        guards.append('(SELECT COUNT_BIG(*) FROM (SELECT ' + key + ' FROM ' + table(lookup) + ' GROUP BY ' + key + ' HAVING COUNT_BIG(*)>1) duplicate_keys)')
        where.append(ref(program['filter_column']) + '=' + _literal(program['filter_value']))
    for restriction in compose(restrictions):
        identity = restriction['field_id']; entry = mapped(identity)
        # REMOVEFILTERS removes all column filters on the declared lookup table;
        # the omission is recorded, never silently carried as a WHERE term.
        if program['kind'] == 'SUMX_RELATED' and catalog[identity]['parent_id'] == program['remove_table']:
            translations.append({'restriction': restriction, 'operation': 'REMOVED_BY_MEASURE_REMOVEFILTERS'})
            continue
        terms = []
        values = restriction['values']
        def condition(column):
            if not values: return '1=0'
            nonnull = [v for v in values if v is not None]
            if nonnull: terms.append(column + ' IN (' + ','.join(_literal(v) for v in nonnull) + ')')
            if None in values: terms.append(column + ' IS NULL')
            return '(' + ' OR '.join(terms) + ')'
        if entry['object_id'] == main:
            predicate = condition(ref(identity))
            relation = None
        else:
            semantic_table = catalog[identity]['parent_id']
            semantic_main = catalog[program.get('filter_column', program['column'])]['parent_id']
            main_name, dim_name = catalog[semantic_main]['name'], catalog[semantic_table]['name']
            candidates = [catalog[r] for r in mapping['relationships'] if r in catalog and catalog[r]['kind'] == 'SemanticRelationship'
                and catalog[r]['metadata'].get('fromTable') == main_name and catalog[r]['metadata'].get('toTable') == dim_name
                and catalog[r]['metadata'].get('isActive', True) is True]
            relation = _one(candidates, 'FILTER_RELATIONSHIP_UNRESOLVED')
            meta = relation['metadata']
            if meta.get('crossFilteringBehavior', 'oneDirection') != 'oneDirection' or meta.get('toCardinality', 'one').casefold() != 'one': raise Refused('FILTER_PROPAGATION_UNSUPPORTED')
            fact_key = mapped(_column(model, main_name, meta['fromColumn'])['id'])
            dim_key = mapped(_column(model, dim_name, meta['toColumn'])['id'])
            if fact_key['object_id'] != main or dim_key['object_id'] != entry['object_id']: raise Refused('RELATIONSHIP_MAPPING_DISAGREES')
            if None in values:raise Refused('DIMENSION_BLANK_MEMBER_SEMANTICS_UNSUPPORTED')
            predicate = ('f.' + _ident(fact_key['column']) + ' IN (SELECT d.' + _ident(dim_key['column']) + ' FROM '
                + table(entry['object_id']) + ' d WHERE ' + condition('d.' + _ident(entry['column'])) + ')')
        where.append(predicate)
        translations.append({'restriction': restriction, 'physical': copy.deepcopy(entry), 'relationship_id': relation['id'] if relation else None, 'predicate': predicate})
    query = 'SELECT SUM(' + ref(program['column']) + ') AS [quantity], ' + ('+'.join(guards) if guards else '0') + ' AS [duplicate_lookup_keys] FROM ' + table(main) + ' f' + related_from
    if where: query += ' WHERE ' + ' AND '.join(where)
    return {'layer_id': mapping['layer_id'], 'endpoint': copy.deepcopy(mapping['endpoint']), 'statement': query, 'requires_lookup_guard': bool(guards),
        'statement_hash': hashlib.sha256(query.encode()).hexdigest(), 'mapping': copy.deepcopy(mapping), 'translations': translations}


def build(model, measure_id, target_id, layer_mappings, *, tolerance):
    """Extract the actual retained visual and all ACTIVE saved defaults first."""
    if not isinstance(tolerance, dict) or set(tolerance) != {'kind', 'value', 'source'} or tolerance['kind'] != 'ABSOLUTE' or not tolerance['source']:
        raise Refused('EXPLICIT_TOLERANCE_REQUIRED')
    try: amount = Decimal(tolerance['value'])
    except (InvalidOperation, TypeError): raise Refused('EXPLICIT_TOLERANCE_REQUIRED')
    if not amount.is_finite() or amount < 0: raise Refused('EXPLICIT_TOLERANCE_REQUIRED')
    options = report_predicates.targets(model, measure_id)
    selected = _one([o for o in options if o['target_id'] == target_id], 'VISUAL_TARGET_UNRESOLVED')
    declaration = copy.deepcopy(selected)
    inventory = declaration['inventory']; evidence = declaration['evidence']
    entries = report_scope.validate_inventory(inventory, declaration['restrictions'], binding=evidence['report_binding'], reports=evidence['report_catalog'])
    forms = [e['opaque_provenance'] for e in entries if e['disposition'] == 'UNSUPPORTED']
    if forms: raise Refused('UNSUPPORTED_DECLARATION:' + ','.join(forms))
    from investigator.adapters.report_cells import addresses
    scope = {'report_binding': evidence['report_binding']}
    cells = addresses(model, report_predicates._document(model, target_id), target_id, measure_id, scope)
    cell = _one(cells, 'CELL_SCOPE_AMBIGUOUS')
    part = _one([part for report in model['context']['reports'] for part in report['report_definitions'] if part['id'] == target_id], 'VISUAL_PART_UNRESOLVED')
    path = part['metadata'].get('path', '')
    page = re.fullmatch(r'definition/pages/([^/]+)/visuals/[^/]+/visual.json', path)
    if page is None: raise Refused('VISUAL_PAGE_UNRESOLVED')
    address = {'report_id': evidence['report_binding']['report_id'], 'page_id': page[1], 'target_id': target_id}
    restrictions = compose(declaration['restrictions'] + cell['key_restrictions'])
    program = measure_program(model, measure_id)
    native = report_predicates.quantity_query(model, measure_id, restrictions)
    layers = []
    for mapping in layer_mappings:
        try: layers.append(compile_layer(model, program, restrictions, mapping))
        except (Refused, KeyError, TypeError) as error:
            layers.append({'layer_id': mapping.get('layer_id', 'UNKNOWN'), 'compilation_error': str(error), 'mapping': copy.deepcopy(mapping)})
    return {'version': VERSION, 'model_id': model['id'], 'context_id': model['context_id'], 'measure_id': measure_id,
        'definition_hash': program['expression_hash'], 'visual_address': address, 'visual_cell': cell, 'inventory': inventory,
        'active_restrictions': declaration['restrictions'], 'restrictions': restrictions,
        'report_binding': evidence['report_binding'], 'report_catalog': evidence['report_catalog'],
        'scope_hash': digest({'visual_address': address, 'visual_cell': cell, 'inventory': inventory, 'active_restrictions': declaration['restrictions']}), 'program': program,
        'tolerance': copy.deepcopy(tolerance), 'native_statement': native, 'layers': layers,
        'qualifications': ['SNAPSHOT_UNVERIFIED'] + (['Saved slicer default positions assumed; current positions not established.']
            if any(e['assumption'] == 'SAVED_DEFAULT' and e['disposition'] == 'ACTIVE' for e in entries) else [])}


def execute(plan, read_native, read_lower, retain):
    """All callbacks are runner-owned; retain each original response unchanged.

    Readers return {status, value, duplicate_lookup_keys?, ...original receipt}.
    This function creates an observational report, never a trusted graph proof.
    The independent engine resolver alone can award VALUE_VERIFIED.
    """
    retained = []
    def probe(layer, statement, reader, compiled=None):
        try: result = reader(statement if compiled is None else compiled)
        except Exception as error:
            from investigator.live_gateway import GatewayDenied
            if isinstance(error,GatewayDenied):raise
            result = {'status': 'FAILED', 'error': {'type': type(error).__name__, 'message': str(error)}}
        retained.append({'layer': layer, 'statement': statement, 'receipt': copy.deepcopy(result)})
        retain(copy.deepcopy(retained[-1]))
        return result
    native = probe('SEMANTIC', plan['native_statement'], read_native)
    if native.get('status') != 'SUCCEEDED':
        return {'status': 'REFUSED', 'layer': 'SEMANTIC', 'reason': 'NATIVE_VISUAL_READ_FAILED', 'reads': retained, 'qualifications': plan['qualifications']}
    if 'value' not in native: return {'status': 'REFUSED', 'layer': 'SEMANTIC', 'reason': 'NATIVE_VALUE_NOT_OBTAINED', 'reads': retained}
    if not plan['layers']: return {'status': 'REFUSED', 'layer': 'STORAGE', 'reason': 'NO_DECLARED_LOWER_MAPPING', 'reads': retained}
    tolerance = Decimal(plan['tolerance']['value']); previous = native['value']; comparisons = []
    for layer in plan['layers']:
        if 'compilation_error' in layer:
            return {'status': 'REFUSED', 'layer': layer['layer_id'], 'reason': layer['compilation_error'], 'reads': retained, 'comparisons': comparisons}
        result = probe(layer['layer_id'], layer['statement'], read_lower, layer)
        reason = None
        if result.get('status') != 'SUCCEEDED': reason = 'LOWER_READ_FAILED'
        elif 'value' not in result: reason = 'LOWER_VALUE_NOT_OBTAINED'
        elif layer.get('requires_lookup_guard') and 'duplicate_lookup_keys' not in result: reason = 'RELATED_LOOKUP_GUARD_NOT_OBTAINED'
        elif result.get('duplicate_lookup_keys', 0) != 0: reason = 'RELATED_LOOKUP_KEYS_NOT_UNIQUE'
        if reason: return {'status': 'REFUSED', 'layer': layer['layer_id'], 'reason': reason, 'reads': retained, 'comparisons': comparisons}
        current = result['value']
        # None is measured BLANK. Absence of the value key is not BLANK.
        equal = previous is None and current is None if previous is None or current is None else abs(Decimal(str(previous)) - Decimal(str(current))) <= tolerance
        comparisons.append({'layer': layer['layer_id'], 'previous': previous, 'value': current, 'equal': equal})
        if not equal:
            return {'status': 'REFUSED', 'layer': layer['layer_id'], 'reason': 'UNEXPLAINED_VALUE_DIFFERENCE', 'reads': retained, 'comparisons': comparisons, 'qualifications': plan['qualifications']}
        previous = current
    return {'status': 'VALUES_AGREE_UNDER_MAPPING', 'reads': retained, 'comparisons': comparisons,
        'qualifications': plan['qualifications'], 'confidence_awarded': False}


def declared_producers(graph, table_ids):
    """Report every declared writer alternative; static text is not a last run."""
    nodes = {node['id']: node for node in graph['nodes']}
    result = []
    for identity in table_ids:
        table = nodes.get(identity)
        if not table or table['kind'] != 'TABLE': raise Refused('PRODUCER_TABLE_UNRESOLVED')
        writers = []
        for edge in graph['edges']:
            if edge['source'] != identity or edge['kind'] != 'DERIVED_IN_STEP': continue
            step = nodes.get(edge['target'])
            if not step or step['kind'] != 'QUERY_STEP': continue
            writers.append({'step_id': step['id'], 'owner': step['owner'], 'expression': step['properties'].get('expression'),
                'language': step['properties'].get('language'), 'provenance': copy.deepcopy(step['provenance']),
                'execution_established': step['properties'].get('execution_established') is True})
        result.append({'table_id': identity, 'asset_id': table['properties'].get('asset_id'),
            'writers': sorted(writers, key=lambda writer: writer['step_id']),
            'last_writer_established': False,
            'remaining_gap': 'Static producer alternatives do not establish which pipeline last ran.' if writers else 'No declared producer.'})
    return result


def main():
    """Offline plan mode: exact retained model/target and optional bridge mappings."""
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--measure-id', required=True)
    parser.add_argument('--target-id', required=True)
    parser.add_argument('--mappings', type=Path)
    parser.add_argument('--tolerance', required=True)
    parser.add_argument('--tolerance-source', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    model = json.loads(args.model.read_bytes())
    mappings = json.loads(args.mappings.read_bytes()) if args.mappings else []
    plan = build(model, args.measure_id, args.target_id, mappings,
        tolerance={'kind':'ABSOLUTE','value':args.tolerance,'source':args.tolerance_source})
    plan['plan_only'] = True
    plan['lower_mapping_complete'] = bool(plan['layers']) and not any('compilation_error' in layer for layer in plan['layers'])
    plan['source_hashes'] = {'model':hashlib.sha256(args.model.read_bytes()).hexdigest(),
        'mappings':hashlib.sha256(args.mappings.read_bytes()).hexdigest() if args.mappings else None}
    with args.output.open('x', encoding='utf-8') as stream: json.dump(plan, stream, sort_keys=True, indent=2)


if __name__ == '__main__': main()
