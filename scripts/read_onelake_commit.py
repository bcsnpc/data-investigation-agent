"""Read bounded Delta commit metadata with the metadata identity; never read table rows."""
import contextlib
import io
import json
import re
from urllib.parse import quote
from urllib.request import Request,build_opener
from uuid import UUID
from metadata_auth import NoRedirect


def read(request):
    workspace=str(UUID(request['workspace']));lakehouse=str(UUID(request['lakehouse']))
    table=request['table']
    if not isinstance(table,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,200}',table):raise ValueError('Invalid table identity')
    from fabric_cli.core.fab_auth import FabAuth
    with contextlib.redirect_stdout(io.StringIO()):
        token=FabAuth().get_access_token(['https://storage.azure.com/.default'],interactive_renew=False)
    if not token:raise RuntimeError('Storage authentication unavailable')
    directory=f'{lakehouse}/Tables/{table}/_delta_log'
    url=(f'https://onelake.dfs.fabric.microsoft.com/{workspace}?resource=filesystem&directory='
         +quote(directory,safe='/')+'&recursive=false&maxResults=100')
    headers={'Authorization':'Bearer '+token}
    with build_opener(NoRedirect()).open(Request(url,headers=headers),timeout=60) as response:
        listing=json.load(response)
    commits=sorted(x['name'] for x in listing.get('paths',[]) if re.search(r'/[0-9]{20}\.json$',x.get('name','')))
    if not commits:return {'status':'EMPTY_RESPONSE','latest_commit':None}
    target='https://onelake.dfs.fabric.microsoft.com/'+workspace+'/'+quote(commits[-1],safe='/')
    with build_opener(NoRedirect()).open(Request(target,headers=headers),timeout=60) as response:
        raw=response.read(1_000_001)
    if len(raw)>1_000_000:raise ValueError('Delta commit metadata exceeds cap')
    actions=[json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    info=next((x['commitInfo'] for x in actions if isinstance(x,dict) and isinstance(x.get('commitInfo'),dict)),None)
    if info is None:return {'status':'EMPTY_RESPONSE','latest_commit':commits[-1]}
    return {'status':'AVAILABLE','latest_commit':commits[-1],
            'commit_info':{k:info[k] for k in ('timestamp','operation','operationParameters','operationMetrics') if k in info}}


if __name__=='__main__':
    import sys
    try:print(json.dumps(read(json.load(sys.stdin))))
    except Exception as exc:
        print(json.dumps({'status':'UNAVAILABLE','error_type':type(exc).__name__}));raise SystemExit(1)
