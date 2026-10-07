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
