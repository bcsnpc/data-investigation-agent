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
from investigator.workspace_api import create_app
from metadata_config import load_config
from run_adaptive_investigation import local_azure_key
from run_native_diagnostic import transport as native_transport
from run_source_diagnostic import transport as source_transport
from serve_investigations import QuietHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--environment', required=True)
    parser.add_argument('--port', type=int, default=8776)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--usage-policy', type=Path)
    parser.add_argument('--azure-settings', type=Path)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Invalid port')
    if args.live and not args.usage_policy:
        parser.error('--live requires --usage-policy')
    config = load_config(args.config)
    store = ModelStore(args.database, config['storage']['database'], args.environment)
    settings = json.loads(args.azure_settings.read_text(encoding='utf-8-sig')) if args.azure_settings else {}
    profile = {'adapter': 'azure', 'endpoint': settings.get('endpoint', os.environ.get('AZURE_OPENAI_ENDPOINT')),
               'deployment': settings.get('deployment', os.environ.get('AZURE_OPENAI_DEPLOYMENT'))}
    policy = json.loads(args.usage_policy.read_text(encoding='utf-8-sig')) if args.usage_policy else None
    runtime = Runtime(store, config, (lambda p: native_transport(config, p)) if args.live else None,
                      (lambda p: source_transport(config, p)) if args.live else None)
    agent = AdaptiveRuntime(runtime, azure_plan if args.live else None, planner_profile=profile, usage_policy=policy)
    workspace = Workspace(agent, execution_enabled=args.live)
    app = create_app(workspace, os.environ.get('INVESTIGATOR_WORKSPACE_TOKEN'), args.port)
    with local_azure_key(args.azure_settings if args.live else None):
        with make_server('127.0.0.1', args.port, app, handler_class=QuietHandler) as server:
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
