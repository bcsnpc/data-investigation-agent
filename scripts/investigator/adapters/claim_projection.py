"""Declared Copy-chain projections through the existing bounded reader ports."""
import copy

from .. import context_search
from ..model_context import assets
from ..onboarding import digest
from ..source_diagnostics import quote
from ..flexible_tools import run as run_query
from ..claim_projection import validate_request, facts, validate
from .record_presence import plan as presence_plan


def mapped(adapter, path, layer, request, scope):
    validate_request(request)
    if not isinstance(scope, dict):
        raise ValueError('Claim projection requires an explicit typed scope.')
    if scope.get('filters') or scope.get('dimension_ids') or any(k not in ('filters', 'dimension_ids') for k in scope):
        raise ValueError('Declared Copy projections cannot translate this filtered or timed scope faithfully.')
    # Reuse the established key/connection/whole-entity/role admission before
    # deriving any new projection. A synthetic key here only compiles metadata;
    # it is not queried or presented as an authored example.
    examples = [{'value': k} for k in request['keys']] or [{'value': '0'}]
    base = presence_plan(adapter, path, layer, examples, scope)
    source_id = adapter.config['source_delivery']['source_asset_id']
    source = next(l for l in path['layers'] if l['id'] == source_id)
    proof = source['copy_mapping_proof']
    index = path['layers'].index(source)
    if index != 2 or len(path['layers']) != 3 or path['layers'][0].get('kind') != 'presentation':
        raise ValueError('Claim projection requires the complete declared semantic, landing and application Copy chain; transformed paths are NOT_COMPARABLE.')
    landing = path['layers'][1]
    binding = landing.get('binding', {})
    partition = binding.get('declared_partition', {})
    if (binding.get('status') != 'RESOLVED' or partition.get('partition_count') != 1 or
            partition.get('source_type') != 'entity' or binding.get('declared_role_count') != 0):
        raise ValueError('Claim projection requires one resolved whole-entity partition and no declared security roles.')
    current = {a['id']: a for a in (context_search.latest(adapter.store) or {}).get('assets', [])
               if a.get('availability') == 'CURRENT'}
    key = current.get(adapter.config['source_delivery']['key_column_id'], {})
    columns = {a['id']: a for a in assets(adapter.model['context']) if a.get('kind') == 'SemanticColumn'}
    table = next((a for a in assets(adapter.model['context']) if a['id'] == path['layers'][0]['id']), None)
    if not table: raise ValueError('Presentation table definition is absent.')
    mappings = proof['mapping']['translator']['mappings']
    source_columns = {c['name']: c for c in proof['source']['metadata']['columns']}
    key_maps = [m for m in mappings if m['source']['name'] == key['name']]
    if len(key_maps) != 1: raise ValueError('Exact key mapping is absent or ambiguous.')
    destination_key = key_maps[0]['destination']['name']
    semantic_keys = [c for c in columns.values() if c['parent_id'] == table['id'] and
                     c.get('metadata', {}).get('sourceColumn') == destination_key and
                     c.get('metadata', {}).get('dataType') == 'int64' and not c.get('metadata', {}).get('expression')]
    if len(semantic_keys) != 1: raise ValueError('One declared integral semantic key is required.')
    native = base['tool'] == 'bounded_dax'
    application = layer['id'] == source_id
    def reference(column):
        if native:
            return "'" + table['name'].replace("'", "''") + "'[" + column['name'].replace(']', ']]') + ']'
        destination = column['metadata']['sourceColumn']
        selected = [m for m in mappings if m['destination']['name'] == destination]
        if len(selected) != 1: raise ValueError('Exact projected column mapping is absent or ambiguous.')
        return quote(selected[0]['source']['name'] if application else destination)
    def select(identity, integral=False):
        column = columns.get(identity, {})
        meta = column.get('metadata', {})
        if (column.get('parent_id') != table['id'] or not meta.get('sourceColumn') or
                meta.get('expression') or meta.get('type') == 'calculated'):
            raise ValueError('Requested field is not one declared physical column of the presentation table.')
        mapped_columns = [m for m in mappings if m['destination']['name'] == meta['sourceColumn']]
        if len(mapped_columns) != 1: raise ValueError('Requested field has no exact Copy mapping.')
        physical = source_columns.get(mapped_columns[0]['source']['name'], {})
        if physical.get('computed_definition', 'missing') is not None:
            raise ValueError('Requested source field is not a declared uncomputed column.')
        from ..source_scope import kind
        physical_type = kind(physical)
        if meta.get('dataType') != physical_type or (integral and physical_type != 'int64'):
            raise ValueError('Projected types lack a faithful declared typed mapping.')
        if physical_type not in ('int64', 'decimal', 'string'):
            raise ValueError('Requested field type is unsupported for exact claim projection.')
        return column
    key_column = select(semantic_keys[0]['id'], integral=True)
    chosen = {'key': key_column}
    if request['kind'] == 'RECORD_VALUE': chosen['field'] = select(request['field_id'])
    if request['kind'] == 'DECOMPOSITION':
        chosen['dimension'] = select(request['dimension_id'], integral=True)
        measure = path['layers'][0].get('measure', {})
        if measure.get('id') != request['measure_id']:
            raise ValueError('Decomposition measure differs from the resolved path.')
        quantity = [c for c in columns.values() if c.get('parent_id') == table['id'] and c.get('name') == landing.get('semantic_column')]
        if len(quantity) != 1: raise ValueError('Decomposition requires a declared direct additive SUM column.')
        # The original whole-entity quantity compiler validates the measure's
        # resolved physical column and approved endpoint; do not approximate it.
        checked, reason = adapter._lower_quantity(landing, {})
        if checked is None: raise ValueError(reason)
        chosen['quantity'] = select(quantity[0]['id'], integral=True)
        # resolve_path already establishes SUM; verify its retained expression
        # independently instead of trusting a caller-provided layer marker.
        import re
        expression = measure.get('metadata', {}).get('expression', '')
        expected = r"\s*SUM\s*\(\s*(?:'" + re.escape(table['name'].replace("'", "''")) + r"'|" + re.escape(table['name']) + r")\s*\[" + re.escape(quantity[0]['name'].replace(']', ']]')) + r"\]\s*\)\s*"
        if not isinstance(expression, str) or not re.fullmatch(expected, expression, re.I):
            raise ValueError('Decomposition cannot substitute a physical sum for this measure.')
    # The full schema needed by projections enters the normal SQL catalog.
    if not native:
        metadata = copy.deepcopy(proof['source']['metadata']) if application else {
            'schema_name': partition['schema_name'], 'name': partition['entity_name'], 'type_desc': 'USER_TABLE',
            'columns': [dict(source_columns[m['source']['name']], name=m['destination']['name']) for m in mappings]}
        base['catalog'] = [{'id': layer['id'], 'metadata': metadata}]
        table_ref = quote(metadata['schema_name']) + '.' + quote(metadata['name'])
    else: table_ref = "'" + table['name'].replace("'", "''") + "'"
    refs = {name: reference(column) for name, column in chosen.items()}
    base.update(refs=refs, table_ref=table_ref, native=native,
                mapping_hash=digest({'proof': proof, 'binding': binding, 'columns': chosen, 'layer': layer['id']}))
    return base


