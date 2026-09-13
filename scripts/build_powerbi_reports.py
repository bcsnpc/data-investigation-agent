"""Generate PBIR reports with explicit measure bindings and order drillthrough."""
import json
from pathlib import Path
from uuid import uuid5,NAMESPACE_URL
ROOT=Path(__file__).resolve().parents[1]
BASE='https://developer.microsoft.com/json-schemas/fabric/item/report/'
def uid(s):return uuid5(NAMESPACE_URL,'orderops/report/'+s).hex[:20]
def lit(s):return {'expr':{'Literal':{'Value':"'"+str(s).replace("'","''")+"'"}}}
def num(n):return {'expr':{'Literal':{'Value':str(n)+'D'}}}
def boolean(v):return {'expr':{'Literal':{'Value':str(v).lower()}}}
def field(table,column,measure=False):
    return {'Measure' if measure else 'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':column}}
def col(table,column,label=None):return (table,column,False,label or column.replace('_',' ').title())
def measure(name):return ('FactOrderLine',name,True,name)
def projection(f):return {'field':field(*f[:3]),'queryRef':f[0]+'.'+f[1],'nativeQueryRef':f[1],'displayName':f[3]}
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')

class Report:
    def __init__(self,slug,model_id):
        self.root=ROOT/'infra/powerbi'/f'{slug}.Report'
        self.pages=[]
        write(self.root/'definition.pbir',{'version':'4.0','datasetReference':{'byConnection':{
         'connectionString':f'Data Source=powerbi://api.powerbi.com/v1.0/myorg/ws-investigator-dev;Initial Catalog={model_id};Integrated Security=ClaimsToken',
         'pbiServiceModelId':None,'pbiModelVirtualServerName':'sobe_wowvirtualserver','pbiModelDatabaseName':model_id,'name':'EntityDataSource','connectionType':'pbiServiceXmlaStyleLive'}}})
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
            data['pageBinding']={'name':'order_details','type':'Drillthrough','parameters':[{'name':'order_parameter','boundFilter':'order_drill','fieldExpr':field('FactOrder','order_id')}],'acceptsFilterContext':'Default'}
            data['filterConfig']={'filters':[{'name':'order_drill','field':field('FactOrder','order_id'),'type':'Categorical','howCreated':'Drillthrough'}]}
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
             'labels':[{'properties':{'fontSize':num(34)}}]}
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

def build(model_id):
    r=Report('ExecutiveSales',model_id)
    r.page('executive','Executive Sales','Order-date cohorts • sales exclude tax • cash includes tax • select one currency')
    for f,x in [(col('DimDate','year_month','Order Month'),24),(col('DimCustomer','customer_segment','Customer Segment'),338),(col('DimCustomer','state_code','State'),652),(col('FactOrder','currency','Currency'),966)]:r.slicer(f,x,290)
    r.cards(['Net Sales','Net Cash','Order Count','Average Order Value'])
    r.visual('lineChart','Sales and net sales by order month',24,300,750,240,{'Category':[col('DimDate','year_month')],'Y':[measure('Sales Amount'),measure('Net Sales')]})
    r.visual('clusteredBarChart','Net sales by product group',798,300,458,240,{'Category':[col('DimProduct','subcategory')],'Y':[measure('Net Sales')]})
    r.visual('clusteredBarChart','Net sales by state',24,558,750,240,{'Category':[col('DimCustomer','state_code')],'Y':[measure('Net Sales')]})
    r.visual('tableEx','Capture and refund reconciliation',798,558,458,240,{'Values':[measure('Captured Amount'),measure('Refund Amount'),measure('Net Cash'),measure('Net Tax')]})
    r.finish()
    r=Report('OrderOperations',model_id)
    r.page('operations','Order Operations','Select an order or right-click an order row → Drill through → Order Detail')
    for f,x in [(col('FactOrder','order_id','Order ID'),24),(col('FactOrder','status','Order Status'),338),(col('DimDate','year_month','Order Month'),652),(col('FactOrder','currency','Currency'),966)]:r.slicer(f,x,290)
    r.cards(['Order Count','Cancelled Orders','Refund Amount','Net Cash'])
    r.visual('clusteredBarChart','Orders by lifecycle status',24,300,420,490,{'Category':[col('FactOrder','status')],'Y':[measure('Order Count')]})
    r.visual('tableEx','Orders • right-click an ID for detail',468,300,788,490,{'Values':[col('FactOrder','order_id'),col('FactOrder','order_day'),col('FactOrder','status'),col('DimCustomer','customer_name'),measure('Captured Amount'),measure('Refund Amount'),measure('Net Cash')]})
    r.page('order-detail','Order Detail','Select an order to trace its captured amount, individual lines and refund events.',True)
    r.slicer(col('FactOrder','order_id','Order ID'),24,600)
    r.slicer(col('FactOrder','currency','Currency'),652,604)
    r.cards(['Captured Amount','Refund Amount','Net Cash','Net Units'])
    r.visual('tableEx','Order lines and product amounts',24,300,1232,240,{'Values':[col('FactOrderLine','order_line_id'),col('DimProduct','product_name'),measure('Units Sold'),measure('Sales Amount'),measure('Tax Amount'),measure('Refund Amount'),measure('Net Cash')]})
    r.visual('tableEx','Refund events • includes paid cancellations before shipment',24,558,1232,240,{'Values':[col('FactRefund','refund_id'),col('FactRefund','payment_id'),col('FactRefund','refund_day'),col('FactRefund','refund_reason'),measure('Event Refund Amount')]})
    r.finish()
    r=Report('ProductPerformance',model_id)
    r.page('product','Product Performance','Product filters use line-level measures • refunded units include paid cancellations')
    for f,x in [(col('DimDate','year_month','Order Month'),24),(col('DimProduct','subcategory','Product Group'),338),(col('DimProduct','product_name','Product'),652),(col('FactOrder','currency','Currency'),966)]:r.slicer(f,x,290)
    r.cards(['Net Sales','Units Sold','Discount %','Refund %'])
    r.visual('clusteredBarChart','Net sales by product group',24,300,440,240,{'Category':[col('DimProduct','subcategory')],'Y':[measure('Net Sales')]})
    r.visual('lineChart','Units sold and refunded by order month',488,300,768,240,{'Category':[col('DimDate','year_month')],'Y':[measure('Units Sold'),measure('Units Refunded')]})
    r.visual('tableEx','Product performance • ratios use totals',24,558,1232,240,{'Values':[col('DimProduct','product_id'),col('DimProduct','product_name'),col('DimProduct','category'),measure('Order Count'),measure('Net Sales'),measure('Units Sold'),measure('Discount %'),measure('Refund %')]})
    r.finish()

if __name__=='__main__':
    config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
    build(config['semantic_model_id'])
    print('Generated three PBIR reports')
