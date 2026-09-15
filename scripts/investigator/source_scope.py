"""Typed SQL predicates over catalog columns and bound NVARCHAR parameters.

Numeric/date conversions apply to parameters. No caller-provided SQL/type syntax.
Diagnostic type compatibility is not DAX/SQL semantic equivalence.
"""
from decimal import Decimal, localcontext

from .filter_scope import scalar
from .onboarding import fields

VERSION = 'typed-source-scope-v1'
STRINGS = {'varchar', 'nvarchar', 'char', 'nchar'}
INTEGER_RANGES = {'tinyint': (0, 255), 'smallint': (-32768, 32767),
                  'int': (-2147483648, 2147483647), 'bigint': (-2**63, 2**63-1)}


def kind(metadata):
    sql_type = metadata.get('data_type')
    if sql_type in STRINGS:return 'string'
    if sql_type in INTEGER_RANGES:return 'int64'
    if sql_type in {'decimal', 'numeric', 'money', 'smallmoney'}:return 'decimal'
    if sql_type in {'date', 'datetime2'}:return 'dateTime'
    if sql_type == 'bit':return 'boolean'
    raise ValueError('Unsupported SQL filter type')


def parameter(value, metadata):
    sql_type = metadata['data_type']; value_kind = kind(metadata)
    _, parsed = scalar(value, value_kind, allow_blank=False)
    if value_kind == 'string':
        if len(value.encode('utf-16-le')) > 400:raise ValueError('Source UTF-16 parameter budget exceeded')
        return value, None
    if value_kind == 'int64':
        low, high = INTEGER_RANGES[sql_type]
        if not low <= parsed <= high:raise ValueError('Value exceeds SQL integer range')
        return str(value), sql_type
    if value_kind == 'boolean':return '1' if value else '0', 'bit'
    if value_kind == 'dateTime':
        if sql_type == 'date' and (parsed.hour or parsed.minute or parsed.second):
            raise ValueError('Date column cannot preserve a time endpoint')
        return parsed.isoformat(timespec='seconds'), sql_type
    scale = 4 if sql_type in {'money', 'smallmoney'} else metadata.get('scale')
    precision = 19 if sql_type == 'money' else 10 if sql_type == 'smallmoney' else metadata.get('precision')
    if type(scale) is not int or type(precision) is not int or not 0 <= scale <= precision <= 38:
        raise ValueError('Exact SQL precision and scale required')
    with localcontext() as ctx:
        ctx.prec=80
        scaled=parsed * (10**scale)
        if scaled != scaled.to_integral_value():raise ValueError('Parameter would round at SQL scale')
        if abs(parsed) >= Decimal(10)**(precision-scale):raise ValueError('Parameter exceeds SQL precision')
    if sql_type == 'smallmoney' and not Decimal('-214748.3648') <= parsed <= Decimal('214748.3647'):
        raise ValueError('Parameter exceeds smallmoney range')
    return value, f'decimal({precision},{scale})'


def compile_filter(spec, metadata, reference, offset):
    fields(spec, ['column_id', 'operator', 'values'])
    values = spec['values']; operator = spec['operator']; value_kind = kind(metadata)
    if not isinstance(values, list) or not 1 <= len(values) <= 50:raise ValueError('Filter values outside budget')
    if operator not in {'in', 'range'}:raise ValueError('Unsupported SQL filter operator')
    parsed = [scalar(v, value_kind, allow_blank=operator=='in')[1] for v in values]
    if len(set(parsed)) != len(parsed):raise ValueError('Duplicate filter values')
    if operator == 'range' and (value_kind not in {'dateTime', 'int64', 'decimal'} or len(values)!=2 or parsed[0]>=parsed[1]):
        raise ValueError('Range requires two increasing numeric/date endpoints')
    parameters=[]; refs=[]
    for value in values:
        if value is None:continue
        encoded, target = parameter(value, metadata)
        name = '@p'+str(offset+len(parameters))
        parameters.append({'name':name, 'value':encoded})
        refs.append(name if target is None else f'CONVERT({target},{name},126)' if value_kind=='dateTime' else f'CAST({name} AS {target})')
    if operator == 'range':
        return f'({reference}>={refs[0]} AND {reference}<{refs[1]})', parameters
    clauses = [reference+' IN ('+','.join(refs)+')'] if refs else []
    if None in values:clauses.append(reference+' IS NULL')
    return '('+' OR '.join(clauses)+')', parameters


def describe(metadata):
    try:
        value_kind=kind(metadata)
        if metadata.get('computed_definition'):raise ValueError('Computed filter unsupported')
        if value_kind=='decimal':parameter('0',metadata)
    except ValueError:return {'state':'UNSUPPORTED','operators':[]}
    return {'state':'SUPPORTED','value_kind':value_kind,
            'operators':['in','range'] if value_kind in {'dateTime','int64','decimal'} else ['in'],
            'null_semantics':'SQL NULL; not certified equivalent to DAX BLANK'}
