"""Read a historical typed-action run; new execution uses the estate runner."""
import argparse
import json
from pathlib import Path
from investigator.estate_installation import build


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--status-only',action='store_true',required=True)
    args=parser.parse_args()
    _,workspace=build(args.manifest,execution_enabled=False)
    print(json.dumps(workspace.agent.runtime.get(args.run_id)))
    return 0


if __name__=='__main__':raise SystemExit(main())
