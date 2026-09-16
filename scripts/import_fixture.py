"""Bounded, content-addressed Import fixtures. Operator tooling, not runtime logic.

The artifact proves what was submitted, not exclusive remote generation stability.
Only typed inline data is compiled; arbitrary Power Query sources are not accepted.
"""
import base64
from collections import Counter
import hashlib
import json
import re


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def name(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_ ]{0,79}', value):
        raise ValueError('Fixture names must be simple identifiers')
    return value


def cell(value, kind):
    if value is None:
        return value
    valid = ((kind == 'string' and isinstance(value, str) and len(value) <= 500)
             or (kind == 'boolean' and type(value) is bool)
             or (kind == 'int64' and type(value) is int and -(2**53) < value < 2**53))
    if not valid:
        raise ValueError('Unsupported or lossy fixture value')
    return value


def m_literal(value):
    if isinstance(value, str):
        # M escapes: escape # first, so literal #(lf) does not become a newline.
        return '"' + value.replace('#', '#(#)').replace('"', '""').replace('\r', '#(cr)').replace('\n', '#(lf)').replace('\t', '#(tab)') + '"'
    return json.dumps(value)


def build(spec):
    if set(spec) != {'tables', 'relationships'}:
        raise ValueError('Expected tables and relationships')
    if not isinstance(spec['tables'], list) or not 1 <= len(spec['tables']) <= 8:
        raise ValueError('Expected one to eight tables')
    tables, inputs, names, measure_names = [], [], set(), set()
    for source in spec['tables']:
        if set(source) != {'name', 'columns', 'rows', 'measures'}:
            raise ValueError('Unexpected table fields')
        table_name = name(source['name'])
        if table_name.casefold() in names:
            raise ValueError('Duplicate table')
        names.add(table_name.casefold())
        if not 1 <= len(source['columns']) <= 20 or len(source['rows']) > 1000:
            raise ValueError('Fixture table budget exceeded')
        columns, column_names = [], set()
        for column in source['columns']:
            if set(column) != {'name', 'type'} or column['type'] not in ('string', 'boolean', 'int64'):
                raise ValueError('Unsupported column')
            column_name = name(column['name'])
            if column_name.casefold() in column_names:
                raise ValueError('Duplicate column')
            column_names.add(column_name.casefold())
            columns.append({'name': column_name, 'dataType': column['type'], 'sourceColumn': column_name, 'summarizeBy': 'none'})
        rows = []
        for row in source['rows']:
            if not isinstance(row, list) or len(row) != len(columns):
                raise ValueError('Invalid row shape')
            rows.append([cell(v, c['dataType']) for v, c in zip(row, columns)])
        measures = []
        if len(source['measures']) > 30:
            raise ValueError('Measure budget exceeded')
        for measure in source['measures']:
            if set(measure) != {'name', 'expression'}:
                raise ValueError('Unexpected measure fields')
            mn = name(measure['name'])
            if mn.casefold() in measure_names or mn.casefold() in column_names:
                raise ValueError('Duplicate measure')
            measure_names.add(mn.casefold())
            if not isinstance(measure['expression'], str) or not 1 <= len(measure['expression']) <= 4000:
                raise ValueError('Invalid measure expression')
            measures.append(dict(measure))
        m_types = {'string': 'nullable text', 'boolean': 'nullable logical', 'int64': 'nullable number'}
        fields = ', '.join('#"' + c['name'] + '" = ' + m_types[c['dataType']] for c in columns)
        data = ', '.join('{' + ', '.join(m_literal(v) for v in row) + '}' for row in rows)
        expression = '#table(type table [' + fields + '], {' + data + '})'
        tables.append({'name': table_name, 'columns': columns, 'measures': measures,
                       'partitions': [{'name': table_name, 'mode': 'import', 'source': {'type': 'm', 'expression': expression}}]})
        inputs.append({'name': table_name, 'columns': source['columns'], 'rows': rows})
    relations = []
    index = {t['name']: t for t in inputs}
    if not isinstance(spec['relationships'], list) or len(spec['relationships']) > 12:
        raise ValueError('Relationship budget exceeded')
    seen_relations = set()
    for relation in spec['relationships']:
        if set(relation) != {'fromTable', 'fromColumn', 'toTable', 'toColumn'}:
            raise ValueError('Only active many-to-one relationships are supported')
        endpoints = []
        for prefix in ('from', 'to'):
            table = index.get(relation[prefix + 'Table'])
            if not table:
                raise ValueError('Unknown relationship table')
            matches = [i for i, c in enumerate(table['columns']) if c['name'] == relation[prefix + 'Column']]
            if not matches:
                raise ValueError('Unknown relationship column')
            i = matches[0]
            endpoints.append((table['columns'][i]['type'], [row[i] for row in table['rows']]))
        if endpoints[0][0] != endpoints[1][0] or None in endpoints[1][1] or len(set(endpoints[1][1])) != len(endpoints[1][1]):
            raise ValueError('Invalid relationship key')
        if not set(endpoints[0][1]) <= set(endpoints[1][1]):
            raise ValueError('Orphan relationship keys')
        rh = digest(relation)
        if rh in seen_relations:
            raise ValueError('Duplicate relationship')
        seen_relations.add(rh)
        relations.append(dict(relation, name=rh, fromCardinality='many', toCardinality='one', crossFilteringBehavior='oneDirection', isActive=True))
    model = {'compatibilityLevel': 1600, 'model': {'culture': 'en-US', 'defaultPowerBIDataSourceVersion': 'powerBI_V3',
             'tables': tables, 'relationships': relations}}
    parts = [{'path': path, 'payload': base64.b64encode(encoded(value)).decode(), 'payloadType': 'InlineBase64'}
             for path, value in [('model.bim', model), ('definition.pbism', {'version': '1.0', 'settings': {}})]]
    body = {'format': 'isolated-import-v1', 'spec': spec, 'inputs': inputs, 'definition': {'parts': parts},
            'input_hash': digest(inputs), 'model_hash': digest(model)}
    return dict(body, bundle_hash=digest(body))


