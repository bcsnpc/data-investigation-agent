"""Reconcile live DAX measures with the verified Gold report and source order."""
import json
from decimal import Decimal
from datetime import datetime,timezone
from fabric_api import api,ROOT
from build_powerbi_model import MONEY,UNITS

config=json.loads((ROOT/'infra/fabric/environment.json').read_text())
workspace=config['workspace_id'];model=config['semantic_model_id']
def query(dax):
    result=api(f'groups/{workspace}/datasets/{model}/executeQueries','post',
      {'queries':[{'query':dax}],'serializerSettings':{'includeNulls':True}},audience='powerbi')['text']
    assert 'error' not in result and 'error' not in result['results'][0],result
    return result['results'][0]['tables'][0]['rows']

gold=api(f"{workspace}/{config['gold_lakehouse_id']}/Files/validation/latest.json",audience='storage')['text']
assert gold['status']=='READY' and all(gold['checks'].values())
assert list(gold['totals_by_currency'])==['USD'],'Baseline validation expects USD; expand cases before changing currencies.'
mapping={**MONEY,**UNITS}
dax='EVALUATE ROW('+','.join(f'"{name}",[{name}]' for name in mapping)+',"Order Count",[Order Count])'
total=query(dax)[0]
for name,metric in mapping.items():
    assert Decimal(str(total[f'[{name}]']))==Decimal(str(gold['totals_by_currency']['USD'][metric])),name
assert total['[Order Count]']==gold['counts']['order_summary']
cases=[
 ('sample',[('FactOrder','order_id','ORD-000002')],1682.64,153,1529.64,1),
 ('sample mouse',[('FactOrder','order_id','ORD-000002'),('DimProduct','product_id','PROD-0062')],153,153,0,1),
 ('sample dock',[('FactOrder','order_id','ORD-000002'),('DimProduct','product_id','PROD-0124')],1529.64,0,1529.64,1),
 ('matching customer',[('FactOrder','order_id','ORD-000002'),('DimCustomer','customer_id','CUST-018515')],1682.64,153,1529.64,1),
 ('different customer',[('FactOrder','order_id','ORD-000002'),('DimCustomer','customer_id','CUST-000001')],0,0,0,0),
 ('paid cancellation',[('FactOrder','order_id','ORD-027698')],1326.54,1326.54,0,1),
]
results=[]
for name,filters,captured,refund,net,count in cases:
    clause=','.join(f'TREATAS({{"{v}"}}, {t}[{c}])' for t,c,v in filters)
    row=query('EVALUATE CALCULATETABLE(ROW("Captured",[Captured Amount],"Refund",[Refund Amount],"Net",[Net Cash],"Orders",[Order Count]),'+clause+')')[0]
    for key,value in [('Captured',captured),('Refund',refund),('Net',net),('Orders',count)]:
        assert Decimal(str(row[f'[{key}]'] or 0))==Decimal(str(value)),(name,key,row)
    results.append({'case':name,'result':row})
for day,expected in [('2025-09-12',Decimal('1529.64')),('2025-09-13',Decimal('0'))]:
    y,m,d=day.split('-')
    row=query(f'EVALUATE CALCULATETABLE(ROW("Net",[Net Cash]),TREATAS({{"ORD-000002"}},FactOrder[order_id]),TREATAS({{DATE({y},{m},{d})}},DimDate[date]))')[0]
    assert Decimal(str(row['[Net]'] or 0))==expected,(day,row)
    results.append({'case':day,'result':row})
refund=query('EVALUATE CALCULATETABLE(ROW("Events",[Refund Events],"Amount",[Event Refund Amount]),TREATAS({"ORD-000002"},FactOrder[order_id]))')[0]
assert refund['[Events]']==1 and Decimal(str(refund['[Amount]']))==Decimal('153')
evidence={'status':'PASSED','gold_run_id':gold['run_id'],'semantic_model_id':model,
 'totals':total,'filter_cases':results,'refund_event':refund,'finished_utc':datetime.now(timezone.utc).isoformat()}
(ROOT/'.local/powerbi-validation.json').write_text(json.dumps(evidence,indent=2))
print('Passed: 15 exact totals, order count, eight filter cases and refund drillthrough reconciliation.')
