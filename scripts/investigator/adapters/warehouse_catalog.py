"""Reader-owned schema for explicitly declared Warehouse audit tables only."""
import re


def read(config, warehouse, table_name, *, execute=None):
    from fabric_sql_surface import read as sql_read
    reader=config['fabric'].get('sql_reader')
    if (not reader or warehouse.get('properties',{}).get('connectionString')!=reader['server']
            or not isinstance(table_name,str)
            or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}\.[A-Za-z_][A-Za-z0-9_]{0,127}',table_name)):
        raise ValueError('Warehouse catalog leaves the approved connection or declared object')
    schema,table=table_name.split('.')
    request={'query':
        'SELECT TOP 250 c.name AS column_name,t.name AS data_type '
        'FROM sys.columns AS c JOIN sys.types AS t ON c.user_type_id=t.user_type_id '
        'JOIN sys.tables AS o ON c.object_id=o.object_id JOIN sys.schemas AS s ON o.schema_id=s.schema_id '
        'WHERE s.name=@schema AND o.name=@table ORDER BY c.column_id',
        'parameters':[{'name':'@schema','value':schema},{'name':'@table','value':table}],
        'read_only_objects':['['+schema+'].['+table+']'],
        'max_rows':251,'result_columns':['column_name','data_type']}
    result=(execute or sql_read)(config,warehouse['displayName'],request)
    report=result.get('surface_report') or {}
    if (report.get('identity')!=reader['account'] or report.get('object')!=warehouse['displayName']
            or report.get('engine')!='Microsoft Azure SQL Data Warehouse'
            or not result.get('read_only_verified') or not result.get('rows') or len(result['rows'])>=250):
        raise ValueError('Warehouse schema lacks complete reader-owned evidence')
    return [{'name':row['column_name'],'data_type':row['data_type']} for row in result['rows']]
