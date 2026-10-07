"""Closed code-source declarations and one bounded, non-executing representation."""
from .privacy_identities import text_digest
import copy
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from jsonschema import Draft202012Validator
from .process_tape import bounded_call, utc_now

MAX_BYTES = 1_000_000
MAX_CELLS = 512

def bounded_file(path):
    with path.open('rb') as stream:
        value=stream.read(MAX_BYTES+1)
    if len(value)>MAX_BYTES:raise ValueError('Code file exceeds bound')
    return value

def obj(properties):
    return {'type':'object','additionalProperties':False,'properties':properties,
            'required':list(properties)}

TEXT={'type':'string','minLength':1,'maxLength':500}
UUID={'type':'string','pattern':r'^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$'}
CODE_SOURCE_SCHEMA={'oneOf':[
    obj({'id':TEXT,'kind':{'const':'GIT_REPOSITORY'},'identity':TEXT,
         'repo_url':TEXT,'ref':TEXT,'path_prefix':TEXT,'token_reference':TEXT}),
    obj({'id':TEXT,'kind':{'const':'LOCAL_PATH'},'identity':TEXT,'path':TEXT}),
    obj({'id':TEXT,'kind':{'const':'PLATFORM_ITEM_API'},'identity':TEXT,
         'workspace':UUID,'item_ids':{'type':'array','items':UUID,'minItems':1,'maxItems':32,'uniqueItems':True}})]}

def relative_path(value):
    if not isinstance(value,str):raise ValueError('code_source.path: safe relative path required')
    p=PurePosixPath(value)
    if not isinstance(value,str) or not value or '\\' in value or p.is_absolute() or '..' in p.parts or ':' in value:
        raise ValueError('code_source.path: safe relative path required')
    return p.as_posix()

def validate_source(source):
    branch=next((b for b in CODE_SOURCE_SCHEMA['oneOf'] if isinstance(source,dict) and b['properties']['kind']['const']==source.get('kind')),None)
    if branch is None:raise ValueError('code_source.kind: unknown code source kind')
    errors=list(Draft202012Validator(branch).iter_errors(source))
    if errors:
        leaf=errors[0]
        field='.'.join(map(str,leaf.path))
        if leaf.validator=='required':field=next(k for k in branch['required'] if k not in source)
        raise ValueError('code_source.'+field+': '+leaf.message)
    if source['kind']=='GIT_REPOSITORY':
        from urllib.parse import urlsplit
        u=urlsplit(source['repo_url'])
        if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment:
            raise ValueError('code_source.repo_url: credential-free HTTPS repository required')
        relative_path(source['path_prefix'])
    return copy.deepcopy(source)

def validate_sources(manifest):
    sources=manifest['lineage'].get('code_sources',[])
    identities={i['id']:i for i in manifest['identities']}
    investigation={l['reach']['reader'] for l in manifest['layers']+manifest['resources']}
    ids=set()
    for source in sources:
        validate_source(source)
        if source['id'] in ids:raise ValueError('manifest.lineage.code_sources.id: duplicate')
        ids.add(source['id'])
        if source['identity'] not in identities:raise ValueError('manifest.lineage.code_sources.identity: undeclared identity')
        scopes=[s for s in identities[source['identity']]['scopes'] if s['resource']==source['id']]
        if len(scopes)!=1 or 'READ' not in scopes[0]['rights']:
            raise ValueError('manifest.lineage.code_sources.identity: no declared READ scope')
        if source['kind']=='GIT_REPOSITORY' and source['token_reference']!=identities[source['identity']]['credential_reference']:
            raise ValueError('manifest.lineage.code_sources.token_reference: differs from declared identity credential')
        if source['kind']=='PLATFORM_ITEM_API':
            if source['identity'] in investigation:
                raise ValueError('manifest.lineage.code_sources.identity: PLATFORM_ITEM_API must not use an investigation reader')
            if not any(l['code']=='CODE_READ_REQUIRES_WRITE_SCOPE' and l['resource']==source['id'] for l in manifest['accepted_limits']):
                raise ValueError('manifest.accepted_limits: PLATFORM_ITEM_API requires CODE_READ_REQUIRES_WRITE_SCOPE for this code source')
    layers={l['id'] for l in manifest['layers']}
    for location in manifest['lineage'].get('code_locations',[]):
        if location['from_layer'] not in layers or location['to_layer'] not in layers:
            raise ValueError('manifest.lineage.code_locations: undeclared boundary layer')
        if location['may_infer_from_code'] and not location['locations']:
            raise ValueError('manifest.lineage.code_locations.locations: inference enabled without code location')
        for file in location['locations']:
            if file['source'] not in ids:raise ValueError('manifest.lineage.code_locations.source: undeclared source')
            relative_path(file['path'])
    return sources

