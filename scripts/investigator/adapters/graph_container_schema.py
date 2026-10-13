"""Exact retained-table schema refresh; no complete database inventory claim."""
import copy
from urllib.parse import quote
from .binding_catalog import read_many


class SqlContainerChanges:
    def __init__(self,identity,config,owners,retained,execute):
        reader=config['fabric']['sql_reader']
        if reader.get('mode')=='federated_scanner':raise ValueError('SCANNER_SQL_CREDENTIAL_FORBIDDEN')
        if not isinstance(owners,dict)or not 1<=len(owners)<=100:raise ValueError('GRAPH_CONTAINER_OWNER_BOUND')
        self.identity,self.config,self.owners,self.retained,self.execute=identity,config,owners,retained,execute
        self.configured_owners=tuple(sorted(owners));self.retained_ids={}
        for objects in owners.values():
            if not isinstance(objects,list)or not 1<=len(objects)<=100:raise ValueError('GRAPH_CONTAINER_TABLE_BOUND')
            if len({(o['connection'],o['database'])for o in objects})!=1:raise ValueError('GRAPH_CONTAINER_DATABASE_DIFFERS')
            if any(o['connection']!=reader['server'] for o in objects):raise ValueError('GRAPH_CONTAINER_READER_SCOPE')
    def list_changes(self):
        # Workspace item modification time does not attest SQL endpoint schema.
        return {'items':[{'owner':owner,'fingerprint':None,'deleted':False}for owner in self.configured_owners],'complete':False}
    def fetch(self,owner):
        if owner not in self.owners:raise ValueError('GRAPH_CONTAINER_OWNER_SCOPE')
        payload=copy.deepcopy(self.retained(owner));assets=payload['assets'];objects=self.owners[owner]
        roots=[a for a in assets if a['id']==owner and a['kind']in ('Lakehouse','Warehouse','SQLEndpoint')]
        if len(roots)!=1:raise ValueError('GRAPH_CONTAINER_ROOT_REQUIRED')
        tables={a['id']:a for a in assets if a['kind']in ('LakehouseTable','WarehouseTable')}
        declared={o['asset_id']:o for o in objects}
        if not tables or len(declared)!=len(objects)or set(declared)!=set(tables):
            raise ValueError('GRAPH_CONTAINER_PARTIAL_TABLE_COVERAGE')
        for aid,table in tables.items():
            obj=declared[aid];meta=obj['catalog']['metadata'];qualified=meta['schema_name']+'.'+meta['name']
            if table['parent_id']!=owner or table['name']not in (qualified,meta['name']):
                raise ValueError('GRAPH_CONTAINER_TABLE_BINDING_DIFFERS')
        # No owner publication until every exact object returns complete bounded
        # columns under the declared investigator's guarded surface.
        observed={}
        for start in range(0,len(objects),8):observed.update(read_many(self.config,objects[start:start+8],execute=self.execute))
        columns=[a for a in assets if a['kind']in ('LakehouseColumn','WarehouseColumn')]
        if any(a['parent_id']not in tables for a in columns):raise ValueError('GRAPH_CONTAINER_COLUMN_PARENT_DIFFERS')
        retained=[a for a in assets if a not in columns and a['kind']!='GraphSchemaEvidence']
        self.retained_ids[owner]=[a['id']for a in retained]
        result=copy.deepcopy(retained)
        for aid,(values,proof)in sorted(observed.items()):
            old={a['name']:a['id']for a in columns if a['parent_id']==aid}
            if len(old)!=len([a for a in columns if a['parent_id']==aid]):raise ValueError('GRAPH_CONTAINER_AMBIGUOUS_COLUMN')
            kind='LakehouseColumn'if tables[aid]['kind']=='LakehouseTable'else'WarehouseColumn'
            for column in values:
                result.append({'id':old.get(column['name'],aid+'/column/'+quote(column['name'],safe='')),
                    'kind':kind,'name':column['name'],'parent_id':aid,'metadata':{**column,'reader_schema_evidence':aid+'/reader-schema-evidence'}})
            result.append({'id':aid+'/reader-schema-evidence','kind':'GraphSchemaEvidence','name':'Exact retained table schema',
                'parent_id':aid,'metadata':{'scope':'DECLARED_RETAINED_TABLE_ONLY','complete_database_inventory':False,'proof':proof}})
        return {'assets':result,'source_asset_ids':payload['source_asset_ids']}
    def reconcile(self,catalog,estate,owner,at,payload):
        return catalog.refresh(estate,owner,at,payload,retained_asset_ids=self.retained_ids[owner])
