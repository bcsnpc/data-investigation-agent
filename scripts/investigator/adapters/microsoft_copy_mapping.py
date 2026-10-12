"""Retained Copy-activity mapping hypotheses, never verification by name alone."""
import copy
import hashlib
import json


def infer_column_mapping(activity, source_columns, destination_columns):
    """Account for every projected output and retain casts as transformations.

    Fabric's omitted translator means automatic name mapping. This inventory is
    an onboarding hypothesis; it cannot itself earn an executable binding.
    """
    from sqlglot import parse, exp
    if activity.get('type') != 'Copy':
        raise ValueError('Expected a Copy activity')
    prop = activity['typeProperties']
    if 'translator' in prop:
        raise ValueError('Explicit translator must use its explicit mapping path')
    source, sink = prop['source'], prop['sink']
    if source.get('type') != 'AzureSqlSource' or sink.get('type') != 'LakehouseTableSink':
        raise ValueError('Unsupported automatic mapping source or destination')
    ds = source['datasetSettings']['typeProperties']
    trees = parse(source['sqlReaderQuery'], read='tsql')
    if len(trees) != 1 or not isinstance(trees[0], exp.Select):
        raise ValueError('Source projection is not one SELECT')
    tree = trees[0]
    if any(tree.args.get(k) for k in ('joins','where','group','having','qualify','distinct','limit','offset','with_')):
        raise ValueError('Source projection changes or bounds the row set')
    origin = tree.args.get('from_')
    if not origin or not isinstance(origin.this, exp.Table):
        raise ValueError('Source relation is not a declared table')
    table = origin.this
    if table.catalog or table.db != ds['schema'] or table.name != ds['table']:
        raise ValueError('Source query differs from declared source object')
    def index(columns):
        rows = list(columns)
        result = {c['name']: c for c in rows}
        if len(result) != len(rows) or len({n.casefold() for n in result}) != len(result):
            raise ValueError('Ambiguous column names')
        return result
    src, dst = index(source_columns), index(destination_columns)
    mappings = []
    for item in tree.expressions:
        expression = item.this if isinstance(item, exp.Alias) else item
        name = item.alias_or_name
        refs = list(expression.find_all(exp.Column))
        if not name or len(refs) != 1 or refs[0].name not in src or name not in dst:
            raise ValueError('Unresolved projected source or destination column')
        if refs[0].table and refs[0].table != table.alias_or_name:
            raise ValueError('Projection references a different relation')
        if not isinstance(expression, (exp.Column, exp.Cast)):
            raise ValueError('Unsupported projected expression')
        if isinstance(expression, exp.Cast) and not isinstance(expression.this, exp.Column):
            raise ValueError('Unsupported cast operand')
        source_meta = src[refs[0].name]
        if source_meta.get('computed_definition') is not None:
            raise ValueError('Computed source column requires its own proof')
        mappings.append({'source': refs[0].name, 'destination': name,
            'source_type': source_meta['data_type'], 'destination_type': dst[name]['data_type'],
            'expression': expression.sql(dialect='tsql'),
            'unchanged_column': isinstance(expression, exp.Column),
            'provenance': 'INFERRED_FROM_CODE', 'verification': 'UNVERIFIED'})
    if len({m['destination'] for m in mappings}) != len(mappings):
        raise ValueError('Duplicate destination projection')
    if set(dst) != {m['destination'] for m in mappings}:
        raise ValueError('Destination columns are not completely accounted for')
    raw = json.dumps(activity, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    return {'activity': activity['name'], 'definition_hash': hashlib.sha256(raw).hexdigest(),
        'mapping_mode': 'AUTOMATIC_BY_COLUMN_NAME', 'provenance': 'INFERRED_FROM_CODE',
        'verification': 'UNVERIFIED', 'mappings': mappings,
        'source_declaration': copy.deepcopy(source['datasetSettings']),
        'destination_declaration': copy.deepcopy(sink['datasetSettings']),
        'row_delivery': sink.get('tableActionOption'),
        'limitations': ['Column-name mapping is inferred, not verified equivalence.',
                        'Casts require independent type and value verification.',
                        'No source capture cut or served snapshot is established.']}
