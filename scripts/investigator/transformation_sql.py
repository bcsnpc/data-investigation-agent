"""Language parser and relational rendering; execution still uses governed SQL."""
from sqlglot import parse,parse_one,exp
from .code_static import Frame,Unsupported

def scalar(node):
    if isinstance(node,exp.Column):return {'kind':'COLUMN','name':node.name}
    if isinstance(node,exp.Literal):
        # Keep decimal literals as text until the compiler constructs a typed
        # numeric literal; avoid a float-roundtrip inventing a precision.
        return {'kind':'LITERAL','value':node.this} if node.is_string else {'kind':'DECIMAL','value':node.this}
    if isinstance(node,exp.Null):return {'kind':'LITERAL','value':None}
    if isinstance(node,exp.Boolean):return {'kind':'LITERAL','value':node.this}
    operators={exp.Add:'ADD',exp.Sub:'SUBTRACT',exp.Mul:'MULTIPLY',exp.Div:'DIVIDE',exp.EQ:'EQ',exp.NEQ:'NE',
        exp.GT:'GT',exp.GTE:'GE',exp.LT:'LT',exp.LTE:'LE',exp.And:'AND',exp.Or:'OR'}
    if type(node) in operators:return {'kind':operators[type(node)],'left':scalar(node.this),'right':scalar(node.expression)}
    functions={exp.Sum:'SUM',exp.Count:'COUNT',exp.Min:'MIN',exp.Max:'MAX',exp.Avg:'AVG',exp.Not:'NOT'}
    if type(node) in functions:
        operand={'kind':'LITERAL','value':1} if isinstance(node.this,exp.Star) else scalar(node.this)
        return {'kind':functions[type(node)],'operand':operand}
    if isinstance(node,exp.Paren):return scalar(node.this)
    raise Unsupported('SQL expression requires model proposal: '+type(node).__name__)

def parse_select(text,catalog):
    trees=parse(text,read='spark')
    if len(trees)!=1 or not isinstance(trees[0],exp.Select):raise Unsupported('Single relational SELECT required')
    query=trees[0]
    if any(query.args.get(k) for k in ('with_','limit','order','qualify','having','offset')):
        raise Unsupported('Unsupported SELECT modifier')
    source=query.args.get('from_')
    if not source or not isinstance(source.this,exp.Table):raise Unsupported('Declared table read required')
    def scan(table):
        if not isinstance(table,exp.Table):raise Unsupported('Unsupported table expression')
        name='.'.join(p.name for p in table.parts)
        if name not in catalog:raise Unsupported('Table is not declared in code catalog: '+name)
        return name,{'kind':'SCAN','table':name,'columns':list(catalog[name])}
    source_name,relation=scan(source.this);columns=dict(catalog[source_name]);aliases={source.this.alias_or_name:catalog[source_name]}
    erased_right_keys=set()
    for join in query.args.get('joins',[]):
        other,right=scan(join.this);how='LEFT' if join.side=='LEFT' else 'INNER'
        if join.side not in ('','LEFT') or join.kind not in ('','INNER','OUTER'):raise Unsupported('Unsupported join kind')
        predicate=join.args.get('on');keys=[]
        terms=list(predicate.flatten()) if isinstance(predicate,exp.And) else [predicate]
        for term in terms:
            if (not isinstance(term,exp.EQ) or not isinstance(term.this,exp.Column) or not isinstance(term.expression,exp.Column)
                    or term.this.name!=term.expression.name or not term.this.table or not term.expression.table
                    or {term.this.table,term.expression.table}!={source.this.alias_or_name,join.this.alias_or_name}):
                raise Unsupported('Join keys require explicit two-sided equality')
            keys.append(term.this.name)
        if not keys or (set(columns)&set(catalog[other]))-set(keys):raise Unsupported('Ambiguous join outputs')
        if any(k not in columns or k not in catalog[other] for k in keys):raise Unsupported('Missing join key')
        # A right key on a LEFT join can be NULL while the left key is not.
        # Never erase that distinction by translating it to the retained key.
        if how=='LEFT':erased_right_keys.update((join.this.alias_or_name,k) for k in keys)
        relation={'kind':'JOIN','left':relation,'right':right,'how':how,'keys':keys}
        columns.update({k:v for k,v in catalog[other].items() if k not in keys});aliases[join.this.alias_or_name]=catalog[other]
    # Resolve every qualified reference before removing SQL aliases in the
    # neutral representation. Unknown aliases and outer-join NULL distinctions
    # must never become plausible references to a similarly named column.
    references=list(query.expressions)+([query.args['where'].this] if query.args.get('where') else [])
    if query.args.get('group'):references+=query.args['group'].expressions
    for expression in references:
        for c in expression.find_all(exp.Column):
            if c.table and (c.table not in aliases or c.name not in aliases[c.table]):raise Unsupported('SQL qualified column is not declared')
            if (c.table,c.name) in erased_right_keys:raise Unsupported('Right-side outer-join key needs explicit representation')
            if c.name not in columns:raise Unsupported('SQL column is absent from declared inputs')
    where=query.args.get('where')
    if where:relation={'kind':'FILTER','input':relation,'predicate':scalar(where.this)}
    fields=[]
    for expression in query.expressions:
        if isinstance(expression,exp.Star):fields.extend({'name':c,'expression':{'kind':'COLUMN','name':c}} for c in columns)
        else:
            name=expression.alias_or_name
            if not name:raise Unsupported('Derived output requires explicit alias')
            fields.append({'name':name,'expression':scalar(expression.unalias())})
    group=query.args.get('group')
    aggregates=any(e.find(exp.AggFunc) for e in query.expressions)
    if group or aggregates:
        groups=[g.name for g in group.expressions] if group else []
        if group and any(not isinstance(g,exp.Column) for g in group.expressions):raise Unsupported('Expression grouping unsupported')
        relation={'kind':'AGGREGATE','input':relation,'groups':groups,'columns':fields}
    else:relation={'kind':'PROJECT','input':relation,'columns':fields}
    if query.args.get('distinct'):relation={'kind':'DEDUPE','input':relation,'keys':[f['name'] for f in fields]}
    frame=Frame({f['name']:columns.get(f['expression'].get('name'),'derived') for f in fields},{})
    frame.plan=relation;return frame

