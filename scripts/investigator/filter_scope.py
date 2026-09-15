"""Metadata-bound DAX filter literals. No SQL/DAX supplied by a caller."""
from datetime import datetime
from decimal import Decimal
import re

from .onboarding import fields

VERSION = 'typed-scope-v1'
SUPPORTED = {'string', 'int64', 'decimal', 'boolean', 'dateTime'}


def scalar(value, kind, allow_blank=True):
    if kind not in SUPPORTED:
        raise ValueError('Column type is not supported')
    if value is None:
        if not allow_blank:
            raise ValueError('BLANK is not a range endpoint')
        return 'BLANK()', None
    if kind == 'string':
        if not isinstance(value, str) or len(value) > 200 or any(ord(c) < 32 for c in value):
            raise ValueError('Expected bounded string')
        return '"' + value.replace('"', '""') + '"', value
    if kind == 'boolean':
        if type(value) is not bool:
            raise ValueError('Expected JSON boolean')
        return 'TRUE()' if value else 'FALSE()', value
    if kind == 'int64':
        if type(value) is not int or abs(value) > 2**53 - 1:
            raise ValueError('Integer exceeds exact diagnostic literal budget')
        return str(value), value
    if kind == 'decimal':
        # Fixed-decimal metadata maps to Currency: four fractional digits and
        # signed 64-bit scaled storage. Floats are never accepted as exact input.
        if not isinstance(value, str) or not re.fullmatch(r'-?(?:0|[1-9][0-9]{0,14})(?:\.[0-9]{1,4})?', value):
            raise ValueError('Expected fixed-decimal text, at most four places')
        parsed = Decimal(value)
        if not Decimal('-922337203685477.5808') <= parsed <= Decimal('922337203685477.5807'):
            raise ValueError('Fixed decimal outside range')
        if abs(parsed) > Decimal('1000000000'):
            raise ValueError('Decimal exceeds exact diagnostic literal budget')
        return 'CURRENCY(' + value + ')', parsed
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}(?:T[0-9]{2}:[0-9]{2}:[0-9]{2})?', value):
        raise ValueError('Expected model-local ISO date or second-resolution datetime')
    parsed = datetime.fromisoformat(value)
    if parsed.year < 1900:
        raise ValueError('Date outside supported range')
    expression = f'DATE({parsed.year},{parsed.month},{parsed.day})'
    if parsed.hour or parsed.minute or parsed.second:
        expression += f'+TIME({parsed.hour},{parsed.minute},{parsed.second})'
    return '(' + expression + ')', parsed


def compile_filter(spec, metadata, reference):
    fields(spec, ['column_id', 'operator', 'values'])
    kind = metadata.get('dataType')
    values = spec['values']
    if not isinstance(values, list) or not 1 <= len(values) <= 50:
        raise ValueError('Filter values outside budget')
    operator = spec['operator']
    if operator == 'in':
        parsed = [scalar(value, kind) for value in values]
        # Reject semantic duplicates, including alternative decimal/date text.
        if len(set(value for _, value in parsed)) != len(parsed):
            raise ValueError('Duplicate filter values')
        return 'TREATAS({' + ','.join(literal for literal, _ in parsed) + '},' + reference + ')'
    if operator != 'range' or kind not in {'int64', 'decimal', 'dateTime'} or len(values) != 2:
        raise ValueError('Unsupported filter operator or range shape')
    lower, lo = scalar(values[0], kind, allow_blank=False)
    upper, hi = scalar(values[1], kind, allow_blank=False)
    if lo >= hi:
        raise ValueError('Range must have increasing endpoints')
    # One predicate per column avoids competing CALCULATE replacements. BLANK
    # exclusion is explicit because DAX comparisons can coerce BLANK to zero.
    return ('FILTER(ALL(' + reference + '),NOT(ISBLANK(' + reference + '))&&' +
            reference + '>=' + lower + '&&' + reference + '<' + upper + ')')


def catalog(model):
    context = model.get('context') or {}
    reports = context.get('reports') or []
    assets = reports[0]['model_assets'] if reports else []
    columns = []
    for asset in assets:
        if asset['kind'] != 'SemanticColumn':
            continue
        kind = asset['metadata'].get('dataType')
        operators = ['in'] if kind in SUPPORTED else []
        if kind in {'int64', 'decimal', 'dateTime'}:
            operators.append('range')
        columns.append({'column_id': asset['id'], 'name': asset['name'], 'table_id': asset['parent_id'],
                        'data_type': kind, 'operators': operators,
                        'state': 'SUPPORTED' if operators else 'UNSUPPORTED'})
    return {'version': VERSION, 'model_id': model['id'], 'context_id': model['context_id'],
            'revision': model['revision'], 'columns': columns,
            'literal_limits': {'integer_absolute_max': 2**53 - 1, 'decimal_absolute_max': '1000000000',
                               'decimal_places': 4, 'datetime_resolution': 'second'},
            'range_semantics': 'lower inclusive, upper exclusive; BLANK excluded',
            'limitation': 'Model-local date values; no timezone conversion, date-role certification or full visual replay.'}
