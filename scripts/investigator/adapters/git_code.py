"""Read-only repository content adapter; no clone, shell or writable token path."""
import base64
import json
import re
from urllib.parse import urlsplit,quote,urlencode
from ..code_sources import MAX_BYTES,relative_path,validate_source
from ..process_tape import bounded_call

class RepositoryReader:
    def __init__(self,request):self.request=request;self.revisions={}
    def __call__(self,source,path,meter):
        validate_source(source)
        if source['kind']!='GIT_REPOSITORY':raise ValueError('Repository code source kind differs')
        url=urlsplit(source['repo_url'])
        parts=url.path.strip('/').removesuffix('.git').split('/')
        if url.hostname!='github.com' or len(parts)!=2 or any(not re.fullmatch(r'[A-Za-z0-9_.-]+',v) for v in parts):
            raise ValueError('Repository host adapter not installed for this source')
        repo='/'.join(parts);key=(source['id'],source['repo_url'],source['ref'],source['identity'])
        def call(endpoint):
            descriptor={'method':'GET','endpoint':endpoint,'identity':source['identity'],'token_reference':source['token_reference']}
            response=meter(lambda:bounded_call('code_repository_http',descriptor,lambda:self.request('GET',endpoint)))
            if response['status']!=200:raise RuntimeError('Repository HTTP '+str(response['status'])+': '+json.dumps(response['body'],sort_keys=True))
            return response['body']
        if key not in self.revisions:
            ref=source['ref']
            if re.fullmatch('[0-9a-f]{40}',ref):revision=ref
            else:
                branch=call('repos/'+repo+'/git/ref/heads/'+quote(ref,safe=''))
                if branch.get('object',{}).get('type')!='commit':raise ValueError('Repository ref is not a commit')
                revision=branch['object']['sha']
            if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('Repository revision is not immutable')
            self.revisions[key]=revision
        revision=self.revisions[key]
        full=relative_path(source['path_prefix'])+'/'+relative_path(path)
        def content(file):
            body=call('repos/'+repo+'/contents/'+quote(file,safe='/')+'?'+urlencode({'ref':revision}))
            if body.get('type')!='file' or body.get('encoding')!='base64' or body.get('path')!=file:
                raise ValueError('Repository content is not the declared regular file')
            if not isinstance(body.get('size'),int) or not 0<=body['size']<=MAX_BYTES:raise ValueError('Repository file exceeds bound')
            raw=base64.b64decode(''.join(body['content'].split()),validate=True)
            if len(raw)!=body['size']:raise ValueError('Repository file size differs')
            return raw
        raw=content(full);identity=None
        if full.endswith('/notebook-content.py'):
            metadata=content(full.rsplit('/',1)[0]+'/.platform')
            identity={'logical_id':json.loads(metadata).get('config',{}).get('logicalId')}
        return {'content':raw.hex(),'item_identity':identity,'locator':source['repo_url']+'@'+revision+':'+full,'revision':revision}
