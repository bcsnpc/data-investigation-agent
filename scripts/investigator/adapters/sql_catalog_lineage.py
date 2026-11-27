"""Static SQL lineage from exact native object/column addresses only.

No SQL execution, schema-name guessing, procedure invocation or dynamic-SQL
expansion. Unresolvable references remain gaps; strings are never object names.
"""
from sqlglot import parse,exp


def extract(assets):
    objects={a['id']:a for a in assets if a['kind']=='SqlObject'}
    addresses={(a.get('parent',a.get('parent_id')),a['name']):a for a in objects.values()}
    columns={(a.get('parent',a.get('parent_id')),a['name']):a['id']for a in assets if a['kind']=='SqlColumn'}
    edges=[];gaps=[]
    def gap(owner,reason):
        value=dict(asset=owner,reason=reason,detail='Native SQL static analysis')
        if value not in gaps:gaps.append(value)
    def add(source,target,kind,owner):
        value=dict(source=source,target=target,kind=kind,evidence=owner,detail='INFERRED_FROM_CODE: native SQL definition')
        if value not in edges:edges.append(value)
    for owner,a in objects.items():
        meta=a.get('meta',a.get('metadata',{}))
        definitions=meta.get('definitions',[])
        for declaration in definitions:
            text=declaration.get('definition')
            if not text:continue
            try:trees=parse(text,read='tsql')
            except Exception:gap(owner,'SQL_DEFINITION_UNPARSEABLE');continue
            for tree in trees:
                if tree is None:continue
                if any(type(n).__name__ in ('Command','Execute','ExecuteSql','ExecuteAs')for n in tree.walk()):
                    gap(owner,'DYNAMIC_SQL_UNRESOLVED');continue
                def target(table):
                    if not isinstance(table,exp.Table)or table.catalog or not table.db:return None
                    return addresses.get((a.get('parent',a.get('parent_id')),table.db+'.'+table.name))
                is_view=isinstance(tree,exp.Create)and str(tree.args.get('kind','')).upper()=='VIEW'
                for selection in tree.find_all(exp.Select):
                    sources=[]
                    for table in selection.find_all(exp.Table):
                        bound=target(table)
                        if bound is None:gap(owner,'SQL_SOURCE_ADDRESS_UNRESOLVED');continue
                        if bound['id']!=owner:
                            sources.append((table,bound))
                            if is_view:add(bound['id'],owner,'data',owner)
                            else:add(owner,bound['id'],'reads',owner)
                    if is_view:
                        for projection in selection.expressions:
                            output=columns.get((owner,projection.alias_or_name))
                            if output is None:continue
                            for ref in projection.find_all(exp.Column):
                                candidates=[bound for table,bound in sources if not ref.table or ref.table in(table.alias_or_name,table.name)]
                                native=[columns[(bound['id'],ref.name)]for bound in candidates if (bound['id'],ref.name)in columns]
                                if len(set(native))==1:add(native[0],output,'data',owner)
                                else:gap(owner,'SQL_COLUMN_ADDRESS_UNRESOLVED')
                for change in list(tree.find_all(exp.Insert))+list(tree.find_all(exp.Delete)):
                    table=change.this
                    if isinstance(table,exp.Schema):table=table.this
                    bound=target(table)
                    if bound and bound['id']!=owner:add(owner,bound['id'],'produces',owner)
                    elif bound is None:gap(owner,'SQL_WRITE_TARGET_ADDRESS_UNRESOLVED')
    return dict(edges=edges,gaps=gaps)
