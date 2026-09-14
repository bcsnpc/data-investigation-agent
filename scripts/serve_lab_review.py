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
MULTI_LINEAGE='6b901118-25b6-4a69-8c78-8f19b392690b'
MULTI_REPORT='lab-three-layer-cash-report'


def setup(folder,multilayer=False):
    lineage=MULTI_LINEAGE if multilayer else LINEAGE
    report=MULTI_REPORT if multilayer else REPORT
    report_name='Lab Three-layer Net Cash' if multilayer else 'Lab Net Cash'
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);database=folder/'review.sqlite'
    with closing(sqlite3.connect(database)) as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS scans(id TEXT PRIMARY KEY,status TEXT);
        CREATE TABLE IF NOT EXISTS assets(scan_id TEXT,id TEXT,parent_id TEXT,kind TEXT,name TEXT,metadata TEXT,content_hash TEXT,PRIMARY KEY(scan_id,id));
        CREATE TABLE IF NOT EXISTS lineage_runs(id TEXT PRIMARY KEY,scan_id TEXT,created TEXT,supplement TEXT);
        CREATE TABLE IF NOT EXISTS lineage_edges(run_id TEXT,source TEXT,target TEXT,kind TEXT,evidence TEXT,PRIMARY KEY(run_id,source,target));
        CREATE TABLE IF NOT EXISTS lineage_gaps(run_id TEXT,asset TEXT,reason TEXT,detail TEXT);
        CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT);''')
        db.execute('CREATE TABLE IF NOT EXISTS lab_review_mode(mode TEXT NOT NULL)')
        mode='three_layer' if multilayer else 'two_layer'
        old=db.execute('SELECT mode FROM lab_review_mode').fetchall()
        if old and old!=[(mode,)]:raise ValueError('Review folder belongs to a different lab mode')
        if not old:
            if multilayer and db.execute('SELECT COUNT(*) FROM scans').fetchone()[0]:raise ValueError('Use a fresh review folder for multi-layer mode')
            db.execute('INSERT INTO lab_review_mode VALUES(?)',(mode,))
        db.execute('INSERT OR IGNORE INTO scans VALUES(?,?)',(lineage,'COMPLETE'))
        for identity,kind,name in [(report,'Report',report_name),('lab-cash','Measure','Net Cash')]:
            db.execute('INSERT OR IGNORE INTO assets VALUES(?,?,?,?,?,?,?)',(lineage,identity,None,kind,name,'{}','local-lab-v1'))
        db.execute('INSERT OR IGNORE INTO lineage_runs VALUES(?,?,?,?)',(lineage,lineage,'2026-09-13','{}'))
        db.execute('INSERT OR IGNORE INTO lineage_edges VALUES(?,?,?,?,?)',(lineage,'lab-cash',report,'binding','{"source":"explicit local lab contract"}'));db.commit()
    return {'storage':{'database':str(database)}},TicketStore(folder/'review-workflow.sqlite')


def components(folder,lab_path,token,policy_loader=None,*,multilayer=False):
    lineage=MULTI_LINEAGE if multilayer else LINEAGE
    report=MULTI_REPORT if multilayer else REPORT
    report_name='Lab Three-layer Net Cash' if multilayer else 'Lab Net Cash'
    config,store=setup(folder,multilayer);estate={'investigation':{'lineage_run':lineage}}
    with closing(sqlite3.connect(config['storage']['database'])) as db:
        db.execute('CREATE TABLE IF NOT EXISTS lab_review_source(path TEXT NOT NULL)')
        source=str(Path(lab_path).resolve());old=db.execute('SELECT path FROM lab_review_source').fetchall()
        if old and old!=[(source,)]:raise ValueError('Review folder belongs to another lab source')
        if not old:db.execute('INSERT INTO lab_review_source VALUES(?)',(source,))
        db.commit()
    graph=load_graph(config['storage']['database'],lineage)
    def planner(identity):
        body=store.get(identity)['ticket']
        supported=body['report'] in (report_name,report)
        scope={'report_id':report if supported else None,'metric':'Net Cash','currency':'USD','order_id':None,
               'questions':[] if supported else ['Use report '+report_name+' for this isolated server.']}
        return plan_ticket(store,identity,graph,lambda _: (scope,{'mode':'fixed_lab_scope_no_llm'}))['id']
    def process(*args,**kwargs):
        def acquire(config,estate,lineage,currency,order_id):
            if currency!='USD' or order_id is not None:raise ValueError('Lab supports full USD scope only')
            if multilayer:
                from multilayer_lab import capture,investigate_layers
                payload=capture(lab_path)
                if any(r['currency']!='USD' for rows in payload['layers'].values() for r in rows):raise ValueError('Lab data exceeds reviewed currency')
                result=investigate_layers(payload,config['storage']['database'])
                return dict(result,metrics={'Net Cash':{'boundaries':[{'status':b['comparison_status']} for b in result['boundaries']]}})
            payload,context=evidence(lab_path,True)
            if any(r['currency']!='USD' for r in payload['rows']):raise ValueError('Lab data exceeds reviewed currency')
            result=investigate(payload,config['storage']['database'],context,lambda p,r:verify(lab_path,p,r))
            return dict(result,metrics={})
        return process_one(*args,execute=acquire,**kwargs)
    worker=BackgroundWorker(store,config,lambda:estate,process=process)
    reviews=PlanReviews(store,config,lambda:estate,planner)
    from routing_review import RoutingReview
    from investigation_evidence_api import EvidenceStore
    routing=RoutingReview(store,EvidenceStore(config['storage']['database']),policy_loader or (lambda:json.loads((ROOT/'infra/routing/ownership.json').read_text())))
    from email_delivery_adapter import EmailAdapter
    from envelope_workflow import EnvelopeWorkflow
    from envelope_review_api import EnvelopeReviewApi
    envelopes=EnvelopeReviewApi(EnvelopeWorkflow(EmailAdapter(routing,None)))
    app=create_app(config['storage']['database'],token,store,lineage,reviews,ui=True,worker_status=worker.status,workspace_mode='local_multilayer_lab' if multilayer else 'local_lab',routing=routing,envelopes=envelopes)
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
