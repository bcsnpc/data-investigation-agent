"""Offline review of explicit INSERT/SELECT citations, never graph promotion.

Original proposals stay immutable. A wider supporting statement is returned as
a separate parser-derived review record, not substituted into the model quote.
"""
import hashlib
import sqlglot
from sqlglot import exp,ErrorLevel


def statements(code):
    if not isinstance(code,str) or not 1<=len(code)<=24000:raise ValueError('SQL_CITATION_CODE_BOUND')
    trees=sqlglot.parse(code,read='tsql',error_level=ErrorLevel.RAISE)
    if len(trees)!=1:raise ValueError('SQL_CITATION_SINGLE_RECIPE_REQUIRED')
    tree=trees[0]
    if isinstance(tree,exp.Create) and tree.args.get('kind')=='PROCEDURE' and isinstance(tree.expression,exp.Block):
        body=tree.expression.expressions
        if any(not isinstance(item,(exp.Delete,exp.Insert,exp.EndStatement))for item in body):
            raise ValueError('SQL_CITATION_CONTROL_FLOW_UNSUPPORTED')
    elif not isinstance(tree,exp.Insert):raise ValueError('SQL_CITATION_FORM_UNSUPPORTED')
    inserts=list(tree.find_all(exp.Insert))
    if len(inserts)!=1:raise ValueError('SQL_CITATION_SINGLE_INSERT_REQUIRED')
    tokens=sqlglot.tokenize(code,read='tsql');starts=[i for i,t in enumerate(tokens)if t.token_type.name=='INSERT']
    if len(starts)!=1:raise ValueError('SQL_CITATION_INSERT_TOKEN_AMBIGUOUS')
    first=starts[0];ends=[t.end+1 for t in tokens[first:]if t.token_type.name=='SEMICOLON']
    if not ends:raise ValueError('SQL_CITATION_TERMINATED_STATEMENT_REQUIRED')
    start,end=tokens[first].start,ends[0]
    insert=sqlglot.parse_one(code[start:end],read='tsql',error_level=ErrorLevel.RAISE)
    if not isinstance(insert,exp.Insert) or insert.sql(dialect='tsql')!=inserts[0].sql(dialect='tsql'):
        raise ValueError('SQL_CITATION_STATEMENT_DIFFERS')
    if not isinstance(insert.this,exp.Schema) or not isinstance(insert.expression,exp.Select):
        raise ValueError('SQL_CITATION_EXPLICIT_INSERT_SELECT_REQUIRED')
    select=insert.expression
    if any(select.args.get(k)for k in ('with_','where','group','having','qualify','limit','distinct')):
        raise ValueError('SQL_CITATION_SELECT_FORM_UNSUPPORTED')
    def table(value):
        if not isinstance(value,exp.Table)or not value.db or not value.name:raise ValueError('SQL_CITATION_DECLARED_TABLE_REQUIRED')
        return '.'.join(p for p in (value.catalog,value.db,value.name)if p)
    target=table(insert.this.this)
    source=select.args.get('from_')
    if source is None or not isinstance(source.this,exp.Table):raise ValueError('SQL_CITATION_SOURCE_REQUIRED')
    tables=[source.this]+[j.this for j in select.args.get('joins',[])]
    aliases={}
    for item in tables:
        name=table(item);alias=item.alias_or_name
        if alias in aliases:raise ValueError('SQL_CITATION_ALIAS_AMBIGUOUS')
        aliases[alias]=name
    def column(value):
        if isinstance(value,exp.Alias):value=value.this
        if not isinstance(value,exp.Column)or value.is_star or value.db or value.catalog:
            raise ValueError('SQL_CITATION_DIRECT_COLUMN_REQUIRED')
        if value.table:
            if value.table not in aliases:raise ValueError('SQL_CITATION_ALIAS_UNRESOLVED')
            source_table=aliases[value.table]
        elif len(aliases)==1:source_table=next(iter(aliases.values()))
        else:raise ValueError('SQL_CITATION_UNQUALIFIED_COLUMN_AMBIGUOUS')
        return source_table+'.'+value.name
    destinations=insert.this.expressions
    if len(destinations)!=len(select.expressions)or any(not isinstance(v,exp.Identifier)for v in destinations):
        raise ValueError('SQL_CITATION_COLUMN_ORDER_REQUIRED')
    mappings={('COPIED_TO',column(src),target+'.'+dst.name)for src,dst in zip(select.expressions,destinations)}
    mappings|={('DERIVED_IN_STEP',table(item),target)for item in tables}
    for join in select.args.get('joins',[]):
        condition=join.args.get('on')
        if not isinstance(condition,exp.EQ):raise ValueError('SQL_CITATION_JOIN_FORM_UNSUPPORTED')
        mappings.add(('JOINED_VIA',column(condition.this),column(condition.expression)))
    return {'start':start,'end':end,'quote':code[start:end]},mappings


def review(task,edges):
    code=task['code'];hash=hashlib.sha256(code.encode()).hexdigest()
    if hash!=task['definition_hash']:raise ValueError('SQL_CITATION_SOURCE_HASH_DIFFERS')
    statement,mappings=statements(code);nodes={n['id']:n for n in task['nodes']};rows=[]
    for edge in edges:
        proof=edge['provenance'];span=proof['span'];props=edge['properties']
        if proof['definition_hash']!=hash or proof['source_id']!=task['source_id']:
            raise ValueError('SQL_CITATION_PROPOSAL_SOURCE_DIFFERS')
        start,end=span.get('start'),span.get('end')
        if (span.get('kind')!='TEXT' or type(start)is not int or type(end)is not int
                or not 0<=start<end<=len(code) or code[start:end]!=props['quote']):
            raise ValueError('SQL_CITATION_ORIGINAL_QUOTE_DIFFERS')
        if edge['source']not in nodes or edge['target']not in nodes:raise ValueError('SQL_CITATION_ENDPOINT_OUTSIDE_SLICE')
        key=(edge['kind'],nodes[edge['source']]['label'],nodes[edge['target']]['label'])
        if key not in mappings:raise ValueError('SQL_CITATION_MAPPING_NOT_SUPPORTED')
        covers=span['start']<=statement['start'] and span['end']>=statement['end']
        rows.append({'original_edge_id':edge['id'],'original_quote_adequate':covers,
            'mapping_supported_by_exact_statement':True,'definition_hash':hash,
            'derived_statement':statement,'derivation':'SQLGLOT_EXPLICIT_INSERT_SELECT',
            'parser_version':sqlglot.__version__,'confidence_ceiling':'INFERRED',
            'execution_established':False,'deployment_binding':'NOT_ESTABLISHED',
            'graph_publication':'NOT_PERFORMED','original_proposal_modified':False})
    return rows
