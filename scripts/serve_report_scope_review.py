"""Serve reviewed report-filter local investigations; no cloud clients or injection."""
import argparse
import os
from pathlib import Path
from wsgiref.simple_server import make_server
from defect_lab import ROOT
from serve_lab_review import components
from serve_investigations import QuietHandler

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',type=Path,required=True)
    parser.add_argument('--review-folder',type=Path,default=ROOT/'.local/report-scope-review')
    parser.add_argument('--port',type=int,default=8775);args=parser.parse_args()
    if not args.lab.is_file():parser.error('Existing report-filter lab database required')
    if not 1<=args.port<=65535:parser.error('Invalid port')
    app,worker,_=components(args.review_folder,args.lab,os.environ.get('INVESTIGATOR_API_TOKEN',''),report_scope=True)
    with make_server('127.0.0.1',args.port,app,handler_class=QuietHandler) as server:
        print(f'Report-filter local review API: http://127.0.0.1:{args.port}; one approved job; no cloud calls',flush=True)
        worker.start()
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:worker.stop()
