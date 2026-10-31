"""HealthNet PBIR authoring. Definitions require native publication and visual checks."""
import json
from pathlib import Path
from uuid import uuid5,NAMESPACE_URL
ROOT=Path(__file__).resolve().parent
from .models import MEASURES
BASE='https://developer.microsoft.com/json-schemas/fabric/item/report/'
def uid(s):return uuid5(NAMESPACE_URL,'healthnet/report/'+s).hex[:20]
def lit(s):return {'expr':{'Literal':{'Value':"'"+str(s).replace("'","''")+"'"}}}
def num(n):return {'expr':{'Literal':{'Value':str(n)+'D'}}}
def boolean(v):return {'expr':{'Literal':{'Value':str(v).lower()}}}
def field(table,column,measure=False):
    return {'Measure' if measure else 'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':column}}
def col(table,column,label=None):return (table,column,False,label or column.replace('_',' ').title())
def measure(name):return (MEASURES[name][0],name,True,name)
def projection(f):return {'field':field(*f[:3]),'queryRef':f[0]+'.'+f[1],'nativeQueryRef':f[0]+'.'+f[1],'displayName':f[3]}
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')

class Report:
    def __init__(self,slug,model_id,root=None):
        self.root=(Path(root)if root else ROOT/'reports')/f'{slug}.Report'
        self.pages=[]
        write(self.root/'definition.pbir',{'version':'4.0','datasetReference':{'byConnection':{
         'connectionString':f'Data Source=powerbi://api.powerbi.com/v1.0/myorg/HealthNet Analytics;Initial Catalog={model_id};Integrated Security=ClaimsToken',
         'pbiServiceModelId':None,'pbiModelVirtualServerName':'sobe_wowvirtualserver','pbiModelDatabaseName':model_id,'name':'EntityDataSource','connectionType':'pbiServiceXmlaStyleLive'}}})
        if model_id is None:
            model_name={'HealthNetOperations':'HealthNet Operations','HealthNetRevenue':'HealthNet Revenue','HealthNetDoctorProductivity':'HealthNet Productivity'}[slug]
            write(self.root/'definition.pbir',{'version':'4.0','datasetReference':{'byPath':{'path':'../../models/'+model_name+'.SemanticModel'}}})
        write(self.root/'definition/version.json',{'$schema':BASE+'definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
        write(self.root/'definition/report.json',{'$schema':BASE+'definition/report/3.0.0/schema.json',
         'themeCollection':{'baseTheme':{'name':'CY24SU06','reportVersionAtImport':{'visual':'1.8.0','page':'1.3.0','report':'2.0.0'},'type':'SharedResources'}},
         'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized','defaultDrillFilterOtherVisuals':True}})
    def page(self,name,title,subtitle,drill=False):
        self.current=uid(name);self.pages.append(self.current);self.seq=0
        data={'$schema':BASE+'definition/page/2.0.0/schema.json','name':self.current,'displayName':title,
         'displayOption':'FitToPage','width':1280,'height':820,
         'objects':{'background':[{'properties':{'color':{'solid':{'color':lit('#F3F6FA')}},'transparency':num(0)}}]}}
        if drill:
            data['pageBinding']={'name':'doctor_details','type':'Drillthrough','parameters':[{'name':'provider_parameter','boundFilter':'provider_drill','fieldExpr':field('core_provider','id')}],'acceptsFilterContext':'Default'}
            data['filterConfig']={'filters':[{'name':'provider_drill','field':field('core_provider','id'),'type':'Categorical','howCreated':'Drillthrough'}]}
        write(self.root/f'definition/pages/{self.current}/page.json',data)
        self.text(title,subtitle)
    def visual(self,kind,title,x,y,w,h,roles=None,objects=None):
        self.seq+=1;name=uid(self.current+str(self.seq))
        visual={'visualType':kind,'visualContainerObjects':{
         'title':[{'properties':{'show':boolean(True),'text':lit(title),'fontSize':num(12),'fontColor':{'solid':{'color':lit('#17324D')}}}}],
         'background':[{'properties':{'show':boolean(True),'color':{'solid':{'color':lit('#FFFFFF')}},'transparency':num(0)}}]}}
        if roles:visual['query']={'queryState':{role:{'projections':[projection(f) for f in fields]} for role,fields in roles.items()}}
        if objects:visual['objects']=objects
        if kind in ('slicer','textbox'):
            visual['visualContainerObjects']['title'][0]['properties']['show']=boolean(False)
        if kind=='card':
            visual['objects']={'categoryLabels':[{'properties':{'show':boolean(False)}}],
             'labels':[{'properties':{'fontSize':num(28),'labelDisplayUnits':num(1)}}]}
        data={'$schema':BASE+'definition/visualContainer/2.4.0/schema.json','name':name,
         'position':{'x':x,'y':y,'width':w,'height':h,'z':self.seq,'tabOrder':self.seq},'visual':visual}
        write(self.root/f'definition/pages/{self.current}/visuals/{name}/visual.json',data)
    def text(self,title,subtitle):
        self.visual('textbox','',24,12,1232,76,objects={'general':[{'properties':{'paragraphs':[
         {'textRuns':[{'value':title,'textStyle':{'fontSize':'23pt','fontWeight':'bold','color':'#17324D'}}]},
         {'textRuns':[{'value':subtitle,'textStyle':{'fontSize':'10pt','color':'#52667A'}}]}]}}]})
    def slicer(self,f,x,w=295):self.visual('slicer',f[3],x,96,w,70,{'Values':[f]}, {'data':[{'properties':{'mode':lit('Dropdown')}}]})
    def cards(self,names):
        for i,name in enumerate(names):self.visual('card',name,24+i*314,180,290,100,{'Values':[measure(name)]})
    def finish(self):
        write(self.root/'definition/pages/pages.json',{'$schema':BASE+'definition/pagesMetadata/1.0.0/schema.json','pageOrder':self.pages,'activePageName':self.pages[0]})


def filter_state(name,table,column,value):
    expr=field(table,column)
    literal={"Literal":{"Value":"'"+str(value).replace("'","''")+"'"}}
    return {"name":name,"type":"Categorical","expression":expr,"filter":{"Version":2,"From":[{"Name":"f","Entity":table,"Type":0}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"f"}},"Property":column}}],"Values":[[literal]]}}}]}}


