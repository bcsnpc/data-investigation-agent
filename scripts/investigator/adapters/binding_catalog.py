"""Reader-owned target types on an exact, already-resolved SQL object."""
import copy
import re


def read(config, obj, *, execute):
    reader=config['fabric']['sql_reader']
    meta=obj['catalog']['metadata']
    schema,table=meta['schema_name'],meta['name']
    if obj.get('surface','FABRIC_SQL')!='FABRIC_SQL' or obj['connection']!=reader['server']:
        raise ValueError('Target catalog leaves the approved Fabric SQL connection')
    if any(not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}',s) for s in (schema,table)):
        raise ValueError('Target catalog object is not an exact declared identifier')
    request={'query':
        'SELECT TOP 250 c.name AS column_name,t.name AS data_type,c.collation_name AS collation_name '
        'FROM sys.columns AS c JOIN sys.types AS t ON c.user_type_id=t.user_type_id '
        'JOIN sys.tables AS o ON c.object_id=o.object_id JOIN sys.schemas AS s ON o.schema_id=s.schema_id '
        'WHERE s.name=@schema AND o.name=@table ORDER BY c.column_id',
        'parameters':[{'name':'@schema','value':schema},{'name':'@table','value':table}],
        'read_only_objects':['['+schema+'].['+table+']'],
        'max_rows':251,'result_columns':['column_name','data_type','collation_name']}
    answer=execute(obj['database'],request)
    report=answer.get('surface_report') or {}
    if (report.get('identity')!=reader['account'] or report.get('object')!=obj['database']
            or report.get('engine')!='Microsoft Azure SQL Data Warehouse'
            or not answer.get('read_only_verified')):
        raise ValueError('Target types lack reader-owned guarded surface evidence')
    rows=answer.get('rows')
    if not isinstance(rows,list) or not 0<len(rows)<250:
        raise ValueError('Target catalog is empty or incomplete')
    columns=[]
    for row in rows:
        if set(row)!={'column_name','data_type','collation_name'}:
            raise ValueError('Target catalog row shape differs')
        if (not isinstance(row['column_name'],str) or not row['column_name']
                or not isinstance(row['data_type'],str) or not row['data_type']
                or (row['collation_name'] is not None and not isinstance(row['collation_name'],str))):
            raise ValueError('Target catalog field type differs')
        columns.append({'name':row['column_name'],'data_type':row['data_type'],'observed_type':row['data_type'],
                        'collation_name':row['collation_name']})
    if len({c['name'] for c in columns})!=len(columns):
        raise ValueError('Target catalog has ambiguous columns')
    proof={'kind':'NATIVE_TARGET_CATALOG','asset_id':obj['asset_id'],
           'database':obj['database'],'schema':schema,'table':table,
           'surface_report':copy.deepcopy(report),'columns':copy.deepcopy(columns)}
    return columns,proof


def request_many(objects):
    """One bounded catalog SELECT for exact objects in one connection/database."""
    if not objects or len(objects)>8:raise ValueError('Target catalog batch bound')
    if len({(o['connection'],o['database']) for o in objects})!=1:
        raise ValueError('Target catalog batch crosses databases')
    names=[];parameters=[];clauses=[]
    for i,obj in enumerate(objects):
        meta=obj['catalog']['metadata'];schema,table=meta['schema_name'],meta['name']
        if any(not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}',x) for x in (schema,table)):
            raise ValueError('Target catalog object is not an exact declared identifier')
        name='['+schema+'].['+table+']'
        if name in names:raise ValueError('Duplicate target catalog object')
        names.append(name)
        parameters += [{'name':'@schema'+str(i),'value':schema},{'name':'@table'+str(i),'value':table}]
        clauses.append('(s.name=@schema'+str(i)+' AND o.name=@table'+str(i)+')')
    return {'query':'SELECT TOP 250 s.name AS schema_name,o.name AS table_name,c.name AS column_name,'
            't.name AS data_type,c.collation_name AS collation_name '
            'FROM sys.columns AS c JOIN sys.types AS t ON c.user_type_id=t.user_type_id '
            'JOIN sys.tables AS o ON c.object_id=o.object_id JOIN sys.schemas AS s ON o.schema_id=s.schema_id '
            'WHERE '+' OR '.join(clauses)+' ORDER BY s.name,o.name,c.column_id',
            'parameters':parameters,'read_only_objects':names,'max_rows':251,
            'result_columns':['schema_name','table_name','column_name','data_type','collation_name']}


def compiled_control_objects(payload):
    """Recognize only byte-exact bounded batch metadata compiled for real objects.

    This grants no sys.* query authority. The gateway separately admits the
    named user tables, CATALOG control, connection and bounds. Permission guards
    continue to check those user tables, never the system catalog views.
    """
    try:
        objects=[]
        for name in payload['read_only_objects']:
            match=re.fullmatch(r'\[([A-Za-z_][A-Za-z0-9_]{0,127})\]\.\[([A-Za-z_][A-Za-z0-9_]{0,127})\]',name)
            if not match:return None
            objects.append({'connection':payload['server'],'database':payload['database'],
                'catalog':{'metadata':{'schema_name':match[1],'name':match[2]}}})
        expected=request_many(objects)
        if any(payload.get(key)!=value for key,value in expected.items()):return None
        return list(expected['read_only_objects'])
    except (KeyError,TypeError,ValueError):
        return None


def read_many(config, objects, *, execute):
    reader=config['fabric']['sql_reader'];request=request_many(objects)
    if any(o.get('surface','FABRIC_SQL')!='FABRIC_SQL' or o['connection']!=reader['server'] for o in objects):
        raise ValueError('Target catalog leaves the approved Fabric SQL connection')
    database=objects[0]['database'];answer=execute(database,request)
    report=answer.get('surface_report') or {}
    if (report.get('identity')!=reader['account'] or report.get('object')!=database or
        report.get('engine')!='Microsoft Azure SQL Data Warehouse' or not answer.get('read_only_verified')):
        raise ValueError('Target types lack reader-owned guarded surface evidence')
    rows=answer.get('rows')
    if not isinstance(rows,list) or not 0<len(rows)<250:raise ValueError('Target catalog is empty or incomplete')
    expected={(o['catalog']['metadata']['schema_name'],o['catalog']['metadata']['name']):o for o in objects}
    grouped={name:[] for name in expected}
    for row in rows:
        if set(row)!=set(request['result_columns']):raise ValueError('Target catalog row shape differs')
        name=(row['schema_name'],row['table_name'])
        if name not in grouped:raise ValueError('Target catalog returned an undeclared object')
        if (not isinstance(row['column_name'],str) or not row['column_name'] or
            not isinstance(row['data_type'],str) or not row['data_type'] or
            row['collation_name'] is not None and not isinstance(row['collation_name'],str)):
            raise ValueError('Target catalog field type differs')
        grouped[name].append({'name':row['column_name'],'data_type':row['data_type'],
            'observed_type':row['data_type'],'collation_name':row['collation_name']})
    result={}
    from ..onboarding import digest
    for name,columns in grouped.items():
        if not columns or len({c['name'] for c in columns})!=len(columns):
            raise ValueError('Target catalog has absent or ambiguous columns')
        obj=expected[name]
        proof={'kind':'NATIVE_TARGET_CATALOG','asset_id':obj['asset_id'],'database':database,
               'schema':name[0],'table':name[1],'surface_report':copy.deepcopy(report),
               'columns':copy.deepcopy(columns),'catalog_batch_request_hash':digest(request),
               'guarded_objects':request['read_only_objects']}
        result[obj['asset_id']]=(columns,proof)
    return result
