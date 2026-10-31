"""Generate HealthNet owner-deployment assets, never DIA configuration.

Unbound connection IDs are explicit in a deployment requirements file. An
asset on disk is not a native deployment or validation result.
"""
import json
from pathlib import Path
from uuid import uuid5,NAMESPACE_URL
from .schema import CLINICAL,BILLING,ddl
from .marts import warehouse_sql


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(value if isinstance(value,str)else json.dumps(value,indent=2)+'\n',encoding='utf8')


def notebook(workspace,lakehouse):
    code='''from pyspark.sql import functions as F
from delta.tables import DeltaTable

# Current MPI resolution follows the explicit native merge relation. No
# fuzzy name matching or invented identity merge is permitted.
patients = spark.table("raw_clinical_patient")
merges = spark.table("raw_clinical_patient_merge").filter("is_deleted = 0")
assert merges.groupBy("duplicate_id").count().filter("count > 1").count() == 0
mapping = patients.select(F.col("id").alias("patient_id"), F.col("id").alias("mpi_patient_id"))
# Resolve transitive merges with bounded convergence and fail on cycles.
seen = set()
for _ in range(100):
    next_map = mapping.alias("p").join(merges.alias("m"), F.col("p.mpi_patient_id") == F.col("m.duplicate_id"), "left").select(F.col("p.patient_id"), F.coalesce(F.col("m.survivor_id"), F.col("p.mpi_patient_id")).alias("mpi_patient_id"))
    changes = next_map.alias("n").join(mapping.alias("p"), "patient_id").filter(F.col("n.mpi_patient_id") != F.col("p.mpi_patient_id")).count()
    mapping = next_map.localCheckpoint(eager=True)
    if changes == 0: break
else: raise ValueError("MPI relation did not converge; inspect cyclic merges")
resolved = patients.join(mapping, patients.id == mapping.patient_id, "inner").drop("patient_id")
resolved.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("stg_patient")
'''
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'language_info':{'name':'python'},'kernelspec':{'name':'synapse_pyspark','display_name':'Synapse PySpark'},'dependencies':{'lakehouse':{'default_lakehouse':lakehouse,'default_lakehouse_name':'hn_raw','default_lakehouse_workspace_id':workspace}}},'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(keepends=True)}]}


