"""Register a completed Gold publication and its exact Silver dependency proof."""
import argparse
from contextlib import closing
import hashlib
import json
import sqlite3
from uuid import UUID
from fabric_api import ROOT,api
from metadata_config import load_config
from source_snapshot import canonical
from gold_snapshot_input import build_gold
from gold_publication import validate
from record_bronze_publication import job_utc


def record(job_id):
    job_id=str(UUID(job_id))
    estate=json.loads((ROOT/'infra/fabric/environment.json').read_text())
    config=load_config(ROOT/'infra/metadata/development.json')
    workspace,gold=estate['workspace_id'],estate['gold_lakehouse_id']
    binding=build_gold(config['storage']['database'],estate)
    job=api(f"workspaces/{workspace}/items/{estate['gold_notebook_id']}/jobs/instances/{job_id}")['text']
    if job['status']!='Completed':raise ValueError('Completed Gold job required')
    latest=api(f'{workspace}/{gold}/Files/validation/latest.json',audience='storage')['text']
    run_id=str(UUID(latest['run_id']))
    report=api(f'{workspace}/{gold}/Files/validation/{run_id}.json',audience='storage')['text']
    if latest!=report:raise ValueError('Named Gold receipt differs')
    if not(job_utc(job['startTimeUtc'])<=job_utc(report['started_utc'])<=job_utc(report['finished_utc'])<=job_utc(job['endTimeUtc'])):
        raise ValueError('Gold receipt outside job time window')
    result=validate(binding,report,f'abfss://{workspace}@onelake.dfs.fabric.microsoft.com/{gold}')
    proof={'report':report,'job':job,'result':result}
    encoded=canonical(proof);digest=hashlib.sha256(encoded.encode()).hexdigest()
    with closing(sqlite3.connect(config['storage']['database'])) as db:
        db.execute('CREATE TABLE IF NOT EXISTS gold_snapshot_publications(run_id TEXT PRIMARY KEY,proof_sha256 TEXT NOT NULL,proof TEXT NOT NULL)')
        old=db.execute('SELECT proof_sha256 FROM gold_snapshot_publications WHERE run_id=?',(run_id,)).fetchone()
        if old and old[0]!=digest:raise ValueError('Gold evidence cannot be replaced')
        if not old:
            db.execute('INSERT INTO gold_snapshot_publications VALUES(?,?,?)',(run_id,digest,encoded));db.commit()
    (ROOT/'.local/gold-snapshot-publication.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--job-id',required=True)
    print(json.dumps(record(parser.parse_args().job_id)))
