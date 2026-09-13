"""Generate a reviewable Direct Lake TMSL model from validated Gold schemas."""
import json
from pathlib import Path
from uuid import uuid5,NAMESPACE_URL

ROOT=Path(__file__).resolve().parents[1]
TABLES={'DimDate':'dim_date','DimCustomer':'dim_customer','DimProduct':'dim_product',
 'FactOrder':'order_summary','FactOrderLine':'order_line_summary','FactRefund':'refund_summary'}
RELATIONSHIPS=[('FactOrder','customer_id','DimCustomer','customer_id'),
 ('FactOrder','order_day','DimDate','date'),('FactOrderLine','order_id','FactOrder','order_id'),
 ('FactOrderLine','product_id','DimProduct','product_id'),('FactRefund','order_id','FactOrder','order_id')]
MONEY={'Gross Sales':'gross_sales_amount','Discount Amount':'discount_amount','Sales Amount':'sales_amount',
 'Tax Amount':'tax_amount','Captured Amount':'captured_amount','Refunded Sales':'refunded_sales_amount',
 'Refunded Tax':'refunded_tax_amount','Refund Amount':'refund_amount','Net Sales':'net_sales_amount',
 'Net Tax':'net_tax_amount','Net Cash':'net_cash_amount'}
UNITS={'Units Ordered':'units_ordered','Units Sold':'units_sold','Units Refunded':'units_returned','Net Units':'net_units'}
def tag(value):return str(uuid5(NAMESPACE_URL,'orderops/'+value))

def measures():
    result=[]
    def add(name,expression,fmt='#,##0.00',description='',folder='Financial'):
        result.append({'name':name,'expression':expression,'formatString':fmt,'description':description,
         'displayFolder':folder,'lineageTag':tag('measure/'+name)})
    for name,column in MONEY.items():
        add(name,f'IF(HASONEVALUE(FactOrderLine[currency]), SUM(FactOrderLine[{column}]))',
         description=f'Gold {column}, by original order-date cohort. Blank across multiple currencies. Paid cancellations preserve capture and refund history.')
    for name,column in UNITS.items():
        add(name,f'SUM(FactOrderLine[{column}])','#,##0',
         'Refunded quantities include paid cancellations before shipment.','Quantities')
    add('Order Count','DISTINCTCOUNT(FactOrderLine[order_id])','#,##0','Distinct orders in the selected product/customer/date context.','Orders')
    add('Funded Orders','CALCULATE([Order Count], FactOrderLine[is_funded] = 1)','#,##0',folder='Orders')
    add('Cancelled Orders','CALCULATE([Order Count], FactOrderLine[status] = "CANCELLED")','#,##0',folder='Orders')
    add('Refunded Orders','CALCULATE([Order Count], FactOrderLine[refund_amount] > 0)','#,##0',folder='Orders')
    add('Average Order Value','DIVIDE([Sales Amount], [Funded Orders])',description='Funded merchandise after discounts, before refunds, per funded order.')
    add('Discount %','DIVIDE([Discount Amount], [Gross Sales])','0.00%','Ratio of totals; both item and coupon discounts.')
    add('Refund %','DIVIDE([Refund Amount], [Captured Amount])','0.00%','Refunded cash divided by captured cash, both including tax.')
    add('Selected Currency','SELECTEDVALUE(FactOrderLine[currency], "Select one currency")','',folder='Context')
    add('Refund Events','COUNTROWS(FactRefund)','#,##0','Refund events in the order/date/customer context. Product filtering applies to line measures, not this event count.','Refund events')
    add('Event Refund Amount','IF(HASONEVALUE(FactRefund[currency]), SUM(FactRefund[refund_amount]))',
      description='Refund headers; use refund_day for refund-calendar analysis. Product filters do not filter refund headers.',folder='Refund events')
    return result

def build(config,evidence):
    assert evidence['status']=='READY'
    tables=[]
    for name,source in TABLES.items():
        columns=[]
        for f in evidence['schemas'][source]['fields']:
            raw=f['type'];typ='decimal' if isinstance(raw,str) and raw.startswith('decimal') else {'string':'string','integer':'int64','long':'int64','date':'dateTime','timestamp':'dateTime','boolean':'boolean'}[raw]
            col={'name':f['name'],'sourceColumn':f['name'],'dataType':typ,'summarizeBy':'none','lineageTag':tag(name+'/'+f['name'])}
            if f['name'].startswith('_') or (name.startswith('Fact') and typ in ('decimal','int64')):col['isHidden']=True
            if raw=='date':col.update(formatString='yyyy-MM-dd',annotations=[{'name':'UnderlyingDateTimeDataType','value':'Date'}])
            if raw=='timestamp':col['formatString']='yyyy-MM-dd HH:mm:ss'
            if typ=='decimal':col['formatString']='#,##0.00'
            if name=='DimDate' and f['name']=='month':col['sortByColumn']='month_number'
            columns.append(col)
        tables.append({'name':name,'lineageTag':tag(name),'columns':columns,
         'description':f'Gold {source}; validated snapshot {evidence["gold_run_id"]}.',
         'partitions':[{'name':name,'mode':'directLake','source':{'type':'entity','schemaName':'dbo','entityName':source,'expressionSource':'GoldSource'}}]})
    tables[4]['measures']=measures()
    relations=[{'name':tag('/'.join(r)),'fromTable':r[0],'fromColumn':r[1],'toTable':r[2],'toColumn':r[3],
     'fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection','isActive':True} for r in RELATIONSHIPS]
    endpoint=config['gold_sql_endpoint']
    return {'compatibilityLevel':1604,'model':{'culture':'en-US','sourceQueryCulture':'en-US',
     'defaultPowerBIDataSourceVersion':'powerBI_V3','discourageImplicitMeasures':True,
     'annotations':[{'name':'GoldValidationRun','value':evidence['gold_run_id']}],
     'expressions':[{'name':'GoldSource','kind':'m','expression':f'let database = Sql.Database("{endpoint}", "{config["gold_sql_endpoint_id"]}") in database'}],
     'tables':tables,'relationships':relations}}

if __name__=='__main__':
    config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
    evidence=json.loads((ROOT/'.local/reporting-dimensions.json').read_text())
    target=ROOT/'infra/powerbi/OrderOps.SemanticModel'
    target.mkdir(parents=True,exist_ok=True)
    (target/'model.bim').write_text(json.dumps(build(config,evidence),indent=2)+'\n')
    (target/'definition.pbism').write_text(json.dumps({'version':'1.0','settings':{}},indent=2)+'\n')
    print('Generated OrderOps.SemanticModel')
