"""Serve saved investigation evidence on loopback for the local operator."""
import argparse
import os
import json
from pathlib import Path
from wsgiref.simple_server import make_server,WSGIRequestHandler
from investigation_evidence_api import create_app
from metadata_config import ROOT,load_config
from ticket_workflow import TicketStore


class QuietHandler(WSGIRequestHandler):
    def log_message(self,format,*args):
        pass  # Do not log URLs or authorization-related input.


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--enable-tickets',action='store_true')
    parser.add_argument('--enable-plan-review',action='store_true')
    parser.add_argument('--enable-planning',action='store_true')
    parser.add_argument('--estate',type=Path,default=ROOT/'infra/fabric/environment.json')
    args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Port must be between 1 and 65535')
    token=os.environ.get('INVESTIGATOR_API_TOKEN')
    if not token:parser.error('Set INVESTIGATOR_API_TOKEN before starting the local API')
    if args.enable_plan_review and not args.enable_tickets:parser.error('Plan review requires --enable-tickets')
    if args.enable_planning and not args.enable_plan_review:parser.error('Planning requires --enable-plan-review')
    config=load_config(args.config)
    database=config['storage']['database']
    workflow=TicketStore(Path(database).with_name('workflow.sqlite')) if args.enable_tickets else None
    lineage=json.loads(args.estate.read_text())['investigation']['lineage_run'] if workflow else None
    reviews=None
    if args.enable_plan_review:
        from plan_review_api import PlanReviews
        from planning_request import launch
        planner=(lambda ticket_id:launch(ticket_id,args.config)) if args.enable_planning else None
        reviews=PlanReviews(workflow,config,lambda: json.loads(args.estate.read_text()),planner)
    app=create_app(database,token,workflow,lineage,reviews,ui=args.enable_plan_review)
    with make_server('127.0.0.1',args.port,app,handler_class=QuietHandler) as server:
        print(f'Investigation evidence API listening on http://127.0.0.1:{args.port}',flush=True)
        server.serve_forever()
