"""Local multi-layer evaluation, including offsetting errors hidden by equal totals."""
from contextlib import closing
from datetime import datetime,timezone
import json
from pathlib import Path
from uuid import uuid4
import duckdb
from defect_lab import ROOT,query
from multilayer_lab import initialize_multilayer,capture,investigate_layers,reset_multilayer

# Expected answers are used only after investigation completes.
CASES={
    'matching': (None, ('0.0000',[]), ('0.0000',[])),
    'propagated': ('bronze', ('10.0000',['ORD-000002']), ('0.0000',[])),
    'gold_omission': ('silver', ('0.0000',[]), ('-99.0000',['ORD-000001'])),
    'offsetting_records': ('bronze', ('0.0000',['ORD-000001','ORD-000002']), ('0.0000',[])),
    'two_boundaries': ('bronze', ('10.0000',['ORD-000002']), ('-99.0000',['ORD-000001'])),
}


def inject(path,name):
    if name not in CASES:raise ValueError('Unknown scenario')
    with closing(duckdb.connect(str(path))) as db:
        db.execute('BEGIN TRANSACTION')
        if name in ('propagated','offsetting_records','two_boundaries'):
            db.execute("UPDATE s_fact_order SET captured_amount=captured_amount+10 WHERE order_id='ORD-000002'")
            db.execute("UPDATE s_fact_order_line SET line_total=line_total+10,unit_price=unit_price+10 WHERE order_id='ORD-000002'")
        if name=='offsetting_records':
            db.execute("UPDATE s_fact_order SET captured_amount=captured_amount-10 WHERE order_id='ORD-000001'")
            db.execute("UPDATE s_fact_order_line SET line_total=line_total-10,unit_price=unit_price-5 WHERE order_id='ORD-000001'")
        db.execute('DELETE FROM g_order_line_summary');db.execute('INSERT INTO g_order_line_summary '+query())
        if name in ('gold_omission','two_boundaries'):db.execute("DELETE FROM g_order_line_summary WHERE order_id='ORD-000001'")
        db.execute('COMMIT')


def assess(name,result):
    first,*expected_boundaries=CASES[name]
    expected_first=None if first is None else {'upstream':first,'downstream':'silver' if first=='bronze' else 'gold'}
    failures=[]
    for key,expected in [('classification','UNRESOLVED'),('root_cause_verified',False),('automatic_defect_routing',False),('first_observed_local_boundary',expected_first)]:
        if result.get(key)!=expected or type(result.get(key)) is not type(expected):failures.append(key)
    boundaries=result.get('boundaries',[])
    if len(boundaries)!=2:failures.append('boundary_count')
    for index,((gap,ids),boundary) in enumerate(zip(expected_boundaries,boundaries)):
        label='boundary_'+str(index)
        if (boundary['upstream'],boundary['downstream']) != (('bronze','silver') if index==0 else ('silver','gold')):failures.append(label+'_layers')
        if boundary['comparison_status']!=('MISMATCH' if ids else 'MATCH'):failures.append(label+'_status')
        impact=boundary['impact_by_currency']
        if set(impact)!={'USD'} or impact['USD']['downstream_minus_upstream']!=gap:failures.append(label+'_impact')
        if impact.get('USD',{}).get('affected_records')!=len(ids):failures.append(label+'_count')
        if sorted(r['order_id'] for r in boundary['affected_records'])!=ids:failures.append(label+'_records')
    return {'passed':not failures,'failures':failures,'expected_first_boundary':expected_first,
            'expected_boundaries':[{'gap_usd':gap,'affected_order_ids':ids} for gap,ids in expected_boundaries]}


def evaluate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);cases=[]
    for name in CASES:
        folder=output/name;folder.mkdir();lab=folder/'lab.duckdb';initialize_multilayer(lab)
        row={'case':name,'evidence_database':name+'/evidence.sqlite'}
        try:
            inject(lab,name)
            result=investigate_layers(capture(lab),folder/'evidence.sqlite')
            row.update(assess(name,result),observed=result,investigation_id=result['id'])
        except Exception as error:row.update(passed=False,failures=['execution'],error_type=type(error).__name__)
        finally:
            try:row['reset_status']=reset_multilayer(lab)['status']
            except Exception:row['reset_status']='FAILED'
        if row['reset_status']!='READY':row['passed']=False;row['failures'].append('reset')
        cases.append(row)
    report={'version':1,'created':datetime.now(timezone.utc).isoformat(),'cases':cases,
            'passed':all(c['passed'] for c in cases),'passed_count':sum(c['passed'] for c in cases),
            'case_count':len(cases),'product_acceptance':False,
            'scope':'Local three-order fixture and deterministic boundary investigation only; no cloud, LLM or routing evaluation.'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.local/multilayer-matrices'/str(uuid4()));args=parser.parse_args()
    report=evaluate(args.output);print(json.dumps({'report':str(args.output/'report.json'),'passed':report['passed'],'passed_count':report['passed_count'],'case_count':report['case_count']}))
    raise SystemExit(0 if report['passed'] else 1)
