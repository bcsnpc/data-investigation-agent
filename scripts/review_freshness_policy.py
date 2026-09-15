"""Review, inspect or revoke scoped UTC watermark policies; performs no cloud reads."""
import argparse
import json
from pathlib import Path

from investigator import freshness
from investigator.onboarding import ModelStore
from metadata_config import load_config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--environment', required=True)
    parser.add_argument('--model-id', required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--register', type=Path)
    action.add_argument('--show')
    action.add_argument('--revoke')
    parser.add_argument('--reason')
    parser.add_argument('--reviewer')
    parser.add_argument('--approve', action='store_true')
    args = parser.parse_args()
    config = load_config(args.config)
    store = ModelStore(args.database, config['storage']['database'], args.environment)
    if args.show:
        result = freshness.read(store, args.model_id, args.show)
    else:
        if not args.approve or not args.reviewer:
            parser.error('Policy changes require --approve and --reviewer')
        if args.register:
            result = freshness.register(store, args.model_id,
                                        json.loads(args.register.read_text(encoding='utf-8-sig')), args.reviewer, config)
        else:
            if not args.reason:parser.error('Revocation requires --reason')
            result = freshness.revoke(store, args.model_id, args.revoke, args.reason, args.reviewer)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
