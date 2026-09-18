"""Create new native Direct Lake model/reports; no investigator configuration edits."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from publish_import_fixture import Publisher, Journal, transport
from challenge_freeze import verify
from build_powerbi_reports import Report, write, BASE


def model(endpoint, vocabulary=None):
    vocabulary=vocabulary or {}
    definitions={
        'Movements':('movement_values',[('product_id','int64'),('movement_id','int64'),('warehouse_id','int64'),('units','int64'),('event_day','string'),('movement_type','string'),('rate_version','int64'),('unit_cost','int64'),('movement_value','int64')]),
        'Warehouses':('warehouse_locations',[('warehouse_id','int64'),('warehouse_name','string')]),
        'Products':('inventory_products',[('product_id','int64'),('product_name','string')]),
        'Purchases':('purchase_orders',[('purchase_order_id','int64'),('warehouse_id','int64'),('product_id','int64'),('ordered_units','int64'),('status','string')]),
        'Adjustments':('inventory_adjustments',[('adjustment_id','int64'),('movement_id','int64'),('units','int64'),('reason_code','string')])}
    tables=[{'name':name,'columns':[{'name':c,'sourceColumn':c,'dataType':t,'summarizeBy':'none'} for c,t in cols],
             'partitions':[{'name':name,'mode':'directLake','source':{'type':'entity','schemaName':'dbo','entityName':source,'expressionSource':'WarehouseSource'}}]}
            for name,(source,cols) in definitions.items()]
    measures={'Movement Units':'SUM(Movements[units])',
              'Received Units':'CALCULATE([Movement Units],Movements[movement_type]="RECEIPT")',
              'Issued Units':'CALCULATE([Movement Units],Movements[movement_type]="ISSUE")',
              'Receipt Share':'DIVIDE([Received Units],[Movement Units])',
              'Net Movement Units':'[Received Units]-[Issued Units]',
              'Movement Value':'SUM(Movements[movement_value])',
              'Value Per Unit':'DIVIDE([Movement Value],[Movement Units])',
              'Movement Rows':'COUNTROWS(Movements)'}
    tables[0]['measures']=[{'name':n,'expression':e} for n,e in measures.items()]
    relations=[{'name':'Movements'+dim,'fromTable':'Movements','fromColumn':col,'toTable':dim,'toColumn':col,
                'fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection','isActive':True}
               for dim,col in [('Warehouses','warehouse_id'),('Products','product_id')]]
    for table in tables:
        table['name']=vocabulary.get(table['name'],table['name'])
        table['partitions'][0]['name']=table['name']
        for measure in table.get('measures',[]):
            measure['name']=vocabulary.get(measure['name'],measure['name'])
            for old,new in vocabulary.items():
                # These are publisher-owned templates, not arbitrary DAX rewriting.
                measure['expression']=measure['expression'].replace('['+old+']','['+new+']').replace(old+'[',"'"+new.replace("'","''")+"'[")
                measure['expression']=measure['expression'].replace('COUNTROWS('+old+')',"COUNTROWS('"+new.replace("'","''")+"')")
    for relation in relations:
        for key in ('fromTable','toTable'):relation[key]=vocabulary.get(relation[key],relation[key])
    return {'compatibilityLevel':1604,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3',
            'expressions':[{'name':'WarehouseSource','kind':'m','expression':'let database = Sql.Database('+json.dumps(endpoint['connectionString'])+', '+json.dumps(endpoint['id'])+') in database'}],
            'tables':tables,'relationships':relations}}


def parts(values):
    return {'parts':[{'path':p,'payloadType':'InlineBase64','payload':base64.b64encode(json.dumps(v).encode()).decode()} for p,v in values.items()]}


def report(folder,workspace,model_id,title,metrics):
    r=Report.__new__(Report);r.root=folder;r.pages=[]
    write(folder/'definition.pbir',{'version':'4.0','datasetReference':{'byConnection':{
        'connectionString':f'Data Source=powerbi://api.powerbi.com/v1.0/myorg/{workspace};Initial Catalog={model_id};Integrated Security=ClaimsToken',
        'pbiServiceModelId':None,'pbiModelVirtualServerName':'sobe_wowvirtualserver','pbiModelDatabaseName':model_id,'name':'EntityDataSource','connectionType':'pbiServiceXmlaStyleLive'}}})
    write(folder/'definition/version.json',{'$schema':BASE+'definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
    write(folder/'definition/report.json',{'$schema':BASE+'definition/report/3.0.0/schema.json',
        'themeCollection':{'baseTheme':{'name':'CY24SU06','reportVersionAtImport':{'visual':'1.8.0','page':'1.3.0','report':'2.0.0'},'type':'SharedResources'}},
        'settings':{'useStylableVisualContainerHeader':True}})
    r.page(title,title,'Warehouse operations | select a location to inspect its activity')
    r.slicer(('Warehouses','warehouse_name',False,'Warehouse'),24)
    for i,name in enumerate(metrics):
        r.visual('card',name,24+i*314,180,290,100,{'Values':[('Movements',name,True,name)]})
    r.visual('tableEx','Activity by warehouse',24,310,1200,420,{'Values':[('Warehouses','warehouse_name',False,'Warehouse')]+[('Movements',n,True,n) for n in metrics]})
    r.finish()
    return parts({p.relative_to(folder).as_posix():json.loads(p.read_text()) for p in folder.rglob('*') if p.is_file()})


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--folder',type=Path,required=True)
    args=parser.parse_args();folder=args.folder;verify(json.loads((folder/'freeze.json').read_text()))
    config=json.loads((folder/'config.json').read_text());w=config['fabric']['workspace_id']
    publisher=Publisher(Journal(folder/'publisher.sqlite'),transport)
    gold=json.loads((folder/'lakehouses.json').read_text())['gold']
    endpoint=publisher.call(f'workspaces/{w}/lakehouses/{gold}')['text']['properties']['sqlEndpointProperties']
    if endpoint.get('provisioningStatus')!='Success':raise RuntimeError('Gold SQL endpoint not ready')
    vocabulary=json.loads((folder/'vocabulary.json').read_text()) if (folder/'vocabulary.json').exists() else {}
    body=model(endpoint,vocabulary)
    definition=parts({'model.bim':body,'definition.pbism':{'version':'1.0','settings':{}}})
    suffix=json.loads((folder/'publisher-input.json').read_text())['suffix']
    result=publisher.item(publisher.post('semantic-model',f'workspaces/{w}/semanticModels',{'displayName':'Warehouse Operations '+suffix,'definition':definition}))
    write(folder/'model.json',result)
    reports=[]
    for title,metrics in [('Inventory Health',['Movement Units','Receipt Share','Net Movement Units','Movement Value']),
                          ('Warehouse Performance',['Received Units','Issued Units','Movement Rows','Value Per Unit'])]:
        definition=report(folder/(title.replace(' ','')+'.Report'),w,result['id'],title,metrics)
        if vocabulary:
            for part in definition['parts']:
                value=json.loads(base64.b64decode(part['payload']))
                def rename(value):
                    if isinstance(value,str):
                        if value in vocabulary:return vocabulary[value]
                        for old,new in vocabulary.items():value=value.replace(old+'.',new+'.').replace('.'+old,'.'+new)
                        return value
                    if isinstance(value,list):return [rename(v) for v in value]
                    if isinstance(value,dict):return {k:rename(v) for k,v in value.items()}
                    return value
                part['payload']=base64.b64encode(json.dumps(rename(value)).encode()).decode()
        reports.append(publisher.item(publisher.post('report-theme-v2-'+title,f'workspaces/{w}/reports',{'displayName':title+' '+suffix,'definition':definition})))
        write(folder/'reports.json',reports)
    print(json.dumps({'model':result['id'],'reports':[r['id'] for r in reports]}))


if __name__=='__main__':main()
