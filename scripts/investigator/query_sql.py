"""Parse and bind a bounded T-SQL SELECT; never execute unvalidated text.

SQLGlot owns syntax/CTE/alias qualification. An explicit AST allowlist is the
security boundary, not a keyword regex. Native SQL remains the calculation engine.
"""
import re
from sqlglot import parse, exp
from sqlglot.errors import OptimizeError
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import traverse_scope

VERSION = 'bounded-tsql-v1'
NODES = set('Select From Table Identifier TableAlias Column Alias Star Where Group Having Order Ordered Limit Join With CTE Subquery Paren And Or Not EQ NEQ GT GTE LT LTE Is In Between Like ILike Add Sub Mul Div Mod Neg Literal Null Boolean Parameter Var Distinct Case If Cast TryCast DataType DataTypeParam Count Sum Avg Min Max Coalesce Nullif Abs Round Floor Ceil DateAdd DateDiff CurrentDate CurrentTimestamp Extract Window RowNumber Partition Offset'.split())


def compile_query(query, objects, *, max_rows=250):
    if not isinstance(query,str) or not 1<=len(query)<=16000:raise ValueError('SQL text budget exceeded')
    if type(max_rows) is not int or not 1<=max_rows<=250:raise ValueError('Invalid row budget')
    statements=parse(query,read='tsql')
    if len(statements)!=1 or not isinstance(statements[0],exp.Select):raise ValueError('One SELECT/CTE query required')
    tree=statements[0]
    if len(list(tree.walk()))>1200:raise ValueError('SQL syntax budget exceeded')
    if any(type(n).__name__ not in NODES for n in tree.walk()):raise ValueError('Unsupported SQL syntax or function')
    if any(n.args.get('recursive') for n in tree.find_all(exp.With)):raise ValueError('Recursive CTE unsupported')
    if len(list(tree.find_all(exp.Join)))>4 or len(list(tree.find_all(exp.Select)))>8:raise ValueError('Relational complexity budget exceeded')
    if any(n.args.get('offset') for n in tree.find_all(exp.Select)):raise ValueError('Offset is unsupported')
    if any(True for _ in tree.find_all(exp.Parameter)):raise ValueError('Use literal values; compiler parameterizes them')
    index={};schema={}
    for asset in objects:
        meta=asset['metadata'];key=(meta['schema_name'].casefold(),meta['name'].casefold())
        if key in index:raise ValueError('Ambiguous SQL catalog')
        index[key]=asset
        schema.setdefault(meta['schema_name'],{})[meta['name']]={c['name']:c['data_type'] for c in meta['columns'] if not c.get('computed_definition')}
    referenced=[];ambiguous=[]
    for scope in traverse_scope(tree):
        source_columns={}
        for name,source in scope.sources.items():
            if not isinstance(source,exp.Table):continue
            if source.catalog or not source.db or not isinstance(source.this,exp.Identifier):raise ValueError('Qualified approved schema/table required')
            asset=index.get((source.db.casefold(),source.name.casefold()))
            if asset is None or asset['metadata']['type_desc']!='USER_TABLE':raise ValueError('SQL object unavailable or view dependencies not validated')
            # Never allow hints, temporal/version modifiers or schema-qualified functions.
            if any(v for k,v in source.args.items() if k not in ('this','db','catalog','alias')):raise ValueError('Unsupported table modifier')
            referenced.append(asset['id'])
            source_columns[name]={c['name'].casefold() for c in asset['metadata']['columns'] if not c.get('computed_definition')}
        for column in scope.columns:
            if column.table:continue
            aliases=[alias for alias,columns in source_columns.items() if column.name.casefold() in columns]
            if len(aliases)>1:
                hint=(column.name,tuple(aliases))
                if hint not in ambiguous:ambiguous.append(hint)
    if not referenced:raise ValueError('At least one approved source asset required')
    try:qualified=qualify(tree,dialect='tsql',schema=schema,validate_qualify_columns=True,identify=True)
    except OptimizeError as exc:
        if ambiguous:
            hints=[{'column':column,'candidate_aliases':list(aliases)} for column,aliases in ambiguous[:4]]
            raise ValueError('SQL binding rejected: ambiguous unqualified columns '+repr(hints)+
                             '. Choose the intended table alias in SELECT, GROUP BY and other references; the query was not executed.') from exc
        raise
    names=qualified.named_selects
    if not 1<=len(names)<=16 or len(set(n.casefold() for n in names))!=len(names) or any(not n or n=='*' or len(n)>128 for n in names):raise ValueError('Bounded uniquely named result columns required')
    # Outer TOP is a result limit, not a scan-cost guarantee. Reject caller TOP
    # modifiers; a smaller caller limit is preserved and labelled separately.
    limit=qualified.args.get('limit');requested=None
    if limit:
        value=limit.expression
        if not isinstance(value,exp.Literal) or not value.is_int or any(v for k,v in limit.args.items() if k!='expression'):
            raise ValueError('Constant TOP without modifiers required')
        requested=int(value.this)
        if requested<1:raise ValueError('Positive TOP required')
    effective=min(requested,max_rows+1) if requested else max_rows+1
    qualified.set('limit',exp.Limit(expression=exp.Literal.number(effective)))
    parameters=[]
    for literal in list(qualified.find_all(exp.Literal)):
        # Structural integers in TOP/type precision are syntax, not data values.
        if isinstance(literal.parent,(exp.Limit,exp.DataTypeParam)):continue
        if len(literal.this)>200:raise ValueError('Parameter value budget exceeded')
        name='p'+str(len(parameters))
        parameters.append({'name':'@'+name,'value':literal.this})
        replacement=exp.Parameter(this=exp.Var(this=name))
        # NVarChar parameters preserve text; explicit casts preserve numeric
        # literal arithmetic instead of accidentally concatenating strings.
        if not literal.is_string:
            if not re.fullmatch(r'\d+(?:\.\d+)?',literal.this):raise ValueError('Unsupported numeric constant')
            replacement=exp.Cast(this=replacement,to=exp.DataType.build('DECIMAL(38,10)' if '.' in literal.this else 'BIGINT',dialect='tsql'))
        literal.replace(replacement)
    if len(parameters)>60:raise ValueError('Parameter budget exceeded')
    return {'query':qualified.sql(dialect='tsql',comments=False),'parameters':parameters,
            'asset_ids':sorted(set(referenced)),'result_columns':names,'max_rows':max_rows+1,
            'caller_limit':requested,'response_mode':'records','validator_version':VERSION,
            'limitation':'TOP limits results, not work scanned. Independent source read; no cross-system equivalence asserted.'}
