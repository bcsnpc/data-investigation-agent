"""Compile enumerated cell scope through an independently verified key mapping.

This is input context, not a proof of measure semantics. The native/proposed
quantity witness still has to verify every cell. Complex SQL scopes and string
collations refuse; neither names nor quantity lineage establish a key mapping.
"""
from sqlglot import parse_one, exp
from ..translation_proposer import _binding_for


def apply(expression, applied, request, objects):
    if not applied:
        return expression
    try:
        proof = _binding_for(request)
    except (ValueError, KeyError, TypeError) as exc:
        raise NotImplementedError('Translated SQL cell scope requires verified column bindings: ' + str(exc)) from exc
    pairs = {entry['native']: entry['proposed'] for entry in proof['declaration']['columns']}
    tree = parse_one(expression, read='tsql')
    if (not isinstance(tree, exp.Select) or len(list(tree.find_all(exp.Select))) != 1
            or tree.args.get('with_') or tree.args.get('group') or tree.args.get('having')):
        raise NotImplementedError('Scoped translation requires one ungrouped relational SELECT')
    tables = list(tree.find_all(exp.Table))
    conditions = []
    for restriction in applied:
        target = pairs.get(restriction['field_id'])
        # Column identities and metadata are supplied by the discovered catalog,
        # independently of the model's expression and object display names.
        candidates = [(obj, column) for obj in objects.values()
                      for column in obj['catalog']['metadata']['columns']
                      if column.get('id') == target]
        if target is None or len(candidates) != 1:
            raise NotImplementedError('Restriction lacks one exact discovered target column binding')
        obj, column = candidates[0]
        metadata = obj['catalog']['metadata']
        occurrences = [table for table in tables if table.name.casefold() == metadata['name'].casefold()
                       and table.db.casefold() == metadata['schema_name'].casefold()]
        if len(occurrences) != 1:
            raise NotImplementedError('Restriction target is absent or has ambiguous SQL occurrences')
        if column['data_type'].casefold() not in ('tinyint', 'smallint', 'int', 'bigint'):
            raise NotImplementedError('Scoped translation needs exact integral key semantics; string collation is not inferred')
        values = restriction['values']
        if any(type(value) is not int and value is not None for value in values):
            raise NotImplementedError('Restriction values differ from verified integral key type')
        index = next(i for i, pair in enumerate(proof['declaration']['columns'])
                     if pair['native'] == restriction['field_id'])
        universe = {key[index] for key in proof['observations'][0]['keys']}
        if any(value not in universe for value in values):
            raise NotImplementedError('Cell key is outside the verified correspondence universe')
        field = exp.column(column['name'], table=occurrences[0].alias_or_name, quoted=True)
        numeric = [exp.Literal.number(value) for value in values if value is not None]
        condition = exp.In(this=field.copy(), expressions=numeric) if numeric else None
        if None in values:
            null = exp.Is(this=field.copy(), expression=exp.Null())
            condition = exp.or_(condition, null) if condition is not None else null
        if condition is None:
            condition = exp.EQ(this=exp.Literal.number(1), expression=exp.Literal.number(0))
        conditions.append(condition)
    for condition in conditions:
        tree = tree.where(condition, append=True)
    # The ordinary SQL parser/compiler performs final binding and parameterises
    # literals. No rendered query bypasses its allowlist or admission guard.
    return tree.sql(dialect='tsql')
