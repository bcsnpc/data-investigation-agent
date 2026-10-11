"""Reader-only, isolated metadata transport for scoped report/page choices."""
import base64
import json
import re
import sys
from investigator.native_identity import profile
from metadata_auth import MetadataHttp


def read(request, *, application=None, token=None, http_factory=MetadataHttp, meter=None):
    if set(request)!={'endpoint','workspace_ids','reader'}:
        raise ValueError('Unexpected report metadata request fields')
    reader=profile(request['reader'])
    match=re.fullmatch(r'groups/([0-9a-f-]{36})/reports(?:/([0-9a-f-]{36})/pages)?',request['endpoint'])
    if not match or match[1] not in request['workspace_ids']:
        raise ValueError('Report metadata endpoint outside declared scope')
    if 'workspace_ids' in reader and not set(request['workspace_ids'])<=set(reader['workspace_ids']):
        raise ValueError('Report metadata workspace exceeds reader allowlist')
    if application is None or token is None:
        from connect_fixture_reader import application, token
    class Tokens:
        def get_token(self,scope):
            if scope!='https://analysis.windows.net/powerbi/api/.default':
                raise ValueError('Unexpected report metadata audience')
            access=token(application(reader['tenant_id']),reader['account'],reader['tenant_id'],scope)
            part=access.split('.')[1]
            claims=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
            if (claims.get('oid')!=reader['principal_id'] or claims.get('tid')!=reader['tenant_id']
                    or claims.get('aud','').rstrip('/')!='https://analysis.windows.net/powerbi/api'
                    or (claims.get('preferred_username') or claims.get('upn') or '').casefold()!=reader['account'].casefold()):
                raise ValueError('Report metadata reader principal differs')
            return access
    result=http_factory(Tokens(),meter=meter)(request['endpoint'],audience='powerbi')
    return {'status_code':result['status_code'],'body':result['text'],
        'reader':{k:reader[k] for k in ('tenant_id','principal_id','account')}}


if __name__=='__main__':
    try:
        metered='--metered' in sys.argv
        request=json.loads(sys.stdin.readline()) if metered else json.load(sys.stdin)
        if not metered:raise ValueError('Live metadata requires physical-request admission')
        from metadata_worker import metered_request
        print(json.dumps(read(request,meter=metered_request)))
    except Exception as exc:
        print(json.dumps({'error_type':type(exc).__name__}))
        raise SystemExit(1)