def pipeline(system,workspace,lakehouse,source_connection,warehouse_connection):
    """One sequential table cohort. Watermarks advance only after copy success.

    The initial watermark and high bound are selected from native data. Delta
    upsert uses the source PK and propagates is_deleted tombstones.
    """
    definitions=CLINICAL if system=='clinical'else BILLING
    incremental={'order_header','order_line','result','medication_admin','encounter','charge','payment','claim','claim_line','remittance','remittance_line','adjustment'}
    activities=[];previous=[]
    for table in definitions:
        lower='lower_'+table;upper='upper_'+table;copy='copy_'+table;commit='commit_'+table
        lookup={'type':'Lookup','policy':{'timeout':'0.00:10:00','retry':1,'retryIntervalInSeconds':30}}
        activities.append({'name':lower,**lookup,'dependsOn':previous,'typeProperties':{'source':{'type':'DataWarehouseSource','sqlReaderQuery':f"SELECT COALESCE(MAX(watermark_utc),CONVERT(DATETIME2,'1900-01-01')) watermark_utc FROM dbo.load_watermark WHERE source_system='{system}'AND table_name='{table}'"},'datasetSettings':{'type':'DataWarehouseTable','externalReferences':{'connection':warehouse_connection}},'firstRowOnly':True}})
        activities.append({'name':upper,**lookup,'dependsOn':[{'activity':lower,'dependencyConditions':['Succeeded']}],'typeProperties':{'source':{'type':'AzureSqlSource','sqlReaderQuery':f"SELECT COALESCE(MAX(updated_at),CONVERT(DATETIME2,'1900-01-01')) watermark_utc FROM app.[{table}]"},'datasetSettings':{'type':'AzureSqlTable','externalReferences':{'connection':source_connection}},'firstRowOnly':True}})
        # Inclusive lower boundary deliberately re-reads ties. Upsert makes it
        # lossless and idempotent even when updated_at is not unique.
        query=f'SELECT * FROM app.[{table}]'
        if table in incremental:
            query={'value':f"@concat('SELECT * FROM app.[{table}] WHERE updated_at >= ''',activity('{lower}').output.firstRow.watermark_utc,''' AND updated_at <= ''',activity('{upper}').output.firstRow.watermark_utc,'''')",'type':'Expression'}
        activities.append({'name':copy,'type':'Copy','dependsOn':[{'activity':upper,'dependencyConditions':['Succeeded']}],'policy':{'timeout':'0.01:00:00','retry':1,'retryIntervalInSeconds':30},'typeProperties':{
            'source':{'type':'AzureSqlSource','sqlReaderQuery':query,'queryTimeout':'01:00:00','partitionOption':'None','datasetSettings':{'type':'AzureSqlTable','typeProperties':{'schema':'app','table':table},'externalReferences':{'connection':source_connection}}},
            'sink':{'type':'LakehouseTableSink','tableActionOption':'Upsert'if table in incremental else'OverwriteSchema','upsertSettings':{'keys':['id']},'datasetSettings':{'type':'LakehouseTable','typeProperties':{'table':'raw_'+system+'_'+table},'linkedService':{'name':'hn_raw','properties':{'type':'Lakehouse','typeProperties':{'workspaceId':workspace,'artifactId':lakehouse,'rootFolder':'Tables'}}}}},'enableStaging':False}})
        script=f"""IF NOT EXISTS (SELECT 1 FROM dbo.load_audit WHERE run_id='@{{pipeline().RunId}}' AND pipeline_name='pl_{system}' AND table_name='{table}')
INSERT INTO dbo.load_audit VALUES ('@{{pipeline().RunId}}','pl_{system}','{table}','@{{pipeline().TriggerTime}}',SYSUTCDATETIME(),'Succeeded',@{{activity('{copy}').output.rowsRead}},@{{activity('{copy}').output.rowsCopied}},'@{{activity('{upper}').output.firstRow.watermark_utc}}');
INSERT INTO dbo.load_watermark VALUES('{system}','{table}','@{{activity('{upper}').output.firstRow.watermark_utc}}',0);"""
        activities.append({'name':commit,'type':'Script','policy':{'timeout':'0.00:10:00','retry':3,'retryIntervalInSeconds':30},'dependsOn':[{'activity':copy,'dependencyConditions':['Succeeded']}],'externalReferences':{'connection':warehouse_connection},'typeProperties':{'scripts':[{'type':'NonQuery','text':'BEGIN TRANSACTION;\n'+script+'\nCOMMIT;'}],'scriptBlockExecutionTimeout':'00:10:00'}})
        previous=[{'activity':commit,'dependencyConditions':['Succeeded']}]
    return {'properties':{'activities':activities,'concurrency':1,'annotations':['Synthetic HealthNet only','No row recount substituted for native Copy output']}}


def reference_dataflow(workspace,lakehouse,warehouse_server,warehouse_id,bindings=None):
    """Explicit destination references; query metadata binds owner connections."""
    header='section Section1;\n'
    queries={
      'ref_payer_group_history':('raw_billing_payer_plan_history','ref_payer_group_history'),
      'ref_department_mapping':('raw_clinical_provider_assignment','ref_department_mapping'),
    }
    metadata={'formatVersion':'202502','name':'df_reference_mapping','documentLocale':'en-US','computeEngineSettings':{'maxConcurrency':1},'queriesMetadata':{},'connections':[]}
    for key,kind in [('lakehouse','Lakehouse'),('warehouse','Warehouse')]:
        connection=(bindings or{}).get(key)
        if connection:
            metadata['connections'].append({'path':kind,'kind':kind,'connectionId':json.dumps({
                'ClusterId':connection['cluster_id'],'DatasourceId':connection['id']},separators=(',',':'))})
    for name,(source,target)in queries.items():
        destination=name+'_DataDestination'
        header+=f'''[DataDestinations = {{[Definition = [Kind = "Reference", QueryName = "{destination}", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}}]
shared {name} = let Source = Lakehouse.Contents([]), Workspace = Source{{[workspaceId="{workspace}"]}}[Data], Lake = Workspace{{[lakehouseId="{lakehouse}"]}}[Data], Rows = Lake{{[Id="{source}",ItemKind="Table"]}}[Data], Active = Table.SelectRows(Rows, each [is_deleted] = 0) in Active;
shared {destination} = let Source = Fabric.Warehouse([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]), Workspace = Source{{[workspaceId="{workspace}"]}}[Data], Warehouse = Workspace{{[warehouseId="{warehouse_id}"]}}[Data], Target = Warehouse{{[Schema="dbo",Item="{target}"]}}?[Data]? in Target;
'''
        for query,hidden in[(name,False),(destination,True)]:
            metadata['queriesMetadata'][query]={'queryId':str(uuid5(NAMESPACE_URL,'healthnet/'+query)),'queryName':query,'isHidden':hidden,'loadEnabled':not hidden}
    return header,metadata


