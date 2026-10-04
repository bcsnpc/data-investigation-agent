"""Serve historical evidence read-only; investigation uses the manifest workspace."""
import argparse
import os
from pathlib import Path
from wsgiref.simple_server import make_server,WSGIRequestHandler
from investigation_evidence_api import create_app
from investigator.estate_manifest import load
from investigator.adapters.estate_installation import configuration


class QuietHandler(WSGIRequestHandler):
    def log_message(self,format,*args):pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Port must be between 1 and 65535')
    token=os.environ.get('INVESTIGATOR_API_TOKEN')
    if not token:parser.error('Set INVESTIGATOR_API_TOKEN before starting the local API')
    config=configuration(load(args.manifest))
    app=create_app(config['storage']['database'],token)
    with make_server('127.0.0.1',args.port,app,handler_class=QuietHandler) as server:
        print(f'Historical evidence API listening on http://127.0.0.1:{args.port}',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
    return 0


if __name__=='__main__':raise SystemExit(main())