def bookmark(report,title,filters):
    name=uid(title)
    report_path=report.root/'definition/report.json'
    definition=json.loads(report_path.read_text())
    definition.setdefault('filterConfig',{}).setdefault('filters',[])
    for f in filters:
        if not any(existing['name']==f['name']for existing in definition['filterConfig']['filters']):
            definition['filterConfig']['filters'].append({'name':f['name'],'field':f['expression'],'type':'Categorical','howCreated':'User'})
    write(report_path,definition)
    write(report.root/f'definition/bookmarks/{name}.bookmark.json',{'$schema':BASE+'definition/bookmark/2.1.0/schema.json','name':name,'displayName':title,'options':{'suppressData':False,'suppressDisplay':True},'explorationState':{'version':'1.0','activeSection':report.pages[0],'filters':{'byExpr':[dict(f,howCreated=1) for f in filters]},'sections':{report.pages[0]:{'visualContainers':{}}}}})
    path=report.root/'definition/bookmarks/bookmarks.json'
    metadata=json.loads(path.read_text())if path.exists()else{'$schema':BASE+'definition/bookmarksMetadata/1.0.0/schema.json','items':[]}
    metadata['items']=[item for item in metadata['items']if item.get('name')!=name]+[{'name':name}]
    write(path,metadata)