def nightly_pipeline(workspace,notebook_id,dataflow_id,warehouse_connection):
    # Both independent preparation steps must succeed before the mart rebuild.
    policy={'timeout':'0.01:00:00','retry':0,'retryIntervalInSeconds':30}
    return {'properties':{'concurrency':1,'activities':[
        {'name':'reference_mapping','type':'RefreshDataFlow','dependsOn':[],
         'policy':policy,'typeProperties':{'dataflowId':dataflow_id,'workspaceId':workspace,
         'dataflowType':'DataflowFabric','notifyOption':'NoNotification'}},
        {'name':'patient_mpi','type':'TridentNotebook','dependsOn':[],
         'policy':policy,'typeProperties':{'notebookId':notebook_id,'workspaceId':workspace}},
        {'name':'warehouse_run_all','type':'Script','policy':policy,
         'dependsOn':[{'activity':name,'dependencyConditions':['Succeeded']}for name in('reference_mapping','patient_mpi')],
         'externalReferences':{'connection':warehouse_connection},
         'typeProperties':{'scripts':[{'type':'NonQuery','text':'EXEC dbo.sp_run_all;'}],
         'scriptBlockExecutionTimeout':'01:00:00'}}]}}


def warehouse_item_binding(value,workspace,warehouse_id,warehouse_server):
    """A Warehouse credential is generic; the item address must also be exact."""
    link={'name':'hn_dw','properties':{'type':'DataWarehouse','typeProperties':{
        'endpoint':warehouse_server,'artifactId':warehouse_id,'workspaceId':workspace}}}
    for activity in value['properties']['activities']:
        if activity['type']=='Script':
            import copy
            connection=copy.deepcopy(link)
            connection['properties']['externalReferences']=activity.pop('externalReferences')
            activity['connectionSettings']=connection
            activity['typeProperties']['database']='hn_dw'
        if activity['type']=='Lookup'and activity['typeProperties']['source']['type']=='DataWarehouseSource':
            import copy
            dataset=activity['typeProperties']['datasetSettings']
            connection=copy.deepcopy(link)
            connection['properties']['externalReferences']=dataset.pop('externalReferences')
            dataset['connectionSettings']=connection
    return value


def build(root,workspace,lakehouse,warehouse_server,warehouse_id,connections=None,items=None,dataflow_bindings=None):
    root=Path(root);connections=connections or{}
    items=items or{}
    for system in('clinical','billing'):write(root/'sql'/('hn_'+system+'.sql'),ddl(system,'azure'))
    write(root/'sql/hn_dw.sql',warehouse_sql())
    write(root/'notebooks/nb_patient_mpi.ipynb',notebook(workspace,lakehouse))
    pq,metadata=reference_dataflow(workspace,lakehouse,warehouse_server,warehouse_id,dataflow_bindings)
    write(root/'dataflows/df_reference_mapping/mashup.pq',pq)
    write(root/'dataflows/df_reference_mapping/queryMetadata.json',metadata)
    for system in('clinical','billing'):
        # Definition templates are clearly labelled until credentials are bound.
        value=pipeline(system,workspace,lakehouse,connections.get(system,'REQUIRES_OWNER_CONNECTION'),connections.get('warehouse','REQUIRES_OWNER_CONNECTION'))
        write(root/f'pipelines/pl_{system}/pipeline-content.json',warehouse_item_binding(value,workspace,warehouse_id,warehouse_server))
    nightly=nightly_pipeline(workspace,
        items.get('notebook','REQUIRES_PUBLISHED_NOTEBOOK'),items.get('dataflow','REQUIRES_PUBLISHED_DATAFLOW'),
        connections.get('warehouse','REQUIRES_OWNER_CONNECTION'))
    write(root/'pipelines/pl_nightly_run_all/pipeline-content.json',warehouse_item_binding(nightly,workspace,warehouse_id,warehouse_server))
    write(root/'deployment-requirements.json',{'workspace_id':workspace,'lakehouse_id':lakehouse,'warehouse_id':warehouse_id,'warehouse_server':warehouse_server,'connections':connections,'missing_connections':[k for k in('clinical','billing','warehouse')if not connections.get(k)],'native_pipelines_verified':False,'planned_schedules':{'clinical':'daily02UTC','billing':'daily0230UTC','warehouse':'daily03UTC','revenue_model':'daily04UTC'},'cadence_reason':'One source wake per day plus60minute inactivity tail is estimated within the free CPU allowance; continuous4hour wakes are not. Daily cadence deliberately permits latency.','schedule_enablement':'Only after manual verification and free-offer allowance review; never paid fallback'})
