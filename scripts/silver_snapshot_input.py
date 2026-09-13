"""Build Silver input bindings from registered, independently verified Bronze evidence."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import UUID

from bronze_publication import validate_verification
from ingestion_contract import plan
from metadata_config import load_config
from source_snapshot import canonical, verify_registered

ROOT = Path(__file__).resolve().parents[1]


def bind(expected, proof, proof_hash):
    if hashlib.sha256(canonical(proof).encode()).hexdigest() != proof_hash:
        raise ValueError('Registered Bronze proof hash differs')
    result = validate_verification(expected, proof['publication'], proof['verification'], proof['job'])
    if result != proof['result']:
        raise ValueError('Registered verification result differs')
    return {
        'format_version': 1,
        'status': 'BOUND_INPUTS',
        'source_snapshot_id': result['source_snapshot_id'],
        'source_manifest_sha256': result['source_manifest_sha256'],
        'bronze_verification_id': proof['verification']['verification_id'],
        'bronze_proof_sha256': proof_hash,
        'tables': [{key: row[key] for key in
                    ('source_table', 'destination', 'delta_table_id', 'delta_version', 'delta_schema', 'rows')}
                   for row in proof['verification']['tables']],
        'scope': 'Input binding only; no Silver publication or end-to-end comparability claim',
    }


def build(database, snapshot_id, verification_id, workspace, lakehouse):
    snapshot_id, verification_id = str(UUID(snapshot_id)), str(UUID(verification_id))
    reference = verify_registered(database, snapshot_id)
    expected = plan(ROOT / '.local/source-snapshots' / snapshot_id,
                    reference['manifest_sha256'], workspace, lakehouse)
    with closing(sqlite3.connect(database)) as db:
        row = db.execute('SELECT source_snapshot_id,source_manifest_sha256,proof_sha256,proof '
                         'FROM bronze_snapshot_verifications WHERE verification_id=?',
                         (verification_id,)).fetchone()
    if not row or row[:2] != (snapshot_id, reference['manifest_sha256']):
        raise ValueError('Matching registered Bronze verification required')
    proof = json.loads(row[3])
    if proof['verification']['verification_id'] != verification_id:
        raise ValueError('Verification registry identity differs')
    return bind(expected, proof, row[2])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot-id', required=True)
    parser.add_argument('--verification-id', required=True)
    args = parser.parse_args()
    config = load_config(ROOT / 'infra/metadata/development.json')
    estate = json.loads((ROOT / 'infra/fabric/environment.json').read_text())
    binding = build(config['storage']['database'], args.snapshot_id, args.verification_id,
                    estate['workspace_id'], estate['bronze_lakehouse_id'])
    target = ROOT / '.local/silver-snapshot-input.json'
    target.write_text(json.dumps(binding, indent=2), encoding='utf-8')
    print(json.dumps({'status': binding['status'], 'tables': len(binding['tables']), 'output': str(target)}))
