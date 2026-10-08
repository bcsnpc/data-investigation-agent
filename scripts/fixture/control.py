"""Create-only fixture controls, separate from diagnostic execution identities.

Every physical dispatch is admitted by the existing estate governor. Mutation
receipts are durable and never retried after an uncertain dispatch. Tokens are
held in memory and are absent from the request/response journal.
"""
import json
import time
from pathlib import Path
from urllib.request import Request, build_opener
from urllib.error import HTTPError
from uuid import UUID
from datetime import datetime, timezone
from metadata_auth import NoRedirect
from publish_import_fixture import Journal
from investigator.onboarding import digest


class ControlError(RuntimeError):
    pass


class FixtureControl:
    def __init__(self, workspace, governor, directory, session, transport,
                 sleep=time.sleep):
        self.workspace=str(UUID(workspace));self.governor=governor
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.session=session;self.transport=transport;self.sleep=sleep
        self.dispatched=0
        self.journal=Journal(self.directory/'mutations.sqlite')
        self.path=self.directory/(session+'.json')
        if self.path.exists():raise FileExistsError('Preserve original control session; use a distinct continuation')
        self.record={'started':datetime.now(timezone.utc).isoformat(),'workspace_id':self.workspace,
                     'session_id':session,'status':'PREPARING','requests':[],
                     'budget_before':governor.snapshot()}
        self.save()

    def save(self):
        self.record['seal']=digest({k:v for k,v in self.record.items() if k!='seal'})
        self.path.write_text(json.dumps(self.record,indent=2)+'\n',encoding='utf8')

    def close(self):
        self.journal.db.close()

    def __enter__(self):return self
    def __exit__(self,*args):self.close()

    def call(self, endpoint, method='GET', body=None, *, audience='fabric', key=None):
        if '://' in endpoint or endpoint.startswith('/') or '..' in endpoint.split('/'):
            raise ValueError('Control endpoint must be relative')
        if audience=='fabric':
            permitted=endpoint.startswith('workspaces/'+self.workspace+'/') or endpoint=='workspaces/'+self.workspace
            permitted|=(endpoint.startswith('operations/') and method=='GET') or (endpoint.startswith('connections/') and method=='GET')
        elif audience=='powerbi':permitted=endpoint.startswith('groups/'+self.workspace+'/')
        else:permitted=False
        if not permitted:raise ValueError('Control escaped approved workspace/surface')
        if method!='GET' and not key and not endpoint.split('?')[0].endswith('/getDefinition'):
            raise ValueError('Mutation needs durable key')
        entry={'endpoint':endpoint,'method':method,'body':body,'audience':audience,
               'started':datetime.now(timezone.utc).isoformat()}
        self.record['requests'].append(entry);self.save()
        request={'endpoint':endpoint,'method':method,'body':body,'audience':audience}
        def dispatch():
            self.dispatched+=1
            return self.transport(**request)
        def send():
            return self.governor.metered_read(self.session,'request-'+str(len(self.record['requests'])),
                                             dispatch)
        try:
            response=self.journal.mutation(key,request,send) if key else send()
            entry.update(response=response,ended=datetime.now(timezone.utc).isoformat());self.save()
            if response.get('status_code') not in (200,201,202):
                raise ControlError('HTTP '+str(response.get('status_code'))+': '+json.dumps(response.get('text')))
            return response
        except Exception as exc:
            entry.update(error_type=type(exc).__name__,error=str(exc));self.save();raise

    def resolve(self, response, *, expect_result=True):
        if response['status_code']!=202:return response['text']
        headers={k.lower():v for k,v in response.get('headers',{}).items()}
        operation=str(UUID(headers['x-ms-operation-id']))
        for _ in range(12):
            self.sleep(min(60,max(1,int(headers.get('retry-after','5')))))
            status=self.call('operations/'+operation)['text']
            if status.get('status')=='Succeeded':
                return self.call('operations/'+operation+'/result')['text'] if expect_result else status
            if status.get('status') in ('Failed','Cancelled'):raise ControlError('Provisioning '+json.dumps(status))
        raise ControlError('Bounded LRO still pending; inspect same operation, never re-create')

    def create(self, key, collection, body):
        result=self.resolve(self.call('workspaces/'+self.workspace+'/'+collection,'POST',body,key=key))
        str(UUID(result['id']))
        if result.get('workspaceId',self.workspace)!=self.workspace:raise ControlError('Returned item outside approved workspace')
        return result

    def finish(self, status, *, error=None, details=None):
        self.record.update(status=status,ended=datetime.now(timezone.utc).isoformat(),budget_after=self.governor.snapshot())
        self.record['physical_requests']=self.dispatched
        if error:self.record.update(error_type=type(error).__name__,error=str(error))
        if details:self.record['details']=details
        self.save();return self.record


def publisher_transport(tokens):
    """Existing publisher login only; no login, new audience grant or redirect."""
    services={'fabric':('https://api.fabric.microsoft.com/v1/','https://api.fabric.microsoft.com/.default'),
              'powerbi':('https://api.powerbi.com/v1.0/myorg/','https://analysis.windows.net/powerbi/api/.default')}
    def send(endpoint,method,body,audience):
        base,scope=services[audience]
        request=Request(base+endpoint,method=method,data=json.dumps(body).encode() if body is not None else None,
                        headers={'Authorization':'Bearer '+tokens.get_token(scope),'Content-Type':'application/json'})
        try:
            with build_opener(NoRedirect()).open(request,timeout=90) as response:
                raw=response.read(4_000_001);status=response.status;headers=dict(response.headers)
        except HTTPError as error:raw=error.read(4_000_001);status=error.code;headers=dict(error.headers)
        if len(raw)>4_000_000:raise ControlError('Control response exceeded bound')
        try:body=json.loads(raw) if raw else {}
        except (ValueError,UnicodeDecodeError):body=raw.decode('utf8',errors='replace')
        return {'status_code':status,'headers':headers,'text':body}
    return send
