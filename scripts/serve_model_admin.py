"""Local model onboarding over retained metadata; no live source queries."""
import argparse
import os
from pathlib import Path
from wsgiref.simple_server import make_server
from investigator.onboarding import ModelStore
from investigator.admin_api import create_app
from serve_investigations import QuietHandler


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    parser.add_argument('--port',type=int,default=8774)
    args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Invalid port')
    app=create_app(ModelStore(args.database,args.inventory,args.environment),
                   os.environ.get('INVESTIGATOR_ADMIN_TOKEN'),os.environ.get('INVESTIGATOR_READER_TOKEN'))
    with make_server('127.0.0.1',args.port,app,handler_class=QuietHandler) as server:
        print(f'Model admin: http://127.0.0.1:{args.port}',flush=True)
        server.serve_forever()
