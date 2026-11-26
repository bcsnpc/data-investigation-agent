"""Read-only metadata on an already admitted endpoint, without new credentials.

Catalog objects are database metadata, not invented graph data tables. The route
anchor is retained separately from the named metadata targets in every record.
"""
import re


def _bound(query, layer, rows, targets):
    anchors=[a['id'] for a in layer['objects'][:1]]
    if not anchors:raise ValueError('METADATA_ADMITTED_ROUTE_REQUIRED')
    return {'query':query,'compiled_read':query,'parameters':[],'asset_ids':anchors,
            'max_rows':rows+1,'validator_version':'read-only-metadata-v1',
            'metadata_scope':{'targets':targets,'route_anchor_only':True,
                              'not_a_business_table_read':True}}


def sql(text, layer, rows):
    from sqlglot import parse,exp
    from .query_sql import NODES
    statements=parse(text,read='tsql')
    if len(statements)!=1 or not isinstance(statements[0],exp.Select):return None
    tree=statements[0];tables=list(tree.find_all(exp.Table))
    metadata=[t for t in tables if t.db.casefold() in ('sys','information_schema')]
    scalar_nodes={'ObjectId','ObjectName','SchemaName','CurrentDatabase','National'}
    scalar_functions={'DB_ID','DB_NAME','SCHEMA_ID','SCHEMA_NAME','OBJECT_ID','OBJECT_NAME',
                      'OBJECT_SCHEMA_NAME','COLUMNPROPERTY','COL_LENGTH','HAS_PERMS_BY_NAME',
                      'DATABASEPROPERTYEX','SERVERPROPERTY','IS_ROLEMEMBER'}
    scalar_metadata=not tables and any(type(n).__name__ in scalar_nodes-{'National'} or
        isinstance(n,exp.Anonymous)and n.name.upper()in scalar_functions for n in tree.walk())
    if not metadata and not scalar_metadata:return None
    # Never let a metadata spelling turn an unadmitted business table into a
    # permitted source. Join catalog views together; read data separately.
    aliases={c.alias_or_name.casefold() for c in tree.find_all(exp.CTE)}
    if any(t not in metadata and (t.db or t.name.casefold() not in aliases) for t in tables):
        raise ValueError('METADATA_AND_BUSINESS_TABLE_READS_MUST_BE_SEPARATE')
    allowed=NODES|scalar_nodes|{'Anonymous','DBName'}
    if len(list(tree.walk()))>1200 or {type(n).__name__ for n in tree.walk()}-allowed:
        raise ValueError('UNSUPPORTED_METADATA_READ_SYNTAX')
    if any(w.args.get('recursive') for w in tree.find_all(exp.With)):
        raise ValueError('RECURSIVE_METADATA_READ_REFUSED')
    for table in metadata:
        if table.catalog or any(v for k,v in table.args.items() if k not in ('this','db','catalog','alias')):
            raise ValueError('METADATA_CURRENT_DATABASE_ONLY')
        if not isinstance(table.this,exp.Identifier):
            if not (table.db.casefold()=='sys' and isinstance(table.this,exp.Anonymous)
                    and re.fullmatch(r'dm_[a-z0-9_]+',table.this.name,re.I)):
                raise ValueError('METADATA_FUNCTION_REFUSED')
    safe_scalar=scalar_functions
    for function in tree.find_all(exp.Anonymous):
        if function.name.upper() in safe_scalar:continue
        if (isinstance(function.parent,exp.Table) and function.parent in metadata
                and function.parent.db.casefold()=='sys' and re.fullmatch(r'dm_[a-z0-9_]+',function.name,re.I)):continue
        raise ValueError('METADATA_FUNCTION_REFUSED')
    if list(tree.find_all(exp.Parameter)):raise ValueError('METADATA_CALLER_PARAMETERS_REFUSED')
    if any(len(n.this)>4000 for n in tree.find_all(exp.Literal)):raise ValueError('METADATA_LITERAL_BOUND')
    limit=tree.args.get('limit');requested=rows+1
    if limit:
        value=limit.expression
        if (not isinstance(value,exp.Literal) or not value.is_int or int(value.this)<1
                or any(v for k,v in limit.args.items() if k!='expression')):
            raise ValueError('CONSTANT_METADATA_TOP_REQUIRED')
        requested=min(requested,int(value.this))
    tree.set('limit',exp.Limit(expression=exp.Literal.number(requested)))
    # SQLGlot serializes parsed literals, including N'...', rather than joining
    # caller strings into executable text. No command/INTO/EXEC AST is admitted.
    columns=[item.alias_or_name for item in tree.expressions]
    if any(isinstance(item,exp.Star) or isinstance(item,exp.Column) and isinstance(item.this,exp.Star) for item in tree.expressions):
        columns=[]  # Native cursor supplies metadata schema after guarded read.
    elif not columns or any(not name for name in columns) or len(set(columns))!=len(columns):
        raise ValueError('METADATA_EXPLICIT_UNIQUE_RESULT_COLUMNS_REQUIRED')
    bound=_bound(tree.sql(dialect='tsql',comments=False),layer,rows,
                 [t.sql(dialect='tsql',comments=False) for t in metadata]or['CURRENT_DATABASE_METADATA_SCALAR'])
    bound['result_columns']=columns
    return bound