def validate(bundle):
    rebuilt = build(bundle['spec'])
    if encoded(rebuilt) != encoded(bundle):
        raise ValueError('Fixture artifact differs from compiled inputs')
    return rebuilt


def query(table):
    name(table['name'])
    columns = ', '.join('"c' + str(i) + '", \'' + table['name'] + '\'[' + name(c['name']) + ']'
                        for i, c in enumerate(table['columns']))
    # A sentinel above the admitted fixture size exposes extra remote rows.
    return 'EVALUATE TOPN(1001, SELECTCOLUMNS(\'' + table['name'] + '\', ' + columns + '))'


def verify_table(table, response):
    if response.get('error') or len(response.get('results', [])) != 1:
        raise ValueError('Query failed or returned ambiguous results')
    result = response['results'][0]
    if result.get('error') or len(result.get('tables', [])) != 1:
        raise ValueError('Query failed or returned ambiguous tables')
    output = result['tables'][0]
    if output.get('error') or not isinstance(output.get('rows'), list) or len(output['rows']) > 1000:
        raise ValueError('Incomplete or oversized readback')
    keys = ['[c' + str(i) + ']' for i in range(len(table['columns']))]
    actual = []
    for row in output['rows']:
        if set(row) != set(keys):
            raise ValueError('Readback columns or explicit nulls missing')
        actual.append([cell(row[k], c['type']) for k, c in zip(keys, table['columns'])])
    same = Counter(map(encoded, actual)) == Counter(map(encoded, table['rows']))
    return {'table': table['name'], 'matches': same, 'expected_rows': len(table['rows']), 'observed_rows': len(actual),
            'observed_hash': digest(sorted(actual, key=encoded)), 'generation_proven': False}


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    bundle = build(json.loads(args.input.read_text(encoding='utf-8')))
    # Exclusive creation prevents accidentally overwriting a reviewed artifact.
    with args.output.open('xb') as handle:
        handle.write(encoded(bundle))
    print(json.dumps({k: bundle[k] for k in ('bundle_hash', 'input_hash', 'model_hash')}))
