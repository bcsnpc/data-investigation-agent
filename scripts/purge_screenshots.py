"""Bounded platform retention control; never an investigation or model call."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import time


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--environment',required=True)
    parser.add_argument('--replay-mirror',type=Path,required=True)
    parser.add_argument('--limit',type=int,default=100)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    from investigator.shared_state import configured_state
    from investigator.shared_catalog import SharedCatalog
    from investigator.onboarding import ModelStore
    from investigator.screenshot_intake import Screenshots
    state=configured_state()
    if state is None:raise ValueError('POSTGRES_SCREENSHOT_STATE_REQUIRED')
    args.replay_mirror.parent.mkdir(parents=True,exist_ok=True)
    store=ModelStore.__new__(ModelStore)
    store.database=args.replay_mirror;store.environment=args.environment;store.shared_accounting=None
    store.shared_catalog=SharedCatalog(state,args.environment)
    workspace=SimpleNamespace(store=store,clock=time.time,intake_configuration=None,agent=SimpleNamespace(config={}))
    result=Screenshots(workspace).pixels.purge(args.limit)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    with args.receipt.open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
