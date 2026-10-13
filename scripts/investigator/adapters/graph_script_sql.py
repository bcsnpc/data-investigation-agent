"""Static Script activity declarations, scoped by its explicit Warehouse ID."""
import sqlglot
from sqlglot import exp


def attach_scripts(graph,parent,activity,index,proof):
    scripts=activity.get('typeProperties',{}).get('scripts',[])
    if not isinstance(scripts,list) or len(scripts)>256:raise ValueError('Script declaration bound exceeded')
    link=activity.get('linkedService',{}).get('properties',{}).get('typeProperties',{})
    workspace,artifact=link.get('workspaceId'),link.get('artifactId')
    warehouses=[a for a in graph.assets.values() if a['kind']=='Warehouse' and
        a.get('metadata',{}).get('id')==artifact and a.get('metadata',{}).get('workspaceId')==workspace]
    database=warehouses[0]['id'] if len(warehouses)==1 else None
    objects={};columns={};db_names={}
    for aid,a in graph.assets.items():
        if a['kind'] in ('Warehouse','Lakehouse') and a.get('metadata',{}).get('workspaceId')==workspace:
            db_names.setdefault(a['name'],[]).append(aid)
        if a['kind'] in ('WarehouseTable','LakehouseTable'):
            schema=a.get('metadata',{}).get('schema_name') or a.get('metadata',{}).get('reader_schema',{}).get('schema_name')
            name=a['name'] if '.' in a['name'] else (schema+'.' if schema else '')+a['name']
            objects[(a.get('parent_id'),name)]=graph.by_asset[aid]
    for edge in graph.edges.values():
        if edge['kind']!='CONTAINS':continue
        node=graph.nodes[edge['target']]
        if node['kind'] in ('COLUMN','CALCULATED_COLUMN'):columns.setdefault(edge['source'],{})[node['label']]=node['id']
    for node in graph.nodes.values():
        props=node['properties']
        if 'script_database' in props:objects[(props['script_database'],props['script_name'])]=node['id']
    def code_column(root,name,at):
        if name in columns.get(root,{}):return columns[root][name]
        identity=graph.add('COLUMN',name,['script-column',root,name],at,
            {'schema_evidence':'CODE_DECLARED_NOT_OBSERVED'},owner=graph.nodes[root]['owner'])
        columns.setdefault(root,{})[name]=identity;graph.link('CONTAINS',root,identity,at);return identity
    def name(table):return (table.db+'.' if table.db else '')+table.name
    def resolve(table):
        db=database
        if table.catalog:
            matches=db_names.get(table.catalog,[])
            if len(matches)!=1:return None
            db=matches[0]
        return objects.get((db,name(table)))
    for number,script in enumerate(scripts):
        text=script.get('text') if isinstance(script,dict) else None
        if not isinstance(text,str):continue
        at={**proof,'span':{'kind':'JSON_POINTER','path':f'/properties/activities/{index}/typeProperties/scripts/{number}/text'}}
        step=graph.add('QUERY_STEP','Declared SQL script',[parent,'script',index,number],at,
            {'language':'TSQL','expression':text,'execution_established':False})
        graph.link('CONTAINS',graph.by_asset[parent],step,at)
        def gap(reason):graph.gap(step,reason,'Retain this exact Script text and resolve its declared connection/schema or use a bounded interpreter; verify inferred mappings.',at)
        if database is None:gap('Script Warehouse binding is missing or ambiguous.');continue
        try:trees=sqlglot.parse(text,read='tsql')
        except sqlglot.errors.ParseError:gap('Script SQL cannot be statically parsed.');continue
        if len(trees)!=1 or not isinstance(trees[0],exp.Create) or trees[0].kind not in ('TABLE','VIEW'):
            gap('Script is not a supported single CREATE TABLE/VIEW declaration; procedure, execution or control flow remains unresolved.');continue
        tree=trees[0];target=tree.this.this if isinstance(tree.this,exp.Schema) else tree.this
        if not isinstance(target,exp.Table) or target.catalog:
            gap('Script target is outside its explicitly bound database.');continue
        root=objects.get((database,name(target)))
        if root is None:
            root=graph.add('VIEW' if tree.kind=='VIEW' else 'TABLE',name(target),['script-object',database,name(target)],at,
                {'schema_evidence':'CODE_DECLARED_NOT_OBSERVED','execution_established':False,
                 'script_database':database,'script_name':name(target)},owner=graph.nodes[graph.by_asset[database]]['owner'])
            objects[(database,name(target))]=root;graph.link('CONTAINS',graph.by_asset[database],root,at)
        graph.link('DERIVED_IN_STEP',root,step,at)
        query=tree.expression
        if query is None and isinstance(tree.this,exp.Schema):
            for definition in tree.this.expressions:
                if isinstance(definition,exp.ColumnDef):code_column(root,definition.name,at)
            continue
        if (not isinstance(query,exp.Select) or query.args.get('with_') or query.find(exp.Star)
                or len(list(query.find_all(exp.Select)))!=1):
            gap('Script query is not a supported explicit-column SELECT; set operations, CTEs or stars remain unresolved.');continue
        tables={};unresolved=False
        for table in query.find_all(exp.Table):
            resolved=resolve(table)
            if resolved is None or table.alias_or_name in tables:
                gap('Script source table is unresolved or ambiguous: '+table.sql(dialect='tsql'));unresolved=True
            else:tables[table.alias_or_name]=resolved
        if unresolved:continue
        def refs(expression):
            found=set()
            for col in expression.find_all(exp.Column):
                options=[tables[col.table]] if col.table in tables else list(tables.values()) if not col.table else []
                matches=[columns[t][col.name] for t in options if col.name in columns.get(t,{})]
                if len(matches)!=1:raise ValueError('Script column is unresolved or ambiguous: '+col.sql(dialect='tsql'))
                found.add(matches[0])
            return found
        try:
            projected=[(p.alias_or_name,refs(p)) for p in query.expressions]
            conditions=[(clause,refs(clause)) for clause in [*query.find_all(exp.Where),*query.find_all(exp.Join)]]
            if any(not label for label,_ in projected):raise ValueError('Script projection has no stable output name.')
        except ValueError as error:gap(str(error));continue
        for label,inputs in projected:
            output=code_column(root,label,at)
            graph.link('DERIVED_IN_STEP',output,step,at)
            for source in sorted(inputs):graph.link('COMPUTED_FROM',output,source,at)
        for offset,(clause,inputs) in enumerate(conditions):
            join=isinstance(clause,exp.Join)
            operation=graph.add('QUERY_STEP' if join else 'FILTER','Declared SQL join' if join else 'Declared SQL filter',
                [step,'condition',offset],at,{'expression':clause.sql(dialect='tsql'),'scope':'transformation','predicate_present':True})
            graph.link('JOINED_VIA' if join else 'FILTERED_BY',root,operation,at)
            for source in sorted(inputs):graph.link('COMPUTED_FROM',operation,source,at)
