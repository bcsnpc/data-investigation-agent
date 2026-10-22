"""Local investigator commands; no control-plane changes implicit in a command."""
import argparse
import json
from pathlib import Path
import time

WORKSPACE_TOKEN_HELP = '''Missing local workspace access key. This is not an Entra/Fabric token:
the local Windows operator owns it; reader identities and tenant permissions are unchanged.
Demo never creates a key. As that operator, run PowerShell from the repository:
  $workspaceKeyPath = Join-Path (Get-Location) '.local/workspace-access.dpapi'
If an existing key is provisioned, use its existing secret-store path. Otherwise
the operator can provision this local-only key (not an Azure credential):
  New-Item -ItemType Directory -Force .local | Out-Null
  $workspaceBytes = New-Object byte[] 48
  $workspaceRng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  $workspaceRng.GetBytes($workspaceBytes)
  $workspaceKey = [Convert]::ToBase64String($workspaceBytes)
  $workspaceRng.Dispose()
  [Array]::Clear($workspaceBytes, 0, $workspaceBytes.Length)
  ConvertTo-SecureString $workspaceKey -AsPlainText -Force | ConvertFrom-SecureString | Set-Content -LiteralPath $workspaceKeyPath
Load it into this process without printing it:
  $workspaceSecure = Get-Content -LiteralPath $workspaceKeyPath -Raw | ConvertTo-SecureString
  $env:INVESTIGATOR_WORKSPACE_TOKEN = [System.Net.NetworkCredential]::new('', $workspaceSecure).Password
  Remove-Variable workspaceKey -ErrorAction SilentlyContinue
Then re-run dia demo with the approved manifest and case. DPAPI is bound to this
Windows user; never commit the file, put the key in a URL, or use an Entra token.'''

class WorkspaceTokenRequired(ValueError): pass


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
        raise WorkspaceTokenRequired(WORKSPACE_TOKEN_HELP)
    manifest, workspace = build(manifest_path, execution_enabled=live)
    if manifest.get('recording',{}).get('tape_class') == 'PRIVACY_PROJECTED':
        workspace.close()
        raise ValueError('Projected installations use atomic investigate/replay; the asynchronous demo interface is not exposed')
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
    ask_command = commands.add_parser('ask', help='Explain an admitted calculation or observed change history')
    ask_command.add_argument('question')
    ask_command.add_argument('--estate',required=True,type=Path)
    access = commands.add_parser('check-access', help='Probe the declared permission map as each real identity')
    access.add_argument('--map', type=Path, default=Path(__file__).resolve().parents[1]/'config/permission-map.yaml')
    access.add_argument('--bindings', type=Path, required=True, help='Deployment-owned identity/probe references, never secret values')
    access.add_argument('--scope', help='Ticket route scope; omit for the complete map')
    access.add_argument('--json', action='store_true')
    rotate = commands.add_parser('rotate-connection-secret', help='Rotate the approved app, vault and both fixed connections')
    rotate.add_argument('--config', type=Path, required=True)
    rotate.add_argument('--apply', action='store_true')
    run = commands.add_parser('run',help='Run a typed ticket or check through the pinned container runner')
    run.add_argument('target')
    run.add_argument('--estate',required=True,type=Path)
    run.add_argument('--runtime',choices=('local','azure','worker'),default='local')
    schedule=commands.add_parser('schedule',help='Plan or apply daily smoke to the configured existing job')
    schedule.add_argument('--estate',required=True,type=Path)
    schedule.add_argument('--existing-job',type=Path)
    schedule.add_argument('--apply',action='store_true')
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
    if args.command=='ask':
        from investigator.explain_questions import main as ask_main
        return ask_main(args)
    if args.command=='check-access':
        from investigator.access_check import main as access_main
        return access_main(args)
    if args.command=='rotate-connection-secret':
        from investigator.connection_rotation import main as rotation_main
        return rotation_main(args)
    if args.command=='schedule':
        from investigator.unified_runner import load
        from investigator.adapters.runner_schedule import plan,apply
        config=load(args.estate)
        if args.apply:
            from investigator.adapters.control_failure import ControlCommandFailure
            try:result=apply(config)
            except ControlCommandFailure as error:
                from investigator.process_tape import bytes_of,uuid4
                path=args.estate.resolve().parent/('control-failure-'+str(uuid4())+'.json')
                with path.open('xb') as stream:stream.write(bytes_of(error.receipt))
                print(json.dumps({'status':'FAILED','operation':error.receipt['operation'],'returncode':error.receipt['returncode'],'stderr':error.receipt['stderr'],'receipt':str(path)}))
                return 1
        else:
            if args.existing_job is None:parser.error('Schedule planning requires --existing-job retained observation')
            result=plan(config,json.loads(args.existing_job.read_bytes()))
        print(json.dumps(result,sort_keys=True));return 0
    elif args.command == 'run':
        from investigator.unified_runner import main as run_main
        return run_main(args)
    elif args.command == 'retain':
        from investigator.estate_manifest import load
        from investigator.retention import DEFAULT, plan, apply, summary
        manifest = load(args.manifest)
        planned = plan(manifest.get('retention', DEFAULT), root=args.root,
                       tapes=args.tapes, ledger=args.ledger, now=time.time())
        print(json.dumps(summary(planned), indent=2))
        if args.apply: apply(planned, root=args.root, audit=args.audit)
    elif args.command == 'demo':
        try:demo(args.manifest, args.case, args.port, args.live)
        except WorkspaceTokenRequired as exc:
            import sys
            print(str(exc),file=sys.stderr)
            return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
