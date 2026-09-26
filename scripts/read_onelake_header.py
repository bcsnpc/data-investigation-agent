"""List a table's data files or read a bounded data-file header with the metadata identity; never decode rows."""
import contextlib
import io
import json
import re
from urllib.parse import quote
from uuid import UUID

HEADER_BYTES=4
LISTING_BYTES=1_000_000


def _directory(request):
    lakehouse=str(UUID(request['lakehouse']));table=request['table']
    if not isinstance(table,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,200}',table):raise ValueError('Invalid table identity')
    return lakehouse+'/Tables/'+table


def inspect(request,get):
    """`get(url,headers,limit)` returns (status, bytes). Mode `listing` or `header`; counts and statuses only."""
    base='https://onelake.dfs.fabric.microsoft.com/'+str(UUID(request['workspace']))
    directory=_directory(request)
    if request['mode']=='listing':
        status,raw=get(base+'?resource=filesystem&directory='+quote(directory,safe='/')+'&recursive=false&maxResults=100',
                       {},LISTING_BYTES)
        files=sorted(x['name'] for x in json.loads(raw).get('paths',[])
                     if x.get('name','').endswith('.parquet') and x['name'].startswith(directory+'/')
                     and '..' not in x['name'].split('/'))
        return {'status':'AVAILABLE','http_status':status,'data_files':files}
    if request['mode']=='header':
        name=request['file']
        if not isinstance(name,str) or not name.startswith(directory+'/') or not name.endswith('.parquet') or '..' in name.split('/'):
            raise ValueError('Invalid data file identity')
        status,raw=get(base+'/'+quote(name,safe='/'),{'Range':f'bytes=0-{HEADER_BYTES-1}'},HEADER_BYTES)
        return {'status':'AVAILABLE','http_status':status,'bytes_read':len(raw),'parquet_magic_matches':raw==b'PAR1'}
    raise ValueError('Unsupported mode')


def bounded_get(token):
    def get(url,headers,limit):
        from urllib.request import Request,build_opener
        from metadata_auth import NoRedirect
        with build_opener(NoRedirect()).open(Request(url,headers={'Authorization':'Bearer '+token,**headers}),timeout=45) as response:
            raw=response.read(limit+1)
            if len(raw)>limit:raise ValueError('Byte limit exceeded')
            return response.status,raw
    return get


if __name__=='__main__':
    import sys
    try:
        request=json.load(sys.stdin)
        from fabric_cli.core.fab_auth import FabAuth
        with contextlib.redirect_stdout(io.StringIO()):
            token=FabAuth().get_access_token(['https://storage.azure.com/.default'],interactive_renew=False)
        if not token:raise RuntimeError('Storage authentication unavailable')
        print(json.dumps(inspect(request,bounded_get(token))))
    except Exception as exc:
        code=getattr(exc,'code',None)
        print(json.dumps({'status':'UNAVAILABLE','error_type':type(exc).__name__,
                          'http_status':code if isinstance(code,int) else None}));raise SystemExit(1)