def plan(adapter, path, layer, request, scope):
    compiled = mapped(adapter, path, layer, request, scope)
    refs, table, native = compiled['refs'], compiled['table_ref'], compiled['native']
    if request['kind'] != 'DECOMPOSITION':
        projections = []
        if request['kind'] == 'MULTIPLICITY':
            if native:
                projections.extend(['"all_rows"', 'COALESCE(COUNTROWS(' + table + '),0)',
                    '"distinct_keys"', 'COALESCE(COUNTROWS(FILTER(DISTINCT(' + refs['key'] + '),NOT(ISBLANK(' + refs['key'] + ')))),0)',
                    '"null_keys"', 'COALESCE(COUNTROWS(FILTER(' + table + ',ISBLANK(' + refs['key'] + '))),0)'])
            else:
                projections.extend(['COUNT(*) AS [all_rows]', 'COUNT(DISTINCT ' + refs['key'] + ') AS [distinct_keys]',
                    'COUNT(CASE WHEN ' + refs['key'] + ' IS NULL THEN 1 END) AS [null_keys]'])
        for i, key in enumerate(request['keys']):
            condition = refs['key'] + (' == ' if native else ' = ') + key
            if native:
                filtered = 'FILTER(' + table + ',' + condition + ')'
                projections.extend(['"count_' + str(i) + '"', 'COALESCE(COUNTROWS(' + filtered + '),0)'])
                if request['kind'] == 'RECORD_VALUE':
                    projections.extend(['"value_' + str(i) + '"', 'MAXX(' + filtered + ',' + refs['field'] + ')'])
            else:
                projections.append('COUNT(CASE WHEN ' + condition + ' THEN 1 END) AS [count_' + str(i) + ']')
                if request['kind'] == 'RECORD_VALUE':
                    projections.append('MAX(CASE WHEN ' + condition + ' THEN ' + refs['field'] + ' END) AS [value_' + str(i) + ']')
        query = 'EVALUATE ROW(' + ','.join(projections) + ')' if native else 'SELECT ' + ','.join(projections) + ' FROM ' + table
        maximum = 2
    else:
        key_filter = refs['key'] + ' IN {' + ','.join(request['keys']) + '}' if request['keys'] else None
        if native:
            # Every aggregate is written from bound model members. Generated
            # rowset aliases are not admitted as invented model measures.
            grouped = 'TOPN(200,DISTINCT(' + refs['dimension'] + '),' + refs['dimension'] + ',ASC)'
            selected = 'SELECTCOLUMNS(' + grouped + ',"marker",0,"group_value",' + refs['dimension'] + ',"quantity",CALCULATE(SUM(' + refs['quantity'] + ')),"row_count",CALCULATE(COUNTROWS(' + table + ')))'
            if key_filter: selected = 'CALCULATETABLE(' + selected + ',FILTER(' + table + ',' + key_filter + '))'
            query = 'EVALUATE UNION(ROW("marker",1,"group_value",BLANK(),"quantity",BLANK(),"row_count",BLANK()),' + selected + ')'
        else:
            where = ' WHERE ' + refs['key'] + ' IN (' + ','.join(request['keys']) + ')' if request['keys'] else ''
            query = 'SELECT 0 AS [marker],' + refs['dimension'] + ' AS [group_value],SUM(' + refs['quantity'] + ') AS [quantity],COUNT(*) AS [row_count] FROM ' + table + where + ' GROUP BY ' + refs['dimension']
        maximum = 200
    if native:
        from .microsoft_self_report import compose
        query = compose(query)
    compiled.update(query=query, max_rows=maximum)
    return compiled