def compiled_control_objects(payload):
    """Revalidate an investigation metadata read at the transport boundary.

    The caller's metadata flag conveys no authority. The gateway must still
    admit CATALOG, the connection, and every existing user-object route anchor.
    """
    try:
        anchors=payload['read_only_objects'];limit=payload['max_rows']
        if (not isinstance(anchors,list) or not anchors or
                any(not isinstance(a,str) or not a for a in anchors) or
                type(limit)is not int or not 2<=limit<=251 or
                payload.get('parameters')!=[]):return None
        bound=sql(payload['query'],{'objects':[{'id':a}for a in anchors]},limit-1)
        if bound is None or any(payload.get(k)!=bound[k]
                for k in ('query','parameters','max_rows','result_columns')):return None
        return anchors
    except (KeyError,TypeError,ValueError):
        return None


def dax_rowset_expression(text):
    """Read-only INFO rowsets with projection and literal TOPN composition.

    Projection references bind to documented rowset columns, never model
    measures. Unknown INFO schemas can be read directly, not projected using
    unbound [Measure] references. Filters/joins require separate grammar work.
    """
    from .semantic_graph import tokenize
    tokens,gaps=tokenize(text)
    if gaps or not tokens or tokens[0][1].upper()!='EVALUATE':return None
    if not any(k=='name' and v.upper()=='INFO' for k,v in tokens):return None
    if len(tokens)>1600:raise ValueError('DAX_METADATA_TOKEN_BOUND')
    columns={'INFO.PARTITIONS':set(name.casefold() for name in (
        'ID','TableID','Name','Description','DataSourceID','QueryDefinition','State',
        'Type','PartitionStorageID','Mode','DataView','ModifiedTime','RefreshedTime',
        'SystemFlags','ErrorMessage','RetainDataTillForceCalculate','RangeStart',
        'RangeEnd','RangeGranularity','RefreshBookmark','QueryGroupID',
        'ExpressionSourceID','MAttributes'))}
    position=1;targets=[]
    def take(expected=None):
        nonlocal position
        if position>=len(tokens) or expected is not None and tokens[position][1].upper()!=expected:
            raise ValueError('DAX_METADATA_READ_GRAMMAR')
        value=tokens[position];position+=1;return value
    def table(depth=0):
        if depth>12:raise ValueError('DAX_METADATA_NESTING_BOUND')
        kind,name=take();name=name.upper()
        if kind!='name':raise ValueError('DAX_INFO_ROWSET_REQUIRED')
        if name=='INFO':
            parts=[name]
            while position<len(tokens) and tokens[position][1]=='.':
                take('.');part_kind,part=take()
                if part_kind!='name':raise ValueError('DAX_INFO_ROWSET_REQUIRED')
                parts.append(part.upper())
            if not 2<=len(parts)<=3:raise ValueError('DAX_INFO_ROWSET_REQUIRED')
            take('(');args=[]
            if position<len(tokens) and tokens[position][1]!=')':
                while True:
                    arg_kind,arg=take()
                    if arg_kind not in ('string','number'):raise ValueError('DAX_INFO_LITERAL_RESTRICTIONS_ONLY')
                    args.append(arg)
                    if position<len(tokens) and tokens[position][1]==',':take(',')
                    else:break
            take(')')
            if len(args)%2:raise ValueError('DAX_INFO_RESTRICTION_PAIRS_REQUIRED')
            target='.'.join(parts);targets.append(target)
            return target+'('+','.join(args)+')',columns.get(target)
        if name=='SELECTCOLUMNS':
            take('(');source,known=table(depth+1);parts=[source];projected=set()
            while position<len(tokens) and tokens[position][1]==',':
                take(',');alias_kind,alias=take();take(',');ref_kind,ref=take()
                if alias_kind!='string' or ref_kind!='ref' or known is None:
                    raise ValueError('DAX_METADATA_PROJECTION_REQUIRES_DOCUMENTED_ROWSET_COLUMNS')
                field=ref[1:-1].replace(']]',']').casefold()
                if field not in known:raise ValueError('DAX_METADATA_COLUMN_NOT_IN_ROWSET')
                projected.add(alias[1:-1].replace('""','"').casefold());parts.extend([alias,ref])
            take(')')
            if not projected:raise ValueError('DAX_METADATA_PROJECTION_REQUIRED')
            return 'SELECTCOLUMNS('+','.join(parts)+')',projected
        if name=='TOPN':
            take('(');count_kind,count=take();take(',')
            if count_kind!='number' or not count.isdigit() or not 1<=int(count)<=251:
                raise ValueError('DAX_METADATA_CONSTANT_TOP_BOUND')
            source,known=table(depth+1);take(')')
            return 'TOPN('+count+','+source+')',known
        raise ValueError('DAX_METADATA_AND_BUSINESS_READS_MUST_BE_SEPARATE')
    expression,_=table()
    if position!=len(tokens):raise ValueError('ONE_DAX_INFO_READ_REQUIRED')
    return expression,targets


