"""Bounded archive-only continuation; no deletion, model call, or estate read.

Each launch uses a new directory and pinned accounting checkpoint. An interrupted
batch is resumed explicitly with archive_streaming_bundle.py and the preserved
plans/journal; never restart this controller against stale baseline accounting.
"""
import argparse
from datetime import datetime,timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import shutil

from investigator.artifact_store import ArtifactError,canonical,digest
from investigator.archive_migration import load_pinned
from investigator.streaming_archive_bundle import prepare,publish
from investigator.resumable_archive import Journal
from plan_archive_batches import batch


def pinned_json(record):
    raw=Path(record['path']).read_bytes()
    if digest(raw)!=record['sha256']:raise ArtifactError('BACKGROUND_INPUT_SHA_DIFFERS')
    return json.loads(raw)


def admission(policy,stored,controls):
    integer_fields=['batch_stored_bytes','batch_controls','total_stored_bytes']
    money_fields=['egress_usd_per_gb','control_usd_each','archive_usd_per_gb_month',
                  'platform_baseline_usd_month','transfer_usd_cap','control_usd_cap','platform_total_usd_cap']
    if any(type(policy[key]) is not int or policy[key]<1 for key in integer_fields):
        raise ArtifactError('BACKGROUND_COST_POLICY')
    if any(type(policy[key]) is not str or not Decimal(policy[key]).is_finite() or Decimal(policy[key])<0
           for key in money_fields):raise ArtifactError('BACKGROUND_COST_POLICY')
    if type(stored) is not int or type(controls) is not int or min(stored,controls)<0:
        raise ArtifactError('BACKGROUND_ACCOUNTING_CHECKPOINT')
    reserved_bytes=stored+policy['batch_stored_bytes']
    reserved_controls=controls+policy['batch_controls']
    if reserved_bytes>policy['total_stored_bytes']:
        raise ArtifactError('BACKGROUND_STORED_BYTE_CAP')
    gb=Decimal(reserved_bytes)/Decimal(10**9)
    transfer=gb*Decimal(policy['egress_usd_per_gb'])
    operations=Decimal(reserved_controls)*Decimal(policy['control_usd_each'])
    storage=gb*Decimal(policy['archive_usd_per_gb_month'])
    projected=Decimal(policy['platform_baseline_usd_month'])+transfer+operations+storage
    if transfer>Decimal(policy['transfer_usd_cap']) or operations>Decimal(policy['control_usd_cap']):
        raise ArtifactError('BACKGROUND_TRANSFER_CONTROL_CAP')
    if projected>Decimal(policy['platform_total_usd_cap']):
        raise ArtifactError('BACKGROUND_PLATFORM_COST_CAP')
    return {'reserved_bytes':reserved_bytes,'reserved_controls':reserved_controls,
            'projected_platform_usd':str(projected),'free_egress_credited':False}


def write_new(path,value):
    with Path(path).open('xb') as stream:stream.write(canonical(value))
    return digest(canonical(value))


