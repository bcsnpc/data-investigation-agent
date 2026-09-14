"""Isolated lab review UI with explicit fixed-scope drafts; never calls cloud providers."""
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
from wsgiref.simple_server import make_server
from background_worker import BackgroundWorker
from defect_lab import ROOT,evidence
from investigation_evidence_api import create_app
from lab_filter_cause import verify
from lab_investigator import investigate
from lineage_graph import load_graph
from plan_review_api import PlanReviews
from serve_investigations import QuietHandler
from ticket_planner import plan_ticket
from ticket_worker import process_one
from ticket_workflow import TicketStore

LINEAGE='194e3b0c-9c06-4c83-aaba-cae2736e3164'
REPORT='lab-cash-report'


def setup(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);database=folder/'review.sqlite'
    with closing(sqlite3.connect(database)) as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS scans(id TEXT PRIMARY KEY,status TEXT);
        CREATE TABLE IF NOT EXISTS assets(scan_id TEXT,id TEXT,parent_id TEXT,kind TEXT,name TEXT,metadata TEXT,content_hash TEXT,PRIMARY KEY(scan_id,id));
        CREATE TABLE IF NOT EXISTS lineage_runs(id TEXT PRIMARY KEY,scan_id TEXT,created TEXT,supplement TEXT);
        CREATE TABLE IF NOT EXISTS lineage_edges(run_id TEXT,source TEXT,target TEXT,kind TEXT,evidence TEXT,PRIMARY KEY(run_id,source,target));
        CREATE TABLE IF NOT EXISTS lineage_gaps(run_id TEXT,asset TEXT,reason TEXT,detail TEXT);
        CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT);''')
        db.execute('INSERT OR IGNORE INTO scans VALUES(?,?)',(LINEAGE,'COMPLETE'))
        for identity,kind,name in [(REPORT,'Report','Lab Net Cash'),('lab-cash','Measure','Net Cash')]:
            db.execute('INSERT OR IGNORE INTO assets VALUES(?,?,?,?,?,?,?)',(LINEAGE,identity,None,kind,name,'{}','local-lab-v1'))
        db.execute('INSERT OR IGNORE INTO lineage_runs VALUES(?,?,?,?)',(LINEAGE,LINEAGE,'2026-09-13','{}'))
        db.execute('INSERT OR IGNORE INTO lineage_edges VALUES(?,?,?,?,?)',(LINEAGE,'lab-cash',REPORT,'binding','{"source":"explicit local lab contract"}'));db.commit()
    return {'storage':{'database':str(database)}},TicketStore(folder/'review-workflow.sqlite')


def components(folder,lab_path,token):
    config,store=setup(folder);estate={'investigation':{'lineage_run':LINEAGE}}
    graph=load_graph(config['storage']['database'],LINEAGE)
    def planner(identity):
        body=store.get(identity)['ticket']
        supported=body['report'] in ('Lab Net Cash',REPORT)
        scope={'report_id':REPORT if supported else None,'metric':'Net Cash','currency':'USD','order_id':None,
               'questions':[] if supported else ['Use report Lab Net Cash for this isolated server.']}
        return plan_ticket(store,identity,graph,lambda _: (scope,{'mode':'fixed_lab_scope_no_llm'}))['id']
    def process(*args,**kwargs):
        def acquire(config,estate,lineage,currency,order_id):
            if currency!='USD' or order_id is not None:raise ValueError('Lab supports full USD scope only')
            payload,context=evidence(lab_path,True)
            if any(r['currency']!='USD' for r in payload['rows']):raise ValueError('Lab data exceeds reviewed currency')
            result=investigate(payload,config['storage']['database'],context,lambda p,r:verify(lab_path,p,r))
            return dict(result,metrics={})
        return process_one(*args,execute=acquire,**kwargs)
    worker=BackgroundWorker(store,config,lambda:estate,process=process)
    reviews=PlanReviews(store,config,lambda:estate,planner)
    app=create_app(config['storage']['database'],token,store,LINEAGE,reviews,ui=True,worker_status=worker.status,workspace_mode='local_lab')
    return app,worker,store


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8772);args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Invalid port')
    token=os.environ.get('INVESTIGATOR_API_TOKEN','')
    lab=ROOT/'.local/defect-lab/lab.duckdb'
    if not lab.is_file():parser.error('Initialize the local defect lab first')
    app,worker,_=components(ROOT/'.local/defect-lab/review',lab,token)
    with make_server('127.0.0.1',args.port,app,handler_class=QuietHandler) as server:
        print(f'Local lab review: http://127.0.0.1:{args.port}; one approved job; no cloud calls',flush=True)
        worker.start()
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:worker.stop()