def build(model_ids=None,root=None):
    model_ids=model_ids or{'HealthNet Operations':None,'HealthNet Revenue':None,'HealthNet Productivity':None}
    r=Report('HealthNetOperations',model_ids['HealthNet Operations'],root)
    r.page('operations','HealthNet Operations','Fully synthetic | local-midnight census differs from encounters | select a period')
    for f,x in[(col('core_facility','name','Facility'),24),(col('core_department','name','Department'),438),(col('core_date','year_month','Month'),852)]:r.slicer(f,x,390)
    r.cards(['Midnight Census','Bed Occupancy %','ED Door-to-Provider (median)','LWBS %'])
    r.visual('clusteredBarChart','ED arrivals by local hour',24,300,590,230,{'Category':[col('mart_ed_visit','arrival_hour')],'Y':[measure('ED Visits')]})
    r.visual('clusteredBarChart','ALOS by service line',638,300,618,230,{'Category':[col('mart_encounter','service_line')],'Y':[measure('ALOS')]})
    r.visual('tableEx','Order lines by type and status',24,548,590,240,{'Values':[col('mart_order','order_type'),col('mart_order','status'),measure('Order Count'),measure('Completed Orders')]})
    r.visual('tableEx','Masked synthetic patient rows',638,548,618,240,{'Values':[col('mart_encounter','masked_mrn'),col('mart_encounter','masked_given_name'),col('mart_encounter','masked_family_name'),col('mart_encounter','encounter_number')]})
    page_path=r.root/f'definition/pages/{r.current}/page.json'
    page_definition=json.loads(page_path.read_text());page_definition['height']=1070;write(page_path,page_definition)
    r.visual('tableEx','Admissions, discharges and readmissions',24,808,590,240,{'Values':[measure('Visits'),measure('Admissions'),measure('Discharges'),measure('30-day Readmission %')]})
    r.visual('clusteredBarChart','Resulted order turnaround',638,808,618,240,{'Category':[col('mart_order','order_type')],'Y':[measure('Order Turnaround (minutes)')]})
    bookmark(r,'North ED only',[filter_state('facility_scope','core_facility','name','HealthNet North'),filter_state('department_scope','core_department','service_line','ED')])
    r.finish()
    r=Report('HealthNetRevenue',model_ids['HealthNet Revenue'],root)
    r.page('revenue','HealthNet Revenue','Fully synthetic | service date and post date differ | pending claims excluded from denial rates')
    for f,x in[(col('core_facility','name','Facility'),24),(col('core_payer','payer_group','Payer'),438),(col('core_date','year_month','Month'),852)]:r.slicer(f,x,390)
    r.cards(['Gross Charges','Net Revenue','Collections','Initial Denial Rate (count)'])
    r.visual('lineChart','Gross service date vs post date',24,300,700,230,{'Category':[col('core_date','year_month')],'Y':[measure('Gross Charges'),measure('Gross Charges by Post Date'),measure('Collections')]})
    r.visual('clusteredBarChart','Original denied dollars by category',748,300,508,230,{'Category':[col('mart_remittance','denial_category')],'Y':[measure('Denied Dollars')]})
    r.visual('clusteredBarChart','A/R aging at latest snapshot',24,548,390,240,{'Category':[col('mart_ar_aging','aging_bucket')],'Y':[measure('A/R Balance')]})
    r.visual('clusteredBarChart','Payer mix by service-date charges',438,548,390,240,{'Category':[col('core_payer','payer_group')],'Y':[measure('Gross Charges')]})
    r.visual('tableEx','Denial definitions and writeoffs',852,548,404,240,{'Values':[measure('Initial Denial Rate (count)'),measure('Final Denial Rate'),measure('Denial Rate ($)'),measure('Writeoffs')]})
    r.visual('card','Charge Rows',24,806,390,100,{'Values':[measure('Charge Rows')]})
    revenue_page=r.root/f'definition/pages/{r.current}/page.json'
    page=json.loads(revenue_page.read_text());page['height']=940;write(revenue_page,page)
    bookmark(r,'Commercial payers',[filter_state('payer_scope','core_payer','payer_group','Commercial')])
    r.finish()
    r=Report('HealthNetDoctorProductivity',model_ids['HealthNet Productivity'],root)
    r.page('productivity','Doctor Productivity','Synthetic workload units are not licensed RVUs | right-click a doctor for detail')
    r.slicer(col('core_department','name','Department'),24,600)
    r.slicer(col('core_date','year_month','Month'),652,604)
    r.cards(['Visits','Unique Patients'])
    r.visual('tableEx','Department and doctor leaderboard',24,300,1232,480,{'Values':[col('core_department','name','Department'),col('core_provider','id','Doctor ID'),col('core_provider','name','Doctor'),measure('Visits'),measure('Procedures'),measure('Order Count'),measure('RVU-style Workload per FTE')]})
    r.page('doctor-detail','Doctor Detail','Drillthrough uses the selected provider ID; cost and margin are OLS-hidden for Doctor.',True)
    r.visual('tableEx','Doctor encounters',24,110,1232,670,{'Values':[col('core_provider','name'),col('mart_encounter','encounter_number'),col('mart_encounter','service_day'),col('mart_encounter','masked_mrn','Masked MRN'),col('mart_encounter','masked_given_name','Masked Given Name'),col('mart_encounter','masked_family_name','Masked Family Name'),measure('Visits')]})
    r.finish()