def dax(text, layer, rows):
    parsed=dax_rowset_expression(text)
    if parsed is None:return None
    expression,targets=parsed
    return _bound('EVALUATE TOPN('+str(rows+1)+','+expression+')',layer,rows,targets)


def spark(text, layer, rows):
    # DESCRIBE has dialect-specific parser gaps. This deliberately small read
    # grammar admits identifiers, never paths, commands, SQL clauses or code.
    word=r'(?:[A-Za-z_][A-Za-z_0-9]*|`(?:[^`]|``)+`)'
    match=re.fullmatch(r'\s*(?:DESCRIBE|DESC)\s+(?:(HISTORY|DETAIL|TABLE(?:\s+EXTENDED)?|EXTENDED)\s+)?('+word+r')\.('+word+r')(?:\s+LIMIT\s+([1-9][0-9]*))?\s*;?\s*',text,re.I)
    if not match:return None
    kind=(match[1]or'TABLE').upper();schema=match[2].strip('`').replace('``','`');name=match[3].strip('`').replace('``','`')
    objects=[a for a in layer['objects'] if a['metadata']['schema_name'].casefold()==schema.casefold()
             and a['metadata']['name'].casefold()==name.casefold()]
    if len(objects)!=1:raise ValueError('DESCRIBE_OBJECT_OUTSIDE_ADMITTED_GRAPH')
    if match[4] and kind!='HISTORY':raise ValueError('DESCRIBE_LIMIT_ONLY_FOR_HISTORY')
    query='DESCRIBE '+kind+' `'+schema.replace('`','``')+'`.`'+name.replace('`','``')+'`'
    if kind=='HISTORY':query+=' LIMIT '+str(min(int(match[4]or rows+1),rows+1))
    bound=_bound(query,layer,rows,[schema+'.'+name]);bound['asset_ids']=[objects[0]['id']]
    if kind=='HISTORY':bound['metadata_scope']['history_limit']=min(int(match[4]or rows+1),rows+1)
    return bound
