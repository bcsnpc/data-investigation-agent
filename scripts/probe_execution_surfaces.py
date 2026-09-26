"""Operator probe of which execution surfaces are reachable.

Receipts record a SHA-256 of each result as a comparison fingerprint, not the value
itself. The fingerprint is not confidential: a hash of a scalar is brute-forceable.

Each probe reports REACHABLE, UNAVAILABLE or NOT_APPLICABLE with the stage and error
type where it failed. A failed probe never stops the others and is never replaced by
a substitute. Reachability is not comparability: no probe here compiles a lower-layer
quantity or compares values.

The Fabric SQL analytics endpoint is deliberately not probed (AADSTS65002 is an
app-registration decision outside this probe set).

Correction, 2026-09-26: the parenthetical above describes the Fabric CLI client,
not the endpoint. A tenant administrator's Azure CLI token was accepted only by
the dev workspace's SQL endpoint. The investigation workspace's Gold endpoint is
untested, and it remains outside this probe set until a human decides which
identity should hold that access. The "isolated metadata identity" used below is
the tenant administrator. See docs/execution-surface-inventory.md.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time

PROBES=('semantic_dax','source_sql','onelake_commit_metadata','onelake_table_data')
from read_onelake_header import HEADER_BYTES


def _now():return datetime.now(timezone.utc).isoformat()


def values_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest()


def receipt(probe,surface,identity_role,started,**fields):
    result={'probe':probe,'execution_surface':surface,'identity_role':identity_role,
            'started_utc':started,'finished_utc':_now()}
    result.update(fields)
    if result.get('status')=='REACHABLE' and (not isinstance(surface,dict)
            or any(not isinstance(surface.get(k),str) or not surface.get(k) for k in ('engine','connection','object'))):
        raise ValueError('A reachable probe must identify its execution surface')
    return result


def failed(probe,surface,identity_role,started,stage,exc):
    return receipt(probe,surface,identity_role,started,status='UNAVAILABLE',stage=stage,
                   error_type=type(exc).__name__,
                   http_status=getattr(exc,'code',None) if isinstance(getattr(exc,'code',None),int) else None)


def probe_semantic(adapter,path,measure_id):
    """Presentation baseline through the adapter's own evaluate(); the value is hashed."""
    started=_now();layer=path['layers'][0]
    try:probe=adapter.evaluate(layer,measure_id,{})
    except Exception as exc:return failed('semantic_dax',None,'NATIVE_READER',started,'evaluate',exc)
    evidence=probe.evidence or {}
    return receipt('semantic_dax',probe.execution_surface,'NATIVE_READER',started,
        status='REACHABLE' if probe.status=='OBSERVED' else 'UNAVAILABLE',
        stage='complete' if probe.status=='OBSERVED' else 'evaluate',
        probe_status=probe.status,reason=probe.reason,layer=layer['id'],tool='bounded_dax',
        receipt_id=evidence.get('id'),request_hash=evidence.get('request_hash'),
        completeness=evidence.get('completeness'),returned_rows=len(evidence.get('values') or []),
        values_sha256=values_hash(probe.value) if probe.status=='OBSERVED' else None)


def source_query(objects):
    """Deterministic, name-free choice: the first approved object by asset identity."""
    if not objects:return None,None
    identity=sorted(objects)[0];meta=objects[identity]['metadata']
    from investigator.source_diagnostics import quote as quote_sql
    name=quote_sql(meta['schema_name'])+'.'+quote_sql(meta['name'])
    return identity,f'SELECT COUNT_BIG(*) AS probe FROM {name}'


def probe_source(store,model,config,execute,meter):
    from investigator.flexible_tools import run as run_query
    from investigator.source_diagnostics import snapshot
    started=_now();connection='sql://'+config['sql']['server']+'/'+config['sql']['database']
    try:objects,_=snapshot(store,model,config)
    except Exception as exc:return failed('source_sql',None,'SOURCE_READER',started,'catalog_snapshot',exc)
    identity,query=source_query(objects)
    if identity is None:
        return receipt('source_sql',None,'SOURCE_READER',started,status='NOT_APPLICABLE',stage='catalog_snapshot',
                       reason='No approved source object is present in the pinned catalog snapshot.')
    meta=objects[identity]['metadata']
    surface={'engine':'AZURE_SQL','connection':connection,'object':meta['schema_name']+'.'+meta['name']}
    plan={'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],
          'query':query,'max_rows':20}
    try:result=meter('bounded_sql',lambda:run_query(store,plan,config,'bounded_sql',execute))
    except Exception as exc:return failed('source_sql',surface,'SOURCE_READER',started,'dispatch',exc)
    body=result.get('result',{});completed=result.get('status')=='COMPLETED'
    principal=(body.get('execution_identity') or {}).get('principal') if completed else None
    return receipt('source_sql',surface,'SOURCE_READER',started,
        status='REACHABLE' if completed else 'UNAVAILABLE',stage='complete' if completed else 'query',
        tool='bounded_sql',object_asset_id=identity,receipt_id=result.get('id'),
        request_hash=result.get('request_hash'),read_status=result.get('status'),
        error_type=None if completed else body.get('error_type'),
        sql_error_number=None if completed else body.get('error_number'),
        principal=principal,completeness=body.get('completeness'),returned_rows=body.get('returned_rows'),
        values_sha256=values_hash(body.get('rows')) if completed else None,
        limitation='Proves reader, transport and object permission only; no layer quantity was compiled.')


