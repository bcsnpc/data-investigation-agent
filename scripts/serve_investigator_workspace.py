"""Run the local business/technical workspace; --live explicitly enables execution."""
import argparse
import json
import os
from pathlib import Path
from threading import Thread
from wsgiref.simple_server import make_server

from investigator.onboarding import ModelStore
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.adaptive_planner import azure_plan
from investigator.workspace import Workspace
from investigator.question_intake import azure_resolve
from investigator.screenshot_intake import azure_extract
from investigator.workspace_api import create_app, WorkspaceServer
from metadata_config import load_config
from run_adaptive_investigation import local_azure_key
from run_native_diagnostic import transport as native_transport
from run_source_diagnostic import transport as source_transport
from serve_investigations import QuietHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8776)
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Invalid port')
    from investigator.estate_installation import build
    manifest,workspace=build(args.manifest,execution_enabled=args.live)
    workspace.screenshots.extractor=azure_extract if args.live else None
    model=manifest['model']
    settings={**model['credential'],'endpoint':model['endpoint'],'deployment':model['deployment']}
    app = create_app(workspace, os.environ.get('INVESTIGATOR_WORKSPACE_TOKEN'), args.port)
    with local_azure_key(settings if args.live else None):
        with make_server('127.0.0.1', args.port, app, server_class=WorkspaceServer, handler_class=QuietHandler) as server:
            worker = Thread(target=workspace.work, daemon=True)
            if args.live:
                worker.start()
            print(f'Investigation workspace: http://127.0.0.1:{args.port} (execution {"enabled" if args.live else "disabled"})', flush=True)
            try:
                server.serve_forever()
            finally:
                workspace.stopping.set()


if __name__ == '__main__':
    main()
