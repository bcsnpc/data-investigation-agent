"""Isolated workflow acceptance fixtures; no cloud calls or business mutations."""
import argparse
from contextlib import closing
from datetime import datetime,timezone
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
from unittest.mock import patch
from uuid import uuid4
from background_worker import BackgroundWorker
from cross_layer_investigation import boundaries,metric_observation,LAYERS
from explanation_request import request_explanation
from investigation_evidence_api import create_app,EvidenceStore
from investigation_explanation import explain
from lineage_graph import Graph
from plan_review_api import PlanReviews
from ticket_planner import plan_ticket
from ticket_worker import process_one
from ticket_workflow import TicketStore


def run_case(name,values,snapshot=False,missing=False):
    with tempfile.TemporaryDirectory() as folder:
        database=Path(folder)/'evidence.sqlite';store=TicketStore(Path(folder)/'workflow.sqlite')
        lineage=str(uuid4());config={'storage':{'database':str(database)}}
        estate={'investigation':{'lineage_run':lineage}}
        graph=Graph([{'id':x,'kind':'Table','name':x} for x in LAYERS]+
                    [{'id':'report','kind':'Report','name':'Sales'},{'id':'measure','kind':'Measure','name':'Net Cash'}])
        for left,right in zip(LAYERS,LAYERS[1:]):graph.edge(left,right,'data',left,{})
        graph.edge('semantic','measure','data','semantic',{});graph.edge('measure','report','binding','measure',{})
        with closing(sqlite3.connect(database)) as db:
            db.execute('CREATE TABLE investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT)');db.commit()
        calls={'acquisition':0,'model_selection':0}
        def planner(identity):
            return plan_ticket(store,identity,graph,lambda _:({'report_id':'report','metric':'Net Cash','currency':'USD','order_id':'ORD-000002','questions':[]},{}))['id']
        reviews=PlanReviews(store,config,lambda:estate,planner)
        app=create_app(database,'x'*32,store,lineage,reviews)
        def http(path,body=None,key=None):
            payload=json.dumps(body).encode() if body is not None else b'';status=[]
            response=b''.join(app({'PATH_INFO':path,'QUERY_STRING':'','REQUEST_METHOD':'POST' if body is not None else 'GET',
                'HTTP_AUTHORIZATION':'Bearer '+'x'*32,'HTTP_IDEMPOTENCY_KEY':key or '',
                'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(payload)),'wsgi.input':BytesIO(payload)},
                lambda value,headers:status.append(value)))
            if not status[0].startswith(('200','201')):raise AssertionError(status[0])
            return json.loads(response)
        def acquire(*args):
            calls['acquisition']+=1;chain=[]
            for layer,value in zip(LAYERS,values):
                raw={'values':{'net_cash':value},'query':'acceptance fixture','captured_at':'2026-09-13T12:00:00Z'}
                if missing and layer=='sql':raw={'error':'FIXTURE_UNAVAILABLE'}
                observation=metric_observation(layer,'net_cash',raw,'USD','ORD-000002',layer)
                if snapshot:observation['source_snapshot']={'fixture':'common-snapshot'}
                chain.append(observation)
            result={'id':str(uuid4()),'classification':'UNRESOLVED','metrics':{'net_cash':boundaries(graph,chain)}}
            request={'observations':{'net_cash':chain},'kind':'acceptance_fixture'}
            with closing(sqlite3.connect(database)) as db:
                db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)',(result['id'],lineage,'2026-09-13T12:00:00Z',json.dumps(request),json.dumps(result)));db.commit()
            return result
        evidence=EvidenceStore(database)
        def generate(identity):
            calls['model_selection']+=1
            return explain(store,evidence.get(identity),lambda _:({'finding_ids':['observation-0'],'next_step_ids':['review-scope']},{'mode':'fixture'}))['id']
        callback=lambda identity:request_explanation(store,evidence,identity,generate)
        parent=http('/api/tickets',{'title':name,'report':'Sales','description':'Check USD cash for ORD-000002'},str(uuid4()))['ticket_id']
        draft=http('/api/tickets/'+parent+'/plan',{'confirm':True},str(uuid4()))['plan_id']
        with patch('review_ticket_plan.load_graph',return_value=graph),patch('ticket_worker.load_graph',return_value=graph):
            detail=http('/api/plans/'+draft)
            approval={'confirm':True,'plan_hash':detail['plan_hash']}
            child=http('/api/plans/'+draft+'/approve',approval)['ticket_id']
            assert http('/api/plans/'+draft+'/approve',approval)['ticket_id']==child
            worker=BackgroundWorker(store,config,lambda:estate,process=lambda *a,**k:process_one(*a,execute=acquire,**k),explain=callback)
            worker.start();worker.thread.join(10)
            if worker.thread.is_alive():worker.stop();raise AssertionError('Worker exceeded fixture budget')
        ticket=http('/api/tickets/'+child)['ticket'];run=ticket['investigation_run_id']
        result=http('/api/investigations/'+run)
        assert ticket['status']=='COMPLETED' and worker.status()['status']=='JOB_LIMIT'
        assert callback(run)['replayed'] and calls=={'acquisition':1,'model_selection':1}
        assert http('/api/tickets/'+parent)['related']['items'][0]['status']=='COMPLETED'
        assert store.get(parent)['status']=='QUEUED'
        assert result['explanation']['status']=='VALIDATED' and result['summary']['classification']=='UNRESOLVED'
        assert result['capabilities']['route_defects'] is False
        metric=result['investigation']['result']['metrics']['net_cash']
        return {'case':name,'classification':result['summary']['classification'],
                'boundary_statuses':[b['status'] for b in metric['boundaries']],
                'first_verified_divergence':metric['first_verified_divergence'],
                'calls':calls,'workflow_passed':True}


def evaluate():
    cases=[run_case('equal_values_unpinned',['1529.6400']*5),
           run_case('source_unavailable',['1529.6400']*5,missing=True),
           run_case('comparable_gold_divergence',['1529.6400']*3+['1500.0000']*2,snapshot=True)]
    assert set(cases[0]['boundary_statuses'])=={'NOT_COMPARABLE'}
    assert cases[1]['boundary_statuses'][0]=='UNAVAILABLE' and cases[1]['first_verified_divergence'] is None
    assert cases[2]['first_verified_divergence']=={'upstream':'silver','downstream':'gold'}
    return {'mode':'isolated fixtures; deterministic model selections and cloud observations',
            'workflow_passed':True,'product_acceptance_complete':False,'cases':cases,
            'pending':['EXPECTED_BEHAVIOR requires verified business explanation, not matching totals alone',
                       'Comparable divergence still requires root-cause, affected-record and impact verification',
                       'Live model snapshot comparability remains unproven',
                       'Resettable multi-layer defect lab and routing acceptance are not implemented']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=Path('.local/acceptance-baseline.json'))
    args=parser.parse_args();report=evaluate();report['created_at']=datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
