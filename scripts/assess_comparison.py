"""Assess saved native/source observations without dispatching cloud queries."""
import argparse
import json
from pathlib import Path
from investigator.onboarding import ModelStore
from investigator.comparisons import assess

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    parser.add_argument('--model-id',required=True)
    parser.add_argument('--request',type=Path,required=True)
    args=parser.parse_args()
    store=ModelStore(args.database,args.inventory,args.environment)
    print(json.dumps(assess(store,args.model_id,json.loads(args.request.read_text(encoding='utf-8-sig')))))
