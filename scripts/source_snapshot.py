"""Publish and verify transaction-consistent, content-addressed source artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sqlite3
from contextlib import closing
import tempfile
import uuid

from metadata_config import ROOT, load_config

TABLES = frozenset(('customers','products','orders','order_lines','payments','shipments',
                    'shipment_lines','refunds','refund_lines','audit_log'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def verify(folder, expected_manifest_sha256=None, pending=False):
    folder = Path(folder).resolve()
    manifest_path = folder/('.manifest.pending' if pending else 'manifest.json')
    manifest_hash = digest(manifest_path)
    if expected_manifest_sha256 is not None and manifest_hash != expected_manifest_sha256:
        raise ValueError('Manifest does not match the expected immutable reference')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest['format_version'] != 1 or manifest['status'] != 'READY' or manifest['isolation'] != 'SNAPSHOT':
        raise ValueError('Ready SNAPSHOT manifest required')
    uuid.UUID(manifest['snapshot_id'])
    if manifest.get('transaction_completed') is not True:
        raise ValueError('Successful transaction receipt required')
    tables = manifest['tables']
    if len(tables) != len(TABLES) or {t['name'] for t in tables} != TABLES:
        raise ValueError('Exact ten-table extraction required')
    for table in tables:
        if table['file'] != table['name']+'.jsonl':
            raise ValueError('Unexpected artifact filename')
        path = (folder/table['file']).resolve()
        if path.parent != folder:
            raise ValueError('Artifact escapes extraction directory')
        if digest(path) != table['sha256']:
            raise ValueError('Content checksum mismatch: '+table['name'])
        columns = table['columns']
        if not columns or len({c['name'] for c in columns}) != len(columns):
            raise ValueError('Invalid schema')
        if hashlib.sha256(canonical(columns).encode()).hexdigest() != table['schema_sha256']:
            raise ValueError('Schema checksum mismatch')
        count = 0
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                row = json.loads(line)
                if not isinstance(row, list) or len(row) != len(columns) or any(v is not None and not isinstance(v,str) for v in row):
                    raise ValueError('Invalid typed row array')
                count += 1
        if type(table['rows']) is not int or count != table['rows']:
            raise ValueError('Row count mismatch')
    return {'snapshot_id':manifest['snapshot_id'], 'manifest_sha256':manifest_hash,
            'tables':len(tables), 'rows':sum(t['rows'] for t in tables)}


def capture(config):
    snapshot_id = str(uuid.uuid4())
    folder = ROOT/'.local/source-snapshots'/snapshot_id
    folder.mkdir(parents=True, exist_ok=False)
    request = {'snapshot_id':snapshot_id,'output':str(folder),'server':config['sql']['server'],
               'database':config['sql']['database'],'credential_file':config['sql']['auth']['credential_file']}
    with tempfile.TemporaryDirectory() as temp:
        request_path = Path(temp)/'request.json'
        request_path.write_text(json.dumps(request))
        subprocess.run(['powershell','-NoProfile','-File',str(ROOT/'infra/scripts/Export-SourceSnapshot.ps1'),
                        '-RequestPath',str(request_path)], check=True, timeout=1800)
    receipt = json.loads((folder/'receipt.json').read_text(encoding='utf-8-sig'))
    if receipt['snapshot_id'] != snapshot_id or receipt['transaction_completed'] is not True or receipt['isolation'] != 'SNAPSHOT':
        raise ValueError('Invalid transaction receipt')
    for table in receipt['tables']:
        table['sha256'] = digest(folder/table['file'])
        table['schema_sha256'] = hashlib.sha256(canonical(table['columns']).encode()).hexdigest()
    manifest = dict(receipt, format_version=1,status='READY',encoding='utf-8-jsonl-string-arrays',
                    source={'server':request['server'],'database':request['database'],'schema':'app'},
                    exporter_sha256=digest(ROOT/'infra/scripts/Export-SourceSnapshot.ps1'))
    # Verify the candidate in the private run directory before publishing the readiness marker.
    candidate = folder/'.manifest.pending'
    with candidate.open('x',encoding='utf-8') as stream:
        stream.write(canonical(manifest))
    result = verify(folder, pending=True)
    candidate.rename(folder/'manifest.json')
    with closing(sqlite3.connect(config['storage']['database'])) as db:
        db.execute('CREATE TABLE IF NOT EXISTS source_snapshots(snapshot_id TEXT PRIMARY KEY, manifest_sha256 TEXT NOT NULL, directory TEXT NOT NULL, source TEXT NOT NULL, captured_at TEXT NOT NULL)')
        db.execute('INSERT INTO source_snapshots VALUES(?,?,?,?,?)', (snapshot_id,result['manifest_sha256'],str(folder),canonical(manifest['source']),receipt['finished_at']))
        db.commit()
    result['folder'] = str(folder)
    return result


def verify_registered(database, snapshot_id):
    with closing(sqlite3.connect(database)) as db:
        row=db.execute('SELECT directory,manifest_sha256 FROM source_snapshots WHERE snapshot_id=?',(str(uuid.UUID(snapshot_id)),)).fetchone()
    if not row:
        raise ValueError('Registered snapshot not found')
    result=verify(row[0],row[1])
    if result['snapshot_id'] != snapshot_id:
        raise ValueError('Snapshot identity differs from registry')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--verify',type=Path)
    parser.add_argument('--manifest-sha256')
    parser.add_argument('--snapshot-id')
    args=parser.parse_args()
    config=load_config(args.config)
    if args.snapshot_id:
        result=verify_registered(config['storage']['database'],args.snapshot_id)
    elif args.verify:
        result=verify(args.verify,args.manifest_sha256)
    else:
        result=capture(config)
    print(json.dumps(result,indent=2))
