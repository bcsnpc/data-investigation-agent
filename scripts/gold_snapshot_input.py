"""Resolve Gold inputs from a registered Silver publication and its Bronze proof."""
from contextlib import closing
import hashlib
import json
import sqlite3
from uuid import UUID
from source_snapshot import canonical
from silver_snapshot_input import build
from silver_publication import validate


def validate_proof(binding, proof, digest, silver_root, run_id):
    if hashlib.sha256(canonical(proof).encode()).hexdigest() != digest:
        raise ValueError('Silver proof hash differs')
    result = validate(binding, proof['report'], silver_root)
    if result != proof['result'] or proof['report']['run_id'] != run_id:
        raise ValueError('Silver proof identity/result differs')
    if proof['job'].get('status') != 'Completed':
        raise ValueError('Completed Silver job required')
    return {'status':'BOUND_SILVER','silver_proof_sha256':digest,'report':proof['report']}


def build_gold(database, estate):
    run_id = str(UUID(estate['snapshot_silver']['run_id']))
    snapshot = estate['snapshot_bronze']
    binding = build(database, snapshot['source_snapshot_id'], snapshot['verification_id'],
                    estate['workspace_id'], estate['bronze_lakehouse_id'])
    with closing(sqlite3.connect(database)) as db:
        row = db.execute('SELECT proof_sha256,proof FROM silver_snapshot_publications WHERE run_id=?',(run_id,)).fetchone()
    if not row: raise ValueError('Registered Silver publication required')
    root=f"abfss://{estate['workspace_id']}@onelake.dfs.fabric.microsoft.com/{estate['silver_lakehouse_id']}"
    return validate_proof(binding,json.loads(row[1]),row[0],root,run_id)