def expected_surface(adapter, compiled):
    if compiled['tool'] == 'bounded_dax':
        return {'engine': 'OLAP Server', 'connection': adapter.model['workspace'],
                'object': adapter.model['native_id'], 'identity': adapter.config['fabric']['native_reader']['account']}
    if compiled['tool'] == 'bounded_sql':
        from application_sql_surface import ENGINE
        return {'engine': ENGINE, 'connection': 'sql://' + adapter.config['sql']['server'],
                'object': compiled['database'], 'identity': adapter.config['sql']['auth']['account']}
    reader = adapter.config['fabric']['sql_reader']
    return {'engine': 'Microsoft Azure SQL Data Warehouse', 'connection': 'sql://' + reader['server'],
            'object': compiled['database'], 'identity': reader['account']}


def admitted_request(adapter, layer, request, compiled):
    surface = expected_surface(adapter, compiled)
    address = {'kind': 'CLAIM_PROJECTION', 'layer': layer['id'], 'projection': copy.deepcopy(request),
               'mapping_hash': compiled['mapping_hash'], 'surface': surface}
    payload = {'model_id': adapter.model['id'], 'revision': adapter.model['revision'],
               'context_id': adapter.model['context_id'], 'query': compiled['query'],
               'max_rows': compiled['max_rows'], 'read_address': address}
    if compiled['native']:
        from .microsoft_process import SEMANTIC_REPORT
        payload['surface_report'] = SEMANTIC_REPORT
    return payload


