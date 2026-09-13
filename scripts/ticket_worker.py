"""Process one queued ticket with bounded deterministic read-only acquisition."""
import argparse
import json
from pathlib import Path
from cross_layer_investigation import acquire
from investigation_query_worker import filters
from lineage_graph import load_graph
from metadata_config import ROOT,load_config
from ticket_workflow import TicketStore


def process_one(store,config,estate,execute=acquire):
    job=store.claim()
    if not job:return {'status':'IDLE'}
    body=job['body']
    try:
        if job['lineage_run']!=estate.get('investigation',{}).get('lineage_run'):
            store.finish(job,'NEEDS_INPUT',{'reason':'Configured lineage changed; submit against the current context'})
            return {'id':job['id'],'status':'NEEDS_INPUT'}
        if body.get('metric') not in ('Order Count','Net Cash') or not body.get('currency'):
            store.finish(job,'NEEDS_INPUT',{'reason':'Provide metric Order Count or Net Cash and an explicit three-letter currency'})
            return {'id':job['id'],'status':'NEEDS_INPUT'}
        try:filters(body['currency'],body.get('order_id'))
        except ValueError:
            store.finish(job,'NEEDS_INPUT',{'reason':'Unsupported currency or order filter'})
            return {'id':job['id'],'status':'NEEDS_INPUT'}
        graph=load_graph(config['storage']['database'],job['lineage_run'])
        report=graph.assets.get(body['report'])
        if not report or report['kind']!='Report':
            identity=graph.find('Report',body['report']);report=graph.assets.get(identity)
        if not report or not any(a['kind']=='Measure' and a['name']==body['metric'] for a in graph.traverse(report['id'])['assets']):
            store.finish(job,'NEEDS_INPUT',{'reason':'Report/metric not uniquely resolved in the selected lineage'})
            return {'id':job['id'],'status':'NEEDS_INPUT'}
        result=execute(config,estate,job['lineage_run'],body['currency'],body.get('order_id'))
        statuses=sorted({b['status'] for metric in result['metrics'].values() for b in metric['boundaries']})
        outcome={'classification':result['classification'],'boundary_statuses':statuses,
                 'scope':'Bounded Order Count/Net Cash checks only; ticket narrative is not interpreted by an LLM',
                 'limitation':'Completed means evidence acquisition finished, not that the ticket is resolved',
                 'report_asset':report['id'],'metric':body['metric'],'automatic_defect_routing':False}
        store.finish(job,'COMPLETED',outcome,result['id'])
        return {'id':job['id'],'status':'COMPLETED','investigation_run_id':result['id']}
    except Exception as exc:
        from ticket_workflow import Conflict
        if isinstance(exc,Conflict):raise
        store.finish(job,'FAILED',{'error':'INVESTIGATION_EXECUTION_FAILED','error_type':type(exc).__name__})
        return {'id':job['id'],'status':'FAILED'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--estate',type=Path,default=ROOT/'infra/fabric/environment.json')
    args=parser.parse_args();config=load_config(args.config)
    store=TicketStore(Path(config['storage']['database']).with_name('workflow.sqlite'))
    print(json.dumps(process_one(store,config,json.loads(args.estate.read_text()))))