def extract_statement(text,catalog):
    statements=parse(text,read='spark');writes={}
    for statement in statements:
        if isinstance(statement,exp.Create) and statement.kind=='TABLE' and isinstance(statement.expression,exp.Select):
            target=statement.this
        elif isinstance(statement,exp.Insert) and isinstance(statement.expression,exp.Select) and isinstance(statement.this,exp.Table):target=statement.this
        else:raise Unsupported('SQL requires explicit CREATE TABLE AS or INSERT SELECT target')
        name='.'.join(p.name for p in target.parts)
        if name in writes:raise Unsupported('Multiple SQL writers for one target')
        writes[name]=parse_select(statement.expression.sql(dialect='spark'),catalog)
    return writes

def compile_quantity(relation,column,catalog):
    """Construct expressions, then let the existing parser govern the result."""
    number=0
    def identifier(name):return exp.to_identifier(name,quoted=True)
    def scalar_sql(node,alias):
        kind=node['kind']
        if kind=='COLUMN':return exp.Column(this=identifier(node['name']),table=identifier(alias))
        if kind=='DECIMAL':return exp.Literal.number(node['value'])
        if kind=='LITERAL':
            value=node['value']
            if value is None:return exp.Null()
            if type(value) is bool:return exp.Boolean(this=value)
            if isinstance(value,str):return exp.Literal.string(value)
            return exp.Literal.number(str(value))
        operators={'ADD':exp.Add,'SUBTRACT':exp.Sub,'MULTIPLY':exp.Mul,'DIVIDE':exp.Div,'EQ':exp.EQ,'NE':exp.NEQ,
            'GT':exp.GT,'GE':exp.GTE,'LT':exp.LT,'LE':exp.LTE,'AND':exp.And,'OR':exp.Or}
        if kind in operators:return operators[kind](this=scalar_sql(node['left'],alias),expression=scalar_sql(node['right'],alias))
        functions={'SUM':exp.Sum,'COUNT':exp.Count,'MIN':exp.Min,'MAX':exp.Max,'AVG':exp.Avg,'NOT':exp.Not}
        return functions[kind](this=scalar_sql(node['operand'],alias))
    def wrapped(query):
        nonlocal number
        alias='read_stage_'+str(number);number+=1
        return exp.Subquery(this=query,alias=exp.TableAlias(this=identifier(alias))),alias
    def build(plan):
        kind=plan['kind']
        if kind=='SCAN':
            asset=catalog[plan['table']];meta=asset['metadata']
            table=exp.Table(this=identifier(meta['name']),db=identifier(meta['schema_name']))
            return exp.select(*[exp.Column(this=identifier(c)) for c in plan['columns']]).from_(table),plan['columns']
        if kind=='JOIN':
            left,lc=build(plan['left']);right,rc=build(plan['right']);ls,la=wrapped(left);rs,ra=wrapped(right)
            predicate=None
            for key in plan['keys']:
                equality=exp.EQ(this=exp.column(key,table=la,quoted=True),expression=exp.column(key,table=ra,quoted=True))
                predicate=equality if predicate is None else exp.And(this=predicate,expression=equality)
            columns=lc+[c for c in rc if c not in plan['keys']]
            fields=[exp.column(c,table=la if c in lc else ra,quoted=True) for c in columns]
            return exp.select(*fields).from_(ls).join(rs,on=predicate,join_type=plan['how']),columns
        source,columns=build(plan['input']);table,alias=wrapped(source)
        if kind in ('PROJECT','AGGREGATE'):
            fields=[exp.alias_(scalar_sql(c['expression'],alias),c['name'],quoted=True) for c in plan['columns']]
            query=exp.select(*fields).from_(table)
            if kind=='AGGREGATE' and plan['groups']:query=query.group_by(*[exp.column(g,table=alias,quoted=True) for g in plan['groups']])
            return query,[c['name'] for c in plan['columns']]
        query=exp.select(*[exp.column(c,table=alias,quoted=True) for c in columns]).from_(table)
        if kind=='FILTER':query=query.where(scalar_sql(plan['predicate'],alias))
        elif kind=='DEDUPE':
            if set(plan['keys'])!=set(columns):raise Unsupported('Partial-key deduplication cannot select faithful survivors')
            query=query.distinct()
        else:raise Unsupported('Unsupported relational operation')
        return query,columns
    query,columns=build(relation)
    if column not in columns:raise Unsupported('Compared column absent from expression output')
    table,alias=wrapped(query)
    query=exp.select(exp.alias_(exp.Sum(this=exp.column(column,table=alias,quoted=True)),'quantity',quoted=True)).from_(table)
    from .query_sql import compile_query
    text=query.sql(dialect='tsql')
    compile_query(text,list(catalog.values()),max_rows=1)
    return text
