"""Adapter-owned expression forms; unknown or mislabelled forms fail closed."""
from sqlglot import parse_one, exp
from ..query_dax import Parser, compile_query as dax_compile
from ..query_sql import compile_query as sql_compile


def dax_form(expression, form, catalog):
    if form not in ('PREDICATE','TABLE_FILTER'):raise ValueError('Unknown filter form')
    parser=Parser(expression,catalog,strict_forms=True)
    _,kind=parser.expression()
    if parser.peek():raise ValueError('Filter form requires one expression, not a statement')
    expected='boolean' if form=='PREDICATE' else 'table'
    if kind!=expected:
        raise ValueError('FILTER_FORM_MISMATCH: declared '+form+'; observed '+kind)
    return expression


def dax_quantity(measure, column, expression, form, catalog):
    dax_form(expression,form,catalog)
    argument='FILTER(ALL('+column+'),'+expression+')' if form=='PREDICATE' else expression
    query='EVALUATE ROW("quantity",CALCULATE('+measure+','+argument+'))'
    dax_compile(query,catalog)
    return query


def sql_filter(base_query, expression, form, *, key_pairs, catalog):
    """Only already scoped rowsets and declared key pairs; never guessed joins."""
    base=parse_one(base_query,read='tsql');condition=parse_one(expression,read='tsql')
    if not isinstance(base,exp.Select):raise ValueError('One base SELECT required')
    sql_compile(base_query,catalog)
    if form=='PREDICATE':
        if not isinstance(condition,(exp.Predicate,exp.And,exp.Or,exp.Not)):
            raise ValueError('FILTER_FORM_MISMATCH: declared PREDICATE; not Boolean')
        result=base.where(condition,append=True)
    elif form=='TABLE_FILTER':
        if not isinstance(condition,exp.Select):
            raise ValueError('FILTER_FORM_MISMATCH: declared TABLE_FILTER; not a SELECT')
        sql_compile(expression,catalog)
        if not key_pairs or len(set(key_pairs))!=len(key_pairs):raise ValueError('Declared unique key pairs required')
        if any(right not in condition.named_selects for _,right in key_pairs):raise ValueError('Filter table key projection absent')
        # DISTINCT prevents selected-key multiplicity from multiplying base rows.
        selected=exp.select(*[exp.column(right,table='f',quoted=True) for _,right in key_pairs]).distinct().from_(condition.subquery('f'))
        terms=[]
        for left,right in key_pairs:
            matches=[column for column in base.expressions if isinstance(column,exp.Column) and column.name==left]
            if len(matches)!=1:raise ValueError('Filter join needs one declared direct base key projection')
            source=matches[0].copy();target=exp.column(right,table='selected',quoted=True)
            terms.append(exp.or_(exp.EQ(this=source.copy(),expression=target.copy()),
                exp.and_(exp.Is(this=source,expression=exp.Null()),exp.Is(this=target,expression=exp.Null()))))
        result=base.join(selected.subquery('selected'),on=exp.and_(*terms),join_type='INNER')
    else:raise ValueError('Unknown filter form')
    text=result.sql(dialect='tsql');sql_compile(text,catalog);return text
