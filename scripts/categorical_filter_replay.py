"""Execute explicit categorical predicates in the isolated Silver/Gold lab."""
from contextlib import closing
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
import duckdb
from defect_lab import evidence as capture
from lab_investigator import reconcile
from report_slicer_context import assess

SUPPORTED={('FactOrder','order_id'),('FactOrder','currency'),('FactOrder','status')}


def execute(lab,definitions,page,selections,database):
    context=assess(definitions,page,selections)
    if context['status']!='CONTEXT_SUPPLIED':raise ValueError('Complete supported slicer context required')
    if any((s['table'],s['column']) not in SUPPORTED for s in context['slicers']):
        raise ValueError('Only FactOrder order_id, currency and status are executable in this lab')
    if not Path(lab).is_file():raise ValueError('Existing isolated lab required')
    with closing(duckdb.connect(str(lab),read_only=True)) as db:
        db.execute('BEGIN TRANSACTION')
        payload=json.loads(json.dumps(capture(lab,connection=db),default=str))
        statuses=db.execute('SELECT order_id,currency,status FROM s_fact_order').fetchall()
    reconcile(payload)  # Validate complete capture before any row can be filtered away.
    attributes={}
    for order,currency,status in statuses:
        if (order,currency) in attributes:raise ValueError('Duplicate source attribute key')
        attributes[(order,currency)]=status
    selected=[];indices=[]
    for index,row in enumerate(payload['rows']):
        values={'order_id':row['order_id'],'currency':row['currency'],'status':attributes.get((row['order_id'],row['currency']))}
        matches=True
        for slicer in context['slicers']:
            choice=slicer['selection']
            if choice['mode']=='all':continue
            value=values[slicer['column']]
            if value is None:raise ValueError('Selected predicate has missing source attributes')
            if value not in choice['values']:matches=False
        if matches:selected.append(row);indices.append(index)
    if selected:
        result=reconcile({'mode':'local_lab','rows':selected})
    else:
        result={'classification':'UNRESOLVED','comparison_status':'NO_MATCHES','compared_boundary':{'upstream':'silver','downstream':'gold'},'affected_records':[],'impact_by_currency':{},'root_cause_verified':False,'automatic_defect_routing':False}
    identity=str(uuid4())
    result.update(id=identity,selected_records=len(selected),captured_records=len(payload['rows']),
                  predicate_replay_completed=True,runtime_filter_verified=False,
                  limitation='Local same-transaction categorical replay only. Exact case-sensitive strings; OR within each slicer and AND across slicers. Status attributes come from Silver. Does not establish Power BI collation, relationships, RLS, DAX, live snapshot parity or a root cause.')
    request={'kind':'categorical_filter_replay','slicer_context':context,'lab_evidence':payload,
             'status_attributes':[{'order_id':o,'currency':c,'status':s} for o,c,s in statuses],
             'selected_row_indices':indices,'capture_scope':'local_single_transaction'}
    request['evidence_hash']=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
    Path(database).parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(database)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT)')
        db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)',(identity,None,datetime.now(timezone.utc).isoformat(),json.dumps(request),json.dumps(result)));db.commit()
    return result


if __name__=='__main__':
    import argparse
    from report_definition_evidence import bundle
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',type=Path,required=True)
    parser.add_argument('--metadata',type=Path,required=True)
    parser.add_argument('--scan',required=True)
    parser.add_argument('--report',required=True)
    parser.add_argument('--page',required=True)
    parser.add_argument('--selections',type=Path,required=True)
    parser.add_argument('--database',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(execute(args.lab,bundle(args.metadata,args.scan,args.report),args.page,json.loads(args.selections.read_text()),args.database),indent=2))
