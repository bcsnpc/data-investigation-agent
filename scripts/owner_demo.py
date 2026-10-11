"""Isolated owner portal. Live mode refuses until shared transactional budgets exist."""
import argparse
from contextlib import closing
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

DEADLINE = '2026-10-11T23:30:00-05:00'


def prepare(source_manifest, folder):
    from investigator.estate_manifest import load
    source_manifest = Path(source_manifest).resolve()
    source_root = source_manifest.parents[3]
    manifest = copy.deepcopy(load(source_manifest))
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    original = copy.deepcopy(manifest)
    hashes = {}
    for key in ('catalog', 'inventory'):
        source = (source_root / manifest['storage'][key]).resolve()
        target = folder / (key + '.sqlite')
        if source == target:
            raise ValueError('OWNER_DEMO_SOURCE_STORAGE_ALIAS')
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as db:
            with closing(sqlite3.connect(target)) as clone:
                db.backup(clone)
        hashes[key] = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest['storage'][key] = str(target)
    # References resolve to the existing secret mechanism; no secret is copied.
    def absolute_refs(value, key=None):
        if isinstance(value, dict):
            return {k: absolute_refs(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [absolute_refs(v) for v in value]
        if isinstance(value, str) and key in ('credential_file', 'python') and value.startswith('.local/'):
            return str((source_root / value).resolve())
        if isinstance(value, str) and key == 'credential_reference' and value.endswith('.xml') and value.startswith('.local/'):
            return str((source_root / value).resolve())
        return value
    manifest = absolute_refs(manifest)
    destination = folder / 'estate.json'
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding='utf-8')
    (folder / 'isolation.json').write_text(json.dumps({
        'source_manifest': str(source_manifest),
        'source_manifest_sha256': hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
        'clone_sha256': hashes,
        'estate_changes': False, 'copied_secrets': False,
        'live_status': 'BLOCKED_SHARED_TRANSACTIONAL_BUDGET_PORT',
        'reason': 'UsageGovernor reserves in the catalog transaction. A cloned catalog forks the ordinary and round counters; a shared catalog breaks demo isolation.',
        'source_budget_policy': original['budgets'],
        'shared_dollar_ledger': str(source_root / '.local/round-thirteen/model-spend.sqlite'),
        'dollar_guard_microdollars': 190000000,
        'protected_margin_microdollars': 10000000,
        'deadline': DEADLINE,
    }, indent=2, sort_keys=True), encoding='utf-8')
    return destination


def live_admission():
    # Never admit a demo using copied counters, even before the cutoff.
    if datetime.now().astimezone().timestamp() >= datetime.fromisoformat(DEADLINE).timestamp():
        raise ValueError('ROUND_FIFTEEN_DEADLINE')
    raise ValueError('OWNER_DEMO_SHARED_TRANSACTIONAL_BUDGET_PORT_REQUIRED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--folder', type=Path, default=Path('.local/owner-demo'))
    parser.add_argument('--port', type=int, default=8791)
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    if args.live:
        live_admission()
    if shutil.disk_usage(Path.cwd()).free < 10 * 1024 ** 3:
        raise ValueError('OWNER_STORAGE_STOP')
    manifest = prepare(args.source_manifest, args.folder)
    import serve_investigator_workspace
    sys.argv = ['serve_investigator_workspace', '--manifest', str(manifest), '--port', str(args.port), '--open-browser']
    serve_investigator_workspace.main()


if __name__ == '__main__':
    main()