def probe_commit(adapter,path,captured):
    started=_now()
    try:result=adapter.ingestion(path,{})
    except Exception as exc:return failed('onelake_commit_metadata',None,'ISOLATED_METADATA',started,'ingestion',exc)
    request=captured.get('request')
    surface=({'engine':'ONELAKE_DELTA_LOG','connection':'onelake://'+request['workspace']+'/'+request['lakehouse'],
              'object':request['table']} if request else None)
    commit=((result.get('evidence') or {}).get('delta_commit') or {})
    if request is None:
        return receipt('onelake_commit_metadata',None,'ISOLATED_METADATA',started,status='NOT_APPLICABLE',
                       stage='resolve_path',reason=result.get('reason'))
    return receipt('onelake_commit_metadata',surface,'ISOLATED_METADATA',started,
        status='REACHABLE' if result.get('status')=='CURRENT' else 'UNAVAILABLE',
        stage='complete' if result.get('status')=='CURRENT' else 'read',
        read_status=commit.get('status'),error_type=commit.get('error_type'),
        latest_commit=commit.get('latest_commit'),
        operation=(commit.get('commit_info') or {}).get('operation'),
        limitation='Commit metadata only; no table data was read.')


def probe_table_data(request,read):
    """List the bound table's files, then read at most a data-file header.

    `read(request)` runs the isolated metadata-identity reader and returns its JSON
    result; the storage token never enters this process.
    """
    started=_now()
    if request is None:
        return receipt('onelake_table_data',None,'ISOLATED_METADATA',started,status='NOT_APPLICABLE',
                       stage='resolve_path',reason='No declared data asset was resolved.')
    surface={'engine':'ONELAKE_DFS','connection':'onelake://'+request['workspace']+'/'+request['lakehouse'],
             'object':request['table']}
    def unavailable(stage,result,**extra):
        return receipt('onelake_table_data',surface,'ISOLATED_METADATA',started,status='UNAVAILABLE',stage=stage,
                       error_type=result.get('error_type'),http_status=result.get('http_status'),**extra)
    try:listing=read(dict(request,mode='listing'))
    except Exception as exc:return failed('onelake_table_data',surface,'ISOLATED_METADATA',started,'listing',exc)
    if listing.get('status')!='AVAILABLE':return unavailable('listing',listing)
    files=listing.get('data_files') or []
    if not files:
        return unavailable('listing',{},listing_http_status=listing.get('http_status'),data_files_listed=0,
                           reason='The listing returned no data file under the bound table.')
    try:header=read(dict(request,mode='header',file=files[0]))
    except Exception as exc:
        result=failed('onelake_table_data',surface,'ISOLATED_METADATA',started,'data_header',exc)
        result.update(listing_http_status=listing.get('http_status'),data_files_listed=len(files));return result
    if header.get('status')!='AVAILABLE':
        return unavailable('data_header',header,listing_http_status=listing.get('http_status'),data_files_listed=len(files))
    magic=header.get('parquet_magic_matches') is True and header.get('bytes_read')==HEADER_BYTES
    return receipt('onelake_table_data',surface,'ISOLATED_METADATA',started,
        status='REACHABLE' if magic else 'UNAVAILABLE',stage='complete' if magic else 'data_header',
        listing_http_status=listing.get('http_status'),data_files_listed=len(files),
        header_http_status=header.get('http_status'),header_bytes_read=header.get('bytes_read'),
        parquet_magic_matches=header.get('parquet_magic_matches') is True,
        limitation=('Data-file header only. No Delta snapshot was reconstructed, no row was decoded and no '
                    'aggregate was computed; the listing is not the active file set.'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--environment',required=True);parser.add_argument('--model-id',required=True)
    parser.add_argument('--measure-id',required=True);parser.add_argument('--usage-policy',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--approve',action='store_true')
    args=parser.parse_args()
    if not args.approve:parser.error('Explicit --approve required; every probe consumes a cloud-read reservation')
    import sqlite3,subprocess
    from types import SimpleNamespace
    from investigator.onboarding import ModelStore,encoded
    from investigator.runtime import Runtime
    from investigator.usage_governance import UsageGovernor
    from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
    from metadata_config import load_config,ROOT
    from run_native_diagnostic import transport as native_transport
    from run_source_diagnostic import transport as source_transport
    config=load_config(args.config);store=ModelStore(args.database,config['storage']['database'],args.environment)
    @contextmanager
    def db():
        connection=sqlite3.connect(args.database);connection.row_factory=sqlite3.Row
        try:
            with connection:yield connection
        finally:connection.close()
    governor=UsageGovernor(SimpleNamespace(db=db,store=store),json.loads(args.usage_policy.read_text(encoding='utf-8-sig')),time.time)
    identity='execution-surface-probe-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');counter=[0]
    def meter(tool,execute):
        counter[0]+=1;key=f'{identity}:{counter[0]}:{tool}'
        with db() as c:
            c.execute('BEGIN IMMEDIATE');governor.reserve(c,identity,key,'cloud')
        uncertain=True
        try:
            result=execute();uncertain=False;return result
        finally:
            with db() as c:
                c.execute('BEGIN IMMEDIATE');governor.settle(c,identity,key,uncertain=uncertain)
    runtime=Runtime(store,config,lambda p:native_transport(config,p),lambda p:source_transport(config,p))
    captured={}
    def read_ingestion(request):
        captured['request']=request
        def execute():
            completed=subprocess.run([config['fabric']['auth']['python'],str(ROOT/'scripts/read_onelake_commit.py')],
                input=encoded(request),capture_output=True,text=True,encoding='utf-8',timeout=90)
            try:result=json.loads(completed.stdout)
            except (ValueError,TypeError):return {'status':'UNAVAILABLE','error_type':'InvalidResponse'}
            return result if not completed.returncode else {'status':'UNAVAILABLE','error_type':result.get('error_type','TransportError')}
        return meter('onelake_commit',execute)
    model=store.get(args.model_id)
    adapter=MicrosoftProcessAdapter(store,config,model,runtime.native_transport,runtime.source_transport,
                                    meter_read=meter,read_ingestion=read_ingestion)
    args.out.mkdir(parents=True,exist_ok=True)
    before=governor.snapshot();path=adapter.resolve_path(args.measure_id)
    layers=[{'id':x['id'],'kind':x['kind']} for x in path['layers']]
    receipts=[probe_semantic(adapter,path,args.measure_id),
              probe_source(store,model,config,runtime.source_transport,meter),
              probe_commit(adapter,path,captured)]
    def read_data(request):
        def execute():
            completed=subprocess.run([config['fabric']['auth']['python'],str(ROOT/'scripts/read_onelake_header.py')],
                input=encoded(request),capture_output=True,text=True,encoding='utf-8',timeout=90)
            try:return json.loads(completed.stdout)
            except (ValueError,TypeError):return {'status':'UNAVAILABLE','error_type':'InvalidResponse'}
        return meter('onelake_data',execute)
    receipts.append(probe_table_data(captured.get('request'),read_data))
    surfaces=[r['execution_surface'] for r in receipts if r['status']=='REACHABLE']
    record={'probe_session':identity,'environment':args.environment,'model_id':model['id'],
            'model_revision':model['revision'],'context_id':model['context_id'],'measure_id':args.measure_id,
            'resolved_layers':layers,'path_stopped_by':path['stopped_by'],
            'receipts':receipts,'reachable':sum(r['status']=='REACHABLE' for r in receipts),
            'distinct_reachable_surfaces':len({json.dumps(s,sort_keys=True) for s in surfaces}),
            'cloud_reservations':counter[0],'usage_before':before,'usage_after':governor.snapshot(),
            'not_probed':[{'surface':'FABRIC_SQL_ANALYTICS_ENDPOINT',
                           'reason':'Out of scope: which identity may read the endpoint is an open human decision; see docs/execution-surface-inventory.md.'}]}
    (args.out/'surface-probe.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({'probe_session':identity,'reachable':record['reachable'],'cloud_reservations':counter[0],
                      'statuses':{r['probe']:r['status'] for r in receipts}}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
