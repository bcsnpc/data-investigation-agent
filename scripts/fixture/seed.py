"""Read committed synthetic seed literals without executing a fixture notebook.

Publication-only input. This module must never be imported into investigation
planning or used to supply an expected answer to a diagnostic adapter.
"""
import ast
import copy
import hashlib
import json
import re
from pathlib import Path
from uuid import UUID

ROOT=Path(__file__).resolve().parents[2]
NOTEBOOK=ROOT/'fixture-code/7ccafe59-0460-4c8a-a691-bfdfa75a2b25/notebook-content.py'
IDENTIFIER=re.compile(r'[a-z][a-z0-9_]{0,127}\Z')
TYPES={'int':int,'string':str}


def load(path=NOTEBOOK):
    """Only a single literal json.loads assignment is admissible; never eval."""
    raw=Path(path).read_bytes()
    if len(raw)>1_000_000:raise ValueError('Fixture seed notebook exceeds bound')
    tree=ast.parse(raw)
    assignments=[node for node in ast.walk(tree) if isinstance(node,ast.Assign)
        and any(isinstance(target,ast.Name) and target.id=='source_rows' for target in node.targets)]
    if len(assignments)!=1:raise ValueError('Fixture seed assignment must be unique')
    value=assignments[0].value
    if (not isinstance(value,ast.Call) or value.keywords or len(value.args)!=1
        or not isinstance(value.func,ast.Attribute) or value.func.attr!='loads'
        or not isinstance(value.func.value,ast.Name) or value.func.value.id!='json'
        or not isinstance(value.args[0],ast.Constant) or not isinstance(value.args[0].value,str)):
        raise ValueError('Fixture seed is not literal JSON')
    tables=json.loads(value.args[0].value);names=set()
    if not isinstance(tables,list) or not 1<=len(tables)<=32:raise ValueError('Fixture table count is invalid')
    for table in tables:
        if not isinstance(table,dict) or set(table)!={'name','columns','rows'}:raise ValueError('Fixture table fields differ')
        name=table['name']
        if not isinstance(name,str) or not IDENTIFIER.fullmatch(name) or name in names:raise ValueError('Fixture table identity is invalid')
        names.add(name);columns=table['columns'];fields=set()
        if not isinstance(columns,list) or not 1<=len(columns)<=64:raise ValueError('Fixture columns are invalid')
        for column in columns:
            if not isinstance(column,list) or len(column)!=2:raise ValueError('Fixture column declaration is invalid')
            field,kind=column
            if not isinstance(field,str) or not IDENTIFIER.fullmatch(field) or field in fields or kind not in TYPES:
                raise ValueError('Fixture column identity/type is invalid')
            fields.add(field)
        if not isinstance(table['rows'],list) or len(table['rows'])>100000:raise ValueError('Fixture row bound exceeded')
        for row in table['rows']:
            if not isinstance(row,list) or len(row)!=len(columns):raise ValueError('Fixture row shape differs')
            if any(type(v) is not TYPES[c[1]] for v,c in zip(row,columns)):raise ValueError('Fixture value type differs')
            if any(isinstance(v,str) and len(v)>4000 for v in row):raise ValueError('Fixture string bound exceeded')
    return {'source_sha256':hashlib.sha256(raw).hexdigest(),'tables':copy.deepcopy(tables)}


def summary(seed):
    return {'source_sha256':seed['source_sha256'],'synthetic_only':True,
        'tables':[{'name':t['name'],'rows':len(t['rows']),'columns':copy.deepcopy(t['columns'])} for t in seed['tables']]}


def insert_plan(table,schema='app'):
    """Bound values stay parameters; existing objects must never be overwritten."""
    if not IDENTIFIER.fullmatch(schema):raise ValueError('Fixture schema is invalid')
    # Revalidate even if the caller supplied its own dictionary.
    name=table['name'];columns=table['columns']
    if not IDENTIFIER.fullmatch(name) or any(not IDENTIFIER.fullmatch(c[0]) or c[1] not in TYPES for c in columns):
        raise ValueError('Fixture SQL identity is invalid')
    target='['+schema+'].['+name+']'
    ddl=', '.join('['+field+'] '+('int' if kind=='int' else 'varchar(4000)')+' NOT NULL' for field,kind in columns)
    return {'object':target,'precondition':'OBJECT_MUST_NOT_EXIST',
        'create':'CREATE TABLE '+target+' ('+ddl+');',
        'insert':'INSERT INTO '+target+' ('+', '.join('['+c[0]+']' for c in columns)+') VALUES ('+', '.join('?' for c in columns)+');',
        'parameters':copy.deepcopy(table['rows'])}


def notebook_template(workspace,lakehouses,path=NOTEBOOK):
    """Rebind only the three declared container paths in the committed notebook.

    Every transformation remains the recorded one. No notebook is dispatched.
    The application-copy path is separate and needs its own recorded template.
    """
    workspace=str(UUID(workspace))
    if set(lakehouses)!={'bronze','silver','gold'}:raise ValueError('Fixture needs three explicit notebook containers')
    lakehouses={k:str(UUID(v)) for k,v in lakehouses.items()}
    if len(set(lakehouses.values()))!=3:raise ValueError('Fixture containers must be distinct')
    seed=load(path);raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=seed['source_sha256']:raise ValueError('Fixture source changed during planning')
    tree=ast.parse(raw)
    paths=[node for node in tree.body if isinstance(node,ast.Assign)
           and any(isinstance(target,ast.Name) and target.id=='paths' for target in node.targets)]
    if len(paths)!=1 or set(ast.literal_eval(paths[0].value))!=set(lakehouses):
        raise ValueError('Recorded notebook container declaration differs')
    declaration={k:'abfss://'+workspace+'@onelake.dfs.fabric.microsoft.com/'+lakehouses[k]+'/Tables/' for k in lakehouses}
    paths[0].value=ast.parse(repr(declaration),mode='eval').body
    ast.fix_missing_locations(tree)
    return {'source_sha256':seed['source_sha256'],'source':ast.unparse(tree)+'\n',
            'containers':declaration,'provenance':'COMMITTED_FIXTURE_PATH_SUBSTITUTION_ONLY'}
