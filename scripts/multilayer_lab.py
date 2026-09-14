"""Three-layer local fixture and boundary investigation; never reads cloud data."""
from contextlib import closing
from datetime import datetime,timezone
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
import duckdb
from defect_lab import initialize,SOURCE,query,fingerprints,digest,inspect,ROOT
from lab_investigator import reconcile


def bronze_fingerprints(db):
    return {table:digest(json.dumps(db.execute('SELECT * FROM b_'+table[2:]+' ORDER BY ALL').fetchall(),default=str)) for table in SOURCE}


def initialize_multilayer(path):
    initialize(path)
    with closing(duckdb.connect(str(path))) as db:
        for table in SOURCE:db.execute('CREATE TABLE b_'+table[2:]+' AS SELECT * FROM '+table)
        db.execute('CREATE TABLE bronze_fixture_receipt(fingerprints VARCHAR)')
        db.execute('INSERT INTO bronze_fixture_receipt VALUES (?)',[json.dumps(bronze_fingerprints(db))])


def reset_multilayer(path):
    with closing(duckdb.connect(str(path))) as db:
        db.execute('BEGIN TRANSACTION')
        stored=db.execute('SELECT fingerprints FROM bronze_fixture_receipt').fetchall()
        if len(stored)!=1 or json.loads(stored[0][0])!=bronze_fingerprints(db):raise ValueError('Bronze fixture changed; reset refused')
        if inspect(db)['transformation_changed']:raise ValueError('Gold code changed; reset refused')
        for table in SOURCE:
            db.execute('DELETE FROM '+table);db.execute('INSERT INTO '+table+' SELECT * FROM b_'+table[2:])
        db.execute('DELETE FROM g_order_line_summary');db.execute('INSERT INTO g_order_line_summary '+query())
        state=inspect(db)
        if state['status']!='READY':raise ValueError('Reset failed baseline verification')
        db.execute('COMMIT');return state


def capture(path):
    with closing(duckdb.connect(str(path),read_only=True)) as db:
        db.execute('BEGIN TRANSACTION')
        layers={}
        for layer,prefix in (('bronze','b_'),('silver','s_')):
            rows=db.execute('SELECT o.order_id,o.currency,o.captured_amount-COALESCE(r.refunded,0) FROM '+prefix+'fact_order o LEFT JOIN (SELECT l.order_id,SUM(r.merchandise_amount+r.tax_amount) refunded FROM '+prefix+'fact_refund_line r JOIN '+prefix+'fact_order_line l USING(order_line_id) GROUP BY l.order_id) r USING(order_id) ORDER BY 1,2').fetchall()
            layers[layer]=[{'order_id':r[0],'currency':r[1],'net_cash':str(r[2])} for r in rows]
        layers['gold']=[{'order_id':r[0],'currency':r[1],'net_cash':str(r[2])} for r in db.execute('SELECT order_id,currency,SUM(net_cash_amount) FROM g_order_line_summary GROUP BY 1,2 ORDER BY 1,2').fetchall()]
    return {'scope':'local_same_transaction_three_layer','layers':layers}


def investigate_layers(payload,database):
    if set(payload)!={'scope','layers'} or payload['scope']!='local_same_transaction_three_layer' or set(payload['layers'])!={'bronze','silver','gold'}:raise ValueError('Complete local three-layer projection required')
    layers={}
    for layer,rows in payload['layers'].items():
        mapped={}
        for row in rows:
            if set(row)!={'order_id','currency','net_cash'}:raise ValueError('Invalid projection')
            key=(row['order_id'],row['currency'])
            if key in mapped:raise ValueError('Duplicate layer key')
            mapped[key]=row['net_cash']
        layers[layer]=mapped
    boundaries=[]
    for upstream,downstream in (('bronze','silver'),('silver','gold')):
        left,right=layers[upstream],layers[downstream]
        rows=[{'order_id':key[0],'currency':key[1],'silver_net_cash':left.get(key),'gold_net_cash':right.get(key),
               'silver_present':key in left,'gold_present':key in right} for key in sorted(left.keys()|right.keys())]
        checked=reconcile({'mode':'local_lab','rows':rows})
        impact={currency:{'upstream_total':v['silver_total'],'downstream_total':v['gold_total'],
                          'downstream_minus_upstream':v['downstream_minus_upstream'],'affected_records':v['affected_records']} for currency,v in checked['impact_by_currency'].items()}
        affected=[dict(r,status=r['status'].replace('GOLD','DOWNSTREAM'),reference='/request/layers/'+upstream+' and /request/layers/'+downstream) for r in checked['affected_records']]
        boundaries.append({'upstream':upstream,'downstream':downstream,'comparison_status':checked['comparison_status'],
                           'impact_by_currency':impact,'affected_records':affected})
    first=next(({'upstream':r['upstream'],'downstream':r['downstream']} for r in boundaries if r['comparison_status']=='MISMATCH'),None)
    identity=str(uuid4())
    result={'id':identity,'classification':'UNRESOLVED','root_cause_verified':False,'automatic_defect_routing':False,
            'first_observed_local_boundary':first,'boundaries':boundaries,
            'limitation':'Local fixture observations only. Bronze is a baseline copy, not a production ingestion snapshot. No full-estate first-boundary or transformation-cause proof.'}
    with closing(sqlite3.connect(database)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT)')
        db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)',(identity,None,datetime.now(timezone.utc).isoformat(),json.dumps(payload),json.dumps(result)));db.commit()
    return result


def run_case(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False);path=folder/'lab.duckdb'
    initialize_multilayer(path)
    try:
        with closing(duckdb.connect(str(path))) as db:
            db.execute('BEGIN TRANSACTION')
            db.execute("UPDATE s_fact_order SET captured_amount=captured_amount+10 WHERE order_id='ORD-000002'")
            db.execute("UPDATE s_fact_order_line SET line_total=line_total+10,unit_price=unit_price+10 WHERE order_id='ORD-000002'")
            db.execute('DELETE FROM g_order_line_summary');db.execute('INSERT INTO g_order_line_summary '+query());db.execute('COMMIT')
        result=investigate_layers(capture(path),folder/'evidence.sqlite')
    finally:reset=reset_multilayer(path)
    report={'result':result,'reset':reset,'product_acceptance':False}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'.local/multilayer-evaluations'/str(uuid4()));args=parser.parse_args()
    report=run_case(args.output)
    print(json.dumps({'report':str(args.output/'report.json'),'first_boundary':report['result']['first_observed_local_boundary'],'classification':report['result']['classification'],'reset':report['reset']['status']}))
