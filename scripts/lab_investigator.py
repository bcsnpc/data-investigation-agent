"""Deterministic reconciliation over a lab business projection, never evaluator truth."""
from contextlib import closing
from datetime import datetime,timezone
from decimal import Decimal,localcontext
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from uuid import uuid4
from investigation_checks import number


def reconcile(payload):
    if set(payload)!={'mode','rows'} or payload['mode']!='local_lab' or not isinstance(payload['rows'],list):
        raise ValueError('Expected isolated lab evidence')
    if not 1<=len(payload['rows'])<=100000:raise ValueError('Invalid evidence size')
    seen=set();currencies={};affected=[]
    with localcontext() as context:
        context.prec=100
        for i,row in enumerate(payload['rows']):
            if set(row)!={'order_id','currency','silver_net_cash','gold_net_cash','silver_present','gold_present'}:
                raise ValueError('Unsupported record fields')
            if not isinstance(row['order_id'],str) or not re.fullmatch(r'ORD-\d{6}',row['order_id']):raise ValueError('Invalid order key')
            if not isinstance(row['currency'],str) or not re.fullmatch(r'[A-Z]{3}',row['currency']):raise ValueError('Invalid currency')
            key=(row['order_id'],row['currency'])
            if key in seen:raise ValueError('Duplicate business key')
            seen.add(key);values=[]
            for layer in ('silver','gold'):
                present=row[layer+'_present'];value=row[layer+'_net_cash']
                if type(present) is not bool or (not present and value is not None):raise ValueError('Inconsistent presence evidence')
                if present:
                    value=number(str(value) if isinstance(value,Decimal) else value)
                    if abs(value)>=Decimal('1e28') or value.as_tuple().exponent < -4:raise ValueError('Amount outside metric contract')
                else:value=Decimal(0)
                values.append(value)
            if not row['silver_present'] and not row['gold_present']:raise ValueError('Absent on both sides')
            silver,gold=values;difference=gold-silver
            totals=currencies.setdefault(row['currency'],{'silver_total':Decimal(0),'gold_total':Decimal(0),'downstream_minus_upstream':Decimal(0),'affected_records':0})
            totals['silver_total']+=silver;totals['gold_total']+=gold;totals['downstream_minus_upstream']+=difference
            status='MISSING_IN_GOLD' if not row['gold_present'] else 'EXTRA_IN_GOLD' if not row['silver_present'] else 'VALUE_MISMATCH' if difference else 'MATCH'
            if status!='MATCH':
                totals['affected_records']+=1
                affected.append({'order_id':key[0],'currency':key[1],'status':status,
                    'downstream_minus_upstream':format(difference,'.4f'),'reference':'/request/lab_evidence/rows/'+str(i)})
        totals={currency:{key:format(value,'.4f') if isinstance(value,Decimal) else value for key,value in group.items()} for currency,group in currencies.items()}
    return {'classification':'UNRESOLVED','comparison_status':'MISMATCH' if affected else 'MATCH',
            'compared_boundary':{'upstream':'silver','downstream':'gold'},'affected_records':affected,'impact_by_currency':totals,
            'automatic_defect_routing':False,'root_cause_verified':False,
            'limitation':'Local projected records only. Absent records contribute zero to aggregate differences, but remain explicitly missing. Matching records do not establish expected business behavior; differences do not prove a cause or the first boundary across the full estate.'}


def investigate(payload,database,business_context=None,cause_verifier=None):
    result=reconcile(payload);identity=str(uuid4());observations={}
    if business_context is not None:
        from expected_behavior import verify_refunds
        result['business_verification']=verify_refunds(payload,business_context,result)
        if result['business_verification']['verified']:
            result['classification']='EXPECTED_BEHAVIOR'
            result['limitation']='Verified only for the recorded local capture-minus-refund question and compared Silver/Gold records. Does not prove full-estate correctness, business-event legitimacy or period-over-period trends.'
    cause=None
    if cause_verifier is not None:
        cause=cause_verifier(payload,result)
        if cause['verified']:
            classification=cause.get('classification','TECHNICAL_DEFECT')
            if classification not in ('TECHNICAL_DEFECT','REFRESH_FRESHNESS'):raise ValueError('Unsupported verified classification')
            result.update(classification=classification,root_cause_verified=True,
                root_cause=cause['cause'],limitation='Verified against one local build receipt and replay. Not a full-estate first-boundary or production finding; routing remains disabled.')
    for currency,totals in result['impact_by_currency'].items():
        observations['net_cash_'+currency]=[{'layer':layer,'status':'AVAILABLE','data':totals[layer+'_total'],'currency':currency,'filters':{'scope':'local_lab'}} for layer in ('silver','gold')]
    encoded=json.dumps(payload,default=str,sort_keys=True)
    request={'kind':'lab_record_reconciliation','lab_evidence':json.loads(encoded),
             'evidence_hash':hashlib.sha256(encoded.encode()).hexdigest(),'observations':observations}
    if business_context is not None:request['business_context']=json.loads(json.dumps(business_context,default=str))
    if cause is not None:request['cause_evidence']=cause
    request['evidence_hash']=hashlib.sha256(json.dumps({k:request.get(k) for k in ('lab_evidence','business_context','cause_evidence')},sort_keys=True).encode()).hexdigest()
    result['id']=identity;Path(database).parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(database)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT)')
        db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)',(identity,None,datetime.now(timezone.utc).isoformat(),json.dumps(request),json.dumps(result)));db.commit()
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--explain-returns',action='store_true');parser.add_argument('--verify-filter','--verify-cause',dest='verify_filter',action='store_true');args=parser.parse_args()
    from defect_lab import ROOT,evidence
    captured=evidence(ROOT/'.local/defect-lab/lab.duckdb',include_business_drivers=args.explain_returns)
    payload,context=captured if args.explain_returns else (captured,None)
    from lab_filter_cause import verify
    verifier=(lambda payload,result:verify(ROOT/'.local/defect-lab/lab.duckdb',payload,result)) if args.verify_filter else None
    result=investigate(payload,ROOT/'.local/defect-lab/evidence.sqlite',context,verifier)
    print(json.dumps(result,indent=2))
