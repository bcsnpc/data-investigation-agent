"""Render a relational Top-N predicate over an already compiled grouped rowset.

The caller supplies the same scoped rowset and declared ordering. It cannot
substitute an unfiltered source. DAX's tie expansion is preserved on its side;
ROW_NUMBER limits the SQL side. Complete key verification detects that mismatch.
"""
from sqlglot import parse_one, exp
from ..query_sql import compile_query


def compile_ranked_sql(grouped_query, *, keys, ordering, limit, catalog):
    if type(limit) is not int or not 1 <= limit <= 62 or not keys or not ordering:
        raise ValueError('Bounded Top-N keys, ordering and N required')
    base = parse_one(grouped_query, read='tsql')
    if not isinstance(base, exp.Select): raise ValueError('One grouped SELECT required')
    compile_query(grouped_query, catalog)
    outputs = set(base.named_selects)
    if not set(keys) <= outputs or len(keys) != len(set(keys)):
        raise ValueError('Grouping keys absent or repeated')
    orders = []
    for name, direction in ordering:
        if name not in outputs or direction not in ('ASC', 'DESC'):
            raise ValueError('Ordering is not a declared rowset output')
        orders.append(exp.Ordered(this=exp.column(name, table='g', quoted=True), desc=direction == 'DESC'))
    fields = [exp.column(key, table='g', quoted=True) for key in keys]
    rank = exp.Window(this=exp.RowNumber(), order=exp.Order(expressions=orders))
    ranked = exp.select(*fields, exp.alias_(rank, 'translation_rank', quoted=True)).from_(base.subquery('g'))
    result = exp.select(*[exp.alias_(exp.column(key,table='r',quoted=True),
                            'translation_key_'+str(i),quoted=True) for i,key in enumerate(keys)]).from_(ranked.subquery('r'))
    result = result.where(exp.LTE(this=exp.column('translation_rank',table='r',quoted=True),expression=exp.Literal.number(limit)))
    text = result.sql(dialect='tsql')
    compile_query(text, catalog)
    return text
