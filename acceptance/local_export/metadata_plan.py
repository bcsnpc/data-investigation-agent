"""Metadata-only request compiler; native Fabric worker owns attestation cols."""
COLUMNS=['schema_name','table_name','column_id','column_name','native_type','max_length','precision','scale','is_nullable']
def request(control,query,*,source=False):
 if control.get('surface') not in ('AZURE_SQL','FABRIC_SQL'):raise ValueError('EXPORT_SCHEMA_SURFACE')
 if not control.get('item_id') or not control.get('database'):raise ValueError('EXPORT_SCHEMA_ROUTE_FIELDS')
 if '__surface_' in query:raise ValueError('EXPORT_SCHEMA_DUPLICATE_ATTESTATION')
 return {'surface':control['surface'],'export_full':True,'database':control['database'],'query':query,'parameters':[],'read_only_objects':['[INFORMATION_SCHEMA].[COLUMNS]'],'max_rows':251,'result_columns':COLUMNS+(['object_id']if source else []),'asset_ids':[control['item_id']]}