def run(config,output,client_factory,*,planner=batch,preparer=prepare,publisher=publish):
    if not config.get('scope_approval') or config.get('local_deletion') is not False:
        raise ArtifactError('BACKGROUND_ARCHIVE_APPROVAL_REQUIRED')
    if any(type(config[key]) is not int or config[key]<1 for key in ('max_batches','max_files','max_original_bytes')):
        raise ArtifactError('BACKGROUND_SELECTION_BOUNDS')
    root=Path(config['workspace']).resolve(strict=True)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    write_new(output/'config.json',config)
    baseline=pinned_json(config['accounting_checkpoint'])
    stored=baseline['stored_bytes'];controls=baseline['platform_controls']
    pins=list(config['previous_plans']);skip=set()
    for pin in pins:
        prior=load_pinned(pin['path'],pin['sha256'])
        skip.update(row['path'] for row in prior['entries']+prior['excluded'])
    cutoff=datetime.fromisoformat(config['cutoff']).timestamp()
    deadline=datetime.fromisoformat(config['admit_before'])
    if deadline.tzinfo is None:raise ArtifactError('BACKGROUND_DEADLINE_TIMEZONE_REQUIRED')
    stop_file=Path(config['stop_file'])
    rows=[]
    def record(event):
        with (output/'controller.jsonl').open('ab') as stream:
            stream.write(canonical({'at':datetime.now(timezone.utc).isoformat(),**event})+b'\n')
            stream.flush();os.fsync(stream.fileno())
        print(json.dumps(event),flush=True)
    try:
        for index in range(config['max_batches']):
            if datetime.now(timezone.utc)>=deadline or stop_file.exists():
                record({'phase':'ADMISSIONS_CLOSED','index':index,'reason':'deadline or stop file'})
                break
            if shutil.disk_usage(root).free<10*1024**3:raise ArtifactError('BACKGROUND_DISK_FLOOR')
            projected=admission(config['cost_policy'],stored,controls)
            folder=output/f'batch-{index:04d}';folder.mkdir()
            manifest=planner(root,cutoff,max_original_bytes=config['max_original_bytes'],
                             max_files=config['max_files'],protected=config['protected_paths'],skip_paths=skip)
            manifest['previous_plans']=list(pins)
            sha=write_new(folder/'source-plan.json',manifest)
            pin={'path':str((folder/'source-plan.json').resolve()),'sha256':sha}
            pins.append(pin);skip.update(row['path'] for row in manifest['entries']+manifest['excluded'])
            if not manifest['entries']:
                record({'phase':'NO_ELIGIBLE_SELECTION','index':index,'excluded':len(manifest['excluded'])})
                break
            prepared,_=preparer(manifest,sha)
            plan_sha=write_new(folder/'bundle-plan.json',prepared)
            review={'status':'APPROVED','manifest_sha256':sha,
                    'reviewer':'Automated bounded archive under '+config['scope_approval'],
                    'basis':'Pinned historical scope before fixed cutoff; source seal/hash and raw/decoded credential-pattern checks passed. Whole captures only, quarantined peers excluded, private archive, no raw staging or deletion. This is a scope-limited automated check, not a universal privacy claim.'}
            write_new(folder/'privacy-review.json',review)
            if datetime.now(timezone.utc)>=deadline or stop_file.exists():
                record({'phase':'ADMISSIONS_CLOSED','index':index,'reason':'deadline or stop file after preparation'})
                break
            if shutil.disk_usage(root).free<10*1024**3:raise ArtifactError('BACKGROUND_DISK_FLOOR')
            record({'phase':'ADMITTED','index':index,'manifest_sha256':sha,'files':len(manifest['entries']),
                    'excluded':len(manifest['excluded']),**projected})
            client=client_factory(folder,config['cost_policy']['batch_controls'])
            receipt=publisher(prepared,plan_sha,manifest,sha,review,client,
                              Journal(folder/'progress.jsonl',plan_sha,client.account_url),
                              max_stored_bytes=config['cost_policy']['batch_stored_bytes'])
            receipt_sha=write_new(folder/'receipt.json',receipt)
            charged=config['cost_policy']['batch_controls']-client.remaining
            stored+=receipt['stored_bytes'];controls+=charged
            result={'phase':'VERIFIED','index':index,'receipt_sha256':receipt_sha,'files':len(receipt['objects']),
                    'original_bytes':receipt['original_bytes'],'stored_bytes':receipt['stored_bytes'],
                    'platform_controls':charged,'cumulative_stored_bytes':stored,'cumulative_controls':controls}
            rows.append(result);record(result)
    except BaseException as error:
        record({'phase':'STOPPED','type':type(error).__name__,'message':str(error),
                'partial_control_charges':'Read current progress.jsonl.controls.jsonl; do not reuse old baseline.',
                'originals_deleted':False})
        raise
    result={'status':'BOUNDED_PASS_COMPLETE_NOT_FULL_ARCHIVE','batches':rows,'stored_bytes':stored,
            'platform_controls':controls,'local_deletion':False,'estate_reads':0,'model_calls':0}
    write_new(output/'result.json',result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--config-sha256',required=True)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    config=pinned_json({'path':str(args.config),'sha256':args.config_sha256})
    from investigator.live_gateway import current
    from investigator.adapters.platform_credentials import OwnerCliCredential
    from investigator.adapters.platform_archive_client import IdentityArchiveClient
    credential=OwnerCliCredential(Path(config['azure_cli_python']),config['tenant'],config['subscription'])
    def client(folder,cap):
        return IdentityArchiveClient(config['account_url'],credential,current(),config['gateway_channel'],
                                     max_requests=cap,receipts=str(folder/'progress.jsonl')+'.controls.jsonl')
    publisher=publish
    mode=config.get('verification_mode','readback')
    if mode=='block-checksum-v1':
        from investigator.checksum_archive import publish as publisher
    elif mode!='readback':raise ArtifactError('BACKGROUND_VERIFICATION_MODE')
    run(config,args.output,client,publisher=publisher)


if __name__=='__main__':main()
