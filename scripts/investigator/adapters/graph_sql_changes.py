"""Exact-object SQL metadata compilation; schema dates are not data freshness."""
import re
from ..shared_state import sha


def names(obj):
    meta=obj['catalog']['metadata'];schema,name=meta['schema_name'],meta['name']
    if any(not isinstance(value,str)or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}',value)for value in (schema,name)):
        raise ValueError('GRAPH_SQL_EXACT_OBJECT_REQUIRED')
    return schema,name


def request(obj,kind):
    schema,name=names(obj)
    base=' FROM sys.objects AS o JOIN sys.schemas AS s ON o.schema_id=s.schema_id '
    where='WHERE s.name=@schema AND o.name=@table AND o.type IN (\'U\',\'V\',\'P\')'
    if kind=='fingerprint':
        query=('SELECT TOP 250 RTRIM(o.type) AS object_type,CONVERT(varchar(33),o.modify_date,126) AS modified_at,'
            'c.column_id AS column_id,c.name AS column_name,t.name AS data_type,c.collation_name AS collation_name'+base+
            'LEFT JOIN sys.columns AS c ON c.object_id=o.object_id LEFT JOIN sys.types AS t ON c.user_type_id=t.user_type_id '+where+' ORDER BY c.column_id')
        columns=['object_type','modified_at','column_id','column_name','data_type','collation_name'];limit=251
    elif kind=='definition':
        query=('SELECT TOP 1 RTRIM(o.type) AS object_type,CONVERT(varchar(33),o.modify_date,126) AS modified_at,'
            'DATALENGTH(m.definition) AS definition_bytes,CASE WHEN DATALENGTH(m.definition)<=262144 THEN m.definition ELSE NULL END AS definition'+base+
            'LEFT JOIN sys.sql_modules AS m ON o.object_id=m.object_id '+where)
        columns=['object_type','modified_at','definition_bytes','definition'];limit=2
    else:raise ValueError('GRAPH_SQL_CONTROL_KIND')
    return {'query':query,'parameters':[{'name':'@schema','value':schema},{'name':'@table','value':name}],
        'read_only_objects':['['+schema+'].['+name+']'],'max_rows':limit,'result_columns':columns}


def compiled_control_objects(payload):
    try:
        declared=payload['read_only_objects']
        if len(declared)!=1:return None
        match=re.fullmatch(r'\[([A-Za-z_][A-Za-z0-9_]{0,127})\]\.\[([A-Za-z_][A-Za-z0-9_]{0,127})\]',declared[0])
        if not match:return None
        obj={'catalog':{'metadata':{'schema_name':match[1],'name':match[2]}}}
        for kind in ('fingerprint','definition'):
            expected=request(obj,kind)
            if all(payload.get(key)==value for key,value in expected.items()):return declared
    except (KeyError,TypeError,ValueError):pass
    return None


