"""Validate independently acquired, pinned publication evidence."""
from ingestion_contract import validate_receipt


def validate_verification(plan, publication, verification, job):
    validate_receipt(plan,publication)
    validate_receipt(plan,verification)
    if verification.get('mode')!='VERIFY_ONLY':raise ValueError('Independent verification receipt required')
    if not verification.get('verification_id') or verification['verification_id']==publication.get('verification_id'):
        raise ValueError('Verification must be a separate execution')
    if job.get('status')!='Completed' or not job.get('id'):
        raise ValueError('Completed verification job evidence required')
    previous={t['source_table']:t for t in publication['tables']}
    for row in verification['tables']:
        old=previous[row['source_table']]
        for key in ('delta_table_id','delta_version','destination','delta_schema'):
            if row.get(key)!=old.get(key) or row.get(key) is None:
                raise ValueError('Pinned publication identity, version or schema differs')
    return {'status':'SOURCE_TO_BRONZE_VERIFIED','source_snapshot_id':plan['source_snapshot_id'],
            'source_manifest_sha256':plan['source_manifest_sha256'],'tables':len(previous),
            'rows':sum(t['rows'] for t in previous.values()),'verification_job_id':job['id'],
            'scope':'Only the isolated Bronze tables at the recorded Delta versions; not current app/Silver/Gold/model tables'}