def normalize(path, content, *, item_identity=None):
    """Never execute code. Cell text and physical line locations are retained."""
    if not isinstance(content,bytes) or len(content)>MAX_BYTES:raise ValueError('Code content exceeds bound')
    text=content.decode('utf-8-sig');suffix=PurePosixPath(path).suffix.casefold()
    cells=[]
    if suffix=='.ipynb':
        value=json.loads(text)
        if value.get('nbformat')!=4 or not isinstance(value.get('cells'),list):raise ValueError('Unsupported notebook document')
        for index,cell in enumerate(value['cells']):
            if cell.get('cell_type')!='code':continue
            source=cell['source'];source=''.join(source) if isinstance(source,list) else source
            if not isinstance(source,str):raise ValueError('Notebook code source differs')
            language=value.get('metadata',{}).get('language_info',{}).get('name','python')
            cells.append({'id':str(index),'language':language,'source':source,'line_start':1,'line_end':max(1,len(source.splitlines()))})
    elif suffix in ('.py','.sql'):
        language='python' if suffix=='.py' else 'sql'
        lines=text.splitlines(keepends=True);start=1;chunk=[]
        for number,line in enumerate(lines,1):
            if re.match(r'^\s*#\s*(?:COMMAND -+|CELL [*\-]+)\s*$',line):
                if chunk:cells.append({'id':str(len(cells)),'language':language,'source':''.join(chunk),'line_start':start,'line_end':number-1})
                start=number+1;chunk=[]
            else:chunk.append(line)
        if chunk:cells.append({'id':str(len(cells)),'language':language,'source':''.join(chunk),'line_start':start,'line_end':max(start,len(lines))})
    else:raise ValueError('Unsupported code file extension: '+suffix)
    if len(cells)>MAX_CELLS:raise ValueError('Notebook cell count exceeds bound')
    return {'path':relative_path(path),'item_identity':item_identity,'content_hash':text_digest(content),'cells':cells}

def read(source,path,*,meter,root=None,git_fetch=None,item_fetch=None):
    """Each physical retrieval, including local IO, is admitted by the caller.

    Remote adapters return a bounded byte projection; credentials never enter
    the journal. Replay tests that projection, not upstream protocol decoding.
    """
    source=validate_source(source);path=relative_path(path)
    request={'source':source['id'],'kind':source['kind'],'identity':source['identity'],'path':path}
    def retrieve():
        if source['kind']=='LOCAL_PATH':
            folder=Path(source['path'])
            if not folder.is_absolute():
                if root is None:raise ValueError('Local source requires an explicit installation root')
                folder=Path(root)/folder
            folder=folder.resolve();target=(folder/path).resolve()
            if not target.is_relative_to(folder):raise ValueError('Code file leaves declared source root')
            sidecar=target.parent/'.platform'
            result=meter(lambda:bounded_call('code_file',request,lambda:{
                'content':bounded_file(target).hex(),'item_identity':None,'locator':str(target),
                'has_metadata':sidecar.is_file()}))
            # Metadata presence is part of the recorded read, not re-discovered
            # from the live filesystem during replay.
            if result.pop('has_metadata'):
                if not sidecar.resolve().is_relative_to(folder):raise ValueError('Code metadata leaves declared source root')
                metadata=meter(lambda:bounded_call('code_file_metadata',{**request,'path':str(PurePosixPath(path).parent/'.platform')},
                    lambda:{'content':bounded_file(sidecar).hex()}))
                raw_metadata=bytes.fromhex(metadata['content'])
                if len(raw_metadata)>MAX_BYTES:raise ValueError('Code metadata exceeds bound')
                declaration=json.loads(raw_metadata)
                result['item_identity']={'logical_id':declaration.get('config',{}).get('logicalId')}
        else:
            fetch=git_fetch if source['kind']=='GIT_REPOSITORY' else item_fetch
            if fetch is None:raise ValueError('Code source transport unavailable: '+source['kind'])
            result=fetch(source,path,meter)
        if not isinstance(result,dict) or set(result)-{'content','item_identity','locator','revision'} or not {'content','item_identity','locator'}<=set(result):
            raise ValueError('Code source response shape differs')
        if len(result['content'])>MAX_BYTES*2:raise ValueError('Code source response exceeds bound')
        bytes.fromhex(result['content'])
        return result
    # Remote adapters wrap each physical request individually. Wrapping their
    # whole operation would hide nested budget events when replay skips IO.
    body=retrieve()
    raw=bytes.fromhex(body['content'])
    unit=normalize(path,raw,item_identity=body['item_identity'])
    receipt={**request,'locator':body['locator'],'content_hash':unit['content_hash'],'retrieved_at':utc_now(),
             'revision':body.get('revision'),'item_identity':copy.deepcopy(body['item_identity']),'provenance':'CODE_SOURCE_READ','replay_boundary':'BOUNDED_RESPONSE'}
    return unit,receipt
