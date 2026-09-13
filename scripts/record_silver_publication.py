"""Acquire the completed Silver job receipt and persist source/version evidence."""
import argparse
from contextlib import closing
import hashlib
import json
import sqlite3
from uuid import UUID
from fabric_api import ROOT, api
from metadata_config import load_config
from source_snapshot import canonical
from silver_snapshot_input import build
from silver_publication import validate
from record_bronze_publication import job_utc


def record(job_id):
    job_id = str(UUID(job_id))
    estate = json.loads((ROOT/'infra/fabric/environment.json').read_text())
    config = load_config(ROOT/'infra/metadata/development.json')
    workspace, silver = estate['workspace_id'], estate['silver_lakehouse_id']
    snapshot = estate['snapshot_bronze']
    binding = build(config['storage']['database'], snapshot['source_snapshot_id'],
                    snapshot['verification_id'], workspace, estate['bronze_lakehouse_id'])
    job = api(f"workspaces/{workspace}/items/{estate['silver_notebook_id']}/jobs/instances/{job_id}")['text']
    if job['status'] != 'Completed': raise ValueError('Completed Silver job required')
    latest = api(f'{workspace}/{silver}/Files/validation/latest.json', audience='storage')['text']
    run_id = str(UUID(latest['run_id']))
    report = api(f'{workspace}/{silver}/Files/validation/{run_id}.json', audience='storage')['text']
    if latest != report: raise ValueError('Latest and named Silver receipt differ')
    if not (job_utc(job['startTimeUtc']) <= job_utc(report['started_utc']) <=
            job_utc(report['finished_utc']) <= job_utc(job['endTimeUtc'])):
        raise ValueError('Receipt does not belong to completed job time window')
    result = validate(binding, report, f'abfss://{workspace}@onelake.dfs.fabric.microsoft.com/{silver}')
    proof = {'report':report,'job':job,'result':result}
    encoded = canonical(proof)
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    with closing(sqlite3.connect(config['storage']['database'])) as db:
        db.execute('CREATE TABLE IF NOT EXISTS silver_snapshot_publications(run_id TEXT PRIMARY KEY, proof_sha256 TEXT NOT NULL, proof TEXT NOT NULL)')
        previous = db.execute('SELECT proof_sha256 FROM silver_snapshot_publications WHERE run_id=?',(run_id,)).fetchone()
        if previous and previous[0] != digest: raise ValueError('Silver evidence cannot be replaced')
        if not previous:
            db.execute('INSERT INTO silver_snapshot_publications VALUES(?,?,?)',(run_id,digest,encoded))
            db.commit()
    (ROOT/'.local/silver-snapshot-publication.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job-id',required=True)
    print(json.dumps(record(parser.parse_args().job_id)))
