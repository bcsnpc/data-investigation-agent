"""Offline retry inputs from exact retained dependencies; no Azure or model I/O."""
import argparse
from contextlib import closing,contextmanager
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import zipfile
from cloud_runner_context import PREPARED_NAMES

INPUT_MEMBERS=frozenset({'catalog.sqlite','inventory.sqlite','estate.json','verification-spec.json','form.json','operator-plan.json','endpoints.json'})


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def dependency_manifest(path,expected_hash):
    if sha(path)!=expected_hash:raise ValueError('DEPENDENCY_MANIFEST_HASH_DIFFERS')
    v=json.loads(Path(path).read_bytes())
    if v.get('version')!='cloud-verifier-cas-dependencies-v1' or v.get('kind')!='prepared' or v.get('status')!='RETAINED':
        raise ValueError('COMPLETE_PREPARED_DEPENDENCIES_REQUIRED')
    rows=v['files']
    if len(rows)!=len(PREPARED_NAMES) or {r['name'] for r in rows}!=PREPARED_NAMES:
        raise ValueError('PREPARED_DEPENDENCY_INVENTORY_DIFFERS')
    for r in rows:
        if set(r)!={'name','sha256','bytes'} or not re.fullmatch('[a-f0-9]{64}',r['sha256']) or type(r['bytes']) is not int or r['bytes']<0:
            raise ValueError('PREPARED_DEPENDENCY_REFERENCE')
    return v


def restore_dependencies(manifest,files,destination):
    """Caller supplies existing CAS Files. CLI itself exposes local CAS only."""
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=False)
    for row in manifest['files']:
        target=destination/row['name'];files.restore(row['sha256'],target)
        if target.stat().st_size!=row['bytes'] or sha(target)!=row['sha256']:
            raise ValueError('RESTORED_DEPENDENCY_HASH_DIFFERS')
    return destination


def selected_parent(catalog,environment,expected):
    # ModelStore's normal read protocol, with an explicitly readonly connector.
    # No initializer/schema write or shared-state connection is needed offline.
    from investigator.onboarding import ModelStore,digest
    @contextmanager
    def connect():
        with closing(sqlite3.connect(Path(catalog).resolve().as_uri()+'?mode=ro',uri=True)) as db:
            db.row_factory=sqlite3.Row;yield db
    store=ModelStore.__new__(ModelStore);store.shared_catalog=None
    store.environment=environment;store.context_pins={};store.connect=connect
    actual=store.get(expected['id'])
    if actual!=expected:raise ValueError('RETRY_SOURCE_SELECTED_MODEL_DIFFERS_FROM_RETAINED_PARENT')
    return {'model_id':actual['id'],'revision':actual['revision'],'model_sha256':digest(actual)}


def rebuild(source_zip,source_sha256,prepared_manifest,manifest_sha256,prepared_directory,output,*,request_key,decision):
    if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}',request_key) or not isinstance(decision,str) or not decision.strip():
        raise ValueError('RETRY_REQUEST_AND_OWNER_DECISION_REQUIRED')
    source_zip=Path(source_zip);prepared_directory=Path(prepared_directory).resolve()
    if sha(source_zip)!=source_sha256:raise ValueError('SOURCE_INPUT_ZIP_HASH_DIFFERS')
    retained=dependency_manifest(prepared_manifest,manifest_sha256)
    for row in retained['files']:
        path=prepared_directory/row['name']
        if path.is_symlink() or getattr(path.lstat(),'st_file_attributes',0)&0x400:
            raise ValueError('PREPARED_DEPENDENCY_LINK_FORBIDDEN')
        if not path.resolve().is_relative_to(prepared_directory) or path.stat().st_size!=row['bytes'] or sha(path)!=row['sha256']:
            raise ValueError('PREPARED_DEPENDENCY_HASH_DIFFERS')
    with zipfile.ZipFile(source_zip) as original:
        members=original.infolist()
        if len(members)!=len(INPUT_MEMBERS) or {r.filename for r in members}!=INPUT_MEMBERS or sum(r.file_size for r in members)>1_500_000_000:
            raise ValueError('SOURCE_INPUT_INVENTORY_DIFFERS')
        manifest=json.loads(original.read('estate.json'))
        parent=json.loads((prepared_directory/'model.json').read_bytes())
        proof=selected_parent(prepared_directory/'catalog.sqlite',manifest['environment'],parent)
        plan=json.loads(original.read('operator-plan.json'))
        # The original retained discovery context must still be in the new parent.
        with closing(sqlite3.connect((prepared_directory/'catalog.sqlite').as_uri()+'?mode=ro',uri=True)) as db:
            row=db.execute('SELECT hash FROM enterprise_scans WHERE id=? AND environment=?',(plan['source_context'],manifest['environment'])).fetchone()
        if row is None or row[0]!=plan['source_context_hash']:raise ValueError('RETRY_RETAINED_SOURCE_CONTEXT_MISSING')
        form=json.loads(original.read('form.json'));form['request_key']=request_key
        plan['decision']=decision
        plan['retry_parent']={**proof,'source_input_zip_sha256':source_sha256,'dependency_manifest_sha256':manifest_sha256}
        output=Path(output);output.mkdir(parents=True,exist_ok=False)
        target=output/'inputs.zip'
        with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as result:
            for name in sorted(INPUT_MEMBERS):
                if name in ('catalog.sqlite','inventory.sqlite'):
                    result.write(prepared_directory/name,name)
                elif name in ('form.json','operator-plan.json'):
                    result.writestr(name,json.dumps(form if name=='form.json' else plan,sort_keys=True,indent=2).encode())
                else:
                    with original.open(name) as src,result.open(name,'w') as dst:shutil.copyfileobj(src,dst)
    rows={r['name']:r for r in retained['files']}
    receipt={'version':'runner-retry-input-derivation-v1','physical_requests':0,'model_calls':0,
        'source_zip_sha256':source_sha256,'dependency_manifest_sha256':manifest_sha256,
        'selected_parent':proof,'archive_sha256':sha(target),'archive_bytes':target.stat().st_size,
        'catalog_sha256':rows['catalog.sqlite']['sha256'],'inventory_sha256':rows['inventory.sqlite']['sha256'],
        'unchanged_members':sorted(INPUT_MEMBERS-{'catalog.sqlite','inventory.sqlite','form.json','operator-plan.json'}),
        'changes':['exact retained parent catalog and inventory','fresh form request key','owner retry decision and parent provenance'],
        'originals_edited':False}
    (output/'input-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2),encoding='utf8')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source-zip','prepared-manifest','prepared-directory','output'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('source-sha256','manifest-sha256','request-key','decision'):p.add_argument('--'+name,required=True)
    a=p.parse_args();print(json.dumps(rebuild(a.source_zip,a.source_sha256,a.prepared_manifest,a.manifest_sha256,a.prepared_directory,a.output,request_key=a.request_key,decision=a.decision),sort_keys=True))


if __name__=='__main__':main()
