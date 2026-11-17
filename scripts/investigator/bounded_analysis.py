"""Deterministic comparisons over bounded, native query results.

Queries are supplied by the investigator and pass through Queries.run. These
operations describe the queried scopes; they do not invent equivalence or a
causal explanation, and truncation never proves an absent key.
"""
from decimal import Decimal, InvalidOperation, localcontext
from copy import deepcopy
from functools import wraps


def exact_decimal(fn):
    @wraps(fn)
    def run(*args,**kwargs):
        with localcontext() as context:
            context.prec=256
            return fn(*args,**kwargs)
    return run


def _rows(record):
    if record.get('status') != 'SUCCEEDED':
        raise ValueError('ANALYSIS_NEEDS_SUCCESSFUL_NATIVE_READ')
    rows = record['result']['rows']
    if len(rows) > 250 or any(not isinstance(row, dict) for row in rows):
        raise ValueError('ANALYSIS_ROW_BOUND_OR_SHAPE')
    return rows


def _key(row, fields):
    if not 1 <= len(fields) <= 3 or len(set(fields)) != len(fields):
        raise ValueError('ANALYSIS_KEY_FIELDS')
    if any(field not in row for field in fields):
        raise ValueError('ANALYSIS_KEY_COLUMN_MISSING')
    from .estate_graph_contract import canonical
    return canonical([row[field] for field in fields])


@exact_decimal
def contribution(left, right, *, dimensions, value_field, sample_limit=10):
    if type(sample_limit) is not int or not 1 <= sample_limit <= 20:
        raise ValueError('ANALYSIS_SAMPLE_BOUND')
    def group(record):
        result = {}
        for row in _rows(record):
            key = _key(row, dimensions)
            if value_field not in row or isinstance(row[value_field], bool) or row[value_field] is None:
                raise ValueError('CONTRIBUTION_NUMERIC_CELL_REQUIRED')
            try:
                value = Decimal(str(row[value_field]))
            except (InvalidOperation, TypeError, ValueError) as error:
                raise ValueError('CONTRIBUTION_NUMERIC_CELL_REQUIRED') from error
            if not value.is_finite():
                raise ValueError('CONTRIBUTION_FINITE_CELL_REQUIRED')
            if key in result:
                raise ValueError('CONTRIBUTION_GROUP_NOT_UNIQUE')
            result[key] = (value, {field: deepcopy(row[field]) for field in dimensions})
        return result
    before, after = group(left), group(right)
    changes = []
    total = sum((row[0] for row in after.values()), Decimal(0))-sum((row[0] for row in before.values()), Decimal(0))
    absolute = Decimal(0)
    for key in before.keys() | after.keys():
        a = before.get(key, (Decimal(0), None)); b = after.get(key, (Decimal(0), None))
        delta = b[0]-a[0]; absolute += abs(delta)
        changes.append({'slice': b[1] or a[1], 'before': str(a[0]), 'after': str(b[0]), 'difference': str(delta)})
    changes.sort(key=lambda row: (-abs(Decimal(row['difference'])), str(row['slice'])))
    for row in changes:
        delta = Decimal(row['difference'])
        row['share_of_net_difference'] = str(delta/total) if total else None
        row['share_of_absolute_difference'] = str(abs(delta)/absolute) if absolute else None
    complete = not left.get('truncated') and not right.get('truncated')
    return {'query_ids': [left['id'], right['id']], 'complete_returned_groups': complete,
            'net_difference': str(total), 'absolute_difference': str(absolute),
            'ranked_slices': changes[:sample_limit], 'total_slices': len(changes),
            'qualification': 'Contribution within the two queried scopes, not a causal proof. '+
                ('No result truncation reported; native grouping scope still applies.' if complete else
                 'Truncated result: shares describe returned groups only, not the complete population.')}


def row_diff(left, right, *, keys, compare_fields, sample_limit=10):
    if type(sample_limit) is not int or not 1 <= sample_limit <= 20:
        raise ValueError('ANALYSIS_SAMPLE_BOUND')
    if not compare_fields or len(compare_fields) > 20 or len(set(compare_fields)) != len(compare_fields):
        raise ValueError('DIFF_COMPARE_FIELDS')
    def keyed(record):
        result = {}
        for row in _rows(record):
            key = _key(row, keys)
            if key in result:
                raise ValueError('DIFF_BUSINESS_KEY_NOT_UNIQUE')
            if any(field not in row for field in compare_fields):
                raise ValueError('DIFF_COMPARE_COLUMN_MISSING')
            result[key] = row
        return result
    before, after = keyed(left), keyed(right)
    missing = sorted(before.keys()-after.keys()); extra = sorted(after.keys()-before.keys())
    changed = []
    for key in sorted(before.keys() & after.keys()):
        fields = [field for field in compare_fields if before[key][field] != after[key][field]]
        if fields:
            changed.append({'key': {field: deepcopy(before[key][field]) for field in keys},
                            'fields': {field: {'before': deepcopy(before[key][field]), 'after': deepcopy(after[key][field])} for field in fields}})
    complete = not left.get('truncated') and not right.get('truncated')
    return {'query_ids': [left['id'], right['id']], 'complete_returned_scopes': complete,
            'missing_count': len(missing) if complete else None, 'extra_count': len(extra) if complete else None,
            'changed_count': len(changed), 'changed_count_scope': 'Returned matching keys only',
            'left_only_sample': [deepcopy(before[k]) for k in missing[:sample_limit]],
            'right_only_sample': [deepcopy(after[k]) for k in extra[:sample_limit]],
            'changed_sample': changed[:sample_limit],
            'qualification': 'Counts compare the two declared query scopes, not assumed equivalent populations. '+
                ('No result truncation reported.' if complete else
                 'Truncated result: unmatched sampled keys do not establish missing or extra records.')}
