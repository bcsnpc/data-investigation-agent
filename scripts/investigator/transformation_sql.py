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
            if statement.args.get('exists'):
                raise Unsupported('Conditional target creation cannot establish that the selected write ran')
            target=statement.this
        elif isinstance(statement,exp.Insert) and isinstance(statement.expression,exp.Select) and isinstance(statement.this,exp.Table):
            if not statement.args.get('overwrite'):
                raise Unsupported('Append writes depend on prior target state; no whole-target equivalence')
            target=statement.this
        else:raise Unsupported('SQL requires explicit CREATE TABLE AS or INSERT SELECT target')
        name='.'.join(p.name for p in target.parts)
        if name in writes:raise Unsupported('Multiple SQL writers for one target')
        writes[name]=parse_select(statement.expression.sql(dialect='spark'),catalog)
    return writes

def compile_quantity(relation,column,catalog,*,profile=None,sample=None,normalization=None,
                     string_semantics=None,source_string_semantics=None):
    """Construct expressions, then let the existing parser govern the result."""
    number=0
    def exact_strings(declaration):
        if declaration is None:
            raise Unsupported('COLLATION_UNDECLARED: string_semantics must establish code/execution string equality')
        from .string_semantics import binary
        binary(declaration)
    def string_type(value):
        return value in ('string','text','varchar','nvarchar','char','nchar')
    def binary_key(value):
        # UTF-16 on both sides, prefixed by byte length: SQL's padding rules
        # cannot make strings differing only in trailing spaces/zero bytes equal.
        text=exp.Cast(this=value.copy(),to=exp.DataType.build('NVARCHAR(MAX)',dialect='tsql'))
        length=exp.Anonymous(this='DATALENGTH',expressions=[text.copy()])
        return exp.Add(this=exp.Cast(this=length,to=exp.DataType.build('BINARY(8)',dialect='tsql')),
                       expression=exp.Cast(this=text,to=exp.DataType.build('VARBINARY(MAX)',dialect='tsql')))
    def types(plan):
        kind=plan['kind']
        if kind=='SCAN':
            known={c['name']:c.get('data_type','unknown').casefold() for c in catalog[plan['table']]['metadata']['columns']}
            return {c:known.get(c,'unknown') for c in plan['columns']}
        if kind=='JOIN':
            left,right=types(plan['left']),types(plan['right'])
            if any(not comparable(left.get(k)) or not comparable(right.get(k)) for k in plan['keys']):
                raise Unsupported('Join-key comparison semantics are not established across code and execution languages')
            return {**right,**left}
        known=types(plan['input'])
        def scalar_type(node):
            if node['kind']=='COLUMN':return known.get(node['name'],'unknown')
            if node['kind']=='LITERAL':return 'text' if isinstance(node['value'],str) else 'numeric'
            if node['kind']=='DECIMAL':return 'numeric'
            if node['kind'] in ('ADD','SUBTRACT','MULTIPLY','SUM','COUNT','MIN','MAX'):
                operands=[node[x] for x in ('left','right','operand') if x in node]
                return 'numeric' if all(comparable(scalar_type(o)) for o in operands) else 'unknown'
            return 'unknown'
        def predicates(node):
            if node['kind'] in ('EQ','NE','GT','GE','LT','LE') and any(
                    not comparable(scalar_type(node[k])) for k in ('left','right')):
                raise Unsupported('Filter comparison semantics are not established across code and execution languages')
            for key in ('left','right','operand'):
                if key in node:predicates(node[key])
        if kind in ('PROJECT','AGGREGATE'):
            if kind=='AGGREGATE' and any(not comparable(known.get(g)) for g in plan['groups']):
                if all(comparable(known.get(g)) or string_type(known.get(g)) for g in plan['groups']):
                    exact_strings(source_string_semantics)
                else:raise Unsupported('Grouping equivalence is not established across code and execution languages')
            return {c['name']:scalar_type(c['expression']) for c in plan['columns']}
        if kind=='DEDUPE' and any(not comparable(known.get(c)) for c in plan['keys']):
            if source_string_semantics is not None and all(comparable(known.get(c)) or string_type(known.get(c)) for c in plan['keys']):
                exact_strings(source_string_semantics)
                return known
            if profile is not None:
                if normalization and normalization.get('status')=='DECLARED':
                    raise Unsupported('NORMALIZATION_RENDERING_UNSUPPORTED: declared deduplication normalization has no faithful adapter renderer')
                raise Unsupported('COLLATION_UNDECLARED: comparison_normalization must establish code/execution deduplication semantics')
            raise Unsupported('Deduplication equivalence is not established across code and execution languages; no assumed string collation or padding')
        if kind=='FILTER':predicates(plan['predicate'])
        return known
    def comparable(value):
        return value in ('numeric','tinyint','smallint','int','bigint','bit','long','boolean')
    types(relation)
    def identifier(name):return exp.to_identifier(name,quoted=True)
    def scalar_sql(node,alias):
        kind=node['kind']
        if kind=='AVG':
            raise Unsupported('Average result type and precision semantics are not declared')
        if kind=='DIVIDE':
            raise Unsupported('Division result type and zero semantics are not declared; no implicit integer truncation or numeric coercion')
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
            if kind=='AGGREGATE' and plan['groups']:
                known=types(plan['input']);keys=[]
                for g in plan['groups']:
                    value=exp.column(g,table=alias,quoted=True)
                    keys.append(binary_key(value) if string_type(known.get(g)) else value)
                for i,c in enumerate(plan['columns']):
                    node=c['expression']
                    if node['kind']=='COLUMN' and node['name'] in plan['groups'] and string_type(known.get(node['name'])):
                        fields[i]=exp.alias_(exp.Min(this=scalar_sql(node,alias)),c['name'],quoted=True)
                query=exp.select(*fields).from_(table).group_by(*keys)
            return query,[c['name'] for c in plan['columns']]
        query=exp.select(*[exp.column(c,table=alias,quoted=True) for c in columns]).from_(table)
        if kind=='FILTER':query=query.where(scalar_sql(plan['predicate'],alias))
        elif kind=='DEDUPE':
            if set(plan['keys'])!=set(columns):raise Unsupported('Partial-key deduplication cannot select faithful survivors')
            known=types(plan['input'])
            if any(string_type(known.get(c)) for c in columns):
                exact_strings(source_string_semantics)
                fields=[];keys=[]
                for c in columns:
                    value=exp.column(c,table=alias,quoted=True)
                    if string_type(known.get(c)):
                        keys.append(binary_key(value))
                        # Each group is byte-identical; MIN cannot choose a
                        # different padded or case-equivalent survivor.
                        fields.append(exp.alias_(exp.Min(this=value),c,quoted=True))
                    else:keys.append(value.copy());fields.append(value)
                query=exp.select(*fields).from_(table).group_by(*keys)
            else:query=query.distinct()
        else:raise Unsupported('Unsupported relational operation')
        return query,columns
    query,columns=build(relation)
    if column not in columns:raise Unsupported('Compared column absent from expression output')
    table,alias=wrapped(query)
    value=exp.column(column,table=alias,quoted=True)
    if profile is None:
        fields=[exp.alias_(exp.Sum(this=value),'quantity',quoted=True)]
    else:
        from .binding_sample import PROFILES,SAMPLE_SCHEMA
        from jsonschema import Draft202012Validator
        if profile not in PROFILES:raise Unsupported('Unsupported target-type comparison profile')
        Draft202012Validator(SAMPLE_SCHEMA).validate(sample)
        if sample['column'] not in columns:raise Unsupported('Declared sample column absent from expression output')
        target_types=types(relation)
        sample_type=target_types.get(sample['column'],'unknown')
        if sample['kind']=='KEY_RANGE' and not comparable(sample_type):
            raise Unsupported('Declared key-range sample does not have an integral key')
        if sample['kind']=='DATE_WINDOW' and sample_type not in ('date','datetime','datetime2','timestamp'):
            raise Unsupported('SAMPLE_TYPE_UNSUPPORTED: date-window column is text, not a declared temporal type; no implicit cast or string equivalence')
        # COUNT(*) measures sample cardinality, including BLANK/NULL values.
        count=exp.Count(this=exp.Star())
        if profile=='NUMERIC':fields=[exp.alias_(exp.Sum(this=value.copy()),'sum',quoted=True),exp.alias_(count,'count',quoted=True)]
        elif profile=='TEMPORAL':fields=[exp.alias_(exp.Min(this=value.copy()),'min',quoted=True),exp.alias_(exp.Max(this=value.copy()),'max',quoted=True),exp.alias_(count,'count',quoted=True)]
        elif profile=='BOOLEAN':
            truth=exp.Case(ifs=[exp.If(this=exp.EQ(this=value.copy(),expression=exp.Literal.number(1)),true=exp.Literal.number(1))],default=exp.Null())
            fields=[exp.alias_(exp.Count(this=truth),'true_count',quoted=True),exp.alias_(count,'count',quoted=True)]
        else:
            if string_semantics is not None:
                exact_strings(string_semantics)
                key=binary_key(value)
                hashed=exp.Anonymous(this='HASHBYTES',expressions=[exp.Literal.string('SHA2_256'),key.copy()])
                prefix=exp.Substring(this=hashed,start=exp.Literal.number(1),length=exp.Literal.number(4))
                number_hash=exp.Cast(this=exp.Cast(this=prefix,to=exp.DataType.build('BIGINT')),
                                     to=exp.DataType.build('DECIMAL(38,0)',dialect='tsql'))
                fields=[exp.alias_(count,'count',quoted=True),
                        exp.alias_(exp.Count(this=exp.Distinct(expressions=[key])),'distinct_count',quoted=True),
                        exp.alias_(exp.Sum(this=number_hash),'hash_sum',quoted=True)]
            elif normalization and normalization.get('status')=='DECLARED':
                raise Unsupported('NORMALIZATION_RENDERING_UNSUPPORTED: distinct/content profile has no faithful adapter renderer for the declared normalization')
            else:
                raise Unsupported('COLLATION_UNDECLARED: comparison_normalization is required for distinct/content comparison; no implicit padding or case equivalence')
    query=exp.select(*fields).from_(table)
    if profile is not None:
        field=exp.column(sample['column'],table=alias,quoted=True)
        literal=lambda v:exp.Literal.number(v) if type(v) is int else exp.Literal.string(v)
        query=query.where(exp.And(this=exp.GTE(this=field.copy(),expression=literal(sample['lower'])),
                                 expression=(exp.LTE if sample['kind']=='KEY_RANGE' else exp.LT)(this=field.copy(),expression=literal(sample['upper']))))
    from .query_sql import compile_query
    text=query.sql(dialect='tsql')
    compile_query(text,list(catalog.values()),max_rows=1)
    return text
