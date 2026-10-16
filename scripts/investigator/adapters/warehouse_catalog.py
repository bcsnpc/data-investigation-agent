"""Reader-owned Warehouse metadata; visible inventory is explicitly scoped."""
import re


from investigator.adapters.sql_principal import expected as sql_principal


def inventory(config, warehouse, *, execute=None):
    """Read visible tables on one discovered, approved Warehouse connection.

    This does not claim invisible objects are absent. Per-object definition
    visibility and source identity accompany every returned schema.
    """
    from fabric_sql_surface import read as sql_read
    from investigator.control_contract import bounds
    max_rows = bounds('FABRIC_SQL')['maximum_rows']
    visible_limit = max_rows - 1
    reader=config['fabric'].get('sql_reader')
    if not reader or warehouse.get('properties',{}).get('connectionString')!=reader['server']:
        raise ValueError('Warehouse catalog leaves the approved connection')
    request={'query':
        f'SELECT TOP {visible_limit} s.name AS schema_name,o.name AS table_name,c.name AS column_name,'
        't.name AS data_type,c.column_id,c.max_length,c.precision,c.scale,c.is_nullable,'
        "HAS_PERMS_BY_NAME(QUOTENAME(s.name)+'.'+QUOTENAME(o.name),'OBJECT','VIEW DEFINITION') AS can_view_definition "
        'FROM sys.tables o JOIN sys.schemas s ON s.schema_id=o.schema_id '
        'JOIN sys.columns c ON c.object_id=o.object_id '
        'JOIN sys.types t ON t.user_type_id=c.user_type_id '
        'WHERE o.is_ms_shipped=0 ORDER BY s.name,o.name,c.column_id',
        'parameters':[], 'read_only_objects':['[sys].[tables]','[sys].[schemas]','[sys].[columns]','[sys].[types]'],
        'max_rows':max_rows,'result_columns':['schema_name','table_name','column_name','data_type','column_id',
            'max_length','precision','scale','is_nullable','can_view_definition']}
    result=(execute or sql_read)(config,warehouse['displayName'],request)
    report=result.get('surface_report') or {};rows=result.get('rows')
    if (report.get('identity')!=sql_principal(reader) or report.get('object')!=warehouse['displayName']
            or report.get('engine')!='Microsoft Azure SQL Data Warehouse'
            or not result.get('read_only_verified') or not isinstance(rows,list) or len(rows)>=visible_limit):
        raise ValueError('Warehouse inventory lacks bounded reader-owned evidence')
    tables={}
    for row in rows:
        key=(row['schema_name'],row['table_name'])
        table=tables.setdefault(key,{'schema_name':key[0],'name':key[1],'type_desc':'USER_TABLE',
            'columns':[],'definition_visible':True})
        table['definition_visible'] &= row['can_view_definition'] in (True,1,'1')
        table['columns'].append({('name' if k=='column_name' else k):row[k] for k in
            ('column_name','data_type','column_id','max_length','precision','scale','is_nullable')})
    return {'scope':'VISIBLE_OBJECTS_ONLY','complete_schema':False,'tables':list(tables.values()),
            'surface_report':report,'read_only_verified':True}


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
    if (report.get('identity')!=sql_principal(reader) or report.get('object')!=warehouse['displayName']
            or report.get('engine')!='Microsoft Azure SQL Data Warehouse'
            or not result.get('read_only_verified') or not result.get('rows') or len(result['rows'])>=250):
        raise ValueError('Warehouse schema lacks complete reader-owned evidence')
    return [{'name':row['column_name'],'data_type':row['data_type']} for row in result['rows']]
