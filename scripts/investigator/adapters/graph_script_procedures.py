"""Exact same-activity procedure declarations and calls; never execution proof."""
import sqlglot
from sqlglot import exp


def attach(graph,parent,activity,index,proof):
    scripts=activity.get('typeProperties',{}).get('scripts',[])
    if not isinstance(scripts,list)or len(scripts)>256:return
    link=activity.get('linkedService',{}).get('properties',{}).get('typeProperties',{})
    if any(not isinstance(link.get(k),str)or not link[k]for k in ('artifactId','workspaceId')):return
    bound=[a for a in graph.assets.values()if a['kind']=='Warehouse'and a.get('metadata',{}).get('id')==link.get('artifactId')and a.get('metadata',{}).get('workspaceId')==link.get('workspaceId')]
    if len(bound)!=1:return
    declared_database=activity.get('typeProperties',{}).get('database')
    if declared_database is not None and declared_database!=bound[0]['name']:return
    database=bound[0]['id'];objects={};columns={}
    for aid,asset in graph.assets.items():
        if asset.get('parent_id')!=database or asset['kind']!='WarehouseTable':continue
        meta=asset.get('metadata',{});name=asset['name'];schema=meta.get('schema_name')or meta.get('reader_schema',{}).get('schema_name')
        if '.'not in name and schema:name=schema+'.'+name
        node=graph.by_asset[aid]
        objects[name]=node if name not in objects or objects[name]==node else None
    for n in graph.nodes.values():
        props=n['properties']
        if props.get('script_database')==database:
            name=props['script_name'];objects[name]=n['id']if name not in objects or objects[name]==n['id']else None
    for edge in graph.edges.values():
        if edge['kind']=='CONTAINS'and graph.nodes[edge['target']]['kind']in ('COLUMN','CALCULATED_COLUMN'):
            columns.setdefault(edge['source'],{})[graph.nodes[edge['target']]['label']]=edge['target']
    def qualified(table):
        if not isinstance(table,exp.Table)or table.catalog or not table.db:return None
        return table.db+'.'+table.name
    declarations={};calls={}
    for number,script in enumerate(scripts):
        text=script.get('text')if isinstance(script,dict)else None
        if not isinstance(text,str):continue
        try:trees=sqlglot.parse(text,read='tsql')
        except sqlglot.errors.ParseError:continue
        if trees and all(isinstance(tree,exp.Execute)and not tree.expressions for tree in trees):
            for tree in trees:
                name=qualified(tree.this)
                if name:calls.setdefault(name,[]).append(number)
            continue
        if len(trees)!=1:continue
        tree=trees[0]
        if isinstance(tree,exp.Execute)and not tree.expressions:
            name=qualified(tree.this)
            if name:calls.setdefault(name,[]).append(number)
        elif isinstance(tree,exp.Create)and tree.kind=='PROCEDURE'and isinstance(tree.this,exp.StoredProcedure)and not tree.this.expressions:
            name=qualified(tree.this.this)
            if name:declarations.setdefault(name,[]).append((number,text,tree))
    for name in sorted(calls):
        versions=declarations.get(name,[])
        # Multiple declarations, arguments, dynamic calls or cross-database
        # names never choose a convenient body.
        if len(versions)!=1:continue
        number,text,tree=versions[0];block=tree.expression
        if min(calls[name])<=number:continue
        if not isinstance(block,exp.Block):continue
        statements=[s for s in block.expressions if not isinstance(s,exp.EndStatement)]
        if not statements or any(not isinstance(s,(exp.Insert,exp.Delete))for s in statements):continue
        inserts=[s for s in statements if isinstance(s,exp.Insert)]
        if not inserts:continue
        targets={qualified(s.this.this)for s in inserts if isinstance(s.this,exp.Schema)}
        if any(s.args.get('where')or qualified(s.this)not in targets for s in statements if isinstance(s,exp.Delete)):continue
        at={**proof,'span':{'kind':'JSON_POINTER','path':f'/properties/activities/{index}/typeProperties/scripts/{number}/text'}}
        procedure=graph.add('PROCEDURE',name,[parent,'declared-procedure',index,number],at,
            {'expression':text,'language':'TSQL','procedure_database':database,'procedure_name':name,'basis':'EXACT_SAME_ACTIVITY_CREATE_AND_EXECUTE','execution_established':False})
        graph.link('CONTAINS',graph.by_asset[parent],procedure,at)
        for offset,insert in enumerate(inserts):
            target=insert.this;query=insert.expression
            if not isinstance(target,exp.Schema)or not isinstance(query,exp.Select)or query.args.get('with_')or query.find(exp.Star)or len(list(query.find_all(exp.Select)))!=1:continue
            root=objects.get(qualified(target.this));targets=[x.name for x in target.expressions]
            if root is None or len(targets)!=len(query.expressions)or not targets:continue
            aliases={};resolved=True
            for table in query.find_all(exp.Table):
                source=objects.get(qualified(table))
                if source is None or table.alias_or_name in aliases:resolved=False;break
                aliases[table.alias_or_name]=source
            if not resolved:continue
            def refs(expression):
                found=set()
                for col in expression.find_all(exp.Column):
                    options=[aliases[col.table]]if col.table in aliases else list(aliases.values())if not col.table else[]
                    matches=[columns[t][col.name]for t in options if col.name in columns.get(t,{})]
                    if len(matches)!=1:raise ValueError('UNRESOLVED_PROCEDURE_COLUMN')
                    found.add(matches[0])
                return found
            try:
                projections=[refs(p)for p in query.expressions]
                conditions=[(clause,refs(clause))for clause in [*query.find_all(exp.Join),*query.find_all(exp.Where)]]
            except ValueError:continue
            if any(n not in columns.get(root,{})for n in targets):continue
            step=graph.add('QUERY_STEP','Declared procedure INSERT SELECT',[procedure,'insert',offset],at,
                {'expression':text,'insert_index':offset,'basis':'EXACT_SAME_ACTIVITY_CREATE_AND_EXECUTE','execution_established':False})
            graph.link('CONTAINS',procedure,step,at);graph.link('DERIVED_IN_STEP',root,step,at)
            for source in sorted(set(aliases.values())):graph.link('COMPUTED_FROM',step,source,at,properties={'execution_established':False})
            for name,inputs in zip(targets,projections):
                output=columns[root][name];graph.link('DERIVED_IN_STEP',output,step,at)
                for source in sorted(inputs):graph.link('COMPUTED_FROM',output,source,at,properties={'execution_established':False})
            for position,(clause,inputs)in enumerate(conditions):
                op=graph.add('QUERY_STEP'if isinstance(clause,exp.Join)else'FILTER','Declared procedure join'if isinstance(clause,exp.Join)else'Declared procedure filter',[step,'condition',position],at,{'expression':clause.sql(dialect='tsql'),'scope':'transformation','predicate_present':True,'execution_established':False})
                graph.link('JOINED_VIA'if isinstance(clause,exp.Join)else'FILTERED_BY',root,op,at)
                for source in sorted(inputs):graph.link('COMPUTED_FROM',op,source,at)
