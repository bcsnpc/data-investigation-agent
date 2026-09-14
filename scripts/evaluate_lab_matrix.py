"""Repeatable isolated lab evaluation; expected answers never enter investigator inputs."""
from contextlib import closing
from datetime import datetime,timezone
import json
from pathlib import Path
from uuid import uuid4
import duckdb
from defect_lab import initialize,mutate,evidence,ROOT
from lab_filter_cause import verify
from lab_investigator import investigate


CASES = (
    ('matching_without_context',None,False,'UNRESOLVED','0.0000',False,0),
    ('expected_refunds',None,True,'EXPECTED_BEHAVIOR','0.0000',False,0),
    ('unexplained_omission','inject',False,'UNRESOLVED','-99.0000',False,1),
    ('verified_filter','inject-filter',False,'TECHNICAL_DEFECT','-99.0000',True,1),
    ('verified_stale_source','inject-stale',False,'REFRESH_FRESHNESS','99.0000',True,1),
    ('missing_filter_receipt','inject-filter',False,'UNRESOLVED','-99.0000',False,1),
    ('changed_filter_receipt','inject-filter',False,'UNRESOLVED','-99.0000',False,1),
    ('unexplained_value_change',None,False,'UNRESOLVED','10.0000',False,1),
    ('incomplete_business_context',None,True,'UNRESOLVED','0.0000',False,0),
)


def assess(result, classification, gap, verified, affected):
    expected={'classification':classification,'gap_usd':gap,'root_cause_verified':verified,
              'affected_records':affected,'automatic_defect_routing':False}
    observed={'classification':result.get('classification'),
              'gap_usd':result.get('impact_by_currency',{}).get('USD',{}).get('downstream_minus_upstream'),
              'root_cause_verified':result.get('root_cause_verified'),
              'affected_records':len(result.get('affected_records',[])),
              'automatic_defect_routing':result.get('automatic_defect_routing')}
    failures=[key for key in expected if observed[key]!=expected[key] or type(observed[key]) is not type(expected[key])]
    return {'expected':expected,'observed':observed,'failures':failures,'passed':not failures}


def evaluate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for name,action,business,classification,gap,verified,affected in CASES:
        folder=output/name;folder.mkdir();lab=folder/'lab.duckdb';database=folder/'evidence.sqlite'
        initialize(lab)
        row={'case':name,'evidence_database':str(database.relative_to(output))}
        try:
            if action:mutate(lab,action)
            with closing(duckdb.connect(str(lab))) as db:
                if name=='missing_filter_receipt':db.execute('DROP TABLE gold_build_receipt')
                elif name=='changed_filter_receipt':db.execute("UPDATE gold_build_receipt SET query_text='SELECT 1'")
                elif name=='unexplained_value_change':db.execute("UPDATE g_order_line_summary SET net_cash_amount=net_cash_amount+10 WHERE order_id='ORD-000002'")
            captured=evidence(lab,business)
            payload,context=captured if business else (captured,None)
            if name=='incomplete_business_context':context['records'].pop()
            result=investigate(payload,database,context,lambda p,r:verify(lab,p,r))
            row.update(assess(result,classification,gap,verified,affected),investigation_id=result['id'])
        except Exception as error:
            row.update(passed=False,failures=['execution_error'],error_type=type(error).__name__)
        finally:
            try:row['reset_status']=mutate(lab,'reset')['status']
            except Exception:row['reset_status']='FAILED'
        if row['reset_status']!='READY':row['passed']=False;row['failures'].append('reset')
        rows.append(row)
    report={'schema_version':1,'created':datetime.now(timezone.utc).isoformat(),
            'passed':all(row['passed'] for row in rows),'case_count':len(rows),
            'passed_count':sum(row['passed'] for row in rows),'product_acceptance':False,
            'scope':'Local three-order Silver/Gold lab; deterministic investigator only. No cloud, LLM, delivery or full-estate coverage.',
            'cases':rows}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.local/lab-evaluations'/str(uuid4()))
    args=parser.parse_args()
    report=evaluate(args.output)
    print(json.dumps({'report':str(args.output/'report.json'),'passed':report['passed'],
                      'passed_count':report['passed_count'],'case_count':report['case_count'],'product_acceptance':False}))
    raise SystemExit(0 if report['passed'] else 1)
