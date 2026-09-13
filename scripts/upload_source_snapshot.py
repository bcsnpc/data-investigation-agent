"""Upload verified immutable source files to their isolated OneLake directory."""
import argparse
import hashlib
import json
from pathlib import Path
import requests
from uuid import UUID
from source_snapshot import verify_registered, verify, digest
from metadata_config import ROOT, load_config
from metadata_auth import FabricCliTokens


def upload(config, estate, snapshot_id):
    snapshot_id=str(UUID(snapshot_id))
    reference=verify_registered(config['storage']['database'],snapshot_id)
    folder=ROOT/'.local/source-snapshots'/snapshot_id
    verify(folder,reference['manifest_sha256'])
    manifest=json.loads((folder/'manifest.json').read_text())
    workspace=str(UUID(estate['workspace_id']));lakehouse=str(UUID(estate['bronze_lakehouse_id']))
    if workspace != config['fabric']['workspace_id']:raise ValueError('Workspace mismatch')
    token=FabricCliTokens(config['fabric']['auth']['tenant_id']).get_token('https://storage.azure.com/.default')
    session=requests.Session()
    session.headers.update({'Authorization':'Bearer '+token,'x-ms-version':'2021-06-08'})
    base=f'https://onelake.dfs.fabric.microsoft.com/{workspace}/{lakehouse}/Files/source_snapshots'
    def call(method,url,allowed=(200,201,202),**kwargs):
        response=session.request(method,url,timeout=120,allow_redirects=False,**kwargs)
        if response.status_code not in allowed:raise RuntimeError('OneLake upload HTTP '+str(response.status_code))
        return response
    for directory in (base,base+'/'+snapshot_id):
        call('PUT',directory+'?resource=directory',allowed=(200,201,409))
    for name in [t['file'] for t in manifest['tables']]+['manifest.json']:
        path=folder/name;url=base+'/'+snapshot_id+'/'+name
        response=call('PUT',url+'?resource=file',headers={'If-None-Match':'*'},allowed=(200,201,409,412))
        if response.status_code in (409,412):
            remote=call('GET',url,stream=True);h=hashlib.sha256()
            for chunk in remote.iter_content(1048576):h.update(chunk)
            if h.hexdigest()!=digest(path):raise ValueError('Existing staged file differs; refusing overwrite')
        else:
            position=0
            with path.open('rb') as stream:
                while chunk:=stream.read(4*1024*1024):
                    call('PATCH',url+f'?action=append&position={position}',data=chunk)
                    position+=len(chunk)
            call('PATCH',url+f'?action=flush&position={position}&close=true',data=b'')
        print('Staged '+name,flush=True)
    return {'snapshot_id':snapshot_id,'manifest_sha256':reference['manifest_sha256'],
            'source_path':f'abfss://{workspace}@onelake.dfs.fabric.microsoft.com/{lakehouse}/Files/source_snapshots/{snapshot_id}'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--snapshot-id',required=True)
    args=parser.parse_args()
    print(json.dumps(upload(load_config(ROOT/'infra/metadata/development.json'),json.loads((ROOT/'infra/fabric/environment.json').read_text()),args.snapshot_id),indent=2))
