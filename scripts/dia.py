"""Local investigator commands; no control-plane changes implicit in a command."""
import argparse
import json
from pathlib import Path
import time


def demo(manifest_path, case_path, port, live=False):
    """Same existing workspace, exact approved fixture pin; no default execution."""
    import os
    from threading import Thread
    from wsgiref.simple_server import make_server
    from investigator.estate_installation import build
    from investigator.acceptance_context import pin_run_context
    from investigator.workspace_api import create_app, WorkspaceServer
    from serve_investigations import QuietHandler
    from run_adaptive_investigation import local_azure_key
    if type(port) is not int or not 1 <= port <= 65535: raise ValueError('Invalid local demo port')
    token = os.environ.get('INVESTIGATOR_WORKSPACE_TOKEN')
    if not isinstance(token, str) or len(token) < 32 or not token.isascii():
        raise ValueError('Set the existing INVESTIGATOR_WORKSPACE_TOKEN; demo never creates a key')
    manifest, workspace = build(manifest_path, execution_enabled=live)
    selected = pin_run_context(workspace, case_path, fixture=manifest)
    from investigator.screenshot_intake import azure_extract
    workspace.screenshots.extractor = azure_extract if live else None
    model = manifest['model']
    settings = {**model['credential'], 'endpoint':model['endpoint'], 'deployment':model['deployment']} if live else None
    app = create_app(workspace, token, port)
    with local_azure_key(settings):
        with make_server('127.0.0.1', port, app, server_class=WorkspaceServer, handler_class=QuietHandler) as server:
            if live: Thread(target=workspace.work, daemon=True).start()
            print(json.dumps({'url':f'http://127.0.0.1:{port}', 'execution_enabled':live,
                              'context_pins':selected.context_pins, 'fixture_state':selected.acceptance_fixture_state}))
            try: server.serve_forever()
            except KeyboardInterrupt: pass
            finally: workspace.stopping.set()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    retain = commands.add_parser('retain', help='Plan or apply the manifest retention policy locally')
    retain.add_argument('--manifest', required=True, type=Path)
    retain.add_argument('--root', required=True, type=Path)
    retain.add_argument('--tapes', required=True, type=Path)
    retain.add_argument('--ledger', required=True, type=Path)
    retain.add_argument('--audit', required=True, type=Path)
    retain.add_argument('--apply', action='store_true')
    show = commands.add_parser('demo', help='Serve the existing workspace against a pinned approved fixture context')
    show.add_argument('--manifest', required=True, type=Path)
    show.add_argument('--case', required=True, type=Path)
    show.add_argument('--port', type=int, default=8776)
    show.add_argument('--live', action='store_true', help='Explicitly enable existing governed execution')
    args = parser.parse_args(argv)
    if args.command == 'retain':
        from investigator.estate_manifest import load
        from investigator.retention import DEFAULT, plan, apply, summary
        manifest = load(args.manifest)
        planned = plan(manifest.get('retention', DEFAULT), root=args.root,
                       tapes=args.tapes, ledger=args.ledger, now=time.time())
        print(json.dumps(summary(planned), indent=2))
        if args.apply: apply(planned, root=args.root, audit=args.audit)
    elif args.command == 'demo': demo(args.manifest, args.case, args.port, args.live)
    return 0


if __name__ == '__main__': raise SystemExit(main())
