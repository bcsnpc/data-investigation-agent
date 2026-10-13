"""Derive cloud readiness receipts from fresh captured verification, offline only."""
import argparse,base64,hashlib,json
from pathlib import Path
from investigator.onboarding import digest
from investigator.process_tape import Tape
from investigator.estate_readiness import assess_named_scope
from cloud_verification_capture import replay


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2),encoding='utf8');return ref(p)
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}


def unchanged_declarations(old,current):
    def members(scan):
        return {a['id']:a.get('content_hash') for a in scan['assets']}
    old_hashes,new_hashes=members(old),members(current)
    if old_hashes!=new_hashes or not all(old_hashes.values()):
        raise ValueError('RETAINED_DECLARATION_CONTENT_CHANGED')


def build(manifest_path,prepared,retained_facts,capture,output):
    prepared=Path(prepared);capture=Path(capture);output=Path(output)
    if output.exists():raise FileExistsError('READINESS_OUTPUT_EXISTS')
    manifest=read(manifest_path);approval=read(prepared/'approval.json');context=read(prepared/'context.json')
    scan={k:v for k,v in context.items() if k!='version'};old=read(retained_facts)
    unchanged_declarations(old['scan'],scan)
    if approval['context_id']!=context['version'] or approval['context_hash']!=digest(scan):
        raise ValueError('APPROVED_CONTEXT_DIFFERS')
    if approval['manifest_sha256']!=sha(manifest_path):raise ValueError('APPROVED_MANIFEST_DIFFERS')
    tape=Tape(capture/'tape.json');final=json.loads(base64.b64decode(tape.events[-1]['body']))
    if final.get('status')!='COMPLETED' or final.get('result',{}).get('status')!='VERIFIED':
        raise ValueError('VERIFICATION_NOT_COMPLETED')
    boot=tape.bootstrap;inputs=boot['state']['inputs']
    if (inputs['context_hash']!=digest(context) or inputs['engine_fingerprint']!=approval['engine_hash'] or
        inputs.get('native_route_contract')!='declared-native-pair-v1'):
        raise ValueError('VERIFICATION_PINS_DIFFER')
    result=final['result'];spec=inputs['verification_spec']
    if result['verification_reads']!=result['plan']['verification_reads_needed'] or result['verification_reads']>result['plan']['verification_cap']:
        raise ValueError('VERIFICATION_CONSERVATION_FAILED')
    if {digest(p)for p in old['proposals']}!={digest(p)for p in spec['proposals']}:
        raise ValueError('DECLARATION_BINDINGS_CHANGED')
    output.mkdir(parents=True)
    replayed=replay(capture,output/'replayed')
    replayed.update(network_requests=0,recorded_engine_hash=boot['engine_hash'],capture_sha256=sha(capture/'tape.json'))
    replay_ref=write(output/'replay.json',replayed)
    if replayed.get('status')!='COMPLETED' or not replayed.get('matched'):raise ValueError('EXACT_REPLAY_REQUIRED')
    native=result['native_route'];observations=native['observations']
    comparison=[o for o in observations if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    if len(comparison)!=1:raise ValueError('ONE_NATIVE_BOUNDARY_REQUIRED')
    c=comparison[0];ids={c['id'],c['upper_evidence_id'],c['lower_evidence_id']}
    route={'selected_observations':[o for o in observations if o['id'] in ids],
        'read_receipts':native['process_read_receipts'],'captured_run_tape':str((capture/'tape.json').resolve()),
        'captured_run_tape_sha256':sha(capture/'tape.json'),'session_id':native['id']}
    from investigator.adapters.microsoft_readiness import validate_declared_route
    validate_declared_route(route,manifest=manifest,scan=scan)
    model=read(prepared/'model.json')
    pins={'manifest_hash':digest(manifest),'context_identity':approval['context_id'],'context_hash':approval['context_hash'],
        'config_hash':approval['config_hash'],'engine_hash':approval['engine_hash']}
    facts={k:old[k]for k in ('scope','dependency_inventory','discovered_declarations','inventory','extraction_status','boundary_inventory')}
    facts.update(scan=scan,proposals=spec['proposals'],verifications=result['witnesses'],declared_routes=[route],
        model_contexts={model['id']:model['context_id']},compatible_code_units=[],
        publication={'kind':'RETAINED_EXECUTION','executions':[{'capture_ref':ref(capture/'tape.json'),
            'run_ref':write(output/'run-locator.json',{'tape_path':str((capture/'tape.json').resolve())}),
            'replay_ref':replay_ref}]})
    facts_ref=write(output/'facts.json',facts)
    def receipt(filename,fields):
        values={k:facts[k]for k in fields}
        return write(output/filename,{'pins':pins,**values,'sources':[
            {'field':k,**facts_ref,'pointer':'/'+k}for k in fields]})
    discovery=receipt('discovery.json',['scan'])
    approval_ref=write(output/'approval-receipt.json',{'pins':pins,'approval':approval,'manifest':manifest,
        'sources':[{'field':'approval',**ref(prepared/'approval.json'),'pointer':''},
                   {'field':'manifest',**ref(manifest_path),'pointer':''}]})
    transforms=receipt('transformations.json',['discovered_declarations','inventory','extraction_status','boundary_inventory'])
    bindings=receipt('bindings.json',['proposals','scan','declared_routes'])
    verification=receipt('reader-verification.json',['verifications','scan','declared_routes','model_contexts','compatible_code_units'])
    publication=receipt('publication.json',['publication','scan','declared_routes','verifications'])
    scope=receipt('scope.json',['scope','dependency_inventory'])
    index={'version':'estate-readiness-v1','pins':pins,'stages':dict(zip(
        ['discovery','discovery_approval','transformations','bindings','reader_verification','publication'],
        [discovery,approval_ref,transforms,bindings,verification,publication]))}
    write(output/'index.json',index)
    report=assess_named_scope(manifest,pins,index,scope,base=output)
    write(output/'readiness.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('manifest','prepared','retained-facts','capture','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();result=build(a.manifest,a.prepared,a.retained_facts,a.capture,a.output)
    print(json.dumps(result));return 0 if result['status']=='READY' else 2

if __name__=='__main__':raise SystemExit(main())
