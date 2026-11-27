"""One fixed native engine DAX read, no ticket or AI; publish its safe receipt."""
import json
import os
from pathlib import Path
import platform
import time

QUERY = 'EVALUATE ROW("ok", 1)'


def probe(config, model):
    from metadata_config import validate_config
    from investigator.adapters.investigative_native import NativeQueries
    validate_config(config)
    binding=config['fabric']['dax_transport']
    if model not in binding['models']:raise ValueError('Probe model outside XMLA bindings')
    route=dict(kind='DAX',workspace=config['fabric']['workspace_id'],model=model,asset_ids=[],config=config)
    started=time.monotonic()
    result=NativeQueries({'semantic':route})('semantic',dict(query=QUERY,asset_ids=[]),timeout_seconds=30)
    return dict(status='PASS' if result['rows']==[{'[ok]':1}] else 'MISMATCH',query=QUERY,result=result,
                model_id=model,transport='XMLA',entrypoint='NativeQueries.__call__ -> run_native_diagnostic.execute',
                os=platform.system(),seconds=round(time.monotonic()-started,3),ticket_runs=0,ai_calls=0)


def main():
    from investigator.live_gateway import configured, current
    from investigator.adapters.blob_artifacts import bound_credential
    from platform_blob_transfer import transfer
    import hashlib
    config=json.loads(os.environ['DIA_XMLA_PROBE_CONFIG'])
    policy=json.loads(os.environ['DIA_PLATFORM_GATEWAY_POLICY'])
    identity=config['fabric']['auth']['managed_identity']
    with configured(policy):
        try:
            result=probe(config,os.environ['DIA_XMLA_PROBE_MODEL'])
        except Exception as error:
            # Native/SDK messages may contain credentials. Expose safe stages only.
            result=dict(status='FAILED',error_type=type(error).__name__,
                        stage=getattr(error,'stage',None),provider_code=getattr(error,'provider_code',None),
                        http_status=getattr(error,'http_status',None),os=platform.system(),ticket_runs=0,ai_calls=0)
        result['image_source']=json.loads(Path('/app/image-source-manifest.json').read_text())['engine_revision']
        path=Path('/work/xmla-probe-result.json')
        path.write_text(json.dumps(result,sort_keys=True)+'\n',encoding='utf8')
        transfer('put',os.environ['DIA_XMLA_PROBE_RESULT_URL'],path,hashlib.sha256(path.read_bytes()).hexdigest(),
                 credential=bound_credential(identity),gateway=current(),channel='probe-capture',
                 controls=Path('/work/xmla-probe-controls.jsonl'),max_bytes=65536)
        print(json.dumps(result),flush=True)
        return 0 if result['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
