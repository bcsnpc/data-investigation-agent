"""Native Fabric model/report definitions, built without scoring truth."""
import base64
import json
from pathlib import Path
from uuid import NAMESPACE_URL,uuid5

BASE='https://developer.microsoft.com/json-schemas/fabric/item/report/'
TARGETS={
    'A':('dw.LoadedOrderLine','Quantity','Units'),
    'B':('mart.V_PRM_X4','WRITTEN_PRM','Written Premium'),
    'C':('mart.SalesItems','NETWR','Net Sales'),
    'D':('mart.Enrolments',None,'Enrolments'),
}


def parts(files):
    return {'parts':[dict(path=name,payload=base64.b64encode(content.encode('utf8')).decode('ascii'),payloadType='InlineBase64')for name,content in sorted(files.items())]}


def model(spec,table,server,columns):
    schema,item=table.split('.')
    name='Fact'
    def dtype(t):
        t=t.lower()
        return 'dateTime'if 'date'in t else 'boolean'if t=='bit'else 'decimal'if any(k in t for k in('decimal','numeric','float','real'))else 'int64'if 'int'in t else 'string'
    fields=[dict(name=c['name'],sourceColumn=c['name'],dataType=dtype(c['data_type']))for c in columns]
    metric=TARGETS[spec['id']]
    expression='COUNTROWS(Fact)'if metric[1]is None else 'SUM(Fact['+metric[1]+'])'
    tables=[dict(name=name,columns=fields,measures=[dict(name=metric[2],expression=expression)],partitions=[dict(name='Native SQL Import',mode='import',source=dict(type='m',expression=[
        'let',f' Source = Sql.Database("{server}", "{spec["database"]}"),',f' Data = Source{{[Schema="{schema}",Item="{item}"]}}[Data]',
        'in Data']))])]
    roles=[]
    if spec['id']=='D':
        tables.append(dict(name='Staff',columns=[dict(name=n,sourceColumn=n,dataType=t)for n,t in [('StaffId','int64'),('DepartmentId','int64'),('Salary','decimal')]],
            partitions=[dict(name='Staff',mode='import',source=dict(type='m',expression=f'let Source=Sql.Database("{server}","{spec["database"]}") in Source{{[Schema="private",Item="Staff"]}}[Data]'))]))
        roles=[dict(name='DepartmentReader',modelPermission='read',tablePermissions=[dict(name='Staff',filterExpression='Staff[DepartmentId] = 1',columnPermissions=[dict(name='Salary',metadataPermission='none')])])]
    return dict(name=spec['workspace']+' Model',compatibilityLevel=1604,model=dict(culture='en-US',defaultPowerBIDataSourceVersion='powerBI_V3',tables=tables,relationships=[],roles=roles))


def report(spec,model_id):
    page=uuid5(NAMESPACE_URL,'scan-benchmark/'+spec['id']+'/overview').hex[:20]
    visual=uuid5(NAMESPACE_URL,page+'/metric').hex[:20]
    metric=TARGETS[spec['id']][2]
    files={
        'definition.pbir':dict(version='4.0',datasetReference=dict(byConnection=dict(connectionString=f'Data Source=powerbi://api.powerbi.com/v1.0/myorg/{spec["workspace"]};Initial Catalog={model_id};Integrated Security=ClaimsToken',pbiServiceModelId=None,pbiModelVirtualServerName='sobe_wowvirtualserver',pbiModelDatabaseName=model_id,name='EntityDataSource',connectionType='pbiServiceXmlaStyleLive'))),
        'definition/version.json':{'$schema':BASE+'definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'},
        'definition/report.json':{'$schema':BASE+'definition/report/3.0.0/schema.json',
            'themeCollection':{'baseTheme':{'name':'CY24SU06','reportVersionAtImport':{'visual':'1.8.0','page':'1.3.0','report':'2.0.0'},'type':'SharedResources'}},
            'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized','defaultDrillFilterOtherVisuals':True}},
        'definition/pages/pages.json':{'$schema':BASE+'definition/pagesMetadata/1.0.0/schema.json','pageOrder':[page],'activePageName':page},
        f'definition/pages/{page}/page.json':{'$schema':BASE+'definition/page/2.0.0/schema.json','name':page,'displayName':'Overview','displayOption':'FitToPage','width':1280,'height':720},
        f'definition/pages/{page}/visuals/{visual}/visual.json':{'$schema':BASE+'definition/visualContainer/2.4.0/schema.json','name':visual,'position':dict(x=30,y=30,width=400,height=160,z=0,tabOrder=0),
            'visual':dict(visualType='card',query=dict(queryState={'Values':{'projections':[dict(field={'Measure':{'Expression':{'SourceRef':{'Entity':'Fact'}},'Property':metric}},queryRef='Fact.'+metric,nativeQueryRef=metric)]}}))},
    }
    return {k:json.dumps(v,sort_keys=True)for k,v in files.items()}


def write_model(spec,build_plan,server,output):
    address=TARGETS[spec['id']][0]
    # Caller passes owner build column declarations, never expected answers.
    columns=next(o['columns']for o in build_plan['objects']if o['address']==address)
    value=model(spec,address,server,columns)
    files={'model.bim':json.dumps(value,sort_keys=True),'definition.pbism':json.dumps({'version':'1.0','settings':{}})}
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    for key,content in files.items():(root/key).write_text(content,encoding='utf8')
    return files
