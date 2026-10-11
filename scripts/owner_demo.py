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
import os

DEADLINE = '2026-10-11T23:30:00-05:00'


def prepare(source_manifest, folder, *, live=False, budget_manifest=None, context_id=None, context_hash=None):
    from investigator.estate_manifest import load
    source_manifest = Path(source_manifest).resolve()
    source_root = source_manifest.parents[3]
    manifest = copy.deepcopy(load(source_manifest))
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    original = copy.deepcopy(manifest)
    if live:
        if budget_manifest is None or not context_id or not context_hash:
            raise ValueError('OWNER_DEMO_CURRENT_BUDGET_AND_RETAINED_CONTEXT_REQUIRED')
        manifest['budgets']=copy.deepcopy(load(budget_manifest)['budgets'])
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
    if live:
        manifest['storage']['shared_accounting']=str((source_root/original['storage']['catalog']).resolve())
    destination = folder / 'estate.json'
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding='utf-8')
    if live:
        from investigator.estate_installation import build
        from investigator.onboarding import digest
        from investigator.enterprise_discovery import Discovery
        from investigator.runtime import fingerprint
        _,workspace=build(destination,execution_enabled=False)
        with workspace.store.connect() as db:
            row=db.execute('SELECT body,hash,status FROM enterprise_scans WHERE id=? AND environment=?',(context_id,workspace.store.environment)).fetchone()
        if row is None or row['hash']!=context_hash or row['status'] not in ('COMPLETE','PARTIAL'):
            raise ValueError('OWNER_DEMO_RETAINED_CONTEXT_DIFFERS')
        body=json.loads(row['body'])
        if digest(body)!=context_hash:raise ValueError('OWNER_DEMO_RETAINED_CONTEXT_HASH_DIFFERS')
        for key in ('version','graph','changes','inventory_scan_id','created'):body.pop(key,None)
        authority={'owner':'Chaitu','decision':'Round Fifteen isolated live owner demo using unchanged retained original fixture metadata and existing shared accounting; no estate or scope change','metadata_not_recollected':True,'source_context':context_id,'source_hash':context_hash}
        body.update(profile_hash=digest(workspace.agent.config),calls=0,retained_metadata_approval=authority)
        approved=Discovery(workspace.store,workspace.agent.config).run(lambda:body,'owner-demo-retained-approval')
        (folder/'approval.json').write_text(json.dumps({'context_id':approved['id'],'context_hash':approved['hash'],'config_hash':digest(workspace.agent.config),'engine_hash':fingerprint(),'manifest_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'authority':authority,'physical_requests':0,'model_calls':0},indent=2,sort_keys=True),encoding='utf8')
    (folder / 'isolation.json').write_text(json.dumps({
        'source_manifest': str(source_manifest),
        'source_manifest_sha256': hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
        'clone_sha256': hashes,
        'estate_changes': False, 'copied_secrets': False,
        'live_status': 'TRANSACTIONAL_SHARED_ACCOUNTING' if live else 'EXECUTION_DISABLED',
        'reason': 'Only budget tables are attached to the same session transaction; replay materializes a sealed budget-only baseline.',
        'source_budget_policy': original['budgets'],
        'shared_dollar_ledger': str(source_root / '.local/round-thirteen/model-spend.sqlite'),
        'dollar_guard_microdollars': 190000000,
        'protected_margin_microdollars': 10000000,
        'deadline': DEADLINE,
    }, indent=2, sort_keys=True), encoding='utf-8')
    return destination


def live_admission():
    if datetime.now().astimezone().timestamp() >= datetime.fromisoformat(DEADLINE).timestamp():
        raise ValueError('ROUND_FIFTEEN_DEADLINE')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--folder', type=Path, default=Path('.local/owner-demo'))
    parser.add_argument('--port', type=int, default=8791)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--budget-manifest',type=Path)
    parser.add_argument('--context-id')
    parser.add_argument('--context-hash')
    args = parser.parse_args()
    if args.live:
        live_admission()
    if shutil.disk_usage(Path.cwd()).free < 10 * 1024 ** 3:
        raise ValueError('OWNER_STORAGE_STOP')
    manifest = prepare(args.source_manifest, args.folder,live=args.live,budget_manifest=args.budget_manifest,context_id=args.context_id,context_hash=args.context_hash)
    if shutil.disk_usage(Path.cwd()).free < 10 * 1024 ** 3:
        raise ValueError('OWNER_STORAGE_STOP_AFTER_PREPARATION')
    source_root=args.source_manifest.resolve().parents[3]
    if args.live:
        os.environ.update(INVESTIGATOR_EXISTING_SECRET_ROOT=str(source_root),
            INVESTIGATOR_MODEL_SPEND_DB=str(source_root/'.local/round-thirteen/model-spend.sqlite'),
            INVESTIGATOR_MODEL_SPEND_MICRODOLLARS='190000000',
            INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS='10000000',
            INVESTIGATOR_LIVE_ADMISSION_DEADLINE=DEADLINE,
            INVESTIGATOR_RECORD_RUNS='1',INVESTIGATOR_RECORD_PLANNER='1')
    import serve_investigator_workspace
    sys.argv = ['serve_investigator_workspace', '--manifest', str(manifest), '--port', str(args.port), '--open-browser']
    if args.live:sys.argv.append('--live')
    serve_investigator_workspace.main()


if __name__ == '__main__':
    main()
