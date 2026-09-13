"""Acquire completed remote verification receipts and register pinned Bronze evidence."""
import argparse
from contextlib import closing
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from uuid import UUID
from fabric_api import api, ROOT
from ingestion_contract import plan
from source_snapshot import verify_registered, canonical
from metadata_config import load_config
from investigation_checks import timestamp
from bronze_publication import validate_verification


def job_utc(value):
    # Fabric explicitly labels these API fields startTimeUtc/endTimeUtc but omits the suffix.
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def record(snapshot_id, notebook_id, job_id):
    snapshot_id,notebook_id,job_id=map(lambda x:str(UUID(x)),(snapshot_id,notebook_id,job_id))
    config=load_config(ROOT/'infra/metadata/development.json')
    estate=json.loads((ROOT/'infra/fabric/environment.json').read_text())
    workspace=estate['workspace_id'];lakehouse=estate['bronze_lakehouse_id']
    reference=verify_registered(config['storage']['database'],snapshot_id)
    expected=plan(ROOT/'.local/source-snapshots'/snapshot_id,reference['manifest_sha256'],workspace,lakehouse)
    job=api(f'workspaces/{workspace}/items/{notebook_id}/jobs/instances/{job_id}')['text']
    if job['status']!='Completed':raise ValueError('Verification job has not completed successfully')
    directory=f'{lakehouse}/Files/source_snapshots/{snapshot_id}'
    publication=api(f'{workspace}/{directory}/publication.json',audience='storage')['text']
    # OneLake GUID routing requires literal path separators in this query value.
    listing=api(f'{workspace}?resource=filesystem&directory={directory}&recursive=false',audience='storage')['text']
    matches=[]
    for item in listing['paths']:
        name=item['name'].rsplit('/',1)[-1]
        if not name.startswith('verification-') or not name.endswith('.json'):continue
        try:UUID(name[len('verification-'):-len('.json')])
        except ValueError:continue
        evidence=api(f'{workspace}/{directory}/{name}',audience='storage')['text']
        if name!='verification-'+evidence['verification_id']+'.json':raise ValueError('Verification identity mismatch')
        if job_utc(job['startTimeUtc'])<=timestamp(evidence['verified_at'])<=job_utc(job['endTimeUtc']):matches.append(evidence)
    if len(matches)!=1:raise ValueError('Verification receipt not uniquely correlated with completed job')
    verification=matches[0]
    result=validate_verification(expected,publication,verification,job)
    proof={'publication':publication,'verification':verification,'job':job,'result':result}
    encoded=canonical(proof);proof_hash=hashlib.sha256(encoded.encode()).hexdigest()
    with closing(sqlite3.connect(config['storage']['database'])) as db:
        db.execute('CREATE TABLE IF NOT EXISTS bronze_snapshot_verifications(verification_id TEXT PRIMARY KEY,source_snapshot_id TEXT NOT NULL,source_manifest_sha256 TEXT NOT NULL,proof_sha256 TEXT NOT NULL,proof TEXT NOT NULL)')
        previous=db.execute('SELECT proof_sha256 FROM bronze_snapshot_verifications WHERE verification_id=?',(verification['verification_id'],)).fetchone()
        if previous and previous[0]!=proof_hash:raise ValueError('Existing verification differs')
        if not previous:
            db.execute('INSERT INTO bronze_snapshot_verifications VALUES(?,?,?,?,?)',(verification['verification_id'],snapshot_id,reference['manifest_sha256'],proof_hash,encoded));db.commit()
    (ROOT/'.local/snapshot-bronze-verified.json').write_text(json.dumps(proof,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot-id',required=True);parser.add_argument('--notebook-id',required=True);parser.add_argument('--job-id',required=True)
    args=parser.parse_args();print(json.dumps(record(args.snapshot_id,args.notebook_id,args.job_id),indent=2))
