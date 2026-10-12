"""Report six-stage onboarding readiness without any estate or model request."""
import argparse
import json
import sqlite3
from pathlib import Path
from investigator.estate_readiness import assess, assess_named_scope, sha
from investigator.onboarding import digest
from investigator.runtime import fingerprint


def current_pins(manifest_path, approval_path):
    manifest_path = Path(manifest_path)
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    approval = json.loads(Path(approval_path).read_text(encoding='utf-8-sig'))
    from investigator.adapters.estate_installation import configuration
    if sha(raw) != approval['manifest_sha256']:
        raise ValueError('READINESS_MANIFEST_APPROVAL_DIFFERS')
    pins = {'manifest_hash': digest(manifest), 'context_identity': approval['context_id'],
            'context_hash': approval['context_hash'], 'config_hash': digest(configuration(manifest)),
            'engine_hash': fingerprint()}
    # Read-only verification of the selected context. An approval file alone
    # cannot establish that its referenced retained context still exists.
    catalog = Path(manifest['storage']['catalog']).resolve()
    with sqlite3.connect(catalog.as_uri() + '?mode=ro', uri=True) as db:
        found = []
        for table in ('enterprise_scans', 'model_contexts'):
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
                found += db.execute('SELECT body,hash FROM ' + table + ' WHERE id=?', (pins['context_identity'],)).fetchall()
        if len(found) != 1 or found[0][1] != pins['context_hash'] or digest(json.loads(found[0][0])) != pins['context_hash']:
            raise ValueError('READINESS_CURRENT_CONTEXT_MISSING_OR_CHANGED')
    return manifest, pins


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--approval', type=Path, required=True)
    parser.add_argument('--index', type=Path)
    parser.add_argument('--scope', type=Path,
                        help='Hash-bound named dependency scope receipt; never a whole-estate certificate')
    args = parser.parse_args(argv)
    try:
        manifest, pins = current_pins(args.manifest, args.approval)
        index = json.loads(args.index.read_text()) if args.index else None
        base = args.index.parent if args.index else '.'
        if args.scope:
            result = assess_named_scope(manifest, pins, index,
                {'path': str(args.scope.resolve()), 'sha256': sha(args.scope.read_bytes())}, base=base)
        else:
            result = assess(manifest, pins, index, base=base)
    except (ValueError, KeyError, OSError, sqlite3.Error) as exc:
        result = {'status': 'BLOCKED', 'scoring': 'NOT_SCORED', 'reason': 'estate-not-fully-onboarded',
                  'detail': str(exc), 'estate_reads': 0, 'model_calls': 0}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['status'] == 'READY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
