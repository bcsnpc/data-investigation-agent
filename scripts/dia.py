"""Local investigator commands; no control-plane changes implicit in a command."""
import argparse
import json
from pathlib import Path
import time


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
    args = parser.parse_args(argv)
    if args.command == 'retain':
        from investigator.estate_manifest import load
        from investigator.retention import DEFAULT, plan, apply, summary
        manifest = load(args.manifest)
        planned = plan(manifest.get('retention', DEFAULT), root=args.root,
                       tapes=args.tapes, ledger=args.ledger, now=time.time())
        print(json.dumps(summary(planned), indent=2))
        if args.apply: apply(planned, root=args.root, audit=args.audit)
    return 0


if __name__ == '__main__': raise SystemExit(main())