class FabricSqlChanges:
    def __init__(self,identity,config,objects,execute):
        if not isinstance(identity,str)or not 1<=len(identity)<=200:raise ValueError('GRAPH_SQL_COLLECTOR_IDENTITY')
        if not isinstance(objects,dict)or not 1<=len(objects)<=100:raise ValueError('GRAPH_SQL_OWNER_BOUND')
        self.identity,self.config,self.objects,self.execute=identity,config,objects,execute
        self.fingerprints={}
        for obj in objects.values():
            names(obj)
            if obj.get('surface','FABRIC_SQL')!='FABRIC_SQL' or obj['connection']!=config['fabric']['sql_reader']['server']:
                raise ValueError('GRAPH_SQL_READER_SCOPE')
    def read(self,obj,kind):
        req=request(obj,kind);answer=self.execute(obj['database'],req);surface=answer.get('surface_report')or{}
        if (not answer.get('read_only_verified')or surface.get('identity')!=self.config['fabric']['sql_reader']['account']
                or surface.get('object')!=obj['database'] or surface.get('engine')!='Microsoft Azure SQL Data Warehouse'):
            raise RuntimeError('GRAPH_SQL_SURFACE_NOT_ATTESTED')
        rows=answer.get('rows')
        if not isinstance(rows,list)or not rows or len(rows)>=req['max_rows']-int(kind=='fingerprint'):
            raise RuntimeError('GRAPH_SQL_METADATA_ABSENT_OR_TRUNCATED')
        if any(not isinstance(row,dict)or set(row)!=set(req['result_columns'])for row in rows):raise ValueError('GRAPH_SQL_METADATA_SHAPE')
        if len({(row['object_type'],row['modified_at'])for row in rows})!=1:raise RuntimeError('GRAPH_SQL_METADATA_VERSION_DIFFERS')
        if rows[0]['object_type']not in ('U','V','P')or not isinstance(rows[0]['modified_at'],str)or not rows[0]['modified_at']:
            raise ValueError('GRAPH_SQL_METADATA_IDENTITY')
        if kind=='fingerprint':
            columns=[row for row in rows if row['column_id']is not None]
            if rows[0]['object_type']in ('U','V')and not columns:raise RuntimeError('GRAPH_SQL_COLUMNS_UNAVAILABLE')
            if any(type(row['column_id'])is not int or row['column_id']<1 or not isinstance(row['column_name'],str)
                or not row['column_name']or not isinstance(row['data_type'],str)or not row['data_type']
                or row['collation_name']is not None and not isinstance(row['collation_name'],str)for row in columns):
                raise ValueError('GRAPH_SQL_COLUMN_SHAPE')
            if len({row['column_id']for row in columns})!=len(columns):raise ValueError('GRAPH_SQL_DUPLICATE_COLUMN')
        return rows
    def list_changes(self):
        result=[]
        for owner,obj in sorted(self.objects.items()):
            rows=self.read(obj,'fingerprint');self.fingerprints[owner]=rows
            result.append({'owner':owner,'fingerprint':sha(rows),'deleted':False})
        return {'items':result,'complete':False}
    def fetch(self,owner):
        if owner not in self.fingerprints:raise ValueError('GRAPH_SQL_OWNER_NOT_LISTED')
        obj=self.objects[owner];rows=self.fingerprints[owner];first=rows[0];schema,name=names(obj)
        definitions=[]
        if first['object_type']in ('V','P'):
            detail=self.read(obj,'definition')[0]
            if (detail['modified_at'],detail['object_type'])!=(first['modified_at'],first['object_type']):
                raise RuntimeError('GRAPH_SQL_DEFINITION_CHANGED_DURING_COLLECTION')
            if not isinstance(detail['definition'],str)or not detail['definition']or type(detail['definition_bytes'])is not int or not 0<detail['definition_bytes']<=262144:
                raise RuntimeError('GRAPH_SQL_DEFINITION_PERMISSION_OR_SIZE_UNAVAILABLE')
            if len(detail['definition'].encode('utf-16-le'))!=detail['definition_bytes']:
                raise RuntimeError('GRAPH_SQL_DEFINITION_BYTES_DIFFER')
            definitions=[{'definition':detail['definition']}]
        columns=[{'column_id':r['column_id'],'name':r['column_name'],'data_type':r['data_type'],'collation_name':r['collation_name']}for r in rows if r['column_id']is not None]
        aid=obj['asset_id'];meta={'schema_name':schema,'name':name,'type':first['object_type'],'modify_date':first['modified_at'],'definitions':definitions,'columns':columns}
        assets=[{'id':aid,'kind':'SqlObject','name':schema+'.'+name,'parent_id':None,'metadata':meta}]
        assets.extend({'id':aid+'/column/'+str(col['column_id']),'kind':'SqlColumn','name':col['name'],'parent_id':aid,'metadata':col}for col in columns)
        return {'assets':assets,'source_asset_ids':[]}