def contract(adapter, path, layer, request, scope):
    """Independent pure compilation for the consumer, never a producer flag."""
    from ..flexible_tools import build
    try:
        compiled = plan(adapter, path, layer, request, scope)
        payload = admitted_request(adapter, layer, request, compiled)
        admitted = build(adapter.store, payload, adapter.config, compiled['tool'], catalog=compiled['catalog'])
        return {'status': 'COMPILED', 'request_hash': digest(admitted), 'read_address': payload['read_address']}
    except (ValueError, KeyError, TypeError) as exc:
        return {'status': 'UNAVAILABLE', 'reason': str(exc)}


def read(adapter, path, layer, request, scope):
    try:
        compiled = plan(adapter, path, layer, request, scope)
        payload = admitted_request(adapter, layer, request, compiled)
    except (ValueError, KeyError, TypeError) as exc:
        return {'status': 'UNAVAILABLE', 'reason': str(exc)}
    tool, address = compiled['tool'], payload['read_address']
    surface = address['surface']
    if tool == 'bounded_dax':
        if adapter.execute_native is None: return {'status': 'UNAVAILABLE', 'reason': 'Semantic reader is unconfigured.'}
        dispatch = adapter.execute_native
    elif tool == 'bounded_sql':
        from application_sql_surface import read as sql_read
        dispatch = lambda req: sql_read(adapter.config, req)
    else:
        if adapter.execute_lower is None: return {'status': 'UNAVAILABLE', 'reason': 'Lower reader is unconfigured.'}
        dispatch = lambda req: adapter.execute_lower(compiled['database'], req)
    try:
        execute = lambda: run_query(adapter.store, payload, adapter.config, tool, dispatch, catalog=compiled['catalog'])
        result = adapter.meter_read(tool, execute) if adapter.meter_read else execute()
        if result['status'] != 'COMPLETED':
            return {'status': 'UNAVAILABLE', 'reason': 'Claim projection did not complete.', 'receipt_id': result['id'],
                    'failure': result.get('result', {})}
        if plan(adapter, path, layer, request, scope) != compiled:
            return {'status': 'UNAVAILABLE', 'reason': 'Claim projection mapping changed during read.', 'receipt_id': result['id']}
        body = result['result']
        from ..process_debugging import attest_surface
        evidence = {'id': result['id'], 'status': result['status'], 'tool': tool, 'check_kind': 'CLAIM_PROJECTION',
                    'read_address': address, 'request_hash': result['request_hash'], 'values': body['rows'],
                    'completeness': body['completeness'], 'surface_report': body.get('surface_report'),
                    'surface_report_binding': body.get('surface_report_binding'), 'execution_surface': surface,
                    'surface_attestation': attest_surface(surface, body.get('surface_report'), ('identity', 'engine', 'object')),
                    'claim_projection': facts(request, body['rows'])}
        validate(evidence, adapter.store, adapter.model['id'])
        return {'status': 'OBSERVED', 'evidence': evidence}
    except (ValueError, KeyError, TypeError) as exc:
        return {'status': 'UNAVAILABLE', 'reason': str(exc), **({'receipt_id': result['id']} if 'result' in locals() else {})}
